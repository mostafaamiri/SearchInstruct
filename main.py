from tools import SerpTool, LLM, GoogleSearchTool, SerperTool
from argparse import ArgumentParser
from pipeline import Pipeline
import pandas as pd

# Parse command-line arguments
parser = ArgumentParser(description="Generate instructions using LLM and search tools.")
parser.add_argument("--llm_base_url", required=True, help="Base URL for the LLM API.")
parser.add_argument("--llm_api_key", required=True, help="API key for the LLM.")
parser.add_argument("--model_name", required=True, help="Name of the LLM model to use.")
parser.add_argument(
    "--tool_name",
    choices=['serp_tool', 'serper_tool', 'google_search'],
    required=True,
    help="Name of the search tool to use."
)
parser.add_argument("--search_api_key", default="EMPTY", help="API key for the search tool.")
parser.add_argument("--seed_file", required=True, help="Path to the seed file containing sample questions.")
parser.add_argument(
    "--number_created_questions",
    type=int,
    required=True,
    help="Number of new questions to create for each seed question."
)
parser.add_argument(
    "--number_retrieved_pages",
    type=int,
    required=True,
    help="Number of pages to retrieve from the search tool."
)
parser.add_argument("--verbose", default=False, help="Enable verbose output.")
parser.add_argument(
    "--seed_as_instructs",
    default=False,
    help="Use seed questions as instructions."
)
parser.add_argument("--output_path", required=True, help="Path to save the output JSON file.")
parser.add_argument(
    "--sample_size",
    type=int,
    help="Number of seed questions to randomly select for LLM input."
)
parser.add_argument(
    "--iterations",
    type=int,
    default=1,
    help="Number of times to run the pipeline."
)

args = parser.parse_args()

# Initialize the LLM with base URL and API key
llm = LLM(args.llm_base_url, args.llm_api_key)

# Determine which search tool to use based on the provided tool name
if args.tool_name == 'serp_tool':
    search_tool = SerpTool('serp', args.search_api_key)
elif args.tool_name == 'serper_tool':
    search_tool = SerperTool('serper', args.search_api_key)
elif args.tool_name == 'google_search':
    search_tool = GoogleSearchTool('google_search', llm, args.model_name)
else:
    raise ValueError(f"Unknown tool name: {args.tool_name}")

# Define the sample prompt for question generation
sample_prompt = f"""
You are a question generation expert.
You will be given a sample question.
Your task is to generate {args.number_created_questions} new questions similar to the sample question by changing specific details such as names, numbers, and expression types while maintaining the overall context and structure.
Return the output in JSON format with a key named 'questions', where the value is an array of the generated questions.
Do not include any additional explanations or comments in your response.
"""

# Define the respond prompt for answering questions
respond_prompt = """
Provide accurate and well-explained answers to the user's questions, based on the content provided below.
Ensure your response is as complete and comprehensive as possible.
Do not include information or assumptions outside of this content.
"""

if __name__ == '__main__':
    # Initialize the pipeline with the LLM, model name, prompts, search tool, and number of pages to retrieve
    pipeline = Pipeline(
        llm_agent=llm,
        model_name=args.model_name,
        sample_prompt=sample_prompt,
        respond_prompt=respond_prompt,
        search_tool=search_tool,
        num_retrieved_pages=args.number_retrieved_pages
    )

    # Read seed questions from the seed file
    with open(args.seed_file, 'r') as file:
        seed_questions = [line.strip() for line in file]

    # Run the pipeline to generate instructions
    instructions = pipeline(
        seed_questions=seed_questions,
        verbose=args.verbose,
        seed_as_instructions=args.seed_as_instructs,
        sample_size=args.sample_size,
        iterations=args.iterations  # Pass the iterations argument
    )

    # Convert the instructions to a DataFrame
    instructions_df = pd.DataFrame(instructions)

    # Save the DataFrame as a JSON file
    instructions_df.to_json(
        args.output_path,
        orient="records",
        force_ascii=False,
        indent=4
    )
