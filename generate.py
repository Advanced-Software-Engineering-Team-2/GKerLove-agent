import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = "https://api.ai.cs.ac.cn/v1"


def generate_response(user, context):
    context = user.prompt + context
    chat_completion = openai.ChatCompletion.create(
        model="gpt-4", messages=context
    )
    return chat_completion.choices[0].message.content
