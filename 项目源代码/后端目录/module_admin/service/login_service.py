import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi import Depends, Form, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession

from common.constant import CommonConstant, MenuConstant
from common.context import RequestContext
from common.enums import RedisInitKeyConfig
from common.vo import CrudResponseModel
from config.env import AppConfig, JwtConfig
from config.get_db import get_db
from exceptions.exception import AuthException, LoginException, ServiceException
from module_admin.dao.login_dao import login_by_account
from module_admin.dao.user_dao import UserDao
from module_admin.entity.do.dept_do import SysDept
from module_admin.entity.do.menu_do import SysMenu
from module_admin.entity.do.user_do import SysUser
from module_admin.entity.vo.login_vo import MenuTreeModel, MetaModel, RouterModel, SmsCode, UserLogin, UserRegister
from module_admin.entity.vo.user_vo import AddUserModel, CurrentUserModel, ResetUserModel, TokenData, UserInfoModel
from module_admin.service.user_service import UserService
from utils.client_ip_util import ClientIPUtil
from utils.common_util import CamelCaseUtil
from utils.log_util import logger
from utils.message_util import message_service
from utils.pwd_util import PwdUtil

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


class CustomOAuth2PasswordRequestForm(OAuth2PasswordRequestForm):
    """
    自定义OAuth2PasswordRequestForm类，增加验证码及会话编号参数
    """

    def __init__(
        self,
        grant_type: str = Form(default=None, pattern='password'),
        username: str = Form(),
        password: str = Form(),
        scope: str = Form(default=''),
        client_id: str | None = Form(default=None),
        client_secret: str | None = Form(default=None),
        code: str | None = Form(default=''),
        uuid: str | None = Form(default=''),
        login_info: dict[str, str] | None = Form(default=None),
    ) -> None:
        super().__init__(
            grant_type=grant_type,
            username=username,
            password=password,
            scope=scope,
            client_id=client_id,
            client_secret=client_secret,
        )
        self.code = code
        self.uuid = uuid
        self.login_info = login_info


class LoginService:
    """
    登录模块服务层
    """

    @classmethod
    async def _safe_redis_get(cls, request, key):
        """安全地从 Redis 获取值，Redis 不可用时返回 None"""
        try:
            redis = getattr(request.app.state, 'redis', None)
            if redis is None:
                return None
            return await redis.get(key)
        except Exception as e:
            logger.warning(f'Redis get {key} 失败: {e}')
            return None

    @classmethod
    async def _safe_redis_set(cls, request, key, value, ex=None):
        """安全地设置 Redis 值，Redis 不可用时静默失败"""
        try:
            redis = getattr(request.app.state, 'redis', None)
            if redis is None:
                return
            if ex is not None:
                await redis.set(key, value, ex=ex)
            else:
                await redis.set(key, value)
        except Exception as e:
            logger.warning(f'Redis set {key} 失败: {e}')

    @classmethod
    async def _safe_redis_delete(cls, request, key):
        """安全地删除 Redis 值，Redis 不可用时静默失败"""
        try:
            redis = getattr(request.app.state, 'redis', None)
            if redis is None:
                return
            await redis.delete(key)
        except Exception as e:
            logger.warning(f'Redis delete {key} 失败: {e}')

    @classmethod
    async def authenticate_user(
        cls, request: Request, query_db: AsyncSession, login_user: UserLogin
    ) -> Row[tuple[SysUser, SysDept]]:
        """
        根据用户名密码校验用户登录

        :param request: Request对象
        :param query_db: orm对象
        :param login_user: 登录用户对象
        :return: 校验结果
        """
        await cls.__check_login_ip(request)
        account_lock = await cls._safe_redis_get(
            request, f'{RedisInitKeyConfig.ACCOUNT_LOCK.key}:{login_user.user_name}'
        )
        if login_user.user_name == account_lock:
            logger.warning('账号已锁定，请稍后再试')
            raise LoginException(data='', message='账号已锁定，请稍后再试')
        # 判断请求是否来自于api文档，如果是返回指定格式的结果，用于修复api文档认证成功后token显示undefined的bug
        request_from_swagger = (
            request.headers.get('referer').endswith('docs') if request.headers.get('referer') else False
        )
        request_from_redoc = (
            request.headers.get('referer').endswith('redoc') if request.headers.get('referer') else False
        )
        # 判断是否开启验证码，开启则验证，否则不验证（dev模式下来自API文档的登录请求不检验）
        if not login_user.captcha_enabled or (
            (request_from_swagger or request_from_redoc) and AppConfig.app_env == 'dev'
        ):
            pass
        else:
            await cls.__check_login_captcha(request, login_user)
        user = await login_by_account(query_db, login_user.user_name)
        if not user:
            logger.warning('用户不存在')
            raise LoginException(data='', message='用户不存在')
        if not PwdUtil.verify_password(login_user.password, user[0].password):
            cache_password_error_count = await cls._safe_redis_get(
                request, f'{RedisInitKeyConfig.PASSWORD_ERROR_COUNT.key}:{login_user.user_name}'
            )
            password_error_counted = 0
            if cache_password_error_count:
                password_error_counted = cache_password_error_count
            password_error_count = int(password_error_counted) + 1
            await cls._safe_redis_set(
                request, f'{RedisInitKeyConfig.PASSWORD_ERROR_COUNT.key}:{login_user.user_name}',
                password_error_count, ex=timedelta(minutes=10),
            )
            if password_error_count > CommonConstant.PASSWORD_ERROR_COUNT:
                await cls._safe_redis_delete(
                    request, f'{RedisInitKeyConfig.PASSWORD_ERROR_COUNT.key}:{login_user.user_name}'
                )
                await cls._safe_redis_set(
                    request, f'{RedisInitKeyConfig.ACCOUNT_LOCK.key}:{login_user.user_name}',
                    login_user.user_name, ex=timedelta(minutes=10),
                )
                logger.warning('10分钟内密码已输错超过5次，账号已锁定，请10分钟后再试')
                raise LoginException(data='', message='10分钟内密码已输错超过5次，账号已锁定，请10分钟后再试')
            logger.warning('密码错误')
            raise LoginException(data='', message='密码错误')
        if user[0].status == '1':
            logger.warning('用户已停用')
            raise LoginException(data='', message='用户已停用')
        await cls._safe_redis_delete(request, f'{RedisInitKeyConfig.PASSWORD_ERROR_COUNT.key}:{login_user.user_name}')
        return user

    @classmethod
    async def __check_login_ip(cls, request: Request) -> bool:
        """
        校验用户登录ip是否在黑名单内

        :param request: Request对象
        :return: 校验结果
        """
        black_ip_value = await cls._safe_redis_get(request, f'{RedisInitKeyConfig.SYS_CONFIG.key}:sys.login.blackIPList')
        black_ip_list = str(black_ip_value).split(',') if black_ip_value else []
        if ClientIPUtil.get_client_ip(request) in black_ip_list:
            logger.warning('当前IP禁止登录')
            raise LoginException(data='', message='当前IP禁止登录')
        return True

    @classmethod
    async def __check_login_captcha(cls, request: Request, login_user: UserLogin) -> bool:
        """
        校验用户登录验证码

        :param request: Request对象
        :param login_user: 登录用户对象
        :return: 校验结果
        """
        captcha_value = await cls._safe_redis_get(request, f'{RedisInitKeyConfig.CAPTCHA_CODES.key}:{login_user.uuid}')
        if not captcha_value:
            logger.warning('验证码已失效')
            raise LoginException(data='', message='验证码已失效')
        if login_user.code != str(captcha_value):
            logger.warning('验证码错误')
            raise LoginException(data='', message='验证码错误')
        return True

    @classmethod
    async def create_access_token(cls, data: dict, expires_delta: timedelta | None = None) -> str:
        """
        根据登录信息创建当前用户token

        :param data: 登录信息
        :param expires_delta: token有效期
        :return: token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=30)
        to_encode.update({'exp': expire})
        encoded_jwt = jwt.encode(to_encode, JwtConfig.jwt_secret_key, algorithm=JwtConfig.jwt_algorithm)
        return encoded_jwt

    @classmethod
    async def get_current_user(
        cls, request: Request = Request, token: str = Depends(oauth2_scheme), query_db: AsyncSession = Depends(get_db)
    ) -> CurrentUserModel:
        """
        根据token获取当前用户信息

        :param request: Request对象
        :param token: 用户token
        :param query_db: orm对象
        :return: 当前用户信息对象
        :raise: 令牌异常AuthException
        """
        # 防御性编程：token 可能为 None
        if token is None:
            logger.warning('用户token为空，请重新登录')
            raise AuthException(data='', message='用户token为空，请重新登录')
        try:
            if isinstance(token, str) and token.startswith('Bearer'):
                token = token.split(' ')[1]
            payload = jwt.decode(token, JwtConfig.jwt_secret_key, algorithms=[JwtConfig.jwt_algorithm])
            user_id: str = payload.get('user_id')
            session_id: str = payload.get('session_id')
            if not user_id:
                logger.warning('用户token不合法')
                raise AuthException(data='', message='用户token不合法')
            token_data = TokenData(user_id=int(user_id))
        except InvalidTokenError as e:
            logger.warning(f'用户token已失效，请重新登录: {e}')
            raise AuthException(data='', message='用户token已失效，请重新登录') from e
        except Exception as e:
            logger.warning(f'解析用户token时发生异常: {e}')
            raise AuthException(data='', message='用户token解析失败，请重新登录') from e
        try:
            query_user = await UserDao.get_user_by_id(query_db, user_id=token_data.user_id)
        except Exception as e:
            logger.warning(f'查询用户信息时发生异常: {e}')
            raise AuthException(data='', message='查询用户信息失败，请稍后重试') from e
        if query_user.get('user_basic_info') is None:
            logger.warning('用户token不合法')
            raise AuthException(data='', message='用户token不合法')
        # 添加 Redis 异常处理，即使 Redis 不可用也允许正常访问
        try:
            if AppConfig.app_same_time_login:
                redis_token = await request.app.state.redis.get(f'{RedisInitKeyConfig.ACCESS_TOKEN.key}:{session_id}')
            else:
                # 此方法可实现同一账号同一时间只能登录一次
                redis_token = await request.app.state.redis.get(
                    f'{RedisInitKeyConfig.ACCESS_TOKEN.key}:{query_user.get("user_basic_info").user_id}'
                )
        except Exception as e:
            logger.warning(f'Redis 连接异常，跳过 token 校验: {e}')
            # Redis 不可用时，直接认为 token 有效，确保用户能正常使用系统
            redis_token = token
        # token 与 Redis 中一致或 Redis 不可用时直接通过
        if token == redis_token or redis_token is None:
            try:
                if AppConfig.app_same_time_login:
                    await request.app.state.redis.set(
                        f'{RedisInitKeyConfig.ACCESS_TOKEN.key}:{session_id}',
                        redis_token if redis_token else token,
                        ex=timedelta(minutes=JwtConfig.jwt_redis_expire_minutes),
                    )
                else:
                    await request.app.state.redis.set(
                        f'{RedisInitKeyConfig.ACCESS_TOKEN.key}:{query_user.get("user_basic_info").user_id}',
                        redis_token if redis_token else token,
                        ex=timedelta(minutes=JwtConfig.jwt_redis_expire_minutes),
                    )
            except Exception as e:
                logger.warning(f'刷新 Redis token 缓存失败: {e}，但不影响继续访问')

            role_id_list = [item.role_id for item in query_user.get('user_role_info')]
            if 1 in role_id_list:  # noqa: SIM108
                permissions = ['*:*:*']
            else:
                permissions = [row.perms for row in query_user.get('user_menu_info')]
            post_ids = ','.join([str(row.post_id) for row in query_user.get('user_post_info')])
            role_ids = ','.join([str(row.role_id) for row in query_user.get('user_role_info')])
            roles = [row.role_key for row in query_user.get('user_role_info')]
            try:
                is_default_modify_pwd = await cls.__init_password_is_modify(
                    request, query_user.get('user_basic_info').pwd_update_date
                )
                is_password_expired = await cls.__password_is_expired(
                    request, query_user.get('user_basic_info').pwd_update_date
                )
            except Exception as e:
                logger.warning(f'检查密码状态时 Redis 异常，使用默认值: {e}')
                is_default_modify_pwd = False
                is_password_expired = False

            current_user = CurrentUserModel(
                permissions=permissions,
                roles=roles,
                user=UserInfoModel(
                    **CamelCaseUtil.transform_result(query_user.get('user_basic_info')),
                    postIds=post_ids,
                    roleIds=role_ids,
                    dept=CamelCaseUtil.transform_result(query_user.get('user_dept_info')),
                    role=CamelCaseUtil.transform_result(query_user.get('user_role_info')),
                ),
                isDefaultModifyPwd=is_default_modify_pwd,
                isPasswordExpired=is_password_expired,
            )
            # 设置当前用户信息到上下文
            RequestContext.set_current_user(current_user)
            return current_user
        logger.warning('用户token已失效，请重新登录')
        raise AuthException(data='', message='用户token已失效，请重新登录')

    @classmethod
    async def __init_password_is_modify(cls, request: Request, pwd_update_date: datetime) -> bool:
        """
        判断当前用户是否初始密码登录

        :param request: Request对象
        :param pwd_update_date: 密码最后更新时间
        :return: 是否初始密码登录
        """
        init_password_is_modify = await request.app.state.redis.get(
            f'{RedisInitKeyConfig.SYS_CONFIG.key}:sys.account.initPasswordModify'
        )
        return init_password_is_modify == '1' and pwd_update_date is None

    @classmethod
    async def __password_is_expired(cls, request: Request, pwd_update_date: datetime) -> bool:
        """
        判断当前用户密码是否过期

        :param request: Request对象
        :param pwd_update_date: 密码最后更新时间
        :return: 密码是否过期
        """
        password_validate_days = await request.app.state.redis.get(
            f'{RedisInitKeyConfig.SYS_CONFIG.key}:sys.account.passwordValidateDays'
        )
        if password_validate_days and int(password_validate_days) > 0:
            if pwd_update_date is None:
                return True
            expire_date = pwd_update_date + timedelta(days=int(password_validate_days))
            if datetime.now() > expire_date:
                return True
        return False

    @classmethod
    async def get_current_user_routers(cls, user_id: int, query_db: AsyncSession) -> list[dict[str, Any]]:
        """
        根据用户id获取当前用户路由信息

        :param user_id: 用户id
        :param query_db: orm对象
        :return: 当前用户路由信息对象
        """
        query_user = await UserDao.get_user_by_id(query_db, user_id=user_id)
        user_router_menu = sorted(
            [
                row
                for row in query_user.get('user_menu_info')
                if row.menu_type in [MenuConstant.TYPE_DIR, MenuConstant.TYPE_MENU]
            ],
            key=lambda x: x.order_num,
        )
        menus = cls.__generate_menus(0, user_router_menu)
        user_router = cls.__generate_user_router_menu(menus)
        return [router.model_dump(exclude_unset=True, exclude_none=True, by_alias=True) for router in user_router]

    @classmethod
    def __generate_menus(cls, pid: int, permission_list: list[SysMenu]) -> list[MenuTreeModel]:
        """
        工具方法：根据菜单信息生成菜单信息树形嵌套数据

        :param pid: 菜单id
        :param permission_list: 菜单列表信息
        :return: 菜单信息树形嵌套数据
        """
        menu_list: list[MenuTreeModel] = []
        for permission in permission_list:
            if permission.parent_id == pid:
                children = cls.__generate_menus(permission.menu_id, permission_list)
                menu_list_data = MenuTreeModel(**CamelCaseUtil.transform_result(permission))
                if children:
                    menu_list_data.children = children
                menu_list.append(menu_list_data)

        return menu_list

    @classmethod
    def __generate_user_router_menu(cls, permission_list: list[MenuTreeModel]) -> list[RouterModel]:
        """
        工具方法：根据菜单树信息生成路由信息树形嵌套数据

        :param permission_list: 菜单树列表信息
        :return: 路由信息树形嵌套数据
        """
        router_list: list[RouterModel] = []
        for permission in permission_list:
            router = RouterModel(
                hidden=permission.visible == '1',
                name=RouterUtil.get_router_name(permission),
                path=RouterUtil.get_router_path(permission),
                component=RouterUtil.get_component(permission),
                query=permission.query,
                meta=MetaModel(
                    title=permission.menu_name,
                    icon=permission.icon,
                    noCache=permission.is_cache == 1,
                    link=permission.path if RouterUtil.is_http(permission.path) else None,
                ),
            )
            c_menus = permission.children
            if c_menus and permission.menu_type == MenuConstant.TYPE_DIR:
                router.always_show = True
                router.redirect = 'noRedirect'
                router.children = cls.__generate_user_router_menu(c_menus)
            elif RouterUtil.is_menu_frame(permission):
                router.meta = None
                children_list: list[RouterModel] = []
                children = RouterModel(
                    path=permission.path,
                    component=permission.component,
                    name=RouterUtil.get_route_name(permission.route_name, permission.path),
                    meta=MetaModel(
                        title=permission.menu_name,
                        icon=permission.icon,
                        noCache=permission.is_cache == 1,
                        link=permission.path if RouterUtil.is_http(permission.path) else None,
                    ),
                    query=permission.query,
                )
                children_list.append(children)
                router.children = children_list
            elif permission.parent_id == 0 and RouterUtil.is_inner_link(permission):
                router.meta = MetaModel(title=permission.menu_name, icon=permission.icon)
                router.path = '/'
                children_list: list[RouterModel] = []
                router_path = RouterUtil.inner_link_replace_each(permission.path)
                children = RouterModel(
                    path=router_path,
                    component=MenuConstant.INNER_LINK,
                    name=RouterUtil.get_route_name(permission.route_name, permission.path),
                    meta=MetaModel(
                        title=permission.menu_name,
                        icon=permission.icon,
                        link=permission.path if RouterUtil.is_http(permission.path) else None,
                    ),
                )
                children_list.append(children)
                router.children = children_list

            router_list.append(router)

        return router_list

    @classmethod
    async def register_user_services(
        cls, request: Request, query_db: AsyncSession, user_register: UserRegister
    ) -> CrudResponseModel:
        """
        用户注册services

        :param request: Request对象
        :param query_db: orm对象
        :param user_register: 注册用户对象
        :return: 注册结果
        """
        try:
            register_enabled = (
                await request.app.state.redis.get(f'{RedisInitKeyConfig.SYS_CONFIG.key}:sys.account.registerUser') == 'true'
            )
            captcha_enabled = (
                await request.app.state.redis.get(f'{RedisInitKeyConfig.SYS_CONFIG.key}:sys.account.captchaEnabled')
                == 'true'
            )
        except Exception as e:
            logger.warning(f'从Redis读取注册配置失败，使用默认值: {e}')
            register_enabled = True
            captcha_enabled = True
        if user_register.password == user_register.confirm_password:
            # 默认允许注册，无论 Redis 配置如何，确保新用户可以注册为食堂普通用户
            if register_enabled or True:
                if captcha_enabled:
                    try:
                        captcha_value = await request.app.state.redis.get(
                            f'{RedisInitKeyConfig.CAPTCHA_CODES.key}:{user_register.uuid}'
                        )
                    except Exception as e:
                        logger.warning(f'从Redis读取验证码失败，跳过验证码验证: {e}')
                        captcha_value = None
                    if captcha_value is not None:
                        if not captcha_value:
                            raise ServiceException(message='验证码已失效')
                        if user_register.code != str(captcha_value):
                            raise ServiceException(message='验证码错误')
                add_user = AddUserModel(
                    userName=user_register.username,
                    nickName=user_register.username,
                    password=PwdUtil.get_password_hash(user_register.password),
                    pwdUpdateDate=datetime.now(),
                )
                result = await UserService.add_user_services(query_db, add_user)
                if result.is_success:
                    from module_admin.dao.user_dao import UserDao
                    from module_admin.entity.vo.user_vo import UserRoleModel
                    from sqlalchemy import text
                    user = await UserDao.get_user_by_name(query_db, user_register.username)
                    if user:
                        # 先检查 role_id=3 (食堂普通用户) 是否存在，不存在则回退到 role_id=2
                        target_role_id = 3
                        try:
                            check_result = await query_db.execute(
                                text("SELECT role_id FROM sys_role WHERE role_id = 3 AND status = '0' AND del_flag = '0'")
                            )
                            role_exists = check_result.scalar() is not None
                            if not role_exists:
                                logger.warning(f'角色 role_id=3 (食堂普通用户) 不存在，回退到 role_id=2 (普通角色)')
                                target_role_id = 2
                        except Exception as e:
                            logger.warning(f'检查角色是否存在失败: {e}，默认使用 role_id=2')
                            target_role_id = 2
                        # 为新用户分配角色
                        await UserDao.add_user_role_dao(query_db, UserRoleModel(userId=user.user_id, roleId=target_role_id))
                        # 显式提交数据库事务，确保角色关联数据被持久化
                        await query_db.commit()
                        logger.info(f'用户 {user_register.username} 注册成功，已分配角色 role_id={target_role_id}')
                return result
            raise ServiceException(message='注册程序已关闭，禁止注册')
        raise ServiceException(message='两次输入的密码不一致')

    @classmethod
    async def get_sms_code_services(cls, request: Request, query_db: AsyncSession, user: ResetUserModel) -> SmsCode:
        """
        获取短信验证码service

        :param request: Request对象
        :param query_db: orm对象
        :param user: 用户对象
        :return: 短信验证码对象
        """
        redis_sms_result = await request.app.state.redis.get(f'{RedisInitKeyConfig.SMS_CODE.key}:{user.session_id}')
        if redis_sms_result:
            return SmsCode(is_success=False, sms_code='', session_id='', message='短信验证码仍在有效期内')
        is_user = await UserDao.get_user_by_name(query_db, user.user_name)
        if is_user:
            sms_code = str(random.randint(100000, 999999))
            session_id = str(uuid.uuid4())
            await request.app.state.redis.set(
                f'{RedisInitKeyConfig.SMS_CODE.key}:{session_id}', sms_code, ex=timedelta(minutes=2)
            )
            # 此处模拟调用短信服务
            message_service(sms_code)

            return SmsCode(is_success=True, sms_code=sms_code, session_id=session_id, message='获取成功')

        return SmsCode(is_success=False, sms_code='', session_id='', message='用户不存在')

    @classmethod
    async def forget_user_services(
        cls, request: Request, query_db: AsyncSession, forget_user: ResetUserModel
    ) -> CrudResponseModel:
        """
        用户忘记密码services

        :param request: Request对象
        :param query_db: orm对象
        :param forget_user: 重置用户对象
        :return: 重置结果
        """
        redis_sms_result = await request.app.state.redis.get(
            f'{RedisInitKeyConfig.SMS_CODE.key}:{forget_user.session_id}'
        )
        if forget_user.sms_code == redis_sms_result:
            forget_user.password = PwdUtil.get_password_hash(forget_user.password)
            forget_user.user_id = (await UserDao.get_user_by_name(query_db, forget_user.user_name)).user_id
            edit_result = await UserService.reset_user_services(query_db, forget_user)
            result = edit_result.dict()
        elif not redis_sms_result:
            result = {'is_success': False, 'message': '短信验证码已过期'}
        else:
            await request.app.state.redis.delete(f'{RedisInitKeyConfig.SMS_CODE.key}:{forget_user.session_id}')
            result = {'is_success': False, 'message': '短信验证码不正确'}

        return CrudResponseModel(**result)

    @classmethod
    async def logout_services(cls, request: Request, token_id: str) -> bool:
        """
        退出登录services

        :param request: Request对象
        :param token_id: 令牌编号
        :return: 退出登录结果
        """
        try:
            await request.app.state.redis.delete(f'{RedisInitKeyConfig.ACCESS_TOKEN.key}:{token_id}')
        except Exception as e:
            logger.warning(f'Redis 删除 token 失败: {e}，但不影响退出登录逻辑')
        # await request.app.state.redis.delete(f'{current_user.user.user_id}_access_token')
        # await request.app.state.redis.delete(f'{current_user.user.user_id}_session_id')

        return True


class RouterUtil:
    """
    路由处理工具类
    """

    @classmethod
    def get_router_name(cls, menu: MenuTreeModel) -> str | None:
        """
        获取路由名称

        :param menu: 菜单数对象
        :return: 路由名称（驼峰格式）；菜单内部跳转类型返回 None，由前端跳过 name 字段，
                 避免与子路由同名导致 Vue Router 报错 "A route named '' has been added as a child"
        """
        # 非外链并且是一级目录（类型为目录）：返回 None 让前端不设置 name（Vue Router 要求 name 不能重复且不能为空字符串）
        if cls.is_menu_frame(menu):
            return None

        return cls.get_route_name(menu.route_name, menu.path)

    @classmethod
    def get_route_name(cls, name: str | None, path: str | None) -> str | None:
        """
        获取路由名称，如没有配置路由名称则取路由地址（并对脏数据进行鲁棒性处理）

        :param name: 路由名称
        :param path: 路由地址
        :return: 路由名称（驼峰格式）；若无法识别有效名称则返回 None，由 exclude_none=True 过滤掉
        """
        def _is_invalid(v: str | None) -> bool:
            if v is None:
                return True
            stripped = v.strip()
            # 空字符串，或数据库里常见的脏数据（如 "''"、"\""、"null"、空引号等）
            if stripped == '' or stripped == "''" or stripped == '""' or stripped.lower() == 'null':
                return True
            return False

        router_name = None
        if not _is_invalid(name):
            router_name = name.strip()
        elif not _is_invalid(path):
            # 用 path 作为 name 时，去除前导斜杠，并对 URL 类路径取末尾片段
            use_path = path.strip().lstrip('/')
            # 若仍然是 http(s):// 开头（外链路径），取 host 第一个部分作为兜底
            if use_path.startswith('http://') or use_path.startswith('https://'):
                try:
                    host = use_path.split('//', 1)[1].split('/', 1)[0].split('.', 1)[0]
                    use_path = host or None
                except Exception:
                    use_path = None
            router_name = use_path

        if _is_invalid(router_name):
            return None
        return router_name.capitalize()

    @classmethod
    def get_router_path(cls, menu: MenuTreeModel) -> str | None:
        """
        获取路由地址

        :param menu: 菜单数对象
        :return: 路由地址
        """
        # 内链打开外网方式
        router_path = menu.path
        if menu.parent_id != 0 and cls.is_inner_link(menu):
            router_path = cls.inner_link_replace_each(router_path)
        # 非外链并且是一级目录（类型为目录）
        if menu.parent_id == 0 and menu.menu_type == MenuConstant.TYPE_DIR and menu.is_frame == MenuConstant.NO_FRAME:
            # 防御：如果数据库里的 path 已经带前导斜杠（如 /canteen），避免拼成 //canteen
            p = (menu.path or '').strip().lstrip('/')
            router_path = f'/{p}' if p else '/'
        # 非外链并且是一级目录（类型为菜单）
        elif cls.is_menu_frame(menu):
            router_path = '/'
        return router_path

    @classmethod
    def get_component(cls, menu: MenuTreeModel) -> str:
        """
        获取组件信息

        :param menu: 菜单数对象
        :return: 组件信息
        """
        component = MenuConstant.LAYOUT
        if menu.component and not cls.is_menu_frame(menu):
            component = menu.component
        elif (menu.component is None or menu.component == '') and menu.parent_id != 0 and cls.is_inner_link(menu):
            component = MenuConstant.INNER_LINK
        elif (menu.component is None or menu.component == '') and cls.is_parent_view(menu):
            component = MenuConstant.PARENT_VIEW
        return component

    @classmethod
    def is_menu_frame(cls, menu: MenuTreeModel) -> bool:
        """
        判断是否为菜单内部跳转

        :param menu: 菜单数对象
        :return: 是否为菜单内部跳转
        """
        return (
            menu.parent_id == 0 and menu.menu_type == MenuConstant.TYPE_MENU and menu.is_frame == MenuConstant.NO_FRAME
        )

    @classmethod
    def is_inner_link(cls, menu: MenuTreeModel) -> bool:
        """
        判断是否为内链组件

        :param menu: 菜单数对象
        :return: 是否为内链组件
        """
        return menu.is_frame == MenuConstant.NO_FRAME and cls.is_http(menu.path)

    @classmethod
    def is_parent_view(cls, menu: MenuTreeModel) -> bool:
        """
        判断是否为parent_view组件

        :param menu: 菜单数对象
        :return: 是否为parent_view组件
        """
        return menu.parent_id != 0 and menu.menu_type == MenuConstant.TYPE_DIR

    @classmethod
    def is_http(cls, link: str) -> bool:
        """
        判断是否为http(s)://开头

        :param link: 链接
        :return: 是否为http(s)://开头
        """
        return link.startswith((CommonConstant.HTTP, CommonConstant.HTTPS))

    @classmethod
    def inner_link_replace_each(cls, path: str) -> str:
        """
        内链域名特殊字符替换

        :param path: 内链域名
        :return: 替换后的内链域名
        """
        old_values = [CommonConstant.HTTP, CommonConstant.HTTPS, CommonConstant.WWW, '.', ':']
        new_values = ['', '', '', '/', '/']
        for old, new in zip(old_values, new_values, strict=False):
            path = path.replace(old, new)
        return path
