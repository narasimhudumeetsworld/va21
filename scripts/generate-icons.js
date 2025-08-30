const icongen = require('icon-gen');
const path = require('path');
const fs = require('fs');

const inputSvg = path.join(__dirname, '..', 'assets', 'logo.svg');
const outputDir = path.join(__dirname, '..', 'build', 'icons');

// Create the output directory if it doesn't exist
if (!fs.existsSync(outputDir)) {
  console.log(`Creating output directory: ${outputDir}`);
  fs.mkdirSync(outputDir, { recursive: true });
}

console.log(`Generating icons from ${inputSvg} into ${outputDir}...`);

icongen(inputSvg, outputDir, {
  report: true,
  ico: { name: 'icon', sizes: [16, 24, 32, 48, 64, 128, 256] },
  icns: { name: 'icon', sizes: [16, 32, 64, 128, 256, 512, 1024] },
})
  .then((results) => {
    console.log('Icon generation successful:');
    console.log(results);
  })
  .catch((err) => {
    console.error('Icon generation failed:');
    console.error(err);
    process.exit(1); // Exit with an error code
  });
