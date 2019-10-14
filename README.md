# cacaotasu

![かかおたす](https://raw.githubusercontent.com/kojira/cacaotasu/master/images/screen1.png)

取引所の価格を取得してくるdiscord botです。

現時点で対応しているのは
https://www.unnamed.exchange/
だけです。

随時追加予定。

# 起動方法
`.env.example`ファイルを`.env`にリネームして必要なものを書き込んでください。
```
# botのトークンをしてします
BOT_TOKEN=replace your bot token

# ２４時間変動率によってembedに表示する画像のURLを指定します。
IMAGE_NORMAL=  # -2.5%〜2.5%
IMAGE_HIGH=    #  2.5%〜 25%
IMAGE_HIGH2=   #   25%〜 50%
IMAGE_HIGHEST= #   50%〜
IMAGE_LOW=     #  -25%〜-2.5%
IMAGE_LOW2=    #  -50%〜- 25%
IMAGE_LOWEST=  #  -50%以下

# embedのタイトル文字列
DESCRIPTION_JA=xxxxの価格情報
DESCRIPTION_EN=Price of xxxx

#取引所のURL
EXCHANGE_URL=

# tickerで指定する銘柄コード
BASE=DOGE
TARGET=
```

.envを正しく書き換えた後に
```sh
python bot.py
```
で起動します。


`docker-compose`でも動かせます。

```sh
docker-compose up -d
docker-compose exec app bash
python bot.py
```


