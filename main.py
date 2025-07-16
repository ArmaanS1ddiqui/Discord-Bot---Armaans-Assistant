from typing import Final
import os, asyncio
from dotenv import load_dotenv
from discord import Intents, Client, Message, FFmpegPCMAudio
from responses import get_response
from gtts import gTTS
import openai
from openai import AsyncOpenAI

# Load Discord Bot Token
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY: Final[str] = os.getenv("OPEN_AI_KEY")

open_ai_client = AsyncOpenAI(api_key=os.getenv("OPEN_AI_KEY"))
# Bot setup with required intents
intents: Intents = Intents.default()
intents.message_content = True
intents.dm_messages = True
intents.voice_states = True
client: Client = Client(intents=intents)

# Convert text to speech (TTS) and save as MP3
async def tts_to_mp3(text: str, filename: str) -> None:
    try:        
        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(filename)
    except Exception as e:
        print(f"Error generating TTS: {e}")

# Send message with support for TTS and announcements
async def send_message(message: Message, user_message: str) -> None:
    if not user_message.strip():
        print('(Message was empty, likely due to missing intents)')
        return

    # Private message detection
    is_private = user_message.startswith('?')
    if is_private:
        user_message = user_message[1:].strip()

    # TTS functionality
    if user_message.startswith("$speak") or user_message.startswith("$Speak"):
        content_to_say = user_message[len("$speak"):].strip()

        if not message.guild:
            await message.channel.send("❌ The `$speak` command only works in servers.")
            return

        voice_state = message.author.voice
        if not voice_state or not voice_state.channel:
            await message.channel.send("🔇 Join a voice channel first, then use `$speak …`.")
            return

        # Attempt to connect to voice
        vc = message.guild.voice_client
        try:
            if vc is None or not vc.is_connected():
                vc = await voice_state.channel.connect()
        except Exception as e:
            print(f"Voice connection error: {e}")
            await message.channel.send("❌ Failed to connect to the voice channel.")
            return

        try:
            # Generate and play the MP3 file
            tmp_mp3 = f"/tmp/tts_{message.id}.mp3"
            await tts_to_mp3(content_to_say or "I have nothing to say.", tmp_mp3)
            audio_source = FFmpegPCMAudio(executable="ffmpeg", source=tmp_mp3)
            if not vc.is_playing():
                vc.play(audio_source)
                await message.channel.send("🔈 Speaking now…")
            else:
                await message.channel.send("⏳ Currently busy speaking; try again shortly.")
                return

            # Wait for the playback to complete
            while vc.is_playing():
                await asyncio.sleep(0.5)

            # Disconnect after playback
            await vc.disconnect()
            os.remove(tmp_mp3)
        except Exception as e:
            print(f"Playback error: {e}")
            await message.channel.send("❌ Error during playback.")
            await vc.disconnect()
        return
    
    if user_message.startswith("$ask") or user_message.startswith("$code"):
        prompt = user_message[len("$ask"):].strip()
        if not prompt:
            await message.channel.send("please enter a question or a coding prompt after $ask")
            return 
        await message.channel.send("💬 Thinking...")
        answer = await get_chatgpt_response(prompt)
        await message.channel.send(f"{answer}")
        return 
    
    # Fallback for regular messages
    try:
        response = get_response(user_message)
        if is_private:
            await message.author.send(response)
        else:
            await message.channel.send(response)
    except Exception as e:
        print(f"Response error: {e}")

#chatgpt part 
async def get_chatgpt_response(prompt: str) -> str:
    try:
        response = await open_ai_client.chat.completions.create(
            model = "gpt-3.5-turbo" ,
            messages = [{"role":"user","content":prompt}],
            max_tokens=200, #character count
            temperature=0.7, #creativity - 1 is to creative and 0 is strict
            
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI Error: {e}")
        return "❌ Error getting response please try again."
    

# Handle bot startup
@client.event
async def on_ready() -> None:
    print(f"{client.user} is now running!")

# Handle incoming messages
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return
    print(f"[{message.channel}] {message.author} : '{message.content}'")    
    await send_message(message, message.content.strip())

# Run the bot
if __name__ == '__main__':
    client.run(TOKEN)
