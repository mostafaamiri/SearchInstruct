from .tools import Tools
import requests
from bs4 import BeautifulSoup
from typing import Tuple, List, Optional
from urllib.parse import urlparse

class SerperTool(Tools):
    def __init__(self, name: str, api_key: str):
        """
        Initializes the SerperTool with the given name and API key.

        Parameters:
            name (str): The name of the tool.
            api_key (str): The API key for Serper API.
        """
        super().__init__(name)
        self.api_key = api_key

    def get_context(
        self,
        query: str,
        num_pages: int = 1,
        verbose: bool = False,
        skip_websites: Optional[List[str]] = None,
        used_number_of_links: Optional[int] = None
    ) -> Tuple[str, List[str]]:
        """
        Retrieves context and links for a given query using Serper API.

        Parameters:
            query (str): The search query.
            num_pages (int): Number of pages to retrieve from the search tool.
            verbose (bool): If True, prints additional information.
            skip_websites (List[str], optional): List of website domains to skip.
            used_number_of_links (int, optional): Desired number of successfully fetched links.

        Returns:
            Tuple[str, List[str]]: A tuple containing the context string and a list of used links.
        """
        if skip_websites is None:
            skip_websites = []
        if used_number_of_links is None:
            used_number_of_links = 3  # Default desired number of used links

        url = "https://google.serper.dev/search"
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }

        used_links = []
        context = ""
        total_pages_retrieved = 0
        page = 0  # Pagination counter
        max_attempts = num_pages  # Number of pages to retrieve

        results_per_page = 10  # Number of results per page (Serper API default)

        while (
            len(used_links) < used_number_of_links and
            total_pages_retrieved < num_pages and
            page < max_attempts
        ):
            payload = {
                "q": query,
                "num": results_per_page,
                "start": page * results_per_page
            }

            try:
                response = requests.post(url, headers=headers, json=payload)
                response.raise_for_status()
                results = response.json()
            except requests.RequestException as e:
                if verbose:
                    print(f"Serper API request failed: {e}")
                break  # Exit if API request fails

            # Extract organic search results
            organic_results = results.get("organic", [])
            if not organic_results:
                if verbose:
                    print("No more search results available.")
                break

            if verbose:
                print(f"Retrieved links from page {page + 1}:")

            # Process links
            for res in organic_results:
                if len(used_links) >= used_number_of_links:
                    break

                link = res.get('link')
                if verbose:
                    print(link)

                # Skip links from skipped websites
                parsed_url = urlparse(link)
                domain = parsed_url.netloc

                if any(skip_domain in domain for skip_domain in skip_websites):
                    if verbose:
                        print(f"Skipping link from skipped website: {link}")
                    continue

                try:
                    resp = requests.get(link, timeout=30)
                    resp.raise_for_status()
                    bs = BeautifulSoup(resp.text, 'html.parser')
                    body = bs.find('body')
                    if body:
                        context += body.get_text(separator=' ', strip=True)
                        context += "\n"
                        used_links.append(link)
                except requests.RequestException as e:
                    if verbose:
                        print(f"Failed to fetch {link}: {e}")
                    # Do not count this link as a used link
                    continue

            total_pages_retrieved += 1
            page += 1  # Move to the next page of results

        if len(used_links) < used_number_of_links:
            if verbose:
                print(f"Could only retrieve {len(used_links)} out of {used_number_of_links} desired links.")

        return context, used_links
