import json, sys, pickle
from time import sleep
from bs4 import BeautifulSoup
from urllib.request import urlopen

class Palette:
    def __init__(self, soup):
        self.title = soup.a['title'].replace('Color palette ', '')
        self.title = ' '.join([w.capitalize() for w in self.title.split(' ')])
        self.colours = list()
        for colordiv in soup.findAll('div', {'class': 'palettecolordiv'}):
            self.colours.append(colordiv['style'].replace('background-color:', ''))

    def __repr__(self):
        return f"<Color Palette: {self.title} {self.colours}>"


def saveJSON(palettes, pckl, path="schemes"):
    JSONdata = dict()
    fields = ['fg', 'bg', 'dark', 'light', 'tint']
    for palette in palettes:
        scheme = { fields[i]:colour for (i,colour) in enumerate(palette.colours) }
        JSONdata[palette.title] = scheme
    if not pckl:
        json.dump(JSONdata, open(f'{path}.json', "w"), indent=2)
    else:
        with open(f'{path}.pk', 'wb') as pfile:
            pickle.dump(json.dumps(JSONdata, indent=2), pfile)

def log(msg, colorcode):
    col = dict(
        warn='\033[93m',
        ok='\033[92m',
        status='\033[94m',
        fail='\033[91m'
    )[colorcode]
    print(f"{col}{msg}\033[0m")

if __name__ == '__main__':
    PAGES = 1
    PICKLE = False

    if len(sys.argv) > 1 and '-n' in sys.argv:
        try:
            PAGES = int(sys.argv[sys.argv.index('-n')+1])
        except:
            log("Could not get valid '-n' argument. Defaulting to 1 page (40 items)", 'warn')
    elif len(sys.argv) > 1 and '-n' not in sys.argv:
        log("Could not get '-n' argument. Defaulting to 1 page (40 items)", 'warn')
    if len(sys.argv) > 1 and '-p' in sys.argv:
        try:
            if (pk:=sys.argv[sys.argv.index('-p')+1]) in ('True', 'False'):
                PICKLE = pk == 'True'
            else:
                log("Could not get valid '-p' argument. Defaulting to False", 'warn')
        except:
            log("Could not get '-p' argument. Defaulting to False", 'warn')

    URL = "http://www.color-hex.com/color-palettes/?page={pagenum}"
    PALETTES = list()

    log(f"Scraping {PAGES} page{'s' if PAGES > 1 else ''}...", 'ok')

    for pagenum in range(1, PAGES+1):
        client = urlopen(URL.format(pagenum=pagenum))
        html_data = client.read()
        client.close()
        soup_data = BeautifulSoup(html_data, "html.parser")
        palettes = soup_data.findAll("div", {"class": "palettecontainerlist"})
        palettes = map(Palette, palettes)
        PALETTES += palettes

    log(f"Scraped {len(PALETTES)} palettes", 'ok')
    sleep(1)
    log(f"Saving to schemes.{'pk' if PICKLE else 'json'}...", 'ok')
    saveJSON(PALETTES, PICKLE)
    log("Scrape complete. Palettes saved", 'ok')
