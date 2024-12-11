from .tools import Tools
import requests
from bs4 import BeautifulSoup
from googlesearch import search
from .llm import LLM
from time import sleep
from typing import List, Tuple, Optional
from urllib.parse import urlparse

class GoogleSearchTool(Tools):
    def __init__(
        self,
        name: str,
        agent: Optional[LLM] = None,
        model: str = "gpt-4o-mini"
    ):
        """
        Initializes the GoogleSearchTool.

        Parameters:
            name (str): The name of the tool.
            agent (LLM, optional): An instance of the LLM agent for query preparation.
            model (str): The name of the model to use with the LLM agent.
        """
        super().__init__(name)
        self.agent = agent
        self.model = model

    def get_context(
        self,
        query: str,
        num_pages: int = 1,
        verbose: bool = False,
        skip_websites: Optional[List[str]] = None,
        used_number_of_links: Optional[int] = None
    ) -> Tuple[str, List[str]]:
        """
        Retrieves context and links for the given query using Google search.

        Parameters:
            query (str): The search query.
            num_pages (int): Not used in this implementation as pagination is not supported.
            verbose (bool): If True, prints additional debug information.
            skip_websites (List[str], optional): List of website domains to skip.
            used_number_of_links (int, optional): Desired number of successfully fetched links.

        Returns:
            Tuple[str, List[str]]: A tuple containing the concatenated context string and a list of used links.
        """
        if skip_websites is None:
            skip_websites = []
        if used_number_of_links is None:
            used_number_of_links = 3  # Default desired number of used links

        max_attempts = 3
        attempts = 0
        results_per_page = 10  # Max number of results per search query
        context = ""
        used_links = []

        # Prepare the query, potentially using the LLM agent
        prepared_query = self.prepare_query(query)

        while attempts < max_attempts:
            attempts += 1
            try:
                # Perform Google search
                results = search(
                    prepared_query,
                    num_results=used_number_of_links * 2,  # Fetch more results to account for skips/failures
                    advanced=True,
                    lang="fa"
                )
                if verbose:
                    print(f"Retrieved links:")

                # Process links
                for idx, result in enumerate(results):
                    if len(used_links) >= used_number_of_links:
                        break

                    link = result.url
                    if verbose:
                        print(f"{idx + 1}: {link}")

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
                            print(f"\033[94mCan't open {link}: {e}\033[0m")
                        continue

                # If we've reached the desired number of used links, exit the loop
                if len(used_links) >= used_number_of_links:
                    break

                if len(used_links) < used_number_of_links:
                    if verbose:
                        print(f"Could only retrieve {len(used_links)} out of {used_number_of_links} desired links.")
                    break  # No more results to process

            except Exception as e:
                if verbose:
                    print(f"Error during search: {e}")
                sleep(5)  # Wait before retrying

        return context, used_links

    def prepare_query(self, query: str) -> str:
        """
        Prepares the search query, optionally using the LLM agent.

        Parameters:
            query (str): The original query.

        Returns:
            str: The prepared query for searching.
        """
        if self.agent:
            prompt = (
                "Given an instruction, respond with a search term query "
                "which can be efficiently used to find the answer in search engines. "
                "Do not include any explanations."
            )
            try:
                # Generate the search query using the LLM agent
                completion = self.agent.get_client().chat.completions.create(
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": query}
                    ],
                    model=self.model,
                )
                result = completion.choices[0].message.content.strip()
                return result
            except Exception as e:
                if hasattr(self, 'verbose') and self.verbose:
                    print(f"Error generating query with LLM: {e}")
                return query  # Fallback to the original query
        else:
            return query
