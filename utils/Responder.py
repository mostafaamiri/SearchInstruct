from tools import LLM

def get_response(query: str, context:str, agent: LLM, model: str, prompt: str, verbose: bool= False)-> dict:
    completion = agent.get_client().chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": prompt + context,
            },
            {
                "role": "user",
                "content": query,
            }
        ],
        model=model,
    )
    result = completion.choices[0].message.content
    if verbose:
        print(result)
    return {"instruction": query[4:], "output": result}