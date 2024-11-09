from typing import Tuple, List
from abc import ABC, abstractmethod

class Tools(ABC):
    def __init__(self, name: str):
        """
        Initializes the tool with a name.

        Parameters:
            name (str): The name of the tool.
        """
        self.name = name

    @abstractmethod
    def get_context(self, query: str, num: int = 3, verbose: bool = False) -> Tuple[str, List[str]]:
        """
        Abstract method to get context for a query.

        Parameters:
            query (str): The search query.
            num (int): Number of results to retrieve.
            verbose (bool): If True, prints additional information.

        Returns:
            Tuple[str, List[str]]: Context string and list of links.
        """
        pass
