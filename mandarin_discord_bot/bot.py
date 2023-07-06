import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from dictionary_handler import get_full_dict, stringify_sentence
from chengyu import get_chengyu_generator

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(command_prefix="!", intents=intents)
scheduler = AsyncIOScheduler()
dictionary = get_full_dict()
chengyu_generator = get_chengyu_generator()

CHENGYU_CHANNEL_ID = 1126582313866776616


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")
        await random_chengyu()


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
    msg, chengyus = chengyu_generator.todays_chengyus()
    msg += "\n\t" + "\n\t".join(
        map(
            lambda c: f"{c.rank}: {c.idiom}{(' (HSK'  + c.hsk + ')') if c.hsk else ''}",
            chengyus,
        )
    )

    chengyu_channel = client.get_channel(CHENGYU_CHANNEL_ID)
    await chengyu_channel.send(msg)


if __name__ == "__main__":
    from dotenv import load_dotenv
    from os import getenv

    load_dotenv()
    DISCORD_BOT_KEY = getenv("MANDARIN_BOT_DISC_KEY")

    # scheduler.add_job(
    #     random_chengyu, trigger="cron", hour=5, minute=13, timezone="Australia/Brisbane"
    # )
    # scheduler.start()


    client.run(DISCORD_BOT_KEY)

