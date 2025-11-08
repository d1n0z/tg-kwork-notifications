from aiogram import Dispatcher, types
from kwork import Kwork

from KworkNotifications.core.models import KworkCredentials, Users


async def start_handler(message: types.Message):
    await message.answer(
        "Привет!\nЧтобы добавить аккаунт на мониторинг новых сообщений, введи команду /add [login] [password].\nЧтобы удалить, введи /del [login]."
    )


async def add_handler(message: types.Message):
    args = message.text.split()[1:]
    if len(args) != 2:
        await message.answer("Использование: /add [login] [password].")
        return

    login, password = args
    unread_count = 0
    api = None
    try:
        api = Kwork(login=login, password=password)
        dialogs = await api.get_all_dialogs()
        for dialog in dialogs:
            unread_count += dialog.unread_count or 0
    except Exception as e:
        if api:
            try:
                await api.close()
            except Exception:
                pass
        if 'некорректно' in str(e) or 'неверно' in str(e):
            await message.answer(
                "Логин или пароль указаны неверно. Проверьте правильность введённых данных."
            )
        else:
            await message.answer(
                "Произошла ошибка. Проверьте правильность введённых данных."
            )
        return
    if api:
        try:
            await api.close()
        except Exception:
            pass
    await message.delete()
    user, _ = await Users.get_or_create(tg_id=message.from_user.id)
    await KworkCredentials.create(
        user=user, login=login, password=password, last_unread_count=unread_count
    )
    await message.answer(f"Аккаунт {login} добавлен.")


async def del_handler(message: types.Message):
    await message.delete()
    args = message.text.split()[1:]
    if len(args) != 1:
        await message.answer("Использование: /del [login].")
        return

    login = args[0]
    user = await Users.get_or_none(tg_id=message.from_user.id)
    if not user:
        await message.answer("У вас нет привязанных аккаунтов.")
        return

    deleted = await KworkCredentials.filter(user=user, login=login).delete()
    if deleted:
        await message.answer(f"Аккаунт {login} удален.")
    else:
        await message.answer(f"Аккаунт {login} не найден.")


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_handler, commands=["start"])
    dp.register_message_handler(add_handler, commands=["add"])
    dp.register_message_handler(del_handler, commands=["del"])
