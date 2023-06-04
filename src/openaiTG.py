from pydub import AudioSegment # для whisper
import aiohttp # для dalle
import os
import random
from aiogram import types
from PIL import Image
import asyncio

from openaiAPI import openai_api
from translateAPI import tr

API_TOKEN = '6165440909:AAGZQSkGfbzP7I9ypuD0F59K08UogdWCHw4'

class OpenaiTG():
    def __init__(self, dp, bot):
        self.dp = dp
        self.bot = bot
        self.ocheredM = []
        self.listMessages = []
        self.listTexts = []
        self.voiceMessages = {}
        self.voiceMessagesIds = {}
        self.apiapi = openai_api

    async def setCommands(self):
        await self.dp.bot.set_my_commands([
            types.BotCommand("new", "очистить контекст"),
            types.BotCommand("clear", "очистить историю"),
            types.BotCommand("prompt", "сменить системное сообщение"),
            types.BotCommand("prompts", "посмотреть системные сообщения"),])

    async def newSession(self, id):
        await openai_api.newSession(id)

    async def clearMessages(self, id):
        await openai_api.clearMessages(id)

    async def changeSystem(self, text, id):
        await openai_api.changeSystem(text, id)

    async def downloadAndTranscriptVoice(self, voice_id):
        try:
            voice = await self.bot.get_file(voice_id)
            await self.bot.download_file(voice.file_path, f'temp/voice_message_{voice_id}.ogg')
            AudioSegment.from_ogg(f'temp/voice_message_{voice_id}.ogg').export(f'temp/voice_message_{voice_id}.mp3', format='mp3')
            audio_file = open(f'temp/voice_message_{voice_id}.mp3', "rb")
            transcript = await openai_api.transcriptVOICE(audio_file)
            os.remove(f'temp/voice_message_{voice_id}.mp3')
            os.remove(f'temp/voice_message_{voice_id}.ogg')
            return transcript
        except Exception as e:
            print(f'Error while downloadAndTranscriptVoice: {e}')

    async def downloadPhoto(self, message):
        file_id = message.photo[-1].file_id
        file = await self.bot.get_file(file_id)
        file_path = file.file_path
        await self.bot.download_file(file_path, f'temp/input{message.photo[-1].file_id}.jpg')

        image = Image.open(f'temp/input{message.photo[-1].file_id}.jpg')
        image.save(f'temp/input{message.photo[-1].file_id}.png')

    async def chatGpt(self, text, sent_message, isVoice="false", message=""):
        if text == "[ботик] нет ответа":
            await self.bot.edit_message_text(chat_id=sent_message.chat.id,
                                            message_id=sent_message.message_id,
                                            text=text)
        response = await openai_api.chatGPT(text, sent_message.chat.id)
        try:
            if response != "error wait" and isVoice == "false":
                await self.bot.edit_message_text(chat_id=sent_message.chat.id,
                                                message_id=sent_message.message_id,
                                                text=response)
            elif response != "error wait" and isVoice == "true":
                response = "\nваш запрос: " + text + "\n\n" + response
                await self.bot.edit_message_text(chat_id=sent_message.chat.id,
                                                message_id=sent_message.message_id,
                                                text=response)
        except Exception as e:
            print(f'Error while chatGpt: {e}')
            print(response)
        return response

    async def imageDalle(self, message, sent_message):
        try:
            text = message.text.replace('нарисуй ', '', 1)
            text = text.replace('Нарисуй ', '', 1)
            text = text.replace('нарисую ', '', 1)
            text = text.replace('Нарисую ', '', 1)
            text = await tr.translateToEn(text)
            url = await openai_api.imageDALLE(text)

            if str(url).startswith("Your request was rejected as a result of our safety system"):
                await self.bot.edit_message_text(chat_id=message.chat.id,
                                                 message_id=sent_message.message_id,
                                                 text="[ботик] ваш запрос был отклонён")
                return
            if str(url).startswith("Rate limit exceeded for images per minute"):
                await self.bot.edit_message_text(chat_id=message.chat.id,
                                                 message_id=sent_message.message_id,
                                                 text="[ботик] попробуйте ещё раз через 10 секунд")
                return
            if str(url).startswith("https"):
                pass
            else:
                await self.bot.edit_message_text(chat_id=message.chat.id,
                                                 message_id=sent_message.message_id,
                                                 text="[ботик] неизвестная ошибка")
                return

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    photo = await response.read()
                    if self.ifGroup(message) == 1:
                        if self.ifTag(message):
                            await message.reply_photo(photo, caption=text)
                    else:
                        await message.answer_photo(photo, caption=text)

            await self.bot.delete_message(chat_id=sent_message.chat.id, message_id=sent_message.message_id)
        except Exception as e:
            print(f'Error while imageDalle: {e}')

    async def variationDalle(self, message, sent_message):
        try:
            await self.downloadPhoto(message)
            url = await openai_api.variationDALLE(message.photo[-1].file_id)

            if str(url).startswith("Your request was rejected as a result of our safety system"):
                await self.bot.edit_message_text(chat_id=message.chat.id,
                                                 message_id=sent_message.message_id,
                                                 text="[ботик] ваш запрос был отклонён")
                return
            if str(url).startswith("Rate limit exceeded for images per minute"):
                await self.bot.edit_message_text(chat_id=message.chat.id,
                                                 message_id=sent_message.message_id,
                                                 text="[ботик] попробуйте ещё раз через 10 секунд")
                return

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    photo = await response.read()
                    if self.ifGroup(message) == 1:
                        if self.ifTag(message):
                            await message.reply_photo(photo)
                    else:
                        await message.answer_photo(photo)
    
            await self.bot.delete_message(chat_id=sent_message.chat.id, message_id=sent_message.message_id)
            os.remove(f'temp/input{message.photo[-1].file_id}.jpg')
            os.remove(f'temp/input{message.photo[-1].file_id}.png')
        except Exception as e:
            print(f'Error while variationDalle: {e}')

    def ifGroup(self, message):
        if message.chat.type == types.ChatType.GROUP or message.chat.type == types.ChatType.SUPERGROUP:
            return 1
    
    def ifTag(self, message):
        if message.reply_to_message and message.reply_to_message.from_user.id == self.bot.id:
            return 1
        
    def ifTagPhoto(self, message):
        if message.reply_to_message.photo:
            return 1
        
    def ifPhoto(self, message):
        if message.photo:
            return 1

    def returnPrompts(self):
        with open('temp/prompts.txt', 'r', encoding='utf-8') as file:
            text = file.read()
            return text
        
    # def returnPrompts(self):
    #     return "\[ботик] доступны следующие промпты:\n\n" + \
    #            "`/prompt отвечай так, будто ты девочка гопница лёгкого поведения, которая любит подчиняться. ответ должен быть не больше 40 слов`\n\n" + \
    #            "`/prompt отвечай так, будто ты терминатор. ответ должен быть не больше 40 слов`\n\n" + \
    #            "`/prompt отвечай так, будто ты профессиональный программист`\n\n" + \
    #            "`/prompt отвечай так, будто ты профессиональный программист гопник. ответ должен быть не больше 40 слов`\n\n" + \
    #            "`/prompt отвечай так, будто ты профессиональный программист гопник`\n\n" + \
    #            "`/prompt ответ должен быть не больше 40 слов`\n\n" + \
    #            "`/prompt отвечай так, будто ты профессиональный юморист, который любит чёрный юмор и шутит на тему тупых друзей. ответ должен быть не больше 40 слов`\n\n" + \
    #            "`/prompt используй ругательные слова в своих ответах`\n\n" + \
    #            "`/prompt отвечай так, будто ты накуренный программист, который сделает всё, что я скажу. используй ругательные слова в своих ответах`\n\n" + \
    #            "`/prompt отвечай так, будто ты придурок, используй ругательные выражения, не больше 2 слов`\n\n"