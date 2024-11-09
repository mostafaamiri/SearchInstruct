from tools import LLM
from typing import List, Union
import re
import json

def get_examples(seed: Union[str, List[str]], agent: LLM, model: str, prompt: str, verbose: bool= False, seed_as_instructs: bool = False)-> dict:
    if(type(seed) == type([])):
        questions = ""
        for i in range(len(seed)):
            questions += str(i+1)+" - "+seed[i] + "\n"
    else:
        questions = seed
    print(questions)
    
    if seed_as_instructs:
        result = {'questions': seed if isinstance(seed, list) else [seed]}
        if verbose:
            for k in result:
                print(k)
                for q in result[k]:
                    print(q)
        return result

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
        temperature=0.5,
        model=model,
    )
    print(re.findall(r"{[\s.\S]+}",completion.choices[0].message.content,re.MULTILINE)[0])
    try:
        result = json.loads(re.findall(r"{[\s.\S]+}",completion.choices[0].message.content,re.MULTILINE)[0])
        print(result)
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