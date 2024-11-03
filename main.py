from tools import SerpTool, LLM
from argparse import ArgumentParser
from pipeline import Pipeline


parser = ArgumentParser()
parser.add_argument("--llm_base_url")
parser.add_argument("--llm_api_key")
parser.add_argument("--model_name")
parser.add_argument("--serp_api_key")
parser.add_argument("--seed_file")
parser.add_argument("--num")
parser.add_argument("--verbose")
parser.add_argument("--output_path")

args = parser.parse_args()


llm = LLM(args.llm_base_url, args.llm_api_key)
tool = SerpTool('serp', args.serp_api_key)
model = args.model_name
num = int(args.num)
seed_file = args.seed_file
verbose = args.verbose
output_path = args.output_path

sample_prompt = """
You are a data generation expert.
You will be given a sample question. 
Try to generate 3 other questions similar to this question by changing the specific names and the question expression type and return the output to JSON format which has a key named 'question' and the questions are arrays in its value.
DON'T RESPOND ANY EXTRA EXPLANATION.
"""
respond_prompt = """
Try to answer the user's question accurately and correctly and with sufficient explanations only according to this content that you see below:\n
"""

if __name__ == '__main__':
    pipeline = Pipeline(llm, model, sample_prompt, respond_prompt, tool, num)
    seeds = []
    with open(seed_file, 'r') as f:
        for line in f.readlines():
            seeds.append(line.strip())
    instructions = pipeline(seeds, verbose)

    with open(output_path, 'w') as f:
        for ins in instructions:
            f.write(str(ins))
            f.write("\n")