import requests
import os
from .. import loader, utils
from hikkatl.tl.types import Message

@loader.tds
class FriendsMod(loader.Module):
    """Модуль для отправки картинки и подписи по команде [prefix]friends"""

    strings = {"name": "Friends"}

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "custom_friends_message",
                "chatgpt",
                doc="Кастомное сообщение для подписи",
            ),
            loader.ConfigValue(
                "friends_banner_url",
                "https://i.imgur.com/op3jqNk.png",
                doc="Ссылка на картинку для отправки",
            ),
        )

    async def friends_cmd(self, message: Message):
        """Отправить картинку и подпись"""
        banner_url = self.config["friends_banner_url"]
        custom_message = self.config["custom_friends_message"]

        # Отправляем картинку с подписью
        await utils.answer_file(
            message,
            banner_url,
            custom_message,
        )

    @loader.command()
    async def setfriends(self, message: Message):
        """Установить кастомное сообщение для подписи"""
        if not (args := utils.get_args_raw(message)):
            return await utils.answer(message, "Укажите новое сообщение для подписи!")

        self.config["custom_friends_message"] = args
        await utils.answer(message, "Сообщение успешно обновлено!")

    @loader.command()
    async def setbanner(self, message: Message):
        """Установить новую картинку для отправки"""
        if not (args := utils.get_args_raw(message)):
            return await utils.answer(message, "Укажите новую ссылку на картинку!")

        self.config["friends_banner_url"] = args
        await utils.answer(message, "Ссылка на картинку успешно обновлена!")
        
#chatgpt $$elfcode