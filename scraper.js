const g = require('google-play-scraper');
const fs = require('fs');


async function main() {
  apps = await g.list({collection: g.collection.TOP_FREE, num: 300})
  console.log(apps)
}

main()
