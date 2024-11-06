from tools import LLM
from typing import List, Union


def get_response(query: str, context:str, links: Union[List[str], str], agent: LLM, model: str, prompt: str, verbose: bool= False)-> dict:
    completion = agent.get_client().chat.completions.create(
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": 'context:' + context},
            { "role": "user", "content": 'query:' + query}
        ],
        temperature=0.1,
        model=model,
    )
    result = completion.choices[0].message.content
    if verbose:
        print(result)
    return {"instruction": query[4:], "output": result, "links": links}