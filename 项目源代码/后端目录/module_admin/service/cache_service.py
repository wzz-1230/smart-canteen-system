from fastapi import Request

from common.enums import RedisInitKeyConfig
from common.vo import CrudResponseModel
from config.get_redis import RedisUtil
from module_admin.entity.vo.cache_vo import CacheInfoModel, CacheMonitorModel


def _safe_decode(value):
    """
    对从Redis返回的值进行安全解码，避免非UTF-8字节导致异常。
    """
    if value is None:
        return None
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin-1', errors='replace')
    if isinstance(value, str):
        return value
    return str(value)


def _safe_info_dict(info_dict):
    """
    对redis.info()返回的字典进行安全处理，确保其中所有值均可被JSON序列化。
    """
    if not isinstance(info_dict, dict):
        return info_dict
    result = {}
    for k, v in info_dict.items():
        safe_key = _safe_decode(k) if isinstance(k, (bytes, str)) else str(k)
        if isinstance(v, dict):
            result[safe_key] = _safe_info_dict(v)
        elif isinstance(v, list):
            result[safe_key] = [
                _safe_decode(item) if isinstance(item, (bytes, str)) else item
                for item in v
            ]
        elif isinstance(v, bytes):
            result[safe_key] = _safe_decode(v)
        elif isinstance(v, str):
            try:
                v.encode('utf-8')
                result[safe_key] = v
            except UnicodeEncodeError:
                result[safe_key] = (
                    v.encode('latin-1', errors='replace').decode('utf-8', errors='replace')
                )
        else:
            result[safe_key] = v
    return result


class CacheService:
    """
    缓存监控模块服务层
    """

    @classmethod
    async def get_cache_monitor_statistical_info_services(
        cls, request: Request
    ) -> CacheMonitorModel:
        """
        获取缓存监控信息service

        :param request: Request对象
        :return: 缓存监控信息
        """
        try:
            info = await request.app.state.redis.info()
        except Exception:
            info = {}
        info = _safe_info_dict(info)
        try:
            db_size = await request.app.state.redis.dbsize()
        except Exception:
            db_size = 0
        try:
            command_stats_dict = await request.app.state.redis.info('commandstats')
        except Exception:
            command_stats_dict = {}
        command_stats_dict = _safe_info_dict(command_stats_dict)
        command_stats = []
        for key, value in command_stats_dict.items():
            try:
                call_num = value.get('calls') if isinstance(value, dict) else value
                command_stats.append(
                    {
                        'name': (
                            str(key).split('_')[-1]
                            if isinstance(key, (bytes, str))
                            else str(key)
                        ),
                        'value': str(call_num) if call_num is not None else '0',
                    }
                )
            except Exception:
                continue
        return CacheMonitorModel(commandStats=command_stats, dbSize=db_size, info=info)

    @classmethod
    async def get_cache_monitor_cache_name_services(cls) -> list[CacheInfoModel]:
        """
        获取缓存名称列表信息service

        :return: 缓存名称列表信息
        """
        return [
            CacheInfoModel(
                cacheKey='',
                cacheName=key_config.key,
                cacheValue='',
                remark=key_config.remark,
            )
            for key_config in RedisInitKeyConfig
        ]

    @classmethod
    async def get_cache_monitor_cache_key_services(
        cls, request: Request, cache_name: str
    ) -> list[str]:
        """
        获取缓存键名列表信息service

        :param request: Request对象
        :param cache_name: 缓存名称
        :return: 缓存键名列表信息
        """
        try:
            cache_keys: list[str] = await request.app.state.redis.keys(f'{cache_name}*')
        except Exception:
            cache_keys = []
        cache_key_list: list[str] = []
        for key in cache_keys:
            try:
                key_str = _safe_decode(key) if isinstance(key, bytes) else str(key)
                if key_str.startswith(f'{cache_name}:'):
                    cache_key_list.append(key_str.split(':', 1)[1])
            except Exception:
                continue
        return cache_key_list

    @classmethod
    async def get_cache_monitor_cache_value_services(
        cls, request: Request, cache_name: str, cache_key: str
    ) -> CacheInfoModel:
        """
        获取缓存内容信息service

        :param request: Request对象
        :param cache_name: 缓存名称
        :param cache_key: 缓存键名
        :return: 缓存内容信息
        """
        try:
            cache_value = await request.app.state.redis.get(
                f'{cache_name}:{cache_key}'
            )
        except Exception:
            cache_value = None
        if isinstance(cache_value, (bytes, str)):
            cache_value = _safe_decode(cache_value)
        return CacheInfoModel(
            cacheKey=cache_key, cacheName=cache_name, cacheValue=cache_value, remark=''
        )

    @classmethod
    async def clear_cache_monitor_cache_name_services(
        cls, request: Request, cache_name: str
    ) -> CrudResponseModel:
        """
        清除缓存名称对应所有键值service

        :param request: Request对象
        :param cache_name: 缓存名称
        :return: 操作缓存响应信息
        """
        try:
            cache_keys = await request.app.state.redis.keys(f'{cache_name}*')
        except Exception:
            cache_keys = []
        if cache_keys:
            try:
                await request.app.state.redis.delete(*cache_keys)
            except Exception:
                pass
        return CrudResponseModel(is_success=True, message=f'{cache_name}对应键值清除成功')

    @classmethod
    async def clear_cache_monitor_cache_key_services(
        cls, request: Request, cache_key: str
    ) -> CrudResponseModel:
        """
        清除缓存名称对应所有键值service

        :param request: Request对象
        :param cache_key: 缓存键名
        :return: 操作缓存响应信息
        """
        try:
            cache_keys = await request.app.state.redis.keys(f'*{cache_key}')
        except Exception:
            cache_keys = []
        if cache_keys:
            try:
                await request.app.state.redis.delete(*cache_keys)
            except Exception:
                pass
        return CrudResponseModel(is_success=True, message=f'{cache_key}清除成功')

    @classmethod
    async def clear_cache_monitor_all_services(cls, request: Request) -> CrudResponseModel:
        """
        清除所有缓存service

        :param request: Request对象
        :return: 操作缓存响应信息
        """
        try:
            cache_keys = await request.app.state.redis.keys()
        except Exception:
            cache_keys = []
        if cache_keys:
            try:
                await request.app.state.redis.delete(*cache_keys)
            except Exception:
                pass
        try:
            await RedisUtil.init_sys_dict(request.app.state.redis)
            await RedisUtil.init_sys_config(request.app.state.redis)
        except Exception:
            pass
        return CrudResponseModel(is_success=True, message='所有缓存清除成功')
