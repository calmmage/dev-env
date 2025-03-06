from _app import App
from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from botspot import commands_menu
from botspot.utils import send_safe

router = Router()
app = App()


@commands_menu.add_command("start", "Start the bot")
@router.message(CommandStart())
async def start_handler(message: Message):
    await send_safe(message.chat.id, f"Hello! Welcome to {app.name}!")


@commands_menu.add_command("help", "Show this help message")
@router.message(Command("help"))
async def help_handler(message: Message):
    """Basic help command handler"""
    await send_safe(message.chat.id, f"This is {app.name}. Use /start to begin.")
