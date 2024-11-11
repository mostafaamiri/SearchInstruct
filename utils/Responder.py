from tools import LLM
from typing import List, Union, Dict

def get_response(
    query: str,
    context: str,
    links: Union[List[str], str],
    agent: LLM,
    model: str,
    prompt: str,
    verbose: bool = False
) -> Dict[str, Union[str, List[str]]]:
    """
    Generates a response to the given query using the provided context and LLM agent.

    Parameters:
        query (str): The user's question or instruction.
        context (str): The context information to assist the LLM in generating a response.
        links (List[str] or str): Source links associated with the context.
        agent (LLM): The language model agent to use for generating the response.
        model (str): The name of the model to use.
        prompt (str): The system prompt to guide the LLM's behavior.
        verbose (bool): If True, prints additional information for debugging.

    Returns:
        Dict[str, Union[str, List[str]]]: A dictionary containing the context, instruction, output, and links.
    """
    # Prepare the messages for the LLM
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"Context:\n{context}"},
        {"role": "user", "content": f"Query:\n{query}"}
    ]

    if verbose:
        print("\033[36mSending request to LLM for response generation...\033[0m")
        print("\033[33mQuestion:\033[0m")
        print(f"{query}")

    # Generate the response using the LLM
    try:
        completion = agent.get_client().chat.completions.create(
            messages=messages,
            temperature=0.1,
            model=model
        )
        result = completion.choices[0].message.content.strip()
        if verbose:
            print("\033[32mLLM response:\033[0m")
            print(f"{result}")
    except Exception as e:
        print(f"\033[31mError generating response: {e}\033[0m")
        result = ""

    # Prepare the output dictionary
    response = {
        "context": context,
        "instruction": query,
        "output": result,
        "links": links
    }

    return response
