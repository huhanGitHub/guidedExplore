"""
   Modified from https://gist.github.com/dawand/7b4308d568c6b955b645dd7e707e5cf1
"""
import os
from urllib.parse import quote_plus
import time

import cloudscraper
import definitions
from bs4 import BeautifulSoup
from google_play_scraper.scraper import PlayStoreScraper


def search(query):
    scraper = cloudscraper.create_scraper(delay=1000)
    for i in range(20):
        try:

            res = scraper.get(
                f"https://apkpure.com/search?q={quote_plus(query)}",
            ).text

            soup = BeautifulSoup(res, "html.parser")
            search_result = soup.find("div", {"id": "search-res"}).find(
                "dl", {"class": "search-dl"}
            )
            app_tag = search_result.find("p", {"class": "search-title"}).find("a")
            download_link = "https://apkpure.com" + app_tag["href"]
        except (TypeError, Exception) as e:
            if i == 19:
                raise e
            else:
                print(e)
                time.sleep(.5)
                pass
    return download_link


def download(link, apk_dir=definitions.APK_DIR):
    scraper = cloudscraper.create_scraper(delay=1000)
    if link is None:
        return

    res = scraper.get(f"{link}/download?from=details").text
    soup = BeautifulSoup(res, "html.parser").find("a", {"id": "download_link"})
    if soup["href"]:
        r = scraper.get(soup["href"], stream=True)

        filename = f"{link.split('/')[-1]}"
        filepath = os.path.join(apk_dir, filename)
        with open(filepath, "wb") as file:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        return filepath


def download_apk(app_id, apk_dir=definitions.APK_DIR):
    download_link = search(app_id)

    if download_link is not None:
        print(f"Downloading from {download_link}...")
        path = download(download_link, apk_dir=definitions.APK_DIR)
        print(f"Download from {download_link} completed!")
        return path
    else:
        print(f"Cannot find {app_id}")


def install(path, device):
    print(f"Installing {path} on {device.serial}...")
    device.app_install(path)
    print(f"finish {path} on {device.serial}...")


CATEGORY = {
    "APPLICATION",
    "ANDROID_WEAR",
    "ART_AND_DESIGN",
    "AUTO_AND_VEHICLES",
    "BEAUTY",
    "BOOKS_AND_REFERENCE",
    "BUSINESS",
    "COMICS",
    "COMMUNICATION",
    "DATING",
    "EDUCATION",
    "ENTERTAINMENT",
    "EVENTS",
    "FINANCE",
    "FOOD_AND_DRINK",
    "HEALTH_AND_FITNESS",
    "HOUSE_AND_HOME",
    "LIBRARIES_AND_DEMO",
    "LIFESTYLE",
    "MAPS_AND_NAVIGATION",
    "MEDICAL",
    "MUSIC_AND_AUDIO",
    "NEWS_AND_MAGAZINES",
    "PARENTING",
    "PERSONALIZATION",
    "PHOTOGRAPHY",
    "PRODUCTIVITY",
    "SHOPPING",
    "SOCIAL",
    "SPORTS",
    "TOOLS",
    "TRAVEL_AND_LOCAL",
    "VIDEO_PLAYERS",
    "WEATHER",
    "GAME",
    "GAME_ACTION",
    "GAME_ADVENTURE",
    "GAME_ARCADE",
    "GAME_BOARD",
    "GAME_CARD",
    "GAME_CASINO",
    "GAME_CASUAL",
    "GAME_EDUCATIONAL",
    "GAME_MUSIC",
    "GAME_PUZZLE",
    "GAME_RACING",
    "GAME_ROLE_PLAYING",
    "GAME_SIMULATION",
    "GAME_SPORTS",
    "GAME_STRATEGY",
    "GAME_TRIVIA",
    "GAME_WORD",
    "FAMILY",
    "FAMILY_ACTION",
    "FAMILY_BRAINGAMES",
    "FAMILY_CREATE",
    "FAMILY_EDUCATION",
    "FAMILY_MUSICVIDEO",
    "FAMILY_PRETEND",
}


def top(cate):
    scraper = PlayStoreScraper()
    lst = scraper.get_app_ids_for_collection(category=cate)
    return lst
