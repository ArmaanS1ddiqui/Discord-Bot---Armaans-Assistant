from typing import Final
import os 
from dotenv import load_dotenv
from discord import Intents, Client,Message
from responses import get_response

#Loading the Discord Bot Token 
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')


#BOT SETUP 
intents: Intents = Intents.default()
intents.message_content = True
intents.dm_messages = True
client:Client = Client(intents=intents)


#Message Functionality 
async def send_message(message:Message,user_message:str) -> None:
    if not user_message:
        print('(Message was empty because intents were not enabled probably)')
    
    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    
    if user_message[0] == '$':
        if user_message.startswith('$announce'):
            if not message.mentions:
                await message.channel.send("Please mention at least one user to send the announcement.")
                return

            try:
                content = user_message
                for mention in message.mentions:
                    content = content.replace(f"<@{mention.id}>", "")
                content = content.replace('$announce', '').strip()

            # Send DM to each mentioned user
                for user in message.mentions:
                    await user.send(f"📢 Announcement from {message.author.name}: {content}")
            
                await message.channel.send("✅ Announcement sent successfully.")
            except Exception as e:
                print(f"Error sending announcement: {e}")
                await message.channel.send("❌ Failed to send the announcement.")
            return
        try:
            response: str = get_response(user_message)
            await message.author.send(response) if is_private else await message.channel.send(response)
        except Exception as e:
            print(e)

#handling the startup for our bot
@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running!')

@client.event
async def on_message(message:Message) -> None:
    if message.author == client.user:
        return 
    
    username: str = str(message.author)
    user_message: str = message.content
    channel:str = str(message.channel)

    print(f'[{channel}]{username} : "{user_message}"')
    await send_message(message,user_message)

def main() -> None:
    client.run(token=TOKEN)

if __name__ == '__main__':
    main()


