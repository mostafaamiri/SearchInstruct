from .tools import Tools
import requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch



class SerpTool(Tools):
    def __init__(self, name: str, api_key: str):
        super().__init__(name)
        self.api_key = api_key
    def get_context(self, query: str, num: int = 3, verbose: bool = False)->str:
        params = {
        "engine": "google",
        "q": query,
        "api_key": self.api_key,
        "num": num
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        organic_results = results["organic_results"]
        links = []

        for res in organic_results:
            links.append(res['link'])
        if verbose:
            for l in links:
                print(l)
        context = ""
        for link in links:
            resp =requests.get(link, timeout=30)
            if resp:
                bs = BeautifulSoup(resp.text, 'html.parser')
                context += bs.find('body').getText()
                context += "\n"
        return context