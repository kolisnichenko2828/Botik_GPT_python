import copy
import aiohttp
import json
from aiohttp import FormData
import base64

API_KEY = '<API_KEY>'

class OpenaiAPI:
    def __init__(self):
        self.messagesArchive = {}
        self.systemArchive = {}

    async def newSession(self, id):
        self.messagesArchive[f'{id}'] = [{"role": "system", "content": ""},
                                         {"role": "user", "content": "привет"},
                                         {"role": "assistant", "content": "привет"}]
        self.systemArchive[f'{id}'] = ""

    async def clearMessages(self, id):
        if f'{id}' in self.systemArchive:
            system = self.systemArchive[f'{id}']
        else:
            system = ""
            self.systemArchive[f'{id}'] = system
        self.messagesArchive[f'{id}'] = [{"role": "system", "content": system},
                                         {"role": "user", "content": "привет"},
                                         {"role": "assistant", "content": "привет"}]
        
    async def changeSystem(self, text, id):
        self.systemArchive[f'{id}'] = text + ". "
        self.messagesArchive[f'{id}'] = [{"role": "system", "content": self.systemArchive[f'{id}']},
                                         {"role": "user", "content": "привет"},
                                         {"role": "assistant", "content": "привет"}]

    async def chatGPT(self, text, id):
        messages = []
        tempMessages = []
        responseGPT = []
        try:
            if f'{id}' in self.systemArchive:
                system = self.systemArchive[f'{id}']
            else:
                system = ""
                self.systemArchive[f'{id}'] = system
            if f'{id}' in self.messagesArchive:
                messages = self.messagesArchive[f'{id}']
            else:
                messages = [{"role": "system", "content": system},
                            {"role": "user", "content": "привет"},
                            {"role": "assistant", "content": "привет"}]
                self.messagesArchive[f'{id}'] = messages
            tempMessages = copy.copy(messages)
            messages.append({"role": "user", "content": system + text})

            count = 0
            for message in messages:
                count += len(message['content'])
            count = count + 30

            async with aiohttp.ClientSession() as session:
                url = "https://api.openai.com/v1/chat/completions"
                headers = {"Content-Type": "application/json",
                           "Authorization": f"Bearer {API_KEY}"}
                data = {"model": "gpt-3.5-turbo",
                        "messages": messages,
                        "max_tokens": 4096 - count,
                        "n": 1,
                        "stop": None,
                        "temperature": 1}
                async with session.post(url, headers=headers, data=json.dumps(data)) as response:
                    responseGPT = await response.json()
                    messages.append({"role": "assistant", "content": responseGPT['choices'][0]['message']['content']})
                    self.messagesArchive[f'{id}'] = messages
                    return responseGPT['choices'][0]['message']['content']
        except Exception as e:
            messages = copy.copy(tempMessages)
            if "is less than the minimum of 1" in responseGPT['error']['message']:
                await self.clearMessages(id)
                return "[ботик] достигнут лимит контекста, контекст очищен"
            if responseGPT['error']['message'].startswith("This model's maximum context length is 4097 tokens. However, you requested"):
                await self.clearMessages(id)
                return "[ботик] достигнут лимит контекста, контекст очищен"
            if responseGPT['error']['message'].startswith("Rate limit reached"):
                return "error wait"
            if responseGPT['error']['message'].startswith("That model is currently overloaded with other requests"):
                return "error wait"
            print(f'Error while chatGPT: {e}\n{responseGPT}')
            return "[ботик] произошла неизвестная ошибка"

    async def transcriptVOICE(self, audio_file_path):
        try:
            async with aiohttp.ClientSession() as session:
                url = "https://api.openai.com/v1/audio/transcriptions"
                headers = {"Authorization": f"Bearer {API_KEY}"}
                data = FormData()
                data.add_field('model', 'whisper-1')
                data.add_field('file', audio_file_path, filename='audio.mp3')
                
                async with session.post(url, headers=headers, data=data) as response:
                    transcript = await response.json()
                    return transcript['text']
        except Exception as e:
            if "The server had an error while processing your request. Sorry about that!" in transcript['error']['message']:
                return "[ботик] нет ответа"
            print(f'Error while transcriptVOICE: {e}\n{transcript}')
            return "[ботик] нет ответа"

    async def imageDALLE(self, text):
        try:
            async with aiohttp.ClientSession() as session:
                url = "https://api.openai.com/v1/images/generations"
                headers = {"Content-Type": "application/json",
                           "Authorization": f"Bearer {API_KEY}"}
                data = {"prompt": text,
                        "n": 1,
                        "size": "1024x1024"}
                async with session.post(url, headers=headers, data=json.dumps(data)) as response:
                    response = await response.json()
                    return response["data"][0]["url"]
        except Exception as e:
            if response['error']['message'].startswith("Your request was rejected as a result of our safety system"):
                return response['error']['message']
            if response['error']['message'].startswith("Rate limit exceeded for images per minute"):
                return response['error']['message']
            print(f'Error while imageDALLE: {e}\n{response}')

    async def variationDALLE(self, id):
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': f'Bearer {API_KEY}'}
                data = FormData()
                data.add_field('image', open(f'temp/input{id}.png', 'rb'), filename=f'input{id}.png', content_type='image/png')
                data.add_field('n', '1')
                data.add_field('size', '1024x1024')
                async with session.post('https://api.openai.com/v1/images/variations', headers=headers, data=data) as resp:
                    response = await resp.json()
                    return response["data"][0]["url"]
        except Exception as e:
            print(f'Error while variationDALLE: {e}\n{response}')
            return response['error']['message']

openai_api = OpenaiAPI()
