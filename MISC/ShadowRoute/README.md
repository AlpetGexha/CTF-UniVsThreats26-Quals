# Shadow Route

**Point: 365**

The Helios Space Station has been operational for two years, orbiting Earth at 400km altitude. Recently, ground control detected anomalous network activity from the station's internal systems.
Your mission: intercept the data stream and identify the unauthorized beacon before the station completes its next orbit.
Good luck hunting the unfindable.

Credentials:
pilot:docking-request

## 1. Initial Access & Discovery

- **Connect:** SSH into the restricted shell using `pilot` / `docking-request`.
- **Enumerate:** Use the allowed `nmap` command to scan `127.13.37.0/24` and locate the dynamic internal station host (e.g., `127.13.37.46`).
- **Tunnel:** Port-forward the internal web service (`9043`) and file archive (`8445`) to your local machine.

## 2. Web Exploitation (`www-data`)

- **Credentials:** Extract the Stargate panel credentials (`astrid` / `apollo1`) from the `transmission.txt` file located on the internal file archive.
- **Authenticate:** Log into the Stargate dashboard.
- **RCE:** Upload a PHP web shell disguised as a telemetry file. The application accepts `.php` extensions and executes them, granting `www-data` access in `/var/www/html/cosmos-data/`.

## 3. Privilege Escalation (Root)

- **Identify Cron Job:** A root-level cron job executes `/home/nova/orbit-sync.sh` every minute and copies files from the web upload directory to `/var/backups/telemetry/`.
- **Symlink Abuse (Step 1):** Create a symlink in the web upload directory pointing to `/home/nova/orbit-sync.sh`. The root cron job copies this, creating a mirrored symlink in the destination folder.
- **Symlink Abuse (Step 2):** Replace your original symlink with a malicious bash script.
- **Execution:** On the next cron tick, the root copy operation traverses the destination symlink, effectively overwriting the actual root script with your payload. The subsequent tick executes it, dumping the contents of `/root/root.txt` into the web directory.

## 4. The Flag

`UVT{y0u_f0und_m3_1n_4_d4rk_c0rn3r_fr0m_4_sh4d0w_t3rm1n4l_h0peFully_y0U_WoUlD_r3MemBer_M3!!!_1_will_watch_yOur_m0v3s_frOm_h3r3}`
