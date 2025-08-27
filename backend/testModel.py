import os
from openai import OpenAI

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],
)

completion = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-V3.1:fireworks-ai",
    messages=[
        {
            "role": "user",
            "content": "C'est qui marino?"
        }
    ],
)

print(completion.choices[0].message)