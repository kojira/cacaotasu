import discord
from discord.ext import commands
from dotenv import load_dotenv
import requests
import os

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

DESCRIPTION_JA = os.environ.get("DESCRIPTION_JA")
DESCRIPTION_EN = os.environ.get("DESCRIPTION_EN")

EXCHANGE_URL = os.environ.get("EXCHANGE_URL")

TARGET = os.environ.get("TARGET")
BASE = os.environ.get("BASE")

image_names = ["IMAGE_NORMAL",
               "IMAGE_HIGH", "IMAGE_HIGH2", "IMAGE_HIGHEST",
               "IMAGE_LOW",  "IMAGE_LOW2",  "IMAGE_LOWEST"]

images = {}

for image_name in image_names:
    images[image_name] = os.environ.get(image_name)


def get_market_price_unnamed_exchange(base, target):
    unnamed_api_url = "https://api.unnamed.exchange/v1/Public/Ticker?market={}_{}".format(
        target, base)
    response_target = requests.get(unnamed_api_url).json()
    for_disp = response_target.copy()
    for_disp["change_percent"] = f"{response_target['change']}%"
    for_disp["baseVolume"] = f"{response_target['baseVolume']} {base}"
    for_disp["volume"] = f"{response_target['volume']} {target}"
    for_disp["low"] = f"{response_target['low']:.8f} {base}"
    for_disp["high"] = f"{response_target['high']:.8f} {base}"
    for_disp["close"] = f"{response_target['close']:.8f} {base}"
    for_disp["highestBuy"] = f"{response_target['highestBuy']:.8f} {base}"
    for_disp["lowestSell"] = f"{response_target['lowestSell']:.8f} {base}"

    doge = response_target['close']
    # base通貨のBTC価格を取得
    unnamed_api_url = "https://api.unnamed.exchange/v1/Public/Ticker?market={}_{}".format(
        base, "BTC")
    response_base = requests.get(unnamed_api_url).json()
    btc = response_base['close']
    jpy = get_market_price_doge2jpy(doge, btc)
    usd = get_market_price_doge2usd(doge, btc)
    for_disp[f"{base}_BTC"] = f"{btc:,.8f}"
    for_disp["jpy"] = f"{jpy:.10f}"
    for_disp["yukichi"] = f"{10000/jpy:,.0f} {target}"
    for_disp["usd"] = f"{usd:.10f}"
    for_disp["$100"] = f"{100/usd:,.0f}  {target}"

    return response_target, for_disp


def get_market_price_doge2jpy(doge, btc):
    # coinecheckのAPIを指定
    coincheck_btc_jpy_api_url = "https://coincheck.com/api/ticker"
    coincheck_btc_jpy_api_response = requests.get(
        coincheck_btc_jpy_api_url).json()
    btc_jpy = coincheck_btc_jpy_api_response['last']
    # zaifのAPIを指定
    # zaif_btc_jpy_api_url = "https://api.zaif.jp/api/1/last_price/btc_jpy"
    # zaif_btc_jpy_api_response = requests.get(zaif_btc_jpy_api_url).json()
    # btc_jpy = zaif_btc_jpy_api_response['last_price']
    # 日本円を計算
    result_jpy = doge * btc * btc_jpy
    return round(result_jpy, 10)


def get_market_price_doge2usd(doge, btc):
    # blockchainのAPIを指定
    blockchain_btc_usd_api_url = "https://blockchain.info/ticker"
    blockchain_btc_usd_api_response = requests.get(
        blockchain_btc_usd_api_url).json()
    btc_usd = blockchain_btc_usd_api_response['USD']['last']
    # アメリカドルを計算
    result_usd = doge * btc * btc_usd
    return round(result_usd, 10)


class PriceBot(commands.Bot):
    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)

    async def on_ready(self):
        print('on ready.')


bot = PriceBot(['!', '！'])

# TODO:言語リソースファイルに分離
texts = {
    "embed_title": {"ja": "価格情報", "en": "price"},
    "embed_description": {"ja": DESCRIPTION_JA, "en": DESCRIPTION_EN},
    "change_percent": {"ja": "変化(24h)", "en": "change(24h)"},
    "baseVolume": {"ja": "ベースボリューム(24h)", "en": "base volume(24h)"},
    "volume": {"ja": "ボリューム(24h)", "en": "volume(24h)"},
    "low": {"ja": "最低価格(24h)", "en": "low price(24h)"},
    "high": {"ja": "最高価格(24h)", "en": "high price(24h)"},
    "close": {"ja": "現在価格", "en": "last price"},
    "highestBuy": {"ja": "最高買値", "en": "highest buy"},
    "lowestSell": {"ja": "最低売値", "en": "lowest sell"},
    "jpy": {"ja": "日本円", "en": "JPY"},
    "yukichi": {"ja": "諭吉１枚", "en": "per 10000 jpy"},
    "usd": {"ja": "ドル", "en": "dollar"},
    "$100": {"ja": "100ドルあたり", "en": "per $100"},
    f"{BASE}_BTC": {"ja": f"{BASE}/BTC", "en": f"{BASE}/BTC"},
}


async def __get_price(ctx, lang="ja"):
    embed = discord.Embed(title=texts["embed_title"][lang],
                          description=texts["embed_description"][lang])
    fields = ["change_percent", "baseVolume", "volume", "low",
              "high", "close", "highestBuy", "lowestSell",
              "jpy", "yukichi", "usd", "$100", f"{BASE}_BTC"
              ]
    response, disp = get_market_price_unnamed_exchange(BASE, TARGET)

    if -2.5 < response["change"] <= 2.5:
        image_url = images["IMAGE_NORMAL"]
    elif 2.5 < response["change"] <= 25:
        image_url = images["IMAGE_HIGH"]
    elif 25 < response["change"] <= 50:
        image_url = images["IMAGE_HIGH2"]
    elif 50 < response["change"]:
        image_url = images["IMAGE_HIGHEST"]
    elif -25 < response["change"] <= -2.5:
        image_url = images["IMAGE_LOW"]
    elif -50 < response["change"] <= -25:
        image_url = images["IMAGE_LOW2"]
    elif response["change"] <= -50:
        image_url = images["IMAGE_LOWEST"]

    embed.set_thumbnail(url=image_url)
    for field in fields:
        embed.add_field(name=texts[field][lang],
                        value=disp[field],
                        inline=True)

    embed.add_field(name="Exchange",
                    value=EXCHANGE_URL,
                    inline=False)

    await ctx.send(embed=embed)


@bot.command(name='price')
async def get_price_en(ctx):
    await __get_price(ctx, "en")


@bot.command(name='価格')
async def get_price_ja(ctx):
    await __get_price(ctx, "ja")

if __name__ == '__main__':
    bot.run(os.environ.get("BOT_TOKEN"))
