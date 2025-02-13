from hikka import loader, utils
import asyncio
import random

HEV_PHRASES = [
    "[!] Welcome to the **H.E.V Mark IV**, protective system for use in ***hazardous environment*** conditions.",
    "[+] Automatical medical systems: ***Engaged***.",
    "[+] I am backed.",
    "[+] Reactive armor: ***Activated***.",
    "[+] Atmospheric contaminant sensors: ***Activated***",
    "[+] Vital signs: ***Monitoring***.",
    "[+] Automatic medical systems: ***Engaged***",
    "[+] Defensive weapon selection system: ***Activated***.",
    "[+] Munition level monitoring ***Activated***.",
    "[+] Communications interface: ***Online***.",
    "`Have a very safe day.`"
]

class HEVModule(loader.Module):
    """Модуль, который воспроизводит фразы HEV из Black Mesa."""
    
    strings = {"name": "H.E.V. Init"}
    
    async def hevinitcmd(self, message):
        """Запускает последовательное воспроизведение фраз HEV."""
        output = ""
        for phrase in HEV_PHRASES:
            output += phrase + "\n"
            await utils.answer(message, output.strip())
            await asyncio.sleep(random.uniform(1.14, 2.65))  # Рандомная задержка перед изменением сообщения
        
        await asyncio.sleep(random.uniform(7, 10))  # Рандомная задержка перед финальной фразой
        await utils.answer(message, output.strip() + "\n***[+] H.E.V. boot sequence complete***")
