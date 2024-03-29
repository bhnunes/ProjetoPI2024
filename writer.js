const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

(async () => {
 // Step 1: Read URLs from file
 const urls = fs.readFileSync('D:\\Usuario\\Desktop\\Projeto AVA\\href_links.txt', 'utf8').split('\n');

 // Step 2: Launch the browser
 const browser = await puppeteer.launch();
 const page = await browser.newPage();

 // Step 3: Extract and write data for each URL
 const outputPath = 'D:\\Usuario\\Desktop\\Projeto AVA\\extracted_data.txt';
 let outputData = '';

 for (const url of urls) {
    if (url) { // Check if the URL is not empty
      await page.goto(url);

      // Step 4: Extract data from table
      const data = await page.evaluate(() => {
        const rows = document.querySelectorAll('#tbody_results_ tr');
        let extractedData = [];
        for (const row of rows) {
          const tds = row.querySelectorAll('td');
          if (tds.length >= 5) {
            extractedData.push({
              CEP: tds[0].innerText,
              LOGRADOURO: tds[1].innerText,
              BAIRRO: tds[3].innerText,
              CIDADE: tds[4].innerText
            });
          }
        }
        return extractedData;
      });

      // Format and append data to output string
      data.forEach(item => {
        outputData += `${item.CEP}, ${item.LOGRADOURO}, ${item.BAIRRO}, ${item.CIDADE}\n`;
      });
    }
 }

 // Step 5: Write data to file
 fs.writeFileSync(outputPath, outputData);

 // Close the browser
 await browser.close();
})();
