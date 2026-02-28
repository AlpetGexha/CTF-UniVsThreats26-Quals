# Where is everything

**Point: 50**

HTTP 404: Everything Not Found

## Writeup

The folder already contains all puzzle artifacts and helper scripts:

- `empty.txt` (looks blank, but has space/tab data)
- `empty.png` (looks empty, but has LSB data)
- `empty.js` (contains a big hidden `VOID_PAYLOAD`)
- scripts: `another.js`, `extract_png.js`, `script.js`, `flag.js`

### 1) Decode the hint from `empty.txt`

Run:

```bash
node another.js
```

This decodes spaces/tabs into text and gives the important clue:

- inspect `empty.png`
- use the blue channel LSB
- sample every third pixel
- recovered text will unlock the hidden payload

### 2) Extract the ZIP password from `empty.png`

Install dependency once:

```bash
npm install
```

Then run:

```bash
node extract_png.js
```

Key output:

```text
ZIP_PASSWORD=D4rKm47T3rrr;END
```

So the password is:

```text
D4rKm47T3rrr
```

### 3) Rebuild the hidden archive from `empty.js`

Run:

```bash
node script.js
```

`script.js` extracts `VOID_PAYLOAD` from `empty.js`, maps zero-width chars to bits:

- `\u200B` -> `0`
- `\u200C` -> `1`

and writes the bytes to `flag.zip`.

### 4) Decrypt/extract `flag.zip`

Run:

```bash
tar --passphrase 'D4rKm47T3rrr' -xf flag.zip
```

This extracts `flag.png`.

### 5) Get the flag from `flag.png`

Run:

```bash
node flag.js
```

It prints the embedded flag string:

```text
UVT{N0th1nG_iS_3mp7y_1n_sP4c3}
```

## Flag

`UVT{N0th1nG_iS_3mp7y_1n_sP4c3}`
