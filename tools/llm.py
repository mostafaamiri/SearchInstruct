from openai import OpenAI

class LLM:
    def __init__(self, base_url:str, api_key:str):
        self.base_url = base_url
        self.api_key = api_key
    
    def get_client(self):
        return OpenAI(
            api_key=self.api_key,
        )
    def __call__(self):
        return OpenAI(
            api_key=self.api_key,
        )