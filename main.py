from tools import SerpTool, LLM
from argparse import ArgumentParser
from pipeline import Pipeline

import pandas as pd


parser = ArgumentParser()
parser.add_argument("--llm_base_url")
parser.add_argument("--llm_api_key")
parser.add_argument("--model_name")
parser.add_argument("--serp_api_key")
parser.add_argument("--seed_file")
parser.add_argument("--number_created_questions")
parser.add_argument("--number_retrieved_pages")
parser.add_argument("--verbose")
parser.add_argument("--output_path")

args = parser.parse_args()


llm = LLM(args.llm_base_url, args.llm_api_key)
tool = SerpTool('serp', args.serp_api_key)
model = args.model_name
number_retrieved_pages = int(args.number_retrieved_pages)
number_created_questions = int(args.number_created_questions)
seed_file = args.seed_file
verbose = args.verbose
output_path = args.output_path

sample_prompt = f"""
You are a question generation expert.
You will be given a sample question.
Your task is to generate {number_created_questions} new questions similar to the sample question by changing specific details such as names, numbers, and expression types while maintaining the overall context and structure.
Return the output in JSON format with a key named 'questions', where the value is an array of the generated questions.
Do not include any additional explanations or comments in your response.
"""
respond_prompt = """
Try to answer the user's question accurately and correctly and with sufficient explanations only according to this content that you see below:\n
"""

if __name__ == '__main__':
    pipeline = Pipeline(llm, model, sample_prompt, respond_prompt, tool, number_retrieved_pages)
    seeds = []
    with open(seed_file, 'r') as f:
        for line in f.readlines():
            seeds.append(line.strip())
    instructions = pipeline(seeds, verbose)

    # Convert  to a DataFrame
    df = pd.DataFrame(instructions)

    # Save DataFrame as JSON file
    df.to_json(output_path, orient="records", force_ascii=False, indent=4)