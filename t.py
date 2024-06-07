from langchain.prompts import HumanMessagePromptTemplate

msg = HumanMessagePromptTemplate.from_template(
    [
        (
            {
                "image_url": {
                    # "url": f"data:image/jpeg;base64,{encode_image(user_input['content'])}",
                    "url": "good" + "?x-oss-process=image/resize,l_1024",
                    "detail": "low",
                }
            }
        ),
    ]
)


print(msg.format())