import uuid
from bs4 import BeautifulSoup
import requests
import genanki
import tempfile
import os

WIKIPEDIA_URL = 'https://en.wikipedia.org'
PAGE_NAME = "/wiki/Regions_of_France"
MODEL = genanki.Model(
    1943297000,  # Model ID
    "French Regions",  # Model name
    fields=[
        {"name": "Name"},
        {"name": "Capital"},
        {"name": "Map"},
        {"name": "Flag"},
    ],
    templates=[
        {
            "name": "Name / Capital",
            "qfmt": open("templates/name_capital/front.html", "r").read(),
            "afmt": open("templates/name_capital/back.html", "r").read(),
        },
        {
            "name": "Name / Map",
            "qfmt": open("templates/name_map/front.html", "r").read(),
            "afmt": open("templates/name_map/back.html", "r").read(),
        },
        {
            "name": "Name / Flag",
            "qfmt": open("templates/name_flag/front.html", "r").read(),
            "afmt": open("templates/name_flag/back.html", "r").read(),
        },
        {
            "name": "Capital / Name",
            "qfmt": open("templates/capital_name/front.html", "r").read(),
            "afmt": open("templates/capital_name/back.html", "r").read(),
            
        },
        {
            "name": "Map / Name",
            "qfmt": open("templates/map_name/front.html", "r").read(),
            "afmt": open("templates/map_name/back.html", "r").read(),

        },
        {
            "name": "Flag / Name",
            "qfmt": open("templates/flag_name/front.html", "r").read(),
            "afmt": open("templates/flag_name/back.html", "r").read(),
        },
    ],
    css=open("style.css", "r").read()
)


DECK = genanki.Deck(
    1997108613,  # Deck ID
    "French Regions",  # Deck name
)

PACKAGE = genanki.Package(DECK)


def download_image(url):
    id = uuid.uuid4()
    headers = {
            'User-Agent': 'anki_regions_of_france/0.0 (https://github.com/lthiet/anki_region_france, nguyenthiet.lam@gmail.com)'}
    map_response = requests.get(url, headers=headers)

    # Write the map to a file
    if not os.path.exists('data'):
        os.makedirs('data')
    map_download_path = os.path.join('data', str(id) + '.svg')
    with open(map_download_path, 'wb') as f:
        f.write(map_response.content)

    # return os.path.abspath(map_download_path)
    return map_download_path

if __name__ == "__main__":
    # Get the HTML
    page = requests.get(WIKIPEDIA_URL + PAGE_NAME)

    # Parse the HTML
    soup = BeautifulSoup(page.text, "html.parser")

    # Get the third table
    table = soup.find_all("table", {"class": "wikitable"})[2]

    # Transform the table into a list of lists
    table_rows = table.find_all("tr")
    table_data = []
    for row in table_rows:
        table_data.append([])
        table_data[-1] = [cell for cell in row.find_all("td")]

    # Remove the first row (header)
    table_data.pop(0)

    media_files = []
    # Iterate over the table
    for i, row in enumerate(table_data):
        if i > 12:
            continue
        # Get the name
        name = row[1].find('a').get_text().strip()
        # Get the capital
        capital = row[3].get_text().strip()

        # Get the map
        map_page_url = WIKIPEDIA_URL + row[-1].find('a').get('href')
        map_page = requests.get(map_page_url)
        map_soup = BeautifulSoup(map_page.text, "html.parser")
        map_url = "https:" + \
            map_soup.find('div', {"id": "file"}).find('a').get('href')
        map_abs_path = download_image(map_url)

        # Get the flag
        region_page_url = row[1].find('a').get('href')
        region_soup = BeautifulSoup(requests.get(WIKIPEDIA_URL + region_page_url).text, "html.parser")
        flag_page_url_candidates = region_soup.find_all('a', {"class": "image"})
        candidate_found = False
        for candidate in flag_page_url_candidates:
            if 'Flag' in candidate.get("href"):
                flag_page_url = WIKIPEDIA_URL + candidate.get("href")
                candidate_found = True
                break
        if not candidate_found:
            flag_abs_path = None
        else:
            flag_page = requests.get(flag_page_url)
            flag_soup = BeautifulSoup(flag_page.text, "html.parser")
            flag_url = "https:" + flag_soup.find('div', {"id": "file"}).find('a').get('href')
            flag_abs_path = download_image(flag_url)
        

        # Put media files
        media_files.append(map_abs_path)
        if flag_abs_path:
            media_files.append(flag_abs_path)


        note = genanki.Note(
            model=MODEL,
            fields=[
                name,
                capital,
                f"<img src='{map_abs_path.split('/')[-1]}'>",
                f"<img src='{flag_abs_path.split('/')[-1]}'>" if flag_abs_path else ""
            ]
        )
        DECK.add_note(note)
    
    # Write the package
    PACKAGE.media_files = media_files
    PACKAGE.write_to_file('output.apkg')
