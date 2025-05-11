#deekpeek code

from hikkatl.types import Message
from .. import loader, utils

@loader.tds
class PremiumEmojiSenderMod(loader.Module):
    """Принимает и отправляет премиум-эмодзи"""
    strings = {
        "name": "PremiumEmojiSender",
        "no_args": "🚫 Укажите премиум-эмодзи в формате: <ID>_<Эмодзи>",
        "invalid_format": "🚫 Неверный формат. Используйте: <ID>_<Эмодзи>",
    }

    async def client_ready(self, client, db):
        self._client = client

    @loader.command()
    async def pem(self, message: Message):
        """<ID_Эмодзи> - Отправить премиум-эмодзи"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["no_args"])
            return

        if "_" not in args:
            await utils.answer(message, self.strings["invalid_format"])
            return

        emoji_id, emoji = args.split("_", 1)
        if not emoji_id.isdigit() or not emoji:
            await utils.answer(message, self.strings["invalid_format"])
            return

        await message.delete()
        await self._client.send_message(
            message.peer_id,
            f"<emoji document_id={emoji_id}>{emoji}</emoji>",
        )