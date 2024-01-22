import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"), base_url="https://api.ai.cs.ac.cn/v1"
)


def generate_response(user, context):
    context = user.prompt + context
    chat_completion = client.chat.completions.create(
        model="gpt-4-1106-preview", messages=context, max_tokens=500
    )
    return chat_completion.choices[0].message.content
