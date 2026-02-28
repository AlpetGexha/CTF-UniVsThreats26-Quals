const fs = require('fs');

console.log("Reading empty.js...");

// 1. Read the raw content of empty.js
const fileContent = fs.readFileSync('empty.js', 'utf8');

// 2. Use a regular expression to grab exactly what is inside the backticks of VOID_PAYLOAD
const payloadMatch = fileContent.match(/const VOID_PAYLOAD = `([\s\S]*?)`;/);

if (!payloadMatch) {
    console.error("Error: Could not find VOID_PAYLOAD in empty.js. Make sure the file is in the same folder!");
    process.exit(1);
}

const voidPayload = payloadMatch[1];
console.log(`Successfully extracted invisible payload (Length: ${voidPayload.length} characters)`);

let binaryStr = '';

// 3. Map the zero-width characters back to binary
for (let i = 0; i < voidPayload.length; i++) {
    if (voidPayload[i] === '\u200B') {
        binaryStr += '0'; // Zero-Width Space
    } else if (voidPayload[i] === '\u200C') {
        binaryStr += '1'; // Zero-Width Non-Joiner
    }
}

console.log(`Converted to binary string (Length: ${binaryStr.length} bits)`);

// 4. Convert the binary string into a byte array
const bytes = [];
for (let i = 0; i < binaryStr.length; i += 8) {
    bytes.push(parseInt(binaryStr.slice(i, i + 8), 2));
}

// 5. Write the bytes out to a ZIP file
fs.writeFileSync('flag.zip', Buffer.from(bytes));
console.log('Success! Archive extracted to flag.zip');