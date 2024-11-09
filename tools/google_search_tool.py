from .tools import Tools
import requests
from bs4 import BeautifulSoup
from googlesearch import search
from .llm import LLM
from time import sleep


class GoogleSearchTool(Tools):
    def __init__(self, name: str, agent: LLM = None, model: str = "gpt-4o-mini"):
        super().__init__(name)
        self.agent = agent
        self.model = model

    def get_context(self, query: str, num: int = 3, verbose: bool = False)->str:
        
        retrieval_links = []
        while True:
            results = search(self.prepare_query(query), num_results=20, advanced=True, lang="fa")
            idx = 0
            for r in results:
                idx+=1
                retrieval_links.append(r.url)
                if verbose:
                    print(idx, r)
            print('\033[93m'+"end search"+'\033[0m')
            if idx>0:
                break
            else:
                sleep(10)
        context = ""
        used_links = []
        for link in retrieval_links:
            try:
                resp =requests.get(link, timeout=30)
            except:
                print('\033[94m'+f"can't open{link}"+'\033[0m')
                continue
            num_context = 0
            if resp:
                used_links.append(link)
                bs = BeautifulSoup(resp.text, 'html.parser')
                context += bs.find('body').getText()
                context += "\n"
                num_context+=1
            if num_context > 3:
                break
        return context, used_links
    
    def prepare_query(self, q: str):
        if self.agent:
            prompt = "given you an instruction, respond with a search term query which can be efficiently used for search answer of it in search engines, and don't respond with any explanation"
            completion = self.agent.get_client().chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": prompt,
                    },
                    {
                        "role": "user",
                        "content": q,
                    }
                ],
                model=self.model,
            )
            result = completion.choices[0].message.content
            return result