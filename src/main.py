import logging
from aiogram import Bot, Dispatcher, executor, types
import os # нужно для перезагрузки бота
import sys # нужно для перезагрузки бота
import json

from gpt4free import Provider, Completion

from openaiTG import OpenaiTG
from ocheredTG import OcheredTG
from ochered import Ochered

import asyncio
import aiocron

logging.basicConfig(level=logging.INFO)

try:
    API_TOKEN = '6165440909:AAGZQSkGfbzP7I9ypuD0F59K08UogdWCHw4'
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot)
    mode = "gpt"
    startup = "false"
except Exception as e:
    print(f'Error while set params: {e}')

@aiocron.crontab('* * * * * *')
async def cronTaskStartup():
    try:
        global startup
        if startup == "false":
            await openaiTG.setCommands()
            with open('temp/history.json', 'r') as f:
                openaiTG.apiapi.messagesArchive = json.load(f)
            with open('temp/system.json', 'r') as f:
                openaiTG.apiapi.systemArchive = json.load(f)
            await bot.send_message(chat_id='860189866', text="[ботик] перезагрузился")
            print("Очередь запущена")
            startup = "true"
            await ocheredTG.ocheredFunc()
            # await ochered.startOcheredGpt()
    except Exception as e:
        print(f'Error while on_startup: {e}')

@dp.message_handler(lambda message: message.text.startswith('/'))
async def commandHandler(message: types.Message):
    try:
        if(message.text.lower() == "/start"):
            await message.answer("Привет! Я могу отвечать на вопросы, искать информацию и давать советы. Жду вашего текстового или голосового сообщения. Можете даже отправить мне фото или попросить нарисовать что-то.")
        elif(message.text.lower() == "/new"):
            await openaiTG.newSession(message.chat.id)
            await message.answer("[ботик] новый чат создан")
        elif message.text.lower().startswith("/prompt") and not message.text.lower().startswith("/prompts"):
            if message.text.lower().startswith("/prompt "):
                text = message.text.replace('/prompt ', '', 1)
                await openaiTG.changeSystem(text, message.chat.id)
                await message.answer("[ботик] системное сообщение изменено на: " + text)
            else:
                await message.answer("\[ботик] отклонено. пример команды:\n`/prompt представь, что ты терминатор`", parse_mode = 'Markdown')
        elif(message.text.lower() == "/prompts"):
            await message.answer(openaiTG.returnPrompts(), parse_mode = 'Markdown')
        elif(message.text.lower() == "/restart"):
            if message.chat.id == 860189866:
                await message.answer("[ботик] перезагружаюсь")
                with open('temp/history.json', 'w') as f:
                    json.dump(openaiTG.apiapi.messagesArchive, f)
                with open('temp/system.json', 'w') as f:
                    json.dump(openaiTG.apiapi.systemArchive, f)
                os.execv(sys.executable, ['python'] + sys.argv)
            else:
                await message.answer("[ботик] только админ может меня перезагружать")
        elif(message.text.lower() == "/clear"):
            await openaiTG.clearMessages(message.chat.id)
            await message.answer("[ботик] история сообщений очищена")
    except Exception as e:
        print(f'Error while commandHandler: {e}')

@dp.message_handler(content_types=['photo'])
async def photoHandler(message: types.Message):
    try:
        if openaiTG.ifGroup(message) == 1:
            if openaiTG.ifTag(message):
                sent_message = await message.reply("[ботик] запрос принял")
                await openaiTG.variationDalle(message, sent_message)
        else:
            sent_message = await message.answer("[ботик] запрос принял")
            await openaiTG.variationDalle(message, sent_message)
    except Exception as e:
        print(f'Error while photoHandler: {e}')

@dp.message_handler(content_types=['voice'])
async def voiceHandler(message: types.Message):
    try:
        if openaiTG.ifGroup(message) == 1:
            if openaiTG.ifTag(message):
                sent_message = await message.reply('...')
                # if message.text.lower().startswith('нарису'):
                #     await openaiTG.imageDalle(message, sent_message)
                # else:
                await ocheredTG.sendMessage(message.text, sent_message, isVoice="true", message=message)
                # await ochered.answer(message, sent_message, "gptvoice")
        else:
            sent_message = await message.answer('...')
            # if message.text.lower().startswith('нарису'):
            #     await openaiTG.imageDalle(message, sent_message)
            # else:
            await ocheredTG.sendMessage(message.text, sent_message, isVoice="true", message=message)
            # await ochered.answer(message, sent_message, "gptvoice")
    except Exception as e:
        print(f'Error while voiceHandler: {e}')

@dp.message_handler()
async def textHandler(message: types.Message):
    global mode
    try:
        if(message.text.lower() == "ботик"):
            await message.answer("тут")

        elif openaiTG.ifGroup(message) == 1:
            if openaiTG.ifTag(message):
                if message.text.lower().startswith('нарису'):
                    sent_message = await message.reply("[ботик] запрос принял")
                    await openaiTG.imageDalle(message, sent_message)
                else:
                    sent_message = await message.reply("...")
                    await ocheredTG.sendMessage(message.text, sent_message)
                    # response = Completion.create(Provider.You, prompt=message.text)
                    # response = response.encode().decode('unicode_escape')
                    # await message.answer(response)
        else:
            if message.text.lower().startswith('нарису'):
                sent_message = await message.answer("[ботик] запрос принял")
                await openaiTG.imageDalle(message, sent_message)
            else:
                sent_message = await message.answer("...")
                await ocheredTG.sendMessage(message.text, sent_message)

                # await ochered.answer(message, "gpt")

                # prompt = f"отвечай на русском. {message.text}"
                # response = Completion.create(Provider.You, prompt=prompt, detailed=True)
                # response = response.encode().decode('unicode_escape')
                # await message.answer(response)

    except Exception as e:
        print(f'Error while textHandler: {e}')

if __name__ == '__main__':
    try:
        openaiTG = OpenaiTG(dp, bot)
        ocheredTG = OcheredTG(openaiTG)
        # ochered = Ochered(dp, bot, openaiTG)
        executor.start_polling(dp, skip_updates=True)
    except Exception as e:
        print(f'Error while bot start: {e}')