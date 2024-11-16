#!/bin/bash

# Set the base URL for the LLM API
llm_base_url="https://api.openai.com/v1"

# Set the API key for the LLM (replace with your actual API key)
llm_api_key="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"

# Set the model names to use
model_sampler="gpt-4o-mini"
model_responder="gpt-4o-mini"
model_search="gpt-4o-mini"

# Set the API key for the search tool (replace with your actual API key)
search_api_key="8bf5eb4be94b663d2f367549dd9b58242768f513" 
# 28d356a38c07a660670fd4997362ff32d283af5f 

# Set the path to the seed file containing sample questions
seed_file="iran_tourism_seeds_all.txt"

# Set the number of new questions to create for each seed question
number_created_questions=5

# Set the number of pages to retrieve from the search tool
number_retrieved_pages=10

# Set the desired number of used links
used_number_of_links=3

# List of websites to skip (e.g., instagram, facebook, twitter, etc.)
skip_websites=("instagram" "facebook" "twitter" "X.com" "telegram" "aparat")

# Set the output file path (supports .txt, .json, .jsonl, .csv, .xlsx)
output_path="/home/barati/search_instruct/created_data/test.json"

# Set the number of seed questions to randomly select for LLM input
sample_size=25

# Set the number of times to run the pipeline
iterations_number=1

# Set the name of the search tool to use (options: google_search, serp_tool, serper_tool)
tool_name="serper_tool"

# Set the maximum number of worker threads
max_workers_questions=16
max_workers_iterations=16

# Run the main Python script with the specified arguments
python main.py \
    --llm_base_url "${llm_base_url}" \
    --llm_api_key "${llm_api_key}" \
    --model_sampler "${model_sampler}" \
    --model_responder "${model_responder}" \
    --model_search "${model_search}" \
    --seed_file "${seed_file}" \
    --number_created_questions "${number_created_questions}" \
    --number_retrieved_pages "${number_retrieved_pages}" \
    --used_number_of_links "${used_number_of_links}" \
    --skip_websites "${skip_websites[@]}" \
    --output_path "${output_path}" \
    --verbose \
    --sample_size "${sample_size}" \
    --search_api_key "${search_api_key}" \
    --iterations "${iterations_number}" \
    --max_workers_questions "${max_workers_questions}" \
    --max_workers_iterations "${max_workers_iterations}" \
    --tool_name "${tool_name}"
