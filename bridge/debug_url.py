import requests
import config

base_url = config.BRIDGE_API_URL
print(f"Testing Configured Bridge URL: {base_url}")

endpoints = [
    ("", "GET"),
    ("/", "GET"),
    ("/upload", "POST"),
    ("/analyze", "POST"),
    ("/chat", "POST"),
    ("/docs", "GET")
]

print(f"Probing Bridge URL: {base_url}")

for ep, method in endpoints:
    url = f"{base_url}{ep}"
    try:
        print(f"{method} {url} ... ", end="")
        if method == "GET":
            resp = requests.get(url, timeout=5)
        else:
            # POST 요청시 422(Validation Error)가 뜨더라도 Method Not Allowed(405)는 해결된 것임
            # 채팅의 경우 최소 데이터 보내보기
            json_data = {"question": "ping"} if ep == "/chat" else {}
            resp = requests.post(url, json=json_data, timeout=5)
            
        print(f"{resp.status_code}")
        
        if resp.status_code == 200:
            print(f"   > Content-Type: {resp.headers.get('Content-Type')}")
            try:
                print(f"   > JSON: {resp.json()}")
            except:
                pass
        elif resp.status_code == 422:
             print(f"   > (422 Expected for missing data) Method Allowed!")
    except Exception as e:
        print(f"Error: {e}")
