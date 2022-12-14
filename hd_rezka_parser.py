from bs4 import BeautifulSoup as BS
import requests
from requests_html import HTMLSession


class HdRezkaParser:
    def __init__(self, url):
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}

    def get_content_list(self, mirror):
        session = HTMLSession()
        resp = session.get(self.url, headers=self.headers)
        html = BS(resp.html.html, "html.parser")
        session.close()
        content_list = html.find(
            "div", class_="b-content__inline_items").find_all("div", class_="b-content__inline_item")

        content_list = list(
            map(lambda content: self.get_content_info(content, mirror), content_list))

        return content_list

    @staticmethod
    def get_content_info(content, mirror):
        content_info = {
            "id": int(content.attrs["data-id"]),
            "type": content.find("i", class_="entity").text,
        }
        content_info["title"] = content.find(
            "div", class_="b-content__inline_item-link").find("a").text
        content_info["mirrorLessUrl"] = content.find("div").find(
            "a").attrs["href"]
        content_info["imageUrl"] = content.find("img").attrs["src"]
        item_link = content.find(
            "div", class_="b-content__inline_item-link").find("div").text.split(',')

        content_info["year"] = item_link[0].strip()
        content_info["country"] = item_link[1].strip()
        content_info["genre"] = item_link[2].strip()

        status = content.find("span", class_="info")
        content_info["status"] = None if status is None else status.text

        return content_info

    @staticmethod
    def get_url_by_id(mirror, id):
        url = f"{mirror}engine/ajax/quick_content.php"
        data = {"id": id, "is_touch": 1}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
        r = requests.post(url, headers=headers, data=data)
        html = BS(r.content, "html5lib")
        return html.find("div", class_="b-content__bubble_title").find("a").attrs["href"]

    @staticmethod
    def get_concrete_content_info(url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
        r = requests.get(url, headers=headers)
        html = BS(r.content, "html5lib")

        content_info = {"id": int(html.find(id="post_id").attrs['value'])}
        content_info["url"] = url
        content_info["type"] = html.find(
            'meta', property="og:type").attrs['content'].split(".")[-1]
        content_info["title"] = html.find(
            'div', class_="b-post__title").find("h1").text
        content_info["description"] = html.find(
            'div', class_="b-post__description_text").text.strip()
        content_info["imageUrl"] = html.find(
            'div', class_="b-sidecover").find("a").attrs['href']

        table = html.find("table", class_="b-post__info")
        table_body = table.find("tbody")
        rows = table_body.find_all('tr')
        rows = table_body.find_all('tr')
        
        data = {}
        for row in rows[:-1]:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data[str(DataAtribute(cols[0].replace(":", "")))] = cols[1]

        # convert time 
        time = data.get("time")
        if time is not None:
            time = time.replace(" ??????.", "")
            hour, minute = divmod(int(time), 60)
            if hour < 10:
                hour = f"0{str(hour)}"
            if minute < 10:
                minute = f"0{str(minute)}"
            data["time"] = f"{str(hour)}:{str(minute)}"

        actors = [
            f"{actor.text} " for actor in rows[-1].find_all("span", class_="item")]
        data["actors"] = "".join(actors).replace(" ?? ???????????? ", "").strip()

        data.pop("is_series_bad", None)
        data.pop("list_bad", None)

        content_info["data"] = data

        content_info["translations_id"] = []
        
        translations = html.find("ul", id="translators-list")
        if translations is not None:
            for translation in translations.find_all("li"):
                content_info["translations_id"].append(
                    {"name": translation.text, "id": translation.attrs["data-translator_id"]})

        return content_info


class DataAtribute:
    def __init__(self, name):
        array = {
            "????????????????": "rating",
            "????????????": "slogan",
            "???????? ????????????": "release",
            "????????????": "country",
            "????????????????": "director",
            "????????": "genre",
            "?? ????????????????": "quality",
            "??????????????": "age",
            "??????????": "time",
            "???? ??????????": "is_series_bad",
            "?? ????????????????": "translation",
            "?? ?????????? ????????????": "actors",
            "???????????? ?? ????????????": "list_bad"
        }
        self.name = array[name]

    def __str__(self):
        return self.name