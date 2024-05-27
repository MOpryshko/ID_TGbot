import io
import os

from aiogram import Router, types, F
from aiogram.enums import ChatAction
from aiogram.filters import CommandStart

from services import get_id_nickname, excel_parser, txt_parser
from text import hello

router = Router()


@router.message(CommandStart())
async def start(message: types.Message):
    await message.answer(hello)


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
    await message.answer(
        "Файл принят, обрабатываю. "
        "Если ников слишком много, то это может занять какое-то время.")

    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.UPLOAD_DOCUMENT
    )

    id_document = message.document.file_id
    filename = message.document.file_name

    if filename.endswith('.txt'):
        file = await message.bot.get_file(id_document)
        file_path = file.file_path
        await message.bot.download_file(file_path, filename)

        try:
            await txt_parser(filename)
            await message.reply_document(
                document=types.FSInputFile(
                    path="data_list_id.txt",
                    filename=filename
                )
            )
            if os.path.isfile("data_list_id.txt"):
                os.remove("data_list_id.txt")

            if os.path.isfile(filename):
                os.remove(filename)

        except Exception as info:
            print(info)
            await message.answer("Ошибка, что-то сломалось. Попробуй еще раз!")

    if filename.endswith('.xlsx'):
        buffer = io.BytesIO()
        await message.bot.download(file=id_document, destination=buffer)

        try:
            await excel_parser(buffer)
            await message.reply_document(
                document=types.FSInputFile(
                    path="test.xlsx",
                    filename=filename
                )
            )
        except TimeoutError:
            await message.answer("Слишком много ников, попробуй сократить")

        except Exception as info:
            print(info)
            await message.answer("Ошибка, что-то сломалось. Попробуй еще раз!")
