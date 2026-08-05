import os
import sys
import subprocess

# 切换到脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
print(f"Working directory: {os.getcwd()}")

import uvicorn
from server import create_app

if __name__ == "__main__":
    print("Starting backend server on 0.0.0.0:9099...")
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=9099, workers=1)
