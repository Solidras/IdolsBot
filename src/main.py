import os

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = commands.Bot(command_prefix='*')


#### Bot commands ####

@bot.command()
async def ping(ctx):
    await ctx.message.delete()
    await ctx.send('Yup, I\'m awake.', delete_after=5)


#### Bot event handlers ####

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Unknown command.')
        return
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("You're not authorized to execute this command.")
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing arguments. !help for display help")
        return
    raise error


#### Utilities functions ####


#### Launch bot ####

bot.run(BOT_TOKEN)
