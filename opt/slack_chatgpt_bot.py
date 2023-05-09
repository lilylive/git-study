# slackでのchat-gptを使用したチャットボットの実装
# 2023/04/28
# Author: hiroyuki maruko with chat-gpt-3.5
# ----------------------------------------------
# Slackのchat-gptを使用したチャットボットの実装
# ----------------------------------------------
# ライブラリのインポート
import os
import openai
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from distutils.util import strtobool
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# .envファイルの読み込み
load_dotenv()

import logging
fmt = "%(asctime)s %(levelname)s %(name)s :%(message)s"
logging.basicConfig(level=logging.INFO, format=fmt)


# 環境変数の取得
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
CHARACTER_CONFIG = os.environ["CHARACTER_CONFIG"]

# OpenAIのAPIキーの設定
openai.api_key = OPENAI_API_KEY

# アプリの初期化
app = App(token=SLACK_BOT_TOKEN)

@app.event("app_mention")
def handle_app_mentions(body, say, logger):
    """app_mentionイベントを処理する"""
    text = body["event"]["text"]
    user_id = body["event"]["user"]
    channel = body['event']['channel']

    try:
        result = app.client.conversations_info(channel=channel)
        channel_type = result["channel"]["is_private"]
        if not channel_type:
             # Generate a response using OpenAI's GPT-3
             prompt = f"{CHARACTER_CONFIG} {text} "
             response = openai.Completion.create(
                engine="text-davinci-003",
                max_tokens=150,
                prompt=prompt,
                n=1,
                stop=None,
                temperature=0.5,
            )
            # Extract the generated text　生成されたテキストを抽出する
             gpt_response = response.choices[0].text.strip()
            # Send the response back to the user　ユーザーに応答を送信する
             say(f"<@{user_id}> {gpt_response}")
        else:
            say(f"このボットはプライベートチャンネルでは使えません。")
            return
    except SlackApiError as e:
        logger.error(f"Error fetching conversations info: {e}")


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()


    