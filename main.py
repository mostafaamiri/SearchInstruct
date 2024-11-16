import argparse
import os
import pandas as pd
from pipeline import Pipeline
from tools import LLM, SerpTool, SerperTool, GoogleSearchTool

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Pipeline for generating instructions and responses.')
    parser.add_argument(
        "--llm_base_url",
        type=str,
        required=True,
        help="Base URL for the LLM API."
    )
    parser.add_argument(
        "--llm_api_key",
        type=str,
        required=True,
        help="API key for the LLM."
    )
    parser.add_argument(
        "--model_sampler",
        type=str,
        required=True,
        help="Name of the model to use for sampling."
    )
    parser.add_argument(
        "--model_responder",
        type=str,
        required=True,
        help="Name of the model to use for responding."
    )
    parser.add_argument(
        "--model_search",
        type=str,
        required=False,
        default="gpt-4o-mini",
        help="Name of the model to use for the search tool's query preparation."
    )
    parser.add_argument(
        "--seed_file",
        type=str,
        required=True,
        help="Path to the seed file containing sample questions."
    )
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
    parser.add_argument(
        "--used_number_of_links",
        type=int,
        required=True,
        help="Desired number of successfully fetched links (after skipping specified websites and excluding links that fail to fetch)."
    )
    parser.add_argument(
        "--skip_websites",
        nargs='*',  # Accept zero or more arguments
        default=[],
        help="List of website domains to skip during content retrieval."
    )
    parser.add_argument(
        "--output_path",
        type=str,
        required=True,
        help="Path to save the output file."
    )
    parser.add_argument(
        "--verbose",
        action='store_true',
        help="If set, prints additional information during execution."
    )
    parser.add_argument(
        "--sample_size",
        type=int,
        default=None,
        help="Number of seed questions to randomly select for LLM input."
    )
    parser.add_argument(
        "--search_api_key",
        type=str,
        required=True,
        help="API key for the search tool."
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=1,
        help="Number of times to run the pipeline."
    )
    parser.add_argument(
        "--max_workers_questions",
        type=int,
        default=4,
        help="Maximum number of worker threads to use for processing questions."
    )
    parser.add_argument(
        "--max_workers_iterations",
        type=int,
        default=4,
        help="Maximum number of worker threads for iterations."
    )
    parser.add_argument(
        "--tool_name",
        type=str,
        required=True,
        choices=['serp_tool', 'serper_tool', 'google_search'],
        help="Name of the search tool to use."
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
        search_tool = GoogleSearchTool('google_search', llm, args.model_search)
    else:
        raise ValueError(f"Unknown tool name: {args.tool_name}")

    # Define the sample prompt for question generation
    sample_prompt = f"""
    You are an expert in question generation.
    You will be provided with sample questions.
    Your task is to create exactly **{args.number_created_questions}** new questions inspired by the sample questions.
    Each question should retain the structure and intent of the original sample questions but include variations by modifying specific details.

    The generated questions must:
    1. Be realistic, logical, and coherent.
    2. Showcase creativity while maintaining a challenging nature.
    3. Avoid being overly simple, nonsensical, or repetitive.

    Provide the output in JSON format with the following structure:
    {{
        "questions": [
            "Generated question 1",
            "Generated question 2",
            ...
        ]
    }}

    Do not include any additional explanations, comments, or extra content. Only return the JSON output as specified.
    """

    # Define the respond prompt for answering questions
    respond_prompt = """
    Provide accurate and well-explained answers to the user's questions, based on the content provided below.
    Ensure your response is as complete and comprehensive as possible.
    Do not include information or assumptions outside of this content.
    """

    # Read seed questions from the seed file
    input_extension = os.path.splitext(args.seed_file)[1].lower()
    if input_extension in ['.txt']:
        # Read seed questions from a text file
        with open(args.seed_file, 'r', encoding='utf-8') as file:
            seed_questions = [line.strip() for line in file if line.strip()]
    elif input_extension in ['.json']:
        # Read seed questions from a JSON file
        df = pd.read_json(args.seed_file, orient='records')
        seed_questions = df['question'].tolist()
    elif input_extension in ['.jsonl']:
        # Read seed questions from a JSON Lines file
        df = pd.read_json(args.seed_file, orient='records', lines=True)
        seed_questions = df['question'].tolist()
    elif input_extension in ['.csv']:
        # Read seed questions from a CSV file
        df = pd.read_csv(args.seed_file)
        seed_questions = df['question'].tolist()
    elif input_extension in ['.xlsx']:
        # Read seed questions from an Excel file
        df = pd.read_excel(args.seed_file)
        seed_questions = df['question'].tolist()
    else:
        raise ValueError(f"Unsupported seed file format: {input_extension}")

    # Initialize the pipeline with the LLM, models, prompts, search tool, and new parameters
    pipeline = Pipeline(
        llm_agent=llm,
        model_sampler_name=args.model_sampler,
        model_responder_name=args.model_responder,
        sample_prompt=sample_prompt,
        respond_prompt=respond_prompt,
        search_tool=search_tool,
        number_retrieved_pages=args.number_retrieved_pages,
        skip_websites=args.skip_websites,
        used_number_of_links=args.used_number_of_links
    )

    # Run the pipeline to generate instructions
    instructions = pipeline(
        seed_questions=seed_questions,
        verbose=args.verbose,
        sample_size=args.sample_size,
        iterations=args.iterations,
        max_workers_iterations=args.max_workers_iterations,
        max_workers_questions=args.max_workers_questions
    )

    # Convert the instructions to a DataFrame
    instructions_df = pd.DataFrame(instructions)

    # Save the DataFrame to the output file based on the file format
    output_extension = os.path.splitext(args.output_path)[1].lower()
    if output_extension == '.json':
        instructions_df.to_json(
            args.output_path,
            orient="records",
            force_ascii=False,
            indent=4
        )
    elif output_extension == '.jsonl':
        instructions_df.to_json(
            args.output_path,
            orient="records",
            force_ascii=False,
            lines=True
        )
    elif output_extension in ['.csv']:
        instructions_df.to_csv(
            args.output_path,
            index=False,
            encoding='utf-8-sig'
        )
    elif output_extension == '.xlsx':
        instructions_df.to_excel(
            args.output_path,
            index=False
        )
    elif output_extension == '.txt':
        # Save as a text file with one instruction per line
        with open(args.output_path, 'w', encoding='utf-8') as file:
            for idx, row in instructions_df.iterrows():
                file.write(f"Instruction {idx + 1}:\n")
                file.write(f"Question: {row['instruction']}\n")
                file.write(f"Answer: {row['output']}\n")
                file.write(f"Sources: {row['links']}\n")
                file.write("\n")
    else:
        raise ValueError(f"Unsupported output file format: {output_extension}")

if __name__ == '__main__':
    main()
