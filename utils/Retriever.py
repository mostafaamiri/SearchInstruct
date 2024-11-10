from tools import Tools
def get_context(query: str, tool: Tools, num: int= 3, verbose: bool=False)->str:
    return tool.get_context(query, num, verbose)