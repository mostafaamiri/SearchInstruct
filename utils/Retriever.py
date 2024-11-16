from typing import Tuple, List
from tools import Tools

def make_context(
    query: str,
    tool: Tools,
    num_pages: int = 1,
    verbose: bool = False,
    skip_websites: List[str] = None,
    used_number_of_links: int = None
) -> Tuple[str, List[str]]:
    """
    Retrieves context and links for a given query using the provided tool.

    Parameters:
        query (str): The search query.
        tool (Tools): An instance of a tool that can retrieve context.
        num_pages (int): Number of pages to retrieve from the search tool. Defaults to 1.
        verbose (bool): If True, prints additional information. Defaults to False.
        skip_websites (List[str], optional): List of website domains to skip.
        used_number_of_links (int, optional): Desired number of successfully fetched links.

    Returns:
        Tuple[str, List[str]]: A tuple containing the context string and a list of links.
    """
    return tool.get_context(
        query=query,
        num_pages=num_pages,
        verbose=verbose,
        skip_websites=skip_websites,
        used_number_of_links=used_number_of_links
    )