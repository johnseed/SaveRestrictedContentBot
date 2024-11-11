from pyrogram import Client
from decouple import config

# 从环境变量或 .env 文件中加载 API 信息
API_ID = config("API_ID", cast=int)
API_HASH = config("API_HASH")

# 创建临时客户端获取 session string, input +86phone, not bot
with Client(":memory:", api_id=API_ID, api_hash=API_HASH) as app:
    session_string = app.export_session_string()
    print("Your Session String:", session_string)