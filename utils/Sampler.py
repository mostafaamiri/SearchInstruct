from tools import LLM
from typing import List, Union
import re
import json

def get_examples(seed: Union[str, List[str]], agent: LLM, model: str, prompt: str, verbose: bool= False)-> dict:
    if(type(seed) == type([])):
        questions = ""
        for i in range(len(seed)):
            questions += str(i+1)+" - "+seed[i] + "\n"
    else:
        questions = seed
    print(questions)
    completion = agent.get_client().chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": questions,
            }
        ],
        model=model,
    )
    print(re.findall(r"{[\s.\S]+}",completion.choices[0].message.content,re.MULTILINE)[0])
    try:
        result = json.loads(re.findall(r"{[\s.\S]+}",completion.choices[0].message.content,re.MULTILINE)[0])
        if verbose:
            for k in result:
                print(k)
                for q in result[k]:
                    print(q)
        return result
    except Exception as e:
        # TODO: extracting json from text
        print(e)
        return None