import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def generate_response(user, context):
    context = user.prompt + context
    chat_completion = client.chat.completions.create(
        model="gpt-4-1106-preview", messages=context
    )
    return chat_completion.choices[0].message.content
