import httpx
import openpyxl

from typing import IO


async def get_id_nickname(name):
    name = name.strip()
    if len(name.split()) > 1:
        return f"Пользователь с ником {name} не найден"
    data = None

    try:
        response = httpx.get(f"https://api.tanki.su/wot/account/list/?application_id=6e76bdefe5b324d811d62bd6bc861e02&search={name}")
        data = response.json()
    except httpx.ReadTimeout:
        response = httpx.get(f"https://api.tanki.su/wot/account/list/?application_id=6e76bdefe5b324d811d62bd6bc861e02&search={name}")
        data = response.json()

    if data["status"] != "ok":
        return f"Пользователь с ником {name} не найден"

    if not data["data"]:
        return f"Пользователь с ником {name} не найден"

    nickname = data["data"][0]["nickname"]
    if nickname.lower() != name.lower():
        return f"Пользователь с ником {name} не найден"

    id_ = data["data"][0]["account_id"]
    return str(id_)


async def excel_parser(file: IO[bytes]):
    wb = openpyxl.load_workbook(file, keep_vba=True)
    sheet = wb.active
    max_rows = sheet.max_row

    if max_rows > 500:
        raise TimeoutError

    for i in range(1, max_rows + 1):
        nickname = sheet.cell(row=i, column=1)
        if not nickname.value:
            continue
        id_ = await get_id_nickname(nickname.value)
        nickname.value = id_
        wb.save(file)
    wb.close()
