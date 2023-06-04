import asyncio

class OcheredTG:
    def __init__(self, openaiTG):
        self.bot = openaiTG.bot
        self.openaiTG = openaiTG
        self.ocheredStart = "false"

    async def ocheredFunc(self):
        try:
            current_index = 0
            temp_index = -1
            while True:
                    mes = "error wait"
                    if len(self.openaiTG.ocheredM) != 0:
                        index = self.openaiTG.ocheredM.index(self.openaiTG.listMessages[-1].message_id)
                        if index != temp_index:
                            i = 0
                            while i < len(self.openaiTG.ocheredM):
                                try:
                                    time = 20 * (i + 1)
                                    await self.bot.edit_message_text(chat_id=self.openaiTG.listMessages[i].chat.id,
                                                                message_id=self.openaiTG.listMessages[i].message_id,
                                                                text=f"... ожидайте\nпозиция в очереди: {i}\nвремя ожидания: {time} секунд")
                                except Exception as e:
                                    if str(e) == "Message to edit not found":
                                        self.openaiTG.ocheredM.pop(i)
                                        self.openaiTG.listTexts.pop(i)
                                        self.openaiTG.listMessages.pop(i)
                                        continue
                                i = i + 1
                        temp_index = index
                    await asyncio.sleep(5)
                    if len(self.openaiTG.ocheredM) != 0:
                        if f'{self.openaiTG.ocheredM[0]}' in self.openaiTG.voiceMessagesIds:
                            text = await self.openaiTG.downloadAndTranscriptVoice(self.openaiTG.voiceMessagesIds[f'{self.openaiTG.ocheredM[0]}'])
                            mes = await self.openaiTG.chatGpt(text, self.openaiTG.listMessages[0], isVoice="true")
                        else:
                            mes = await self.openaiTG.chatGpt(self.openaiTG.listTexts[0], self.openaiTG.listMessages[0])
                    if mes != "error wait":
                        self.openaiTG.ocheredM.pop(0)
                        self.openaiTG.listTexts.pop(0)
                        self.openaiTG.listMessages.pop(0)

        except Exception as e:
            print(f"error while ocheredFunc: {e}")

    async def addToOchered(self, text, sent_message):
        self.openaiTG.ocheredM.append(sent_message.message_id)
        self.openaiTG.listTexts.append(text)
        self.openaiTG.listMessages.append(sent_message)
        index = self.openaiTG.ocheredM.index(self.openaiTG.listMessages[-1].message_id)
        time = 20 * (index + 1)
        await self.bot.edit_message_text(chat_id=self.openaiTG.listMessages[-1].chat.id,
                                    message_id=self.openaiTG.listMessages[-1].message_id,
                                    text=f"... oжидайте\nпозиция в очереди: {index}\nвремя ожидания: {time} секунд")

    async def sendMessage(self, text, sent_message, isVoice="false", message=""):
        if len(self.openaiTG.ocheredM) == 0:
            if isVoice == "false":
                mes = await self.openaiTG.chatGpt(text, sent_message)
            elif isVoice == "true":
                text = await self.openaiTG.downloadAndTranscriptVoice(message.voice.file_id)
                mes = await self.openaiTG.chatGpt(text, sent_message, isVoice="true", message=message)
                if mes == "error wait":
                    self.openaiTG.voiceMessagesIds[f'{sent_message.message_id}'] = message.voice.file_id
                    await self.addToOchered(text, sent_message)
                    return
            if mes == "error wait":
                await self.addToOchered(text, sent_message)
                return
            return
        if isVoice == "false":
            await self.addToOchered(text, sent_message)
        elif isVoice == "true":
            self.openaiTG.voiceMessagesIds[f'{sent_message.message_id}'] = message.voice.file_id
            await self.addToOchered(text, sent_message)