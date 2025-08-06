import discord
from discord import app_commands
import os
from dbHandler import steamUidCheck, registerAccount
from dotenv import load_dotenv
import asyncio



load_dotenv()

GUILD_ID = discord.Object(id=843881691037696071)

class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=GUILD_ID)
        await self.tree.sync(guild=GUILD_ID)

client = MyClient()



@client.event
async def on_ready():
    await client.tree.sync()
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send(message.author.id)

@client.tree.command(name="register", description="Use to register your steam account")
@app_commands.describe(steam_link="Link to your steam account")
async def register(interaction: discord.Interaction, steam_link: str):
    await interaction.response.defer()

    steam_data = steamUidCheck(steam_uid=steam_link)

    print(steam_data)

    if steam_data == "No data found":
        await interaction.followup.send(f"Could not find steam profile.")
        return

    # Compose profile info (maybe a name or a Steam profile link)
    profile_msg = f"Is this your Steam profile: {steam_data['profileurl']}?"

    message = await interaction.followup.send(profile_msg)
    await message.add_reaction("✅")
    await message.add_reaction("❌")

    def check(reaction, user):
        return (
            user == interaction.user  # Only accept reactions from the command user
            and reaction.message.id == message.id  # Only on this message
            and str(reaction.emoji) in ["✅", "❌"]
        )

    try:
        reaction, user = await client.wait_for("reaction_add", timeout=30.0, check=check)

        if str(reaction.emoji) == "✅":
            # Proceed with registration
            registerAccount(discord_uid=message.author.id, steam_uid=steam_data['steamid'])
            await interaction.followup.send(f"Steam profile registered successfully!")
        else:
            await interaction.followup.send(f"Registration cancelled.")

    except asyncio.TimeoutError:
        await interaction.followup.send("No reaction received. Registration timed out.")

client.run(os.getenv("DISCORD_TOKEN"))