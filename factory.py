from bs4 import BeautifulSoup
import requests
import genanki
import tempfile

WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/Regions_of_France"
MODEL = genanki.Model(
    1980728030,  # Model ID
    "French Regions",  # Model name
    fields=[
        {"name": "Name"},
        {"name": "Capital"},
        {"name": "Flag"},
        {"name": "Map"},
    ],
    templates=[
        {
            "name": "Name / Capital",
            "qfmt": "{{Name}}",
            "afmt": "{{FrontSide}}<hr id=answer>{{Capital}}",
        },
    ],
)

DECK = genanki.Deck(
    1997108613,  # Deck ID
    "French Regions",  # Deck name
)


if __name__ == "__main__":
    # Get the HTML
    page = requests.get(WIKIPEDIA_URL)

    # Parse the HTML
    soup = BeautifulSoup(page.text, "html.parser")

    # Get the table
    table = soup.find("table", {"class": "wikitable"})

    # Transform the table into a list of lists
    table_rows = table.find_all("tr")
    table_data = []
    for row in table_rows:
        table_data.append([])
        table_data[-1] = [cell for cell in row.find_all("td")]

    # Remove the first row (header)
    table_data.pop(0)

    # Iterate over the table
    for row in table_data:
        # Get the name
        name = row[2].get_text()
        # Get the capital
        capital = row[4].get_text()

        # Get the flag URL
        flag_url_tmp = row[0].find("a").get("href")
        # Add the wiki link to it
        flag_url_tmp = "https://en.wikipedia.org" + flag_url_tmp
        # Request the page for the flag
        flag_page = requests.get(flag_url_tmp)
        # Parse the HTML
        flag_soup = BeautifulSoup(flag_page.text, "html.parser")
        # Find the div containing the flag, it has an id of "file"
        flag_div = flag_soup.find("div", {"id": "file"})
        # Get the URL of the flag
        flag_url = "http:" + flag_div.find("a").get("href")

        # Download the flag to a temporary file
        flag_file = requests.get(flag_url, stream=True)
        with tempfile.NamedTemporaryFile() as f:
            for chunk in flag_file.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
            # Get the path of the file
            flag_path = f.name

        # # Put the flag into the media
        # DECK.media_files = [
        #     flag_path
        # ]

        note = genanki.Note(
            model=MODEL,
            fields={
                "Name": name,
                "Capital": capital,
                "Flag": name, # TODO: Add the flag
                "Map": name # TODO: Add the map
            }
        )
        DECK.add_note(note)

    # Save the deck
    genanki.Package(DECK).write_to_file('output.apkg')
