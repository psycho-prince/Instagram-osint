import requests
from bs4 import BeautifulSoup

def dumpor_search(name):
    url = f"https://dumpor.com/search?query={name.replace(' ', '+')}"
    r = requests.get(url, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")
    return list({a.text.strip() for a in soup.find_all("a", class_="profile-name-link")})
