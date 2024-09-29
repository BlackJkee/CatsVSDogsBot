[![Static Badge](https://img.shields.io/badge/Telegram-Bot%20Link-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/catsdogs_game_bot/join?startapp=1197825376)

#  AUTO FARM FOR CatsVSDogsBot 🚀


# 🔥🔥 PYTHON version must be 3.10 🔥🔥

> 🇷 🇺 README in russian available [here](README-RU.md)

## Features  
| Feature                                                   | Supported |
|-----------------------------------------------------------|:---------:|
| Multithreading                                            |     ✔️    |
| Proxy binding to session                                  |     ✔️     |
| User-Agent binding to session                             |     ✔️     |
| Support pyrogram .session                                 |     ✔️     |
| Registration in bot                                       |     ✔️     |
| Auto-tasks                                                |     ✔️     |
| Daily rewards                                             |     ✔️     |



## [Settings]
| Settings                |                                 Description                                 |
|-------------------------|:---------------------------------------------------------------------------:|
| **API_ID / API_HASH**   | Platform data from which to run the Telegram session (by default - android) |
| **SLEEP_TIME**          |           Sleep time between cycles (by default - [7200, 10800])            |
| **START_DELAY**         |            Delay between sessions at start (by default - [5, 25])           |
| **AUTO_TASK**           |                         Auto tasks (default - True)                         |
| **JOIN_CHANNELS**       |              Auto-join for tg channels tasks (default - True)               |
| **CLAIM_REWARD**        |                             Claim daily reward                              |

## Quick Start 📚

To fast install libraries and run bot - open `run.bat` on **Windows** or `run.sh` on **Linux**

## Prerequisites
Before you begin, make sure you have the following installed:
- [**Python**](https://www.python.org/downloads/release/python-3100/) **version 3.10**

## Obtaining API Keys
1. Go to [**my.telegram.org**](https://my.telegram.org/auth) and log in using your phone number.
2. Select `API development tools` and fill out the form to register a new application.
3. Record the `API_ID` and `API_HASH` provided after registering your application in the `.env` file.

## Installation
You can download the [**repository**](https://github.com/BlackJkee/CatsVSDogsBot) by cloning it to your system and installing the necessary dependencies:
```shell
git clone https://github.com/BlackJkee/CatsVSDogsBot.git
cd CatsVSDogsBot
```

Then you can do automatic installation by typing:

Windows:
```shell
run.bat
```

Linux:
```shell
run.sh
```

# Linux manual installation
```shell
sudo sh install.sh
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cp .env-example .env
nano .env  # Here you must specify your API_ID and API_HASH, the rest is taken by default
python3 main.py
```

You can also use arguments for quick start, for example:
```shell
~/CatsVSDogsBot >>> python3 main.py --action (1/2)
# Or
~/CatsVSDogsBot >>> python3 main.py -a (1/2)

# 1 - Run clicker
# 2 - Creates a session
```

# Windows manual installation
```shell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env-example .env
# Here you must specify your API_ID and API_HASH, the rest is taken by default
python main.py
```

You can also use arguments for quick start, for example:
```shell
~/CatsVSDogsBot >>> python main.py --action (1/2)
# Or
~/CatsVSDogsBot >>> python main.py -a (1/2)

# 1 - Run clicker
# 2 - Creates a session
```



