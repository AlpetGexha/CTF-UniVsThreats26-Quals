const fs = require('fs');

console.log("Reading empty.txt...");

try {
    const content = fs.readFileSync('empty.txt', 'utf8');
    let binaryStr = '';
    let foundHidden = false;

    // We'll look for the exact same zero-width steganography used in empty.js
    for (let i = 0; i < content.length; i++) {
        if (content[i] === '\u200B') {
            binaryStr += '0'; // Zero-Width Space
            foundHidden = true;
        } else if (content[i] === '\u200C') {
            binaryStr += '1'; // Zero-Width Non-Joiner
            foundHidden = true;
        }
    }

    if (foundHidden) {
        console.log(`\nSuccess! Found ${binaryStr.length} hidden bits.`);
        
        // Convert the binary string to ASCII text
        let password = '';
        for (let i = 0; i < binaryStr.length; i += 8) {
            const byte = binaryStr.slice(i, i + 8);
            password += String.fromCharCode(parseInt(byte, 2));
        }
        
        console.log(`\nDecoded Password / Payload:`);
        console.log(`>> ${password} <<\n`);
    } else {
        console.log("\nNo zero-width characters (200B/200C) found.");
        console.log("Here is a raw hex dump of empty.txt to see exactly what bytes are hiding in there:");
        
        const buffer = fs.readFileSync('empty.txt');
        const hexDump = buffer.toString('hex').match(/../g).join(' ');
        console.log(hexDump);
    }
} catch (error) {
    console.error("Error reading empty.txt! Make sure it is in the same folder.");
}