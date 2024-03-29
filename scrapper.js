const puppeteer = require('puppeteer');
const fs = require('fs');

var URL='https://codigo-postal.org/pt-br/brasil/sp/americana/';
var REPORT='D:\\Usuario\\Desktop\\Projeto AVA\\href_links.txt';

(async () => {
 // Step 1: Launch the browser and open a new page
 const browser = await puppeteer.launch();
 const page = await browser.newPage();

 // Step 2: Navigate to the page and wait for it to load
 await page.goto(URL);

 // Step 3: Extract the href URLs
 const hrefs = await page.evaluate(() => {
    const listItems = document.querySelectorAll('#ul_list li a');
    return Array.from(listItems, a => a.href);
 });

 // Step 4: Write the URLs to a file
 fs.writeFileSync(REPORT, hrefs.join('\n'));

 // Close the browser
 await browser.close();
})();
