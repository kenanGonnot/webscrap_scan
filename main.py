import os
import re
import shutil
from pathlib import Path

import requests
from bs4 import BeautifulSoup


def extract_chapter(image_page_url):
    extracted_chapter = re.search(".*(chapitre-[0-9]+).*", image_page_url)
    return extracted_chapter.group(1)


def get_scan(url, manga_dir, last_url=""):
    if url == last_url:
        print("on est la")
        return

    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')
    scan_images = soup.find_all('img', {"class": "scan-page"})

    image_page_url = list(scan_images)[0]['src']
    download_image(image_page_url, "./" + manga_dir + "/" + extract_chapter(image_page_url) + "/")

    links = list(soup.select("#ppp a"))
    if len(links) == 0:
        print("Plus de chapitre disponible - webscraping done")
        return

    scan_next_page_url = links[0]['href']

    get_scan(scan_next_page_url, manga_dir, last_url)

    return ""


def download_image(image_page_url, output_directory):
    image_page_url = image_page_url.replace(' ', '')
    Path(output_directory).mkdir(parents=True, exist_ok=True)
    filename = output_directory + image_page_url.split("/")[-1]
    response = requests.get(image_page_url, stream=True)
    # # print(response)
    if response.status_code == 200:
        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        response.raw.decode_content = True

        # Open a local file with wb ( write binary ) permission.
        with open(filename, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
        print('Image sucessfully Downloaded: ', filename)
    else:
        print('Image Couldn\'t be retreived')
        print(response.status_code)


def zip_chapters(scan_dir):
    # Zip all chapters
    all_chapters = next(os.walk(scan_dir))[1]
    all_chapters = filter(lambda x: x != "zip", all_chapters)
    zip_output = scan_dir + "zip/"
    Path(zip_output).mkdir(parents=True, exist_ok=True)
    for chapter_dir in all_chapters:
        full_chapter_dir = scan_dir + chapter_dir
        full_chapter_zip_dir = zip_output + chapter_dir
        print("zip chapter {} in {}".format(chapter_dir, full_chapter_zip_dir))
        shutil.make_archive(full_chapter_zip_dir, 'zip', full_chapter_dir)


if __name__ == "__main__":
    print("Go go")
    # scan_dir = './op_scan/'
    # scan_dir = "./soloLeveling_scan/"
    scan_dir = "./one_punch_man/"
    # scan = get_scan("https://www.scan-vf.net/one_piece/chapitre-1000", "op_scan",
    #                 "https://www.scan-vf.net/one_piece/chapitre-1000.5")
    # scan = get_scan("https://www.scan-vf.net/solo-leveling/chapitre-113", scan_dir)
    # scan = get_scan("https://www.scan-vf.net/one-punch-man/chapitre-173", scan_dir)
    zip_chapters(scan_dir)
