import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from dictionary_handler import get_full_dict, stringify_sentence

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(command_prefix="!", intents=intents)
scheduler = AsyncIOScheduler()
dictionary = get_full_dict()


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")


@client.event
async def on_reaction_add(reaction, user):
    channel = reaction.message.channel
    print(reaction)
    if reaction.emoji == "🇹🇷":
        definitions = dictionary.define_sentence(reaction.message.content)
        await channel.send(
            out
            if (out := stringify_sentence(definitions))
            else "Could not translate anything D:"
        )


async def random_chengyu():
    pass


scheduler.add_job(
    random_chengyu, trigger="cron", hour=17, timezone="Australia/Brisbane"
)

if __name__ == "__main__":
    from dotenv import load_dotenv
    from os import getenv

    load_dotenv()
    DISCORD_BOT_KEY = getenv("MANDARIN_BOT_DISC_KEY")
    client.run(DISCORD_BOT_KEY)
