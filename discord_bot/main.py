# インストールした discord.py を読み込む
import discord
from discord.ext import tasks

# アクセストークンを読み込み
import env

# 曜日のよみこみ
import datetime

import requests
import os

# インテントの設定
intents = discord.Intents.all()

# 接続に必要なオブジェクトを生成
client = discord.Client(intents=intents)

# 時間割の指定
schedule = {
    "月曜日": {
        "classes": ["物理III", "電気磁気学I", "データサイエンス概論", "電気回路論I"],
        "items": ["特になし"],
        "message": "さぁ、地獄の一週間の幕開けじゃあ..."
    },
    "火曜日": {
        "classes": ["情報通信ネットワーク", "英語特講", "電子情報工学実験"],
        "items": ["特になし"],
        "message": "今日の実験はだるだるのダルメシアン(適当)"
    },
    "水曜日": {
        "classes": ["ディジタル回路", "微分積分II", "特活"],
        "items": ["特になし"],
        "message": "早く帰れるっていいよね...:fire:"
    },
    "木曜日": {
        "classes": ["オペレーティングシステム", "データ構造とアルゴリズム", "保健体育", "電子工学I"],
        "items": ["体操服", "タオル"],
        "message": "体育の倒立さえなければなぁ"
    },
    "金曜日": {
        "classes": ["微分積分II", "日本文学", "線形代数II", "ロボットデザイン論/半導体工学概論"],
        "items": ["特になし"],
        "message": "休みだ休みだわっしょっしょい"
    }
}

TEST_DATE = datetime.date(2026, 7, 31)

def get_days_left():
    today = datetime.date.today()
    delta = TEST_DATE - today
    return delta.days

API_KEY = os.getenv("WEATHER_API_KEY")

def get_weather_all():
    lat = 34.8823
    lon = 136.5840

    # 現在の天気
    url_now = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={API_KEY}&lang=ja&units=metric"
    )
    now = requests.get(url_now).json()
    print("NOW:", now)  # デバッグ用

    # weather が無い場合の保険
    if "weather" not in now or "main" not in now:
        return "取得失敗", 0, 0, 0

    weather = now["weather"][0]["description"]
    temp = now["main"]["temp"]
    humidity = now["main"]["humidity"]

    # 降水確率
    url_forecast = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?lat={lat}&lon={lon}&appid={API_KEY}&lang=ja&units=metric"
    )
    forecast = requests.get(url_forecast).json()
    print("FORECAST:", forecast)  # デバッグ用

    if "list" not in forecast or len(forecast["list"]) == 0:
        return weather, temp, humidity, 0

    pop = forecast["list"][0].get("pop", 0)
    pop_percent = int(pop * 100)

    return weather, temp, humidity, pop_percent


# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print(f"{client.user}がログインしました")
    if not morning_notice.is_running():
        morning_notice.start()

CHANNEL_ID = 1388451856455569488  # ←送りたいチャンネルID

JST = datetime.timezone(datetime.timedelta(hours=9), "JST")

@tasks.loop(minutes=1)
async def morning_notice():
    now = datetime.datetime.now(JST)
    if now.hour == 0 and now.minute == 45:
        weekday = now.strftime("%A")  # Monday, Tuesday...
        weekday_key_map = {
            "Monday": "月曜日",
            "Tuesday": "火曜日",
            "Wednesday": "水曜日",
            "Thursday": "木曜日",
            "Friday": "金曜日",
            "Saturday": "土曜日",
            "Sunday": "日曜日",
        }

        weekday_display_map = {
            "Monday": "憂鬱MAX月曜日",
            "Tuesday": "まだまだ憂鬱な火曜日",
            "Wednesday": "ようやく半分水曜日",
            "Thursday": "なんだかんだで木曜日",
            "Friday": "週末襲来金曜日",
            "Saturday": "土曜日",
            "Sunday": "日曜日",
        }

        weekday = now.strftime("%A")

        jp_weekday = weekday_key_map[weekday]
        display_weekday = weekday_display_map[weekday]

        data = schedule.get(jp_weekday)

        weather, temp, humidity, pop = get_weather_all()

        weather_msg = (
            f"ちなみに、今日の鈴鹿市の天気は、**{weather}**。\n"
            f"気温は、**{temp}℃**。\n"
            f"湿度は、**{humidity}%**。\n"
            f"降水確率は、**{pop}%**でござる。ﾆﾝﾆﾝ。\n-# 間違ってたらごめんネ"
        )

        if weekday in ["Saturday"]:
            channel = client.get_channel(CHANNEL_ID)
            await channel.send("# うへへへへへ...土曜だ...土曜だｧｧｧｧｧｧｧｧｧｧ!!!!!!!")
            return
        
        if weekday in ["Sunday"]:
            channel = client.get_channel(CHANNEL_ID)
            await channel.send("# えっもう日曜なの...？早くなーい？")
            return
        
        if data:
            channel = client.get_channel(CHANNEL_ID)
            classes = " / ".join(data["classes"])
            items = "、".join(data["items"])

            msg = f"**# {display_weekday}**\nおはよう！今日も張り切って頑張ろう！\nさてさて、今日の電子情報工学科の時間割は...\n## {classes}\n**持ち物**は...\n## {items}\nなんと、次の試験まで残り**{get_days_left()}日**...ロシアの軍勢恐ロシア...\n" + weather_msg
            await channel.send(msg)

@morning_notice.before_loop
async def before():
    await client.wait_until_ready()

# Botの起動とDiscordサーバーへの接続
client.run(env.BOT_TOKEN)
