from tools import LLM
from typing import List, Union
import re
import json
import random

def get_examples(
    seed: Union[str, List[str]],
    agent: LLM,
    model: str,
    prompt: str,
    verbose: bool = False,
    seed_as_instructs: bool = False,
    sample_size: int = None
) -> dict:
    """
    Generate examples based on seed questions.

    Parameters:
        seed (str or List[str]): Seed question(s) to generate examples from.
        agent (LLM): The language model agent.
        model (str): The name of the model to use.
        prompt (str): The prompt to provide to the LLM.
        verbose (bool): If True, prints additional information.
        seed_as_instructs (bool): If True, use seed questions as instructions without generating new ones.
        sample_size (int, optional): Number of seed questions to randomly select from the seed list.

    Returns:
        dict: A dictionary containing generated questions.
    """
    # Ensure seed is a list of questions
    if isinstance(seed, str):
        seed_questions = [seed]
    elif isinstance(seed, list):
        seed_questions = seed.copy()
    else:
        raise ValueError("Seed must be a string or a list of strings.")

    # Randomly select a subset of seed questions if sample_size is specified
    if sample_size is not None and sample_size < len(seed_questions):
        seed_questions = random.sample(seed_questions, sample_size)
        if verbose:
            print(f"\033[33mRandomly selected {sample_size} seed questions.\033[0m")

    # If verbose, print the seed questions
    if verbose:
        print("\033[33mSeed questions:\033[0m")
        for idx, question in enumerate(seed_questions, start=1):
            print(f"  {idx}. {question}")

    # If seed_as_instructs is True, return the seed questions as instructions
    if seed_as_instructs:
        result = {'questions': seed_questions}
        if verbose:
            print("\033[33mUsing seed questions as instructions.\033[0m")
        return result

    # Prepare the questions string for the LLM prompt
    questions_text = "\n".join(f"{i+1} - {q}" for i, q in enumerate(seed_questions))

    if verbose:
        print("\033[36mSending request to LLM to generate new questions...\033[0m")

    # Generate new questions using the LLM
    completion = agent.get_client().chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": questions_text,
            }
        ],
        temperature=0.5,
        model=model,
    )

    # Extract JSON from the LLM's response
    try:
        json_content = re.search(r"{[\s\S]+}", completion.choices[0].message.content)
        if not json_content:
            raise ValueError("No JSON content found in LLM response.")
        result = json.loads(json_content.group(0))
        if verbose:
            print("\033[32mGenerated questions:\033[0m")
            for idx, question in enumerate(result.get('questions', []), start=1):
                print(f"  {idx}. {question}")
        return result
    except Exception as e:
        print(f"\033[31mError parsing LLM output: {e}\033[0m")
        return None
