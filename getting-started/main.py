from dotenv import load_dotenv
load_dotenv()

import os
from cerebras.cloud.sdk import Cerebras

client = Cerebras(
    api_key=os.environ.get("CEREBRAS_API_KEY"),
)
def get_chat_completion(message_content, model_name):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": message_content,
            }
        ],
        model=model_name,
    )
    return chat_completion


# Example usage:
if __name__ == "__main__":
    response = get_chat_completion(
        message_content="Why is fast inference important?",
        model_name="llama-4-scout-17b-16e-instruct"
    )
    print(response)