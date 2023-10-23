import requests
from bs4 import BeautifulSoup


def get_main_text(URL):
    text = []

    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "lxml")
    for child in soup.html.body.find_all(id="textcontainer"):
        text.append(child)
        # print(soup.html.body.find_all(id="textcontainer")[0].p.contents[1])

    return text
