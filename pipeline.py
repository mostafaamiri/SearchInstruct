from utils import get_examples, make_context, get_response
from typing import List ,Union
from tools import LLM, Tools


class Pipeline():
    def __init__(self, agent: LLM, model: str, sample_prompt: str, respond_prompt: str, tool: Tools, num:int):
        self.llm = agent
        self.model= model
        self.sample_prompt = sample_prompt
        self.respond_prompt = respond_prompt
        self.tool = tool
        self.num = num

    def __call__(
            self, 
            seed: Union[str, List[str]], 
            verbose:bool=False,
            seed_as_instructs:bool=False):
        
        samples = get_examples(seed, self.llm, self.model, self.sample_prompt, verbose, seed_as_instructs)
        print(samples)
        instructions = []
        for q in samples['questions']:
            try:
                context, links = make_context(q, self.tool, self.num, verbose)
                instructions.append(get_response(q, context[:min(200000,len(context))], links, self.llm, self.model, self.respond_prompt, verbose))
            except Exception as err:
                print(print(f"Unexpected {err=}, {type(err)=}"))
        return instructions          
