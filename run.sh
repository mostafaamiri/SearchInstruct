llm_base_url="https://api.openai.com/v1"
llm_api_key="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"
model_name="gpt-4o-mini"
serp_api_key="a95506a9d63c6ec03649c8b8fee4f32cbbddc2d538b598b356f7648a51f197bd"
seed_file="seed_example.txt"
num=30
output_path="output/output.jsonl"
tool_name="google_search_tool" # google_search_tool, serp_tool

python main.py\
    --llm_base_url ${llm_base_url} \
    --llm_api_key ${llm_api_key} \
    --model_name ${model_name} \
    --seed_file ${seed_file} \
    --num ${num} \
    --output_path ${output_path} \
    --verbose true \
    --serp_api_key ${serp_api_key} \
    --tool_name ${tool_name}
