from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

app = Flask(__name__)

SITES = [
    "https://github.com/{}",
    "https://www.reddit.com/user/{}",
    "https://twitter.com/{}",
    "https://instagram.com/{}",
    "https://www.tiktok.com/@{}",
    "https://medium.com/@{}",
    "https://t.me/{}"
]

def search_by_nickname(nickname):
    results = []
    for site in SITES:
        url = site.format(nickname)
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                info = {"url": url, "status": "найден"}
                if "t.me" in url:
                    info["extra"] = parse_telegram(url)
                results.append(info)
            else:
                results.append({"url": url, "status": "не найден"})
        except:
            results.append({"url": url, "status": "ошибка"})
    return results

def parse_telegram(url):
    info = {}
    try:
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.find("meta", property="og:title")
        desc = soup.find("meta", property="og:description")
        if title: info["name"] = title["content"]
        if desc: info["desc"] = desc["content"]
    except:
        pass
    return info

def search_by_phone(phone):
    query = quote_plus(f'"{phone}"')
    return [
        f"https://www.google.com/search?q={query}",
        f"https://www.bing.com/search?q={query}",
    ]

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    phone_links = []
    if request.method == "POST":
        mode = request.form.get("mode")
        if mode == "nickname":
            results = search_by_nickname(request.form.get("nickname"))
        elif mode == "phone":
            phone_links = search_by_phone(request.form.get("phone"))
    return render_template("index.html", results=results, phone_links=phone_links)

if __name__ == "__main__":
    app.run(debug=True)
