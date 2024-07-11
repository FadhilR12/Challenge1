import argparse
import os.path
import sys
from bs4 import BeautifulSoup
import requests
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fatal(message):
    logging.fatal(message)
    sys.exit(1)


def get_chapter():
    chapter = argparse.ArgumentParser(description="chapter")
    chapter.add_argument('--chapter', type=int, default=0, help="chapter yang ingin di download")
    args = chapter.parse_args()
    return args.chapter


def get_imageurl(chapter):
    pageUrl = f"https://kiryuu.id/mercenary-enrollment-chapter-{chapter}/"
    resp = requests.get(pageUrl)
    if resp.status_code != 200:
        return None, f"HTTP request failed with status code {resp.status_code}"

    soup = BeautifulSoup(resp.content, 'html.parser')
    content = soup.find("div", {"id": "readerarea"})
    if content is None:
        return None, "Unable to find the div with id 'readerarea'"

    image_urls = [img.get("src") for img in content.find_all("img") if img.get("src")]
    return image_urls, None


def download_image(chapter, imageUrl):
    resp = requests.get(imageUrl)
    if resp.status_code != 200:
        return None, f"Unable to get image, status code: {resp.status_code}"

    data = resp.content
    download_path = f"./downloads/{chapter}"
    if not os.path.exists(download_path):
        try:
            os.makedirs(download_path, mode=0o755)
        except OSError as e:
            return None, f"Unable to create directory due: {e}"

    image_name = parse_image_name(imageUrl)
    file_path = os.path.join(download_path, image_name)
    try:
        with open(file_path, 'wb') as file:
            file.write(data)
    except OSError as e:
        return None, f"unable to save image due: {e}"
    return file_path, None


def parse_image_name(image_url):
    return image_url.split("/")[-1]


def main():
    chapter = get_chapter()
    logging.info(f"Chapter yang akan didownload: {chapter}")

    image_urls, err = get_imageurl(chapter)
    if err is not None:
        fatal(f"Unable to get image URLs: {err}")

    if len(image_urls) == 0:
        logging.info(f"Chapter {chapter} belum tersedia")
        return

    logging.info(f"Downloading chapter {chapter}")
    for imageUrl in image_urls:
        logging.info(f"Downloading image: {imageUrl}")
        file_path, err = download_image(chapter, imageUrl)
        if err is not None:
            logging.error(f"Error: {err}")
        else:
            logging.info(f"Image downloaded to {file_path}")


if __name__ == "__main__":
    main()
