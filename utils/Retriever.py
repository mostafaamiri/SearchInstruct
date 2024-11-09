from typing import Tuple, List
from tools import Tools

def make_context(
    query: str,
    tool: Tools,
    num: int = 3,
    verbose: bool = False
) -> Tuple[str, List[str]]:
    """
    Retrieves context and links for a given query using the provided tool.

    Parameters:
        query (str): The search query.
        tool (Tools): An instance of a tool that can retrieve context.
        num (int): Number of results to retrieve. Defaults to 3.
        verbose (bool): If True, prints additional information. Defaults to False.

    Returns:
        Tuple[str, List[str]]: A tuple containing the context string and a list of links.
    """
    return tool.get_context(query, num, verbose)
