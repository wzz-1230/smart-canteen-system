import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from config.env import UploadConfig


def mount_staticfiles(app: FastAPI) -> None:
    """
    挂载静态文件
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    profile_dir = os.path.abspath(os.path.join(base_dir, UploadConfig.UPLOAD_PATH))
    os.makedirs(profile_dir, exist_ok=True)
    app.mount(f'{UploadConfig.UPLOAD_PREFIX}', StaticFiles(directory=profile_dir), name='profile')
    # 挂载食堂菜品图片目录，前端通过 /static/canteen-menu-images/红烧肉.jpg 访问
    canteen_img_dir = os.path.abspath(os.path.join(base_dir, UploadConfig.CANTEEN_MENU_IMAGE_PATH))
    os.makedirs(canteen_img_dir, exist_ok=True)
    app.mount(
        f'{UploadConfig.CANTEEN_MENU_IMAGE_PREFIX}',
        StaticFiles(directory=canteen_img_dir),
        name='canteen_menu_images',
    )
    print(f'[INFO] 已挂载静态文件服务: {UploadConfig.UPLOAD_PREFIX} -> {profile_dir}', flush=True)
    print(f'[INFO] 已挂载静态文件服务: {UploadConfig.CANTEEN_MENU_IMAGE_PREFIX} -> {canteen_img_dir}', flush=True)
