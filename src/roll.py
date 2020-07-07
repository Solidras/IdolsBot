import secrets
import asyncio
from datetime import datetime

import discord
from discord.ext import commands

from database import DatabaseIdol, DatabaseDeck


class Roll(commands.Cog):
    def __init__(self, bot):
        """Initial the cog with the bot."""
        self.bot = bot

    #### Commands ####

    @commands.command(description='Roll a random idom and get the possibility to claim it.')
    async def roll(self, ctx):
        minutes = min_until_next_roll(ctx.guild.id, ctx.author.id)
        if minutes != 0:
            await ctx.send(f'You cannot roll right now. The next roll reset is in {minutes} minutes.')
            return

        id_idol = DatabaseIdol.get().get_random_idol_id()
        idol = DatabaseIdol.get().get_idol_information(id_idol)
        if not idol:
            ctx.send("An error occurred. If this message is exceptional, "
                     "please try again. Otherwise, contact the administrator.")

        # Update roll information in database
        DatabaseDeck.get().update_last_roll(ctx.guild.id, ctx.author.id)
        user_nb_rolls = DatabaseDeck.get().get_nb_rolls(ctx.guild.id, ctx.author.id)
        DatabaseDeck.get().set_nb_rolls(ctx.guild.id, ctx.author.id, user_nb_rolls + 1)

        max_rolls = DatabaseDeck.get().get_rolls_per_hour(ctx.guild.id)
        if max_rolls - user_nb_rolls - 1 == 2:
            await ctx.send(f'**{ctx.author.name}**, 2 uses left.')

        embed = discord.Embed(title=idol['name'], description=idol['group'], colour=secrets.randbelow(0xffffff))
        embed.set_image(url=idol['image'])

        id_owner = DatabaseDeck.get().idol_belongs_to(ctx.guild.id, id_idol)

        if id_owner:
            owner = ctx.guild.get_member(id_owner)

            # Could be None if the user left the server
            if owner:
                embed.set_footer(icon_url=owner.avatar_url,
                                 text=f'Belongs to {owner.name if not owner.nick else owner.nick}')

        msg = await ctx.send(embed=embed)

        # Cannot claim if idol already claim
        if id_owner:
            return

        emoji = '\N{TWO HEARTS}'
        await msg.add_reaction(emoji)

        def check(reaction, user):
            return user != self.bot.user and str(reaction.emoji) == emoji and reaction.message.id == msg.id

        is_claimed_or_timeout = False
        claim_timeout = DatabaseDeck.get().get_server_configuration(ctx.guild.id)["time_to_claim"]

        while not is_claimed_or_timeout:
            try:
                _, user = await self.bot.wait_for('reaction_add', timeout=claim_timeout, check=check)
            except asyncio.TimeoutError:
                await msg.clear_reaction(emoji)
                is_claimed_or_timeout = True
            else:
                is_claimed_or_timeout = await claim(ctx, user, idol, msg, embed)


#### Utilities functions ####

async def claim(ctx, user, idol, msg, embed):
    """Add idol to user's deck if he can claim."""
    id_server = ctx.guild.id
    can_claim = False

    last_claim = DatabaseDeck.get().get_last_claim(id_server, user.id)

    time_until_claim = 0

    # User never claimed an idol
    if not last_claim:
        can_claim = True
    else:
        claim_interval = DatabaseDeck.get().get_server_configuration(id_server)['claim_interval']
        date_last_claim = datetime.strptime(last_claim, '%Y-%m-%d %H:%M:%S')
        minute_since_last_claim = divmod((datetime.now() - date_last_claim).seconds, 60)[0]

        if minute_since_last_claim >= claim_interval:
            can_claim = True
        else:
            time_until_claim = claim_interval - minute_since_last_claim

    username = user.name if user.nick is None else user.nick
    if can_claim:
        DatabaseDeck.get().add_to_deck(id_server, idol['id'], user.id)
        await ctx.send(f'{username} claims {idol["name"]}!')

        embed.set_footer(icon_url=user.avatar_url, text=f'Belongs to {username}')
        await msg.edit(embed=embed)
    else:
        time = divmod(time_until_claim, 60)
        await ctx.send(f'{username}, you can\'t claim right now. '
                       f'Please wait {str(time[0])} h {str(time[1])} min.')

    return can_claim


def min_until_next_roll(id_server, id_user):
    """Return minutes until next roll (0 if the user can roll now)."""
    last_roll = DatabaseDeck.get().get_last_roll(id_server, id_user)

    if not last_roll:
        return 0

    last_roll = datetime.strptime(last_roll, '%Y-%m-%d %H:%M:%S')
    now = datetime.now()

    # If a new hour began
    if now.date() != last_roll.date() or (now.date() == last_roll.date() and now.hour != last_roll.hour):
        DatabaseDeck.get().set_nb_rolls(id_server, id_user, 0)
        return 0

    max_rolls = DatabaseDeck.get().get_rolls_per_hour(id_server)
    user_nb_rolls = DatabaseDeck.get().get_nb_rolls(id_server, id_user)

    if user_nb_rolls < max_rolls:
        return 0
    else:
        return 60 - now.minute
