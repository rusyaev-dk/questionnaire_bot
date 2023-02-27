from aiogram import types, Dispatcher
from aiogram.dispatcher.handler import CancelHandler

from tgbot.keyboards.qe_reply_kbs import email_accept_kb
from tgbot.misc.states import UserEmail
from tgbot.infrastructure.database import db_commands
from aiogram.dispatcher.middlewares import BaseMiddleware


class ACLMiddleware(BaseMiddleware):
    async def setup_chat(self, data: dict, user: types.User, message: types.Message = None,
                         call: types.CallbackQuery = None):
        user_id = user.id
        registered = await db_commands.select_user(id=user_id)
        if registered is None:
            dispatcher = Dispatcher.get_current()
            state = dispatcher.current_state()
            state_name = await state.get_state()
            if state_name == "UserEmail:GetEmail":
                return

            text = (f"🔹 Здравствуйте, {user.full_name}! С помощью этого бота Вы сможете создавать и проходить "
                    f"различные опросы. На данный момент у бота базовый функционал, который в дальнейшем будет "
                    f"расширяться.\n\n📧 Пожалуйста, отправьте <b>адрес своей электронной почты</b> для обратной "
                    f"связи с создателями других опросов:")
            flag = 0

            if message:
                await message.answer(text=text, reply_markup=email_accept_kb)
                if message.get_args():
                    flag = 1
            elif call:
                await call.message.delete()
                await call.message.answer(text=text, reply_markup=email_accept_kb)

            await db_commands.add_user(id=user_id, name=user.full_name)
            await UserEmail.GetEmail.set()
            await state.update_data(flag=flag)
            raise CancelHandler()

    async def on_pre_process_message(self, message: types.Message, data: dict):
        await self.setup_chat(data, message.from_user, message=message)

    async def on_pre_process_callback_query(self, call: types.CallbackQuery, data: dict):
        await self.setup_chat(data, call.from_user, call=call)
