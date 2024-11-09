from .tools import Tools
import requests
from bs4 import BeautifulSoup
import json

class SerperTool(Tools):
    def __init__(self, name: str, api_key: str):
        super().__init__(name)
        self.api_key = api_key

    def get_context(self, query: str, num: int = 3, verbose: bool = False) -> str:
        url = "https://google.serper.dev/search"
        payload = {
            "q": query
        }
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }

        # Make a POST request to the Serper API
        response = requests.post(url, headers=headers, json=payload)
        results = response.json()

        # Extract organic search results
        organic_results = results.get("organic", [])
        links = [res.get('link') for res in organic_results[:num]]

        if verbose:
            for link in links:
                print(link)

        # Fetch content from the extracted links
        context = ""
        for link in links:
            try:
                resp = requests.get(link, timeout=30)
                resp.raise_for_status()
                bs = BeautifulSoup(resp.text, 'html.parser')
                body = bs.find('body')
                if body:
                    context += body.get_text(separator=' ', strip=True)
                    context += "\n"
            except requests.RequestException as e:
                if verbose:
                    print(f"Failed to fetch {link}: {e}")

        return context, links
