# ---------------------------------------------------------------------------------
# Name: DiscordStatus
# Description: Модуль для проверки статуса Discord RPC (бот [_b] (общий сервер) + клиент [_c] (если пользователь в друзьях.
# requires: discord.py==2.5.2
# ---------------------------------------------------------------------------------

from hikkatl.types import Message
from .. import loader, utils
import discord
from discord.ext import commands
import asyncio
import time
import logging

logger = logging.getLogger(__name__)

@loader.tds
class DiscordStatusCombinedMod(loader.Module):
    """Модуль для проверки статуса Discord RPC (бот [_b] (общий сервер) + клиент [_c] (если пользователь в друзьях))"""
    strings = {"name": "DiscordStatusCombined"}

    def __init__(self):
        self.bot = None
        self.client = None
        self.bot_ready = False
        self._client_ready = False
        self.config = loader.ModuleConfig(
            "DISCORD_BOT_TOKEN", None, lambda: "Токен Discord бота (для .dcs_b)",
            "DISCORD_USER_TOKEN", None, lambda: "Токен пользователя Discord (для .dcs_c)",
        )

    async def client_ready(self, client, db):
        self._client = client
        self._db = db
        if self.config["DISCORD_BOT_TOKEN"]:
            try:
                await self.start_bot()
            except Exception as e:
                logger.error(f"Ошибка запуска бота: {e}")
        if self.config["DISCORD_USER_TOKEN"]:
            try:
                await self.start_client()
            except Exception as e:
                logger.error(f"Ошибка запуска клиента: {e}")

    async def start_bot(self):
        """Запуск Discord бота (для .dcs_b)"""
        intents = discord.Intents.default()
        intents.presences = True
        intents.members = True

        self.bot = commands.Bot(command_prefix="!", intents=intents, self_bot=False) # префикс НЕ ЮЗЕРБОТА! лучше не менять
        
        @self.bot.event
        async def on_ready():
            self.bot_ready = True
            logger.info(f"Discord бот готов: {self.bot.user.name}")

        asyncio.create_task(self.bot.start(self.config["DISCORD_BOT_TOKEN"]))

    async def start_client(self):
        """Запуск Discord клиента (для .dcs_c)"""
        intents = discord.Intents.all()
        self.client = discord.Client(intents=intents)

        @self.client.event
        async def on_ready():
            self._client_ready = True
            logger.info(f"Discord клиент готов: {self.client.user.name}")

        asyncio.create_task(self.client.start(
            self.config["DISCORD_USER_TOKEN"], 
            bot=False
        ))

    async def dcs_b_cmd(self, message: Message):
        """Проверить статус пользователя через бота (серверы). Использование: .dcs_b <ID/@тег>"""
        if not self.bot_ready:
            await utils.answer(message, "❌ Discord бот не готов. Проверьте токен!")
            return

        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "❌ Укажите ID или @упоминание пользователя")
            return

        try:
            user = await self.parse_user(args, bot_mode=True)
            if not user:
                await utils.answer(message, "❌ Пользователь не найден на общих серверах")
                return

            status = await self.get_user_status(user, bot_mode=True)
            await utils.answer(message, status)

        except Exception as e:
            await utils.answer(message, f"❌ Ошибка: {e}")

    async def dcs_c_cmd(self, message: Message):
        """Проверить статус друга через клиент. Использование: .dcs_c <ID/имя>"""
        if not self._client_ready:
            await utils.answer(message, "❌ Discord клиент не готов. Проверьте токен!")
            return

        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "❌ Укажите ID или имя друга")
            return

        try:
            user = await self.parse_user(args, bot_mode=False)
            if not user:
                await utils.answer(message, "❌ Друг не найден")
                return

            status = await self.get_user_status(user, bot_mode=False)
            await utils.answer(message, status)

        except Exception as e:
            await utils.answer(message, f"❌ Ошибка: {e}")

    async def parse_user(self, args: str, bot_mode: bool) -> discord.User | None:
        """Парсит пользователя из аргументов"""
        if bot_mode:
            try:
                user_id = int(args)
                return await self.bot.fetch_user(user_id)
            except ValueError:
                if args.startswith("<@") and args.endswith(">"):
                    user_id = int(args[2:-1].replace("!", ""))
                    return await self.bot.fetch_user(user_id)
            return None
        else:
            friends = self.client.user.friends
            return next((f for f in friends if f.name == args or str(f.id) == args), None)

    async def get_user_status(self, user: discord.User, bot_mode: bool) -> str:
        """Формирует строку со статусом"""
        member = None
        if bot_mode:
            for guild in self.bot.guilds:
                member = guild.get_member(user.id)
                if member: break
        else:
            member = user

        if not member:
            return f"👤 {user.name} (ID: {user.id})\n🟢 Статус: неизвестен (не на серверах)"

        status = member.status
        activities = member.activities
        rpc_activity = next((a for a in activities if a.type != discord.ActivityType.custom), None)

        base_text = f"👤 `{user.name}`\n🟢 Статус: {status}\n"
        if not rpc_activity:
            return base_text + "📌 Нет активностей"

        activity_type = {
            discord.ActivityType.playing: "🎮 Играет",
            discord.ActivityType.streaming: "📺 Стримит",
            discord.ActivityType.listening: "🎧 Слушает",
            discord.ActivityType.watching: "👀 Смотрит"
        }.get(rpc_activity.type, "❓ Неизвестно")

        elapsed = ""
        if rpc_activity.timestamps and rpc_activity.timestamps.start:
            elapsed_time = int(time.time() - rpc_activity.timestamps.start.timestamp())
            elapsed = f"⏱ {time.strftime('%H:%M:%S', time.gmtime(elapsed_time))}"

        return (f"{base_text}"
                f"**{activity_type}** в ***{rpc_activity.name}***\n"
                f"ℹ️ {rpc_activity.details or 'Нет описания'}\n"
                f"📝 {rpc_activity.state or 'Нет состояния'}\n"
                f"{elapsed}")

    async def on_unload(self):
        if self.bot and self.bot_ready:
            await self.bot.close()
        if self.client and self._client_ready:
            await self.client.disconnect()
