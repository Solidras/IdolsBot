import discord
import asyncio
import secrets

from discord.ext import commands
from database import DatabaseIdol


class Information(commands.Cog):
    def __init__(self, bot):
        """Initial the cog with the bot."""
        self.bot = bot

    #### Commands ####

    @commands.command(aliases=['info'], description='Show information about an idol. '
                                                    'Please enter the name of the idol '
                                                    'with group (optional). Please add ""'
                                                    'if it has spaces\n'
                                                    'Take the first corresponding idol.'
                                                    'See list command for all idols.\n'
                                                    'Example:\n'
                                                    '   *info heejin loona'
                                                    '   *info joy "red velvet"')
    async def information(self, ctx, name, group=None):
        # TODO: add more information to the card (all groups...)
        name = name.strip()

        if group:
            group = group.strip()

        id_idol = None

        if group:
            id_idol = DatabaseIdol.get().get_idol_group_id(name, group)
        else:
            ids = DatabaseIdol.get().get_idol_ids(name)
            if ids:
                id_idol = ids[0]

        if not id_idol:
            msg = f'I searched everywhere for **{name}**'
            if group:
                msg += f' in the group *{group}*'
            msg += ' and I couldn\'t find anything.\nPlease check the command.'
            await ctx.send(msg)
            return

        idol = DatabaseIdol.get().get_idol_information(id_idol)

        # TODO: Add message if idol belongs to a member
        embed = discord.Embed(title=idol['name'], description=idol['group'], colour=secrets.randbelow(0xffffff))

        # TODO: add pages to go through images
        embed.set_image(url=idol['image'])

        await ctx.send(embed=embed)

    @commands.command(description='List all idols with its name')
    async def list(self, ctx, *, name):
        ids = DatabaseIdol.get().get_idol_ids(name)

        description = '' if ids else 'No idols found'
        for id_idol in ids:
            idol = DatabaseIdol.get().get_idol_information(id_idol)
            description += f'**{idol["name"]}** *{idol["group"]}*\n'

        embed = discord.Embed(title=f'{name} idols', description=description)
        await ctx.send(embed=embed)
