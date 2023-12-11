import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

file = client.files.create(
    file=open("files/ucas.txt", "rb"),
    purpose='assistants'
)
