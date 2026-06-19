import requests
from urllib.parse import urlparse, quote
from flask import Flask, render_template, request
from bs4 import BeautifulSoup
from readability import Document

headers = {"User-Agent": "WebLite/0.1 (Webpage Debloater for Slow Networks)"}

class Page:
    def __init__(self, link, images=False, script=False):
        parsed_url = urlparse(link or "")
        self.hostname = parsed_url.hostname
        self.link = link if self.hostname not in ("localhost", "127.0.0.1") else None
        self.images = images
        self.script = script

    # def clean_tags(self, parsed_page):
    #     if not self.script:
    #         try:
    #             parsed_page.script.decompose()
    #         except:
    #             pass
    #     if not self.images:
    #         try:
    #             parsed_page.img.decompose()
    #         except:
    #             pass
    #     try:
    #         parsed_page.video.decompose()
    #     except:
    #         pass

    #     try:
    #         parsed_page.iframe.decompose()
    #     except:
    #         pass

    #     return parsed_page

    def clean_tags(self, parsed_page):
        page = Document(str(parsed_page))
        return page.summary()
    
    def replace_links(self, page):
        # return page
        links = page.find_all("a")
        print(links)
        for link in links:
            try:
                if link['href'].startswith("#"):
                    continue
                if link['href'].startswith("/"):
                    link['href'] = f"?url=https://{self.hostname}/{link['href']}"
            except:
                print("Error")

    def remove_imgs(self, parsed_page):
        imgs = parsed_page.find_all("img")
        print(imgs)
        for img in imgs:
            curr_link = img['src']
            # img['src'] = f"http://{self.hostname}{curr_link}"
            img['src'] = f"?img=https://{self.hostname}{curr_link}"
    

    def get_page(self):
        page_data = requests.get(self.link, headers=headers)

        page_parsed = self.clean_tags(page_data.content)

        page_parsed = BeautifulSoup(page_parsed, "html.parser")
        self.replace_links(page_parsed)
        self.remove_imgs(page_parsed)

        body = page_parsed.find("body")
        body['style'] = "font-family: Arial, sans-serif; line-height: 1.6; margin: 20px;"
        
        page_parsed = str(page_parsed)
        page_parsed = page_parsed.replace("\\n", "")
        page_parsed = page_parsed.replace("<head></head>", f"<head><title>WebLite</title></head>")
        return page_parsed
    
    def get_image(self):
        image_url = self.link
        image = requests.get(image_url, headers=headers)

class WebUI:
    def __init__(self, host="127.0.0.1", port=5000):
        self.host = host
        self.port = port
        self.app = Flask(__name__, static_folder="./static", template_folder="./")
        self._register_routes()

    def _register_routes(self):
        self.app.add_url_rule("/", "home", self.home)

    def home(self):
        try:
            url = request.args.get("url")
        except:
            pass
        if url:
            new_page = Page(url)
            return str(new_page.get_page())
        
        try:
            img = request.args.get("img")
        except:
            pass
        if img:
            image = Page(img)
            return image.get_image()

        return render_template("index.html")
    
    
    # def run(self, debug=False):
    #     self.app.run(host=self.host, port=self.port, debug=debug)


# meow = Page("https://en.wikipedia.org/wiki/Randomness")
# print(meow.get_page())

app = WebUI().app

if __name__=="__main__":
    app.run(debug=True)