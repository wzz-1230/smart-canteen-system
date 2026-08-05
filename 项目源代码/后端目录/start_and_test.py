import os, sys, time, subprocess, urllib.request, json, socket, urllib.parse

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
sys.path.insert(0, script_dir)

BASE_URL = "http://127.0.0.1:9099"

def is_port_open(port, host='127.0.0.1'):
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except Exception:
        return False

if not is_port_open(9099):
    print("[INFO] 启动后端服务 (start_server.py)...")
    proc = subprocess.Popen(
        [sys.executable, "start_server.py"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        cwd=script_dir
    )
    waited = 0
    while waited < 30:
        if is_port_open(9099):
            print(f"[INFO] 服务启动成功 (等待 {waited}s)")
            break
        time.sleep(1)
        waited += 1
    else:
        print("[ERROR] 服务未能在 30 秒内启动！")
        try:
            out, _ = proc.communicate(timeout=3)
            print("[服务输出]")
            print(out.decode('utf-8', errors='ignore')[:3000])
        except Exception:
            pass
        sys.exit(1)

time.sleep(2)

# ========== 测试 ==========
print("\n=== Test 1: Login ===")
login_form = urllib.parse.urlencode({
    "username": "admin",
    "password": "admin123",
    "code": "1",
    "uuid": "test-uuid",
}).encode('utf-8')
login_headers = {"Content-Type": "application/x-www-form-urlencoded"}
req = urllib.request.Request(BASE_URL + "/login", data=login_form, headers=login_headers, method="POST")
token = None
try:
    resp = urllib.request.urlopen(req, timeout=15)
    data = resp.read().decode('utf-8')
    print("Login response:", data[:1000])
    result = json.loads(data)
    if result.get('token'):
        token = result['token']
    elif 'data' in result and 'accessToken' in result['data']:
        token = result['data']['accessToken']
    elif 'data' in result and 'token' in result['data']:
        token = result['data']['token']
    print("Got token:", str(token)[:30] + "..." if token else "NO TOKEN")
except Exception as e:
    print("Login error:", str(e))
    if hasattr(e, 'read'):
        try: print("Server response:", e.read().decode())
        except: pass

print("\n=== Test 2: Menu list ===")
if token:
    auth_headers = {"Content-Type": "application/json", "Authorization": "Bearer " + token}
    req2 = urllib.request.Request(BASE_URL + "/canteen/menu/list?pageNum=1&pageSize=3", headers=auth_headers, method="GET")
    try:
        resp2 = urllib.request.urlopen(req2, timeout=15)
        data2 = resp2.read().decode('utf-8')
        result2 = json.loads(data2)
        print("Success! total:", result2.get('total'), "rows count:", len(result2.get('rows', [])))
        if result2.get('rows'):
            print("First row:")
            print(json.dumps(result2['rows'][0], ensure_ascii=False, indent=2))
    except Exception as e:
        print("Menu list error:", str(e))
        if hasattr(e, 'read'):
            try: print("Server response:", e.read().decode()[:500])
            except: pass
else:
    print("Skipping: no token")

print("\n=== Test 3: Table list ===")
if token:
    req3 = urllib.request.Request(BASE_URL + "/canteen/table/list?pageNum=1&pageSize=3", headers=auth_headers, method="GET")
    try:
        resp3 = urllib.request.urlopen(req3, timeout=15)
        data3 = resp3.read().decode('utf-8')
        result3 = json.loads(data3)
        print("Success! total:", result3.get('total'), "rows count:", len(result3.get('rows', [])))
        if result3.get('rows'):
            print("First row:")
            print(json.dumps(result3['rows'][0], ensure_ascii=False, indent=2))
    except Exception as e:
        print("Table list error:", str(e))
        if hasattr(e, 'read'):
            try: print("Server response:", e.read().decode()[:500])
            except: pass

print("\n=== All tests done ===")
