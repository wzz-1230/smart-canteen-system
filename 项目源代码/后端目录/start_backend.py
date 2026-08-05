"""
简化版后端启动脚本。
直接用一个干净的方式启动 FastAPI 服务，避免 loguru 的 enqueue 子进程问题。
"""
import os
import sys
import time
import threading
import socket
import logging

# ---------- 在任何模块 import 前先 monkey-patch loguru，禁用 enqueue ----------
try:
    from loguru import logger as _loguru_logger

    _orig_add = _loguru_logger.add

    def _patched_add(*args, **kwargs):
        kwargs['enqueue'] = False
        return _orig_add(*args, **kwargs)

    _loguru_logger.add = _patched_add
except Exception:
    pass

# 降低 sqlalchemy 的日志噪音
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

from config.env import AppConfig
from server import create_app
import uvicorn

app = create_app()

if __name__ == '__main__':
    print(f'[INFO] 启动 FastAPI 服务 {AppConfig.app_host}:{AppConfig.app_port}', flush=True)
    uvicorn.run(app, host=AppConfig.app_host, port=AppConfig.app_port, log_level='warning')
