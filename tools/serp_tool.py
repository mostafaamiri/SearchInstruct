from .tools import Tools
import requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch
from typing import Tuple, List

class SerpTool(Tools):
    def __init__(self, name: str, api_key: str):
        """
        Initializes the SerpTool with the given name and API key.

        Parameters:
            name (str): The name of the tool.
            api_key (str): The API key for SerpAPI.
        """
        super().__init__(name)
        self.api_key = api_key

    def get_context(self, query: str, num: int = 3, verbose: bool = False) -> Tuple[str, List[str]]:
        """
        Retrieves context and links for a given query using SerpAPI.

        Parameters:
            query (str): The search query.
            num (int): Number of results to retrieve.
            verbose (bool): If True, prints additional information.

        Returns:
            Tuple[str, List[str]]: A tuple containing the context string and a list of links.
        """
        # Set up parameters for SerpAPI
        params = {
            "engine": "google",
            "q": query,
            "api_key": self.api_key,
            "num": num
        }

        # Perform search using SerpAPI
        search = GoogleSearch(params)
        results = search.get_dict()

        # Extract organic results
        organic_results = results.get("organic_results", [])
        links = [res.get('link') for res in organic_results[:num]]

        if verbose:
            print("Retrieved links:")
            for link in links:
                print(link)

        # Fetch content from the links
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
