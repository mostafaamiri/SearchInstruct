llm_base_url="https://api.openai.com/v1"
llm_api_key="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"
model_name="gpt-4o-mini"
serp_api_key="a95506a9d63c6ec03649c8b8fee4f32cbbddc2d538b598b356f7648a51f197bd"
seed_file="seed_example.txt"
number_created_questions=3
number_retrieved_pages=3
output_path="instruction.json"
tool_name="google_search_tool" # google_search_tool, serp_tool

python main.py\
    --llm_base_url ${llm_base_url} \
    --llm_api_key ${llm_api_key} \
    --model_name ${model_name} \
    --seed_file ${seed_file} \
    --number_created_questions ${number_created_questions}\
    --number_retrieved_pages ${number_retrieved_pages} \
    --output_path ${output_path} \
    --verbose true \
    --serp_api_key ${serp_api_key} \
    --tool_name ${tool_name}
