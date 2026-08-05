import os
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from common.router import auto_register_routers
from config.env import AppConfig
from config.get_db import init_create_table
from config.get_redis import RedisUtil
from sub_applications.handle import handle_sub_applications


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理 - 添加超时和错误处理"""
    try:
        # 1. 初始化数据库表（超时30秒）
        try:
            await asyncio.wait_for(init_create_table(), timeout=30)
        except asyncio.TimeoutError:
            print('[WARN] 数据库初始化超时，跳过...', flush=True)
        except Exception as e:
            print(f'[WARN] 数据库初始化失败: {e}', flush=True)

        # 2. 创建 Redis 连接池（超时10秒）
        try:
            app.state.redis = await asyncio.wait_for(
                RedisUtil.create_redis_pool(log_enabled=False), timeout=10
            )
        except asyncio.TimeoutError:
            print('[WARN] Redis连接超时，继续启动...', flush=True)
            app.state.redis = None
        except Exception as e:
            print(f'[WARN] Redis连接失败: {e}', flush=True)
            app.state.redis = None

        # 3. 初始化字典缓存（超时15秒）
        if app.state.redis:
            try:
                await asyncio.wait_for(
                    RedisUtil.init_sys_dict(app.state.redis), timeout=15
                )
            except asyncio.TimeoutError:
                print('[WARN] 字典缓存初始化超时，跳过...', flush=True)
            except Exception as e:
                print(f'[WARN] 字典缓存初始化失败: {e}', flush=True)

        # 4. 初始化配置缓存（超时15秒）
        if app.state.redis:
            try:
                await asyncio.wait_for(
                    RedisUtil.init_sys_config(app.state.redis), timeout=15
                )
            except asyncio.TimeoutError:
                print('[WARN] 配置缓存初始化超时，跳过...', flush=True)
            except Exception as e:
                print(f'[WARN] 配置缓存初始化失败: {e}', flush=True)

        print('[INFO] 后端服务初始化完成！', flush=True)

    except Exception as e:
        print(f'[ERROR] 生命周期初始化异常: {e}', flush=True)

    yield

    # 关闭资源
    try:
        await RedisUtil.close_redis_pool(app)
    except Exception:
        pass


def create_app() -> FastAPI:
    app = FastAPI(
        title=AppConfig.app_name,
        description=AppConfig.app_name,
        version=AppConfig.app_version,
        default_response_class=JSONResponse,
        lifespan=lifespan,
        root_path_in_openapi=False,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    if os.path.exists(static_dir):
        app.mount('/static', StaticFiles(directory=static_dir), name='static')
        print(f'[INFO] 已挂载静态文件服务: /static -> {static_dir}', flush=True)
    else:
        print(f'[WARN] 静态文件目录不存在: {static_dir}', flush=True)

    # 挂载静态文件（/profile 和 /static/canteen-menu-images）
    handle_sub_applications(app)

    auto_register_routers(app)

    return app
