# python -m src.util.chatgpt_util

DEBUG=False

import os
from dotenv import load_dotenv
import openai

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数の取得
openai.api_key = os.getenv('OPEN_AI')

def get_response(messages):

    if DEBUG:
        print("===raw_messages===")
        print(messages)


    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    if DEBUG:
        print("===raw_responce===")
        print(response)

    return response


if __name__ == "__main__":
    messages=[
        {"role": "user", "content": "こんにちは。あなたは誰ですか？"}
    ]
    response = get_response(messages)

    print(response)