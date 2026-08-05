import uuid
from datetime import timedelta

from fastapi import Request, Response

from common.annotation.rate_limit_annotation import ApiRateLimit, ApiRateLimitPreset
from common.constant import ApiNamespace
from common.enums import RedisInitKeyConfig
from common.router import APIRouterPro
from common.vo import DynamicResponseModel
from module_admin.entity.vo.login_vo import CaptchaCode
from module_admin.service.captcha_service import CaptchaService
from utils.log_util import logger
from utils.response_util import ResponseUtil

captcha_controller = APIRouterPro(order_num=2, tags=['验证码模块'])


@captcha_controller.get(
    '/captchaImage',
    summary='获取图片验证码接口',
    description='用于获取图片验证码',
    response_model=DynamicResponseModel[CaptchaCode],
)
@ApiRateLimit(namespace=ApiNamespace.CAPTCHA_IMAGE, preset=ApiRateLimitPreset.ANON_AUTH_CAPTCHA)
async def get_captcha_image(request: Request) -> Response:
    try:
        captcha_enabled = (
            await request.app.state.redis.get(f'{RedisInitKeyConfig.SYS_CONFIG.key}:sys.account.captchaEnabled') == 'true'
        )
        register_enabled = (
            await request.app.state.redis.get(f'{RedisInitKeyConfig.SYS_CONFIG.key}:sys.account.registerUser') == 'true'
        )
    except Exception as e:
        logger.warning(f'从Redis获取验证码配置失败，使用默认值: {e}')
        captcha_enabled = True
        # 默认开启注册功能，支持用户注册为食堂普通用户
        register_enabled = True
    session_id = str(uuid.uuid4())
    captcha_result = await CaptchaService.create_captcha_image_service()
    image = captcha_result[0]
    computed_result = captcha_result[1]
    try:
        await request.app.state.redis.set(
            f'{RedisInitKeyConfig.CAPTCHA_CODES.key}:{session_id}', computed_result, ex=timedelta(minutes=2)
        )
    except Exception as e:
        logger.warning(f'验证码保存到Redis失败: {e}，继续返回图片')
    logger.info(f'编号为{session_id}的会话获取图片验证码成功')

    return ResponseUtil.success(
        model_content=CaptchaCode(
            captchaEnabled=captcha_enabled, registerEnabled=register_enabled, img=image, uuid=session_id
        )
    )
