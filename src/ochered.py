import asyncio

class Ochered():
	def __init__(self, dp, bot, openaiTG):
		self.dp = dp
		self.bot = bot
		self.openaiAPI = openaiTG.apiapi
		self.openaiTG = openaiTG

		self.mes = []
		self.mesToText = {}
		self.mesToChatid = {}
		self.mesToSentChatid = {}
		self.mesToSentMesid = {}

	async def startOcheredGpt(self):
		print("in startOcheredGpt")
		while True:
			print("in while startOcheredGpt")
			await asyncio.sleep(10)
			if len(self.mes) != 0:
				responseGPT = await self.openaiAPI.chatGPT(self.mesToText[f"{self.mes[0]}"], self.mesToChatid[f"{self.mes[0]}"])
				if responseGPT != "retry":
					await self.bot.edit_message_text(chat_id=self.mesToSentChatid[f"{self.mes[0]}"],
													 message_id=self.mesToSentMesid[f"{self.mes[0]}"],
													 text=responseGPT)
					await self.removeGptFromOchered()
					await self.editGptOchered()

	async def startOcheredWhisper(self):
		print("in startOcheredVoice")
		while True:
			print("in while startOcheredVoice")
			await asyncio.sleep(5)

	async def startOcheredDalle(self):
		print("in startOcheredDalle")
		while True:
			print("in while startOcheredDalle")
			await asyncio.sleep(5)

	async def addGptToOchered(self, message, sent_message):
		print("in addGptToOchered")
		self.mes.append(message.message_id)
		self.mesToText[f"{message.message_id}"] = message.text
		self.mesToChatid[f"{message.message_id}"] = message.chat.id
		self.mesToSentChatid[f"{message.message_id}"] = sent_message.chat.id
		self.mesToSentMesid[f"{message.message_id}"] = sent_message.message_id

	async def addDalleToOchered(self, message):
		print("in addDalleToOchered")
	async def addWhisperToOchered(self, message):
		print("in addGptVoiceToOchered")
	async def addDalleVoiceToOchered(self, message):
		print("in addDalleVoiceToOchered")

	async def removeGptFromOchered(self):
		print("in removeGptFromOchered")
		self.mes.pop(0)
	async def removeDalleFromOchered(self, message):
		print("in removeDalleFromOchered")
	async def removeWhisperFromOchered(self, message):
		print("in removeGptVoiceFromOchered")
	async def removeDalleVoiceFromOchered(self, message):
		print("in removeDalleVoiceFromOchered")

	async def editGptOchered(self):
		print("in editGpt")
		i = 0
		while i < len(self.mes):
			print("in while editGPT")
			time = (i + 1) * 20
			await self.bot.edit_message_text(chat_id=self.mesToSentChatid[f"{self.mes[i]}"],
                                             message_id=self.mesToSentMesid[f"{self.mes[i]}"],
                                             text=f"... ожидайте\nпозиция в очереди: {i}\nвремя ожидания: {time} секунд")
			i = i + 1

	async def editDalle(message):
		print("in editDalle")
	async def editGptVoice(message):
		print("in editGptVoice")
	async def editDalleVoice(message):
		print("in editDalleVoice")

	async def answer(self, message, type):
		print("in answer")
		if type == "gpt":
			if len(self.mes) == 0:
				sent_message = await message.answer("...")
				responseGPT = await self.openaiAPI.chatGPT(message.text, message.chat.id)
				if responseGPT == "retry":
					await self.addGptToOchered(message, sent_message)
				else:
					await self.bot.edit_message_text(chat_id=sent_message.chat.id,
													 message_id=sent_message.message_id,
													 text=responseGPT)
			else:
				sent_message = await message.answer("... ожидайте")
				await self.addGptToOchered(message, sent_message)
		# if type == "dalle":
		# 	if len(self.ocheredDalle) == 0:
		# 		print(1)
		# 	else:
		# 		await addDalleToOchered()
		if type == "gptvoice":
			if len(self.mes) == 0:
				sent_message = await message.answer("...")
				responseWHI = await self.openaiTG.downloadAndTranscriptVoice(message.voice.file_id)
				responseGPT = await self.openaiAPI.chatGPT(responseWHI, message.chat.id)
				if responseGPT == "retry":
					await self.addGptToOchered(message, sent_message)
				else:
					await self.bot.edit_message_text(chat_id=sent_message.chat.id,
													 message_id=sent_message.message_id,
													 text=responseGPT)
			else:
				sent_message = await message.answer("... ожидайте")
				responseWHI = await self.openaiTG.downloadAndTranscriptVoice(message.voice.file_id)
				message.text = responseWHI
				await self.addGptToOchered(message, sent_message)
		# if type == "dallevoice":
		# 	if len(self.ocheredDalleVoice) == 0:
		# 		print(2)
		# 	else:
		# 		await addDalleVoiceToOchered()