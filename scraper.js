const gplay = require('google-play-scraper').memoized();

const fs = require('fs');


async function main() {
  let set = new Set();


  function log(error) {
    if (error) {
      console.log(error)
    }
  }

  function extend(apps) {
    apps.forEach(app => {
      fs.writeFile("apps.json", app.appId + "\n", { flag: "a+" }, log)
    });
  }

  const apps = await gplay.list({
    collection: gplay.collection.TOP_FREE,
    // num: 2
  })
  extend(apps)
  try {
    await Promise.all(apps.map(async app => {
      console.log("for each: ", app.appId)
      await gplay.similar({ appId: app.appId })
        .then(extend, log)
      await gplay.developer({ devId: app.developer })
        .then(extend, log)
      await gplay.search({ term: app.title, throttle: 10 })
        .then(extend, log)
    }))
  } catch (error) {
  }
}

main()
