const fs = require('fs');

console.log("Reading whitespace from empty.txt...");

try {
    const content = fs.readFileSync('empty.txt', 'utf8');
    
    // Split the file line by line
    const lines = content.split('\n');
    let decodedText = '';

    for (let line of lines) {
        // Clean up any stray carriage returns
        line = line.replace('\r', '');
        
        let binaryStr = '';
        
        // Convert spaces to 0 and tabs to 1
        for (let char of line) {
            if (char === ' ') {
                binaryStr += '0';
            } else if (char === '\t') {
                binaryStr += '1';
            }
        }
        
        // If we have at least 8 bits (1 byte), convert it to text
        if (binaryStr.length >= 8) {
            const byte = binaryStr.slice(0, 8); // Grab exactly 8 bits
            decodedText += String.fromCharCode(parseInt(byte, 2));
        }
    }

    console.log("\n--- DECODED MESSAGE ---");
    console.log(decodedText);
    console.log("-----------------------\n");

} catch (error) {
    console.error("Error reading empty.txt!", error.message);
}