import io

from aiogram import Router, types, F
from aiogram.enums import ChatAction
from aiogram.filters import CommandStart

from services import get_id_nickname, excel_parser

router = Router()


# Добавить текст приветствия.
@router.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Hello!")


@router.message(F.text.regexp(r'^[A-Za-z0-9_]+$'))
async def get_id_account(message: types.Message):
    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.TYPING
    )
    response = await get_id_nickname(message.text)
    await message.answer(response)


@router.message(F.document)
async def download_document(message: types.Message):
    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.UPLOAD_DOCUMENT
    )

    await message.answer(
        "Файл принят, обрабатываю. "
        "Если ников слишком много, то это может занять какое-то время.")

    buffer = io.BytesIO()
    id_document = message.document.file_id
    filename = message.document.file_name
    await message.bot.download(file=id_document, destination=buffer)

    try:
        file = await excel_parser(buffer)
        await message.reply_document(
            document=types.BufferedInputFile(
                file=file,
                filename=filename
            )
        )
    except TimeoutError:
        await message.answer("Слишком много ников, попробуйте сократить")

    except Exception:
        await message.answer("Ошибка, что-то сломалось. Попробуйте еще раз!")
