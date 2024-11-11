#!/bin/bash

# Set the base URL for the LLM API
llm_base_url="https://api.openai.com/v1"

# Set the API key for the LLM
llm_api_key="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"

# Set the model name to use
model_name="gpt-4o-mini"

# Set the API key for the search tool
search_api_key="764adea9b10a4d685b919bb33ee81ef0f457076a"

# Set the path to the seed file containing sample questions (supports .txt, .json, .jsonl, .csv, .xlsx)seed_file="iran_tourism_seeds.txt"
seed_file="food_seeds.txt"

# Set the number of new questions to create for each seed question
number_created_questions=3

# Set the number of pages to retrieve from the search tool
number_retrieved_pages=5

# Set the output file path (supports .txt, .json, .jsonl, .csv, .xlsx)
output_path="instruction_food_seeds.xlsx"

# Set the number of seed questions to randomly select for LLM input
sample_size=500

# Set the number of times to run the pipeline
iterations_number=1

# Set the name of the search tool to use (options: google_search, serp_tool, serper_tool)
tool_name="serper_tool"

# Specify the maximum number of threads to use for parallel processing tasks.
max_workers=16

# Run the main Python script with the specified arguments
python main.py \
    --llm_base_url "${llm_base_url}" \
    --llm_api_key "${llm_api_key}" \
    --model_name "${model_name}" \
    --seed_file "${seed_file}" \
    --number_created_questions "${number_created_questions}" \
    --number_retrieved_pages "${number_retrieved_pages}" \
    --output_path "${output_path}" \
    --verbose true \
    --seed_as_instructs true\
    --sample_size "${sample_size}" \
    --search_api_key "${search_api_key}" \
    --iterations "${iterations_number}" \
    --max_workers "${max_workers}" \
    --tool_name "${tool_name}"
