import discord
from discord.ext import commands
import config
from command.verify import VerifyView, setup as setup_verify
from command.ticket import TicketView, CloseTicketView, setup as setup_ticket
from command.youtube import check_youtube

intents=discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot {bot.user} is online!")
    bot.add_view(VerifyView())
    bot.add_view(TicketView())
    bot.add_view(CloseTicketView())
    await bot.tree.sync()
    bot.loop.create_task(check_youtube(bot)) 

setup_verify(bot)
setup_ticket(bot)

bot.run(config.TOKEN)
