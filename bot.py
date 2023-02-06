import logging
from PIL import Image
import os
from env import BOT_TOKEN
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InputFile


logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

keyb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
keyb.add(KeyboardButton("/convert"))

images = {}


@dp.message_handler(content_types=['photo'])
async def doc_handler(message: types.Message):

    photo = await bot.get_file(message.photo[-1].file_id)

    if not(message.chat.id in images.keys()):
        images[message.chat.id] = []
        images[message.chat.id].append(photo.file_path)
    else:
        images[message.chat.id].append(photo.file_path)

    await bot.send_message(chat_id=message.from_user.id, text="send next photo or press convert button", reply_markup=keyb)


@dp.message_handler(commands=['convert'])
async def start_handler(message: types.Message):

    user_imgs = images[message.chat.id]
    srcs = []

    for i in range(len(user_imgs)):

        dwn = await bot.download_file(user_imgs[i])

        srcs.append(user_imgs[i])

        with open(user_imgs[i], 'ab') as new_file:
            new_file.write(dwn.getvalue())

    img_ready = [Image.open(src).convert('RGB') for src in srcs]

    img_ready[0].save(rf'photos/{message.chat.id}.pdf', save_all=True, append_images=img_ready[1:])

    images[message.chat.id].clear()

    pdf = InputFile(f'photos/{message.chat.id}.pdf')
    await bot.send_document(chat_id=message.from_user.id, document=pdf, reply_markup=ReplyKeyboardRemove())

    for file in srcs:
        os.remove(file)

    os.remove(f'./photos/{message.chat.id}.pdf')


executor.start_polling(dp, skip_updates=True)