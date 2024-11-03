llm_base_url="https://api.openai.com/v1"
llm_api_key="EMPTY"
model_name="gpt-4o-mini"
serp_api_key="EMPTY"
seed_file="seed_example.txt"
num=3
output_path="output/output.txt"

python main.py\
    --llm_base_url ${llm_base_url} \
    --llm_api_key ${llm_api_key} \
    --model_name ${model_name} \
    --serp_api_key ${serp_api_key} \
    --seed_file ${seed_file} \
    --num ${num} \
    --output_path ${output_path} \
    --verbose true
