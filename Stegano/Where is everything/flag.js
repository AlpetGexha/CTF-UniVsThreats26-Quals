const fs = require('fs');

console.log("Scanning flag.png for hidden text...\n");

try {
    const buffer = fs.readFileSync('flag.png');
    
    // Extract only standard readable ASCII characters
    let readableText = '';
    for (let i = 0; i < buffer.length; i++) {
        const charCode = buffer[i];
        if (charCode >= 32 && charCode <= 126) {
            readableText += String.fromCharCode(charCode);
        } else {
            readableText += '\n'; // Break the string when hitting raw binary/null bytes
        }
    }

    // Filter out short noise, keep strings 8 characters or longer
    const lines = readableText.split('\n').filter(line => line.length >= 8);
    
    // Specifically hunt for the CTF flag format
    const flagFormat = lines.filter(line => 
        line.toLowerCase().includes('usss{') || 
        line.toLowerCase().includes('flag{')
    );

    if (flagFormat.length > 0) {
        console.log("🎯 BINGO! Found a flag format:");
        flagFormat.forEach(f => console.log(`>> ${f} <<`));
    } else {
        console.log("No obvious flag format found. Here are the longest printable strings hiding in the file:\n");
        // Print unique readable strings to avoid repeating standard PNG chunk headers
        const uniqueLines = [...new Set(lines)];
        uniqueLines.forEach(line => {
            if (!/^(IHDR|IDAT|IEND|sRGB|gAMA|pHYs|cHRM)/.test(line)) {
                console.log(line);
            }
        });
    }

} catch (error) {
    console.error("Error reading flag.png! Make sure it's in the same folder.", error.message);
}