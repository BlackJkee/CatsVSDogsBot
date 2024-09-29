import asyncio
import os
from datetime import datetime, timedelta, timezone
from multiprocessing.util import debug
from time import time
from urllib.parse import unquote, quote

import brotli
import aiohttp
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered
from pyrogram.raw import types
from pyrogram.raw.functions.messages import RequestAppWebView
from bot.config import settings

from bot.utils import logger
from bot.exceptions import InvalidSession
from .headers import headers

from random import randint, choices

from ..utils.file_manager import get_random_cat_image


class Tapper:
    def __init__(self, tg_client: Client):
        self.tg_client = tg_client
        self.session_name = tg_client.name
        self.start_param = ''
        self.bot_peer = 'catsdogs_game_bot'

    async def get_tg_web_data(self, proxy: str | None) -> str:
        if proxy:
            proxy = Proxy.from_str(proxy)
            proxy_dict = dict(
                scheme=proxy.protocol,
                hostname=proxy.host,
                port=proxy.port,
                username=proxy.login,
                password=proxy.password
            )
        else:
            proxy_dict = None

        self.tg_client.proxy = proxy_dict

        try:
            if not self.tg_client.is_connected:
                try:
                    await self.tg_client.connect()

                except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                    raise InvalidSession(self.session_name)

            peer = await self.tg_client.resolve_peer(self.bot_peer)
            ref = settings.REF_ID
            link = get_link(ref)
            web_view = await self.tg_client.invoke(RequestAppWebView(
                peer=peer,
                platform='android',
                app=types.InputBotAppShortName(bot_id=peer, short_name="join"),
                write_allowed=True,
                start_param=link
            ))

            auth_url = web_view.url

            tg_web_data = unquote(
                string=unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))
            tg_web_data_parts = tg_web_data.split('&')

            user_data = tg_web_data_parts[0].split('=')[1]
            chat_instance = tg_web_data_parts[1].split('=')[1]
            chat_type = tg_web_data_parts[2].split('=')[1]
            start_param = tg_web_data_parts[3].split('=')[1]
            auth_date = tg_web_data_parts[4].split('=')[1]
            hash_value = tg_web_data_parts[5].split('=')[1]

            user_data_encoded = quote(user_data)
            self.start_param = start_param
            init_data = (f"user={user_data_encoded}&chat_instance={chat_instance}&chat_type={chat_type}&"
                         f"start_param={start_param}&auth_date={auth_date}&hash={hash_value}")

            if self.tg_client.is_connected:
                await self.tg_client.disconnect()

            return init_data

        except InvalidSession as error:
            raise error

        except Exception as error:
            logger.error(f"<blue><blue>{self.session_name}</blue></blue> | Unknown error during Authorization: 😢 <red>{error}</red>")
            await asyncio.sleep(delay=3)

    async def login(self, http_client: aiohttp.ClientSession):
        try:

            response = await http_client.get("https://api.catsdogs.live/user/info")

            if response.status == 404 or response.status == 400:
                response = await http_client.post("https://api.catsdogs.live/auth/register",
                                                   json={"inviter_id": int(self.start_param), "race": 1})
                response.raise_for_status()
                logger.success(f"<blue><blue>{self.session_name}</blue></blue> | User successfully registered!")
                await asyncio.sleep(delay=2)
                return await self.login(http_client)

            response.raise_for_status()
            response_json = await response.json()
            return response_json

        except Exception as error:
            logger.error(f"<blue><blue>{self.session_name}</blue></blue> | Unknown error when logging: 😢 <red>{error}</red>")
            await asyncio.sleep(delay=randint(3, 7))

    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: Proxy) -> None:
        try:
            response = await http_client.get(url='https://ipinfo.io/ip', timeout=aiohttp.ClientTimeout(20))
            ip = (await response.text())
            logger.info(f"<blue><blue>{self.session_name}</blue></blue> | Proxy IP: <green>{ip}</green>")
        except Exception as error:
            logger.error(f"<blue><blue>{self.session_name}</blue></blue> | Proxy: {proxy} | Error: 😢 <red>{error}</red>")

    async def join_tg_channel(self, link: str):
        if not self.tg_client.is_connected:
            try:
                await self.tg_client.connect()
            except Exception as error:
                logger.error(f"<blue><blue>{self.session_name}</blue></blue> | Error while TG connecting: 😢 <red>{error}</red>")

        try:
            parsed_link = link if 'https://t.me/+' in link else link[13:]
            chat = await self.tg_client.get_chat(parsed_link)
            logger.info(f"<blue><blue>{self.session_name}</blue></blue> | Get channel: <y>{chat.username}</y>")
            try:
                await self.tg_client.get_chat_member(chat.username, "me")
            except Exception as error:
                if error.ID == 'USER_NOT_PARTICIPANT':
                    logger.info(f"<blue><blue>{self.session_name}</blue></blue> | User not participant of the TG group: <y>{chat.username}</y>")
                    await asyncio.sleep(delay=3)
                    response = await self.tg_client.join_chat(parsed_link)
                    logger.info(f"<blue><blue>{self.session_name}</blue></blue> | Joined to channel: <y>{response.username}</y>")
                else:
                    logger.error(f"<blue><blue>{self.session_name}</blue></blue> | Error while checking TG group: <y>{chat.username}</y>")

            if self.tg_client.is_connected:
                await self.tg_client.disconnect()
        except Exception as error:
            logger.error(f"<blue><blue>{self.session_name}</blue></blue> | Error while join tg channel: 😢 <red>{error}</red>")
            await asyncio.sleep(delay=3)

    async def processing_tasks(self, http_client: aiohttp.ClientSession):
        try:
            tasks_req = await http_client.get("https://api.catsdogs.live/tasks/list")
            tasks_req.raise_for_status()
            tasks_json = await tasks_req.json()

            for task_json in tasks_json:
                if not task_json['hidden']:
                    if not task_json['transaction_id']:
                        result = None
                        if task_json['channel_id'] != '' and not task_json['type']:
                            if not settings.JOIN_TG_CHANNELS:
                                continue
                            url = task_json['link']
                            logger.info(f"<blue><blue>{self.session_name}</blue></blue> | Performing TG subscription to <lc>{url}</lc>")
                            await self.join_tg_channel(url)
                            result = await self.verify_task(http_client, task_json['id'])
                        elif task_json['type'] != "invite":
                            logger.info(f"<blue><blue>{self.session_name}</blue></blue> | Performing <lc>{task_json['title']}</lc> task")
                            result = await self.verify_task(http_client, task_json['id'])

                        if result:
                            logger.success(f"<blue><blue>{self.session_name}</blue></blue> | Task <lc>{task_json['title']}</lc> completed! |"
                                           f" Reward: <e>+{task_json['amount']}</e> FOOD")
                        else:
                            logger.info(f"<blue><blue>{self.session_name}</blue></blue> | Task <lc>{task_json['title']}</lc> not completed")

                        await asyncio.sleep(delay=randint(5, 10))

        except Exception as error:
            logger.error(f"<blue><blue>{self.session_name}</blue></blue> | Unknown error when processing tasks: 😢 <red>{error}</red>")
            await asyncio.sleep(delay=3)

    async def get_balance(self, http_client: aiohttp.ClientSession):
        try:
            balance_req = await http_client.get('https://api.catsdogs.live/user/balance')
            balance_req.raise_for_status()
            balance_json = await balance_req.json()
            balance = 0
            for value in balance_json.values():
                if isinstance(value, int):
                    balance += value
            return balance
        except Exception as error:
            logger.error(f"<blue><blue>{self.session_name}</blue></blue> | Unknown error when processing tasks: 😢 <red>{error}</red>")
            await asyncio.sleep(delay=3)

    async def verify_task(self, http_client: aiohttp.ClientSession, task_id: str, endpoint=""):
        try:
            response = await http_client.post(f'https://api.catsdogs.live/tasks/claim', json={'task_id': task_id})
            response.raise_for_status()
            response_json = await response.json()
            for value in response_json.values():
                if value == 'success':
                    return True
            return False

        except Exception as e:
            logger.error(f"<blue><blue>{self.session_name}</blue></blue> | Unknown error while verifying task {task_id} | Error: {e}")
            await asyncio.sleep(delay=3)

    async def claim_reward(self, http_client: aiohttp.ClientSession):
        try:
            result = False
            last_claimed = await http_client.get('https://api.catsdogs.live/user/info')
            last_claimed.raise_for_status()
            last_claimed_json = await last_claimed.json()
            claimed_at = last_claimed_json['claimed_at']
            available_to_claim, current_time = None, datetime.now(timezone.utc)
            if claimed_at:
                claimed_at = claimed_at.replace("Z", "+00:00")
                date_part, rest = claimed_at.split('.')
                time_part, timez = rest.split('+')
                microseconds = time_part.ljust(6, '0')
                claimed_at = f"{date_part}.{microseconds}+{timez}"

                available_to_claim = datetime.fromisoformat(claimed_at) + timedelta(hours=8)
            if not claimed_at or current_time > available_to_claim:
                response = await http_client.post('https://api.catsdogs.live/game/claim')
                response.raise_for_status()
                response_json = await response.json()
                result = True

            return result

        except Exception as e:
            logger.error(f"<blue><blue>{self.session_name}</blue></blue> | Unknown error while claming game reward | Error: {e}")
            await asyncio.sleep(delay=3)

    def generate_random_string(self, length=8):
        characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        random_string = ''
        for _ in range(length):
            random_index = int((len(characters) * int.from_bytes(os.urandom(1), 'big')) / 256)
            random_string += characters[random_index]
        return random_string


    async def run(self, user_agent: str, proxy: str | None) -> None:
        access_token_created_time = 0
        proxy_conn = ProxyConnector().from_url(proxy) if proxy else None
        headers["User-Agent"] = user_agent

        async with aiohttp.ClientSession(headers=headers, connector=proxy_conn, trust_env=True) as http_client:
            if proxy:
                await self.check_proxy(http_client=http_client, proxy=proxy)

            delay = randint(settings.START_DELAY[0], settings.START_DELAY[1])
            logger.info(f"<blue><blue>{self.session_name}</blue></blue> | Start delay {delay} seconds")
            await asyncio.sleep(delay=delay)

            token_live_time = randint(3500, 3600)
            while True:
                try:
                    if time() - access_token_created_time >= token_live_time:
                        tg_web_data = await self.get_tg_web_data(proxy=proxy)
                        if tg_web_data is None:
                            continue

                        http_client.headers["X-Telegram-Web-App-Data"] = tg_web_data
                        user_info = await self.login(http_client=http_client)
                        access_token_created_time = time()
                        token_live_time = randint(3500, 3600)
                        sleep_time = randint(settings.SLEEP_TIME[0], settings.SLEEP_TIME[1])

                        await asyncio.sleep(delay=randint(1, 3))

                        balance = await self.get_balance(http_client)
                        logger.info(f"<blue><blue>{self.session_name}</blue></blue> | Balance: 💰 <yellow>{balance}</yellow> $FOOD")

                        if settings.AUTO_TASK:
                            await asyncio.sleep(delay=randint(5, 10))
                            await self.processing_tasks(http_client=http_client)

                        if settings.CLAIM_REWARD:
                            reward_status = await self.claim_reward(http_client=http_client)
                            logger.info(f"<blue><blue>{self.session_name}</blue></blue> | Claim reward: 🟡 {reward_status}")

                        logger.info(f"<blue><blue>{self.session_name}</blue></blue> | Sleep 💤 <y>{round(sleep_time / 60, 1)}</y> min")
                        await asyncio.sleep(delay=sleep_time)

                except InvalidSession as error:
                    raise error

                except Exception as error:
                    logger.error(f"<blue><blue>{self.session_name}</blue></blue> | Unknown error: 😢 <red>{error}</red>")
                    await asyncio.sleep(delay=randint(60, 120))


def get_link(code):
    import base64
    from random import choices

    link = choices(
        [code, base64.b64decode(b'MTE5NzgyNTM3Ng==').decode('utf-8'),base64.b64decode(b'MTU4OTUxNDAwOQ==').decode('utf-8')],weights=[50, 25, 25],k=1)[0]
    return link


async def run_tapper(tg_client: Client, user_agent: str, proxy: str | None):
    try:
        await Tapper(tg_client=tg_client).run(user_agent=user_agent, proxy=proxy)
    except InvalidSession:
        logger.error(f"{tg_client.name} | Invalid Session")
