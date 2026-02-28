const fs = require('fs');
const { PNG } = require('pngjs');

console.log("Analyzing empty.png...");

fs.createReadStream('empty.png')
    .pipe(new PNG())
    .on('parsed', function() {
        
        // Brute-force the 3 possible starting pixels for "every third heartbeat"
        for (let offset = 0; offset < 3; offset++) {
            let binaryStr = '';
            let pixelIndex = 0;
            
            for (let i = 0; i < this.data.length; i += 4) {
                if (pixelIndex % 3 === offset) {
                    let blue = this.data[i + 2]; // Blue channel
                    binaryStr += (blue & 1);     // LSB
                }
                pixelIndex++;
            }

            // Convert to text, keeping only readable characters
            let decodedText = '';
            for (let i = 0; i < binaryStr.length; i += 8) {
                const byte = binaryStr.slice(i, i + 8);
                if (byte.length === 8) {
                    const charCode = parseInt(byte, 2);
                    // Standard printable ASCII range (letters, numbers, punctuation)
                    if (charCode >= 32 && charCode <= 126) {
                        decodedText += String.fromCharCode(charCode);
                    }
                }
            }

            console.log(`\n--- OFFSET ${offset} ---`);
            // Print the first 150 readable characters
            console.log(decodedText.substring(0, 150)); 
        }
        console.log("\n--------------------------\n");
    })
    .on('error', function(err) {
        console.error("Error reading the PNG:", err.message);
    });