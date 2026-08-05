import sys
import os

os.chdir(r'E:\刘柏霆\RuoYi-Vue3-FastAPI-master\ruoyi-fastapi-backend')
sys.path.insert(0, r'E:\刘柏霆\RuoYi-Vue3-FastAPI-master\ruoyi-fastapi-backend')

import uvicorn
from server import create_app

if __name__ == '__main__':
    app = create_app()
    print(f'Starting server on 0.0.0.0:9099...', flush=True)
    uvicorn.run(
        app=app,
        host='0.0.0.0',
        port=9099,
    )
