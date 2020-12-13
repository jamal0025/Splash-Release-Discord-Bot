import discord
import asyncio
import json
import random
from discord.ext import commands
intents = discord.Intents.all()
client = discord.Client(intents=intents)

def load_settings():
    with open("settings.json", "r") as file:
        config = file.read()
    file.close()
    return json.loads(config)


SETTINGS = load_settings()
bot = commands.Bot(command_prefix='>', intents=intents)
bot.remove_command('help') # Allows you to replace the help command with custom embed

@bot.event
async def on_ready():
    print("Discord Splash Release Bot | Online")


@bot.command(pass_context=True)
async def help(ctx):
    global SETTINGS

    # Filters so only staff users can utilize
    member = ctx.message.author
    for role in member.roles:
        if str(role.id) == SETTINGS["staff_role_id"]: # If user has staff role
            embed=discord.Embed(title=str('Splash release creator'),color=0x36ccf8)
            embed.add_field(name="Commands", value="`>screate`    Creates a new splash release.", inline=True)
            embed.set_footer(text="@thecopbuddy")
            await ctx.message.channel.send(embed=embed)
            break




@bot.command(pass_context=True)
async def screate(ctx):
    global SETTINGS

    async def collect_valid_entries(ctx):
        valid_entries = []
        invalid_entries = []

        for user in ctx.guild.members:
            # Cycle each member in group
            user_roles = []
            valid = True
            for roles in user.roles:
                user_roles.append(str(roles.id))
            for r in SETTINGS["prohibited_role_ids"]:
                if r in user_roles:
                    valid = False
            if valid and (SETTINGS["member_role_id"] in user_roles):
                valid_entries.append(user.id)
            else:
                invalid_entries.append(user.id)

        return valid_entries

    async def notify_winner(ctx, selected_user, release_info):
        # Send logs of valid winners to admin channel for cross-reference
        admin_logs = discord.utils.get(ctx.guild.text_channels, id=int(SETTINGS["admin_channel_id"])) # Change to YOUR admin logs channel
        await admin_logs.send(f"<@{selected_user}> has successfully passed splash to a chance to purchase {release_info['title']}")
        winner_object = ctx.guild.get_member(int(selected_user))

        # Direct message the winner based on splash configuration

        if int(release_info['method']) == 1:  # Gain access to hidden channel
            winners_channel = discord.utils.get(ctx.guild.text_channels, id=int(release_info['winner_channel']))
            await winners_channel.set_permissions(winner_object, send_messages=False, read_messages=True, add_reactions=False, embed_links=True, attach_files=False, read_message_history=True, external_emojis=False)

            embed=discord.Embed(description=f"Congrats! You have passed splash and now have the opportunity to purchase **{release_info['title']}**. Please head to [**#{winners_channel}**](https://discord.com/channels/{ctx.guild.id}/{release_info['winner_channel']}/) to proceed.\n\nYou have 3 minutes to purchase and copies are not reserved. All sales are final.", color=0x9ec8ff)
            await winner_object.send(embed=embed)
            await asyncio.sleep(180)
            await winners_channel.set_permissions(winner_object, send_messages=False, read_messages=False, add_reactions=False, embed_links=True, attach_files=False, read_message_history=True, external_emojis=False) # Removes access to channel after 3 minutes (180 seconds)

        elif int(release_info['method']) == 2:  # Wait for staff DM
            embed=discord.Embed(description=f"Congrats! You have passed splash and have secured **{release_info['title']}** for purchase. Please stand by for a staff DM.", color=0x9ec8ff)
            await winner_object.send(embed=embed)

        else: # DM them password link
            embed=discord.Embed(description=f"Congrats! You have passed and now have the opportunity to purchase **{release_info['title']}**. Please head to *{release_info['prize_url']}* to proceed.\n\nCopies are not reserved and all sales are final.", color=0x9ec8ff)
            await winner_object.send(embed=embed)

    async def start_release(ctx, valid_entries, release_info):
        # Send embed to display channel to alert on creation/oos
        passed_users = []
        channel = discord.utils.get(ctx.guild.text_channels, id=int(release_info['display_channel']))

        embed=discord.Embed(title="SPLASH RELEASE HAS STARTED", description=f"You are currently in line to make the following purchase.", color=0x9ec8ff)
        embed.add_field(name='Information:', value=f"Product: **{release_info['title']}**\nPrice: **{release_info['price']}**\n\nIf you are selected, you will recieve a DM from the bot with instructions on how to proceed. Good luck!", inline=False)
        embed.set_thumbnail(url='https://i.imgur.com/tYpB6CM.gif')
        embed.set_footer(text="@thecopbuddy")
        release_display = await channel.send(embed=embed)

        if not (release_info['oversell_mode']) or (int(release_info['method']) == 2):
            print('\nSTARTING SALE WITH NO OVERSALE')
            pass_interval = float(release_info['time_length_minutes']) / int(release_info['max_winners'])  # 10 mins / 5 winners = chosen every 2 mins
            for _ in range(int(release_info['max_winners'])):
                await asyncio.sleep(pass_interval*60)
                print('Picking new winner')
                selected_user = random.choice(valid_entries)
                passed_users.append(selected_user)
                valid_entries.remove(selected_user)
                print('Randomly selected:',selected_user)
                await notify_winner(ctx, selected_user, release_info)

        else:
            print('\nSTARTING SALE WITH OVERSALE')
            pass_interval = float(release_info['time_length_minutes']) / (int(release_info['max_winners']) * 3) # Allows more users than stock avaliable to introduce raffle -> fcfs aspect. Users are also let into splash faster
            for _ in range((int(release_info['max_winners']) * 3)):
                await asyncio.sleep(pass_interval*60)
                print('Picking new winner')
                selected_user = random.choice(valid_entries)
                passed_users.append(selected_user)
                valid_entries.remove(selected_user)
                print('Randomly selected:',selected_user)
                await notify_winner(ctx, selected_user, release_info)


        embed=discord.Embed(title="SPLASH RELEASE HAS ENDED", description=f"Thank you for participating for the chance to purchase {release_info['title']}.\n\nThere is currently no stock remaining. Better luck next time!", color=0xf04771)
        #embed.add_field(name='Information:', value=f"Product: **{release_info['title']}**\nPrice: **{release_info['price']}**\n\nThere is currently no stock remaining. Better luck next time!", inline=False)
        embed.set_footer(text="@thecopbuddy")
        await release_display.edit(embed=embed)
        print('Release had ended')


    release_info = {
        'title': 'n/a',
        'price': 'n/a',
        'max_winners': 'n/a',
        'time_length_minutes': 'n/a',
        'display_channel': 'n/a',
        'method': 'n/a',
        'oversell_mode': True,
        'winner_channel': 'n/a',
        'prize_url': 'n/a',
    }

    # Add filter for only staff
    member = ctx.message.author
    for role in member.roles:
        if str(role.id) == SETTINGS["staff_role_id"]: # STAFF ROLE
            staff_user = True
            break
        else:
            staff_user = False

    if staff_user:
        await ctx.message.channel.send('What is the name of the prize being distributed?')
        try:
            msg = await bot.wait_for('message', timeout=30.0, check=lambda m: m.author == ctx.author and m.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.message.channel.send('Sorry, release creation has timed out!')
            print('Creation TIMEOUT')
            return
        else:
            release_info['title'] = (msg.content).title()
            print(f"Prize Name: {release_info['title']}")

        await ctx.message.channel.send('How much does the prize cost? (e.g $100 or free)')
        try:
            msg = await bot.wait_for('message', timeout=30.0, check=lambda m: m.author == ctx.author and m.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.message.channel.send('Sorry, release creation has timed out!')
            print('Creation TIMEOUT')
            return
        else:
            release_info['price'] = (msg.content).upper()
            print(f"Prize Fee: {release_info['price']}")

        await ctx.message.channel.send('How many winners should there be?')
        try:
            msg = await bot.wait_for('message', timeout=30.0, check=lambda m: m.author == ctx.author and m.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.message.channel.send('Sorry, release creation has timed out!')
            print('Creation TIMEOUT')
            return
        else:
            release_info['max_winners'] = (msg.content)
            print(f"# Of Winners: {release_info['max_winners']}")

        await ctx.message.channel.send('How long should this release last for? (in minutes)')
        try:
            msg = await bot.wait_for('message', timeout=30.0, check=lambda m: m.author == ctx.author and m.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.message.channel.send('Sorry, release creation has timed out!')
            print('Creation TIMEOUT')
            return
        else:
            release_info['time_length_minutes'] = (msg.content)
            print(f"Time Length of Release: {release_info['time_length_minutes']} minute(s)")


        await ctx.message.channel.send('Please select.\n[1] Continiously choose winners until release time is over.\n[2] Stop selecting winners once winner count has been reached.')
        try:
            msg = await bot.wait_for('message', timeout=30.0, check=lambda m: m.author == ctx.author and m.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.message.channel.send('Sorry, release creation has timed out!')
            print('Creation TIMEOUT')
            return
        else:
            if msg.content == '1':
                release_info['oversell_mode'] = True
                print(f"Oversell mode: {release_info['oversell_mode']}")
            else:
                release_info['oversell_mode'] = False
                print(f"Oversell mode: {release_info['oversell_mode']}")


        await ctx.message.channel.send('Tag the channel where you would like the splash information to appear:')
        try:
            msg = await bot.wait_for('message', timeout=30.0, check=lambda m: m.author == ctx.author and m.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.message.channel.send('Sorry, release creation has timed out!')
            print('Creation TIMEOUT')
            return
        else:
            temp = msg.content.split('>')[0]
            temp = temp.replace('!','')
            temp = temp.replace('#','')
            release_info['display_channel'] = temp.split('<')[1]
            print(f"Display Channel: {release_info['display_channel']}")

        await ctx.message.channel.send('How do you want winners to proceed?\n[1] Gain access to hidden channel\n[2] Tell them to wait for staff DM\n[3] Directly DM them the password link')
        try:
            msg = await bot.wait_for('message', timeout=30.0, check=lambda m: m.author == ctx.author and m.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.message.channel.send('Sorry, release creation has timed out!')
            print('Creation TIMEOUT')
            return
        else:
            release_info['method'] = int(msg.content)
            print(f"Claim prize method: {release_info['method']}")

        if release_info['method'] == 1:
            await ctx.message.channel.send("Tag the channel that you want the winners to gain access to:")
            try:
                msg = await bot.wait_for('message', timeout=30.0, check=lambda m: m.author == ctx.author and m.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.message.channel.send('Sorry, release creation has timed out!')
                print('Creation TIMEOUT')
                return
            else:
                temp = msg.content.split('>')[0]
                temp = temp.replace('!','')
                temp = temp.replace('#','')
                release_info['winner_channel'] = temp.split('<')[1]
                print(f"Channels for winner to view: {release_info['winner_channel']}")
        elif release_info['method'] == 3:
            await ctx.message.channel.send("What password link would you like DM'ed to the winners?")
            try:
                msg = await bot.wait_for('message', timeout=30.0, check=lambda m: m.author == ctx.author and m.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.message.channel.send('Sorry, release creation has timed out!')
                print('Creation TIMEOUT')
                return
            else:
                release_info['prize_url'] = (msg.content)
                print(f"Prize Password URL: {release_info['prize_url']}")
        else:
            await ctx.message.channel.send("Winners will be told to wait for a staff to DM them.")

        print('\n')
        confirmation_text = f"""Prize name: {release_info['title']}
Prize price: {release_info['price']}
Maximum winners: {release_info['max_winners']}
Lenght of release (m): {release_info['time_length_minutes']}
Channel to display info: <#{release_info['display_channel']}>
Distribution Method: {release_info['method']}
Channel for winners: <#{release_info['winner_channel']}>
URL to DM to winners: {release_info['prize_url']}

Please confirm these details by replying YES. After doing so, the release will begin."""

        await ctx.message.channel.send(confirmation_text)
        try:
            msg = await bot.wait_for('message', timeout=30.0, check=lambda m: m.author == ctx.author and m.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.message.channel.send('Sorry, release creation has timed out!')
            print('Creation TIMEOUT')
            return
        else:
            if (msg.content).upper() != 'YES':
                await ctx.message.channel.send('Release has been cancelled. You may start again.')
                print('Cancelled release.')
                return

            else:
                await ctx.message.channel.send(f"Starting release in <#{release_info['display_channel']}>...")

        valid_entries = await collect_valid_entries(ctx)
        await start_release(ctx, valid_entries, release_info)

    else:
        print('[create splash] not staff')



bot.run(SETTINGS["bot_token"])
