import uuid
from bs4 import BeautifulSoup
import requests
import genanki
import tempfile
import os
import regex as re

WIKIPEDIA_URL = 'https://en.wikipedia.org'
PAGE_NAME = "/wiki/Departments_of_France"
MAP_TEMPLATE_URL = "https://upload.wikimedia.org/wikipedia/commons/b/b6/D%C3%A9partements_de_France-simple.svg"
MODEL = genanki.Model(
    2081266965,  # Model ID
    "French Departments",  # Model name
    fields=[
        {"name": "Name"},
        {"name": "Capital"},
        {"name": "Map"},
        {"name": "Map Template"}, # TODO: the script should be parametrized whether we want to use the map template or not
        {"name": "Flag"},
        {"name": "INSEE"},
    ],
    templates=[
        {
            "name": "Name / Capital",
            "qfmt": open("templates/name_capital/front.html", "r").read().replace('#TITLE', '🇫🇷 Département de France 🇫🇷'),
            "afmt": open("templates/name_capital/back.html", "r").read().replace('#TITLE', '🇫🇷 Département de France 🇫🇷'),
        },
        {
            "name": "Name / Map",
            "qfmt": open("templates/name_map/front.html", "r").read().replace('#TITLE', '🇫🇷 Département de France 🇫🇷'),
            "afmt": open("templates/name_map/back.html", "r").read().replace('#TITLE', '🇫🇷 Département de France 🇫🇷'),
        },
        {
            "name": "Name / Flag",
            "qfmt": open("templates/name_flag/front.html", "r").read().replace('#TITLE', '🇫🇷 Département de France 🇫🇷'),
            "afmt": open("templates/name_flag/back.html", "r").read().replace('#TITLE', '🇫🇷 Département de France 🇫🇷'),
        },
        {
            "name": "Name / INSEE",
            "qfmt": open("templates/name_extra/front.html", "r").read().replace('#TITLE', '🇫🇷 Département de France 🇫🇷').replace('#TYPE', 'INSEE'),
            "afmt": open("templates/name_extra/back.html", "r").read().replace('#TITLE', '🇫🇷 Département de France 🇫🇷').replace('#TYPE', 'INSEE'),
        },
        {
            "name": "Capital / Name",
            "qfmt": open("templates/capital_name/front.html", "r").read().replace('#TITLE', '🇫🇷 Département de France 🇫🇷'),
            "afmt": open("templates/capital_name/back.html", "r").read().replace('#TITLE', '🇫🇷 Département de France 🇫🇷'),
        },
        {
            "name": "Map / Name",
            "qfmt": open("templates/map_name/front.html", "r").read().replace('#TITLE', '🇫🇷 Département de France 🇫🇷'),
            "afmt": open("templates/map_name/back.html", "r").read().replace('#TITLE', '🇫🇷 Département de France 🇫🇷'),
        },
        {
            "name": "Flag / Name",
            "qfmt": open("templates/flag_name/front.html", "r").read().replace('#TITLE', '🇫🇷 Département de France 🇫🇷'),
            "afmt": open("templates/flag_name/back.html", "r").read().replace('#TITLE', '🇫🇷 Département de France 🇫🇷'),
        },
        {
            "name": "INSEE / Name",
            "qfmt": open("templates/extra_name/front.html", "r").read().replace('#TITLE', '🇫🇷 Département de France 🇫🇷').replace('#TYPE', 'INSEE'),
            "afmt": open("templates/extra_name/back.html", "r").read().replace('#TITLE', '🇫🇷 Département de France 🇫🇷').replace('#TYPE', 'INSEE'),
        },
    ],
    css=open("style.css", "r").read()
)


DECK = genanki.Deck(
    2075812990,  # Deck ID
    "French Departments",  # Deck name
)

PACKAGE = genanki.Package(DECK)


def download_image(url, name = None, type = None):
    headers = {
        'User-Agent': 'anki_regions_of_france/0.0 (https://github.com/lthiet/anki_region_france, nguyenthiet.lam@gmail.com)'}
    map_response = requests.get(url, headers=headers)

    # Write the map to a file
    if not os.path.exists('data'):
        os.makedirs('data')
    if name is None or type is None:
        map_download_path = os.path.join('data', str(uuid.uuid4()) + '.svg')
    else:
        map_download_path = os.path.join('data', name + '_' + type + '.svg')
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
    table = soup.find_all("table", {"class": "wikitable"})[0]

    # Transform the table into a list of lists
    table_rows = table.find_all("tr")
    table_data = []
    for row in table_rows:
        table_data.append([])
        table_data[-1] = [cell for cell in row.find_all(["td", "th"])]

    # Remove the first row (header)
    table_data.pop(0)


    # Download the map template
    map_template = download_image(MAP_TEMPLATE_URL, 'map_template', 'svg')
    media_files = []
    media_files.append(map_template)

    # Iterate over the table
    for i, row in enumerate(table_data):
        # Get the name
        name = row[3].find('a').get_text().strip()
        # Remove numbers
        name = re.sub(r'\d+', '', name)

        # Get the capital
        capital = row[4].get_text().strip()
        # Remove numbers
        capital = re.sub(r'\d+', '', capital)

        # Get INSEE
        insee = row[0].get_text().strip()

        # Get the map
        # TODO: Manual for overseas and Paris
        if i < len(table_data) - 5 and capital != "Paris":
            dpt_page_url = WIKIPEDIA_URL + row[3].find('a').get('href')
            dpt_page = requests.get(dpt_page_url)
            dpt_soup = BeautifulSoup(dpt_page.text, "html.parser")
            map_page_url = WIKIPEDIA_URL + \
                dpt_soup.find_all("a", {"title": re.compile(r'Location')})[
                    0].get('href')
            map_page = requests.get(map_page_url)
            map_soup = BeautifulSoup(map_page.text, "html.parser")
            map_url = "https:" + \
                map_soup.find('div', {"id": "file"}).find('a').get('href')
            map_abs_path = download_image(map_url, name, "map")

        # Get the flag
        flag_page_url = WIKIPEDIA_URL + row[1].find('a').get('href')
        flag_page = requests.get(flag_page_url)
        flag_soup = BeautifulSoup(flag_page.text, "html.parser")
        flag_url = "https:" + \
            flag_soup.find('div', {"id": "file"}).find('a').get('href')
        flag_abs_path = download_image(flag_url, name, "flag")

        # Put media files
        media_files.append(map_abs_path)
        if flag_abs_path:
            media_files.append(flag_abs_path)

        note = genanki.Note(
            model=MODEL,
            fields=[
                name,
                capital,
                f"<img src='{map_abs_path.split('/')[-1]}'>" if map_abs_path else "",
                f"<img src='{map_template.split('/')[-1]}'>" if map_template else "",
                f"<img src='{flag_abs_path.split('/')[-1]}'>" if flag_abs_path else "",
                insee
            ]
        )
        DECK.add_note(note)

    # Write the package
    PACKAGE.media_files = media_files
    PACKAGE.write_to_file('output.apkg')
