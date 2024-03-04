import glob
import os
from typing import List
import sys

import converter
import requests
from bs4 import BeautifulSoup


def _flatten_list(list_of_lists):
    return [item for sublist in list_of_lists for item in sublist]


def get_urls(pages) -> List[str]:
    counter = 1
    res = []

    while counter != pages:
        # Fetch the content from the URL
        url = f"https://www.ft.dk/da/dokumenter/dokumentlister/referater?pageSize=200&startDate=20000101&endDate=20240131&totalNumberOfRecords=2127&pageNumber={counter}"
        response = requests.get(url)
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")

            # Find all the <tr> tags
            tr_tags = soup.find_all("tr")

            links = []

            # Print or process the <tr> tags as needed
            for tr in tr_tags:
                if "forhandlinger" in str(tr):
                    s = str(tr)
                    s = s.split("data-url=")
                    for i in s:
                        if "forhandlinger" in i:
                            k = i.splitlines()
                            links.append(f'https://www.ft.dk{(k[0].split(" ")[0])}')
                            links = [i.replace('"', "") for i in links]
            res.append(links)

        counter += 1

    return _flatten_list(res)


def extract_file():
    urls = get_urls(12)
    for url in urls:
        ft = url.split(".")[-1]
        filename = url.split(".")[-2].replace("/", "_")

        r = requests.get(url)

        if r.status_code == 200:
            with open(f"data/{filename}.{ft}", "wb") as file:
                file.write(r.content)
                print(f"{ft} file saved successfully with filename {filename}.{ft}")
        else:
            print(f"Failed to retrieve the content. Status code: {r.status_code}")


def clear_dir(dir):
    files = glob.glob(os.path.join(dir, "*"))
    for file_path in files:
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Remove {file_path} successfully")
        except Exception as e:
            print(f"Error occurred while deleting file: {file_path}. Error: {e}")


def main():
    args = sys.argv

    if "--dry" not in args:
        clear_dir("data")

    extract_file()

    if "--no-conversion" not in args:
        converter.convert_files_to_pdf("data")


if __name__ == "__main__":
    main()
