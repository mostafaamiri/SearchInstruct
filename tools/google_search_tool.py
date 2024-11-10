from .tools import Tools
import requests
from bs4 import BeautifulSoup
from googlesearch import search
from .llm import LLM
from time import sleep
from typing import List, Tuple, Optional

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
        num: int = 3,
        verbose: bool = False
    ) -> Tuple[str, List[str]]:
        """
        Retrieves context and links for the given query using Google search.

        Parameters:
            query (str): The search query.
            num (int): The number of links to retrieve content from.
            verbose (bool): If True, prints additional debug information.

        Returns:
            Tuple[str, List[str]]: A tuple containing the concatenated context string and a list of used links.
        """
        retrieval_links = []
        max_attempts = 3
        attempts = 0

        # Prepare the query, potentially using the LLM agent
        prepared_query = self.prepare_query(query)

        # Loop to retry the search if no results are found
        while attempts < max_attempts:
            attempts += 1
            idx = 0
            try:
                # Perform Google search
                results = search(
                    prepared_query,
                    num_results=20,
                    advanced=True,
                    lang="fa"
                )
                # Collect URLs from the search results
                for idx, result in enumerate(results, start=1):
                    retrieval_links.append(result.url)
                    if verbose:
                        print(f"{idx}: {result.url}")
                if verbose:
                    print("\033[93mEnd of search\033[0m")
                # If results are found, break the loop
                if idx > 0:
                    break
            except Exception as e:
                if verbose:
                    print(f"Error during search: {e}")
                sleep(5)  # Wait before retrying

        if idx == 0:
            if verbose:
                print("No search results found after multiple attempts.")
            return "", []

        context = ""
        used_links = []
        num_context = 0

        # Fetch content from the retrieved links
        for link in retrieval_links:
            if num_context >= num:
                break
            try:
                resp = requests.get(link, timeout=30)
                resp.raise_for_status()
                bs = BeautifulSoup(resp.text, 'html.parser')
                body = bs.find('body')
                if body:
                    context += body.get_text(separator=' ', strip=True)
                    context += "\n"
                    used_links.append(link)
                    num_context += 1
            except requests.RequestException as e:
                if verbose:
                    print(f"\033[94mCan't open {link}: {e}\033[0m")
                continue

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
                result = completion.choices[0].message.content
                return result
            except Exception as e:
                if hasattr(self, 'verbose') and self.verbose:
                    print(f"Error generating query with LLM: {e}")
                return query  # Fallback to the original query
        else:
            return query
