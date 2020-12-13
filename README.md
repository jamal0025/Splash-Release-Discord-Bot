# Splash Release Discord Bot
 A discord bot which emulates the 'splash' release type in discord with some customizable features

![Alt Text](https://i.imgur.com/iYw3Qfv.gif)

### Prerequisites
- Python 3+
- Discord.py & Asyncio (`pip install -r requirements.txt`)

### Getting Started
- Edit `settings.json` and enter all appropriate values (keep as string)
- (optional) Edit command prefix on line 17. By default it is `>`

### How To Use
- Type `>screate` to start the creation process. Please note that this is a role-exclusive command.
- Enter the prize name. The first letter of each word is auto-capitalized.
- Enter the price of the prize. Remember currency symbol if not free as it is not auto included.
- Enter the number of winners/stock (Integer).
- Select whether or not to allow more users than stock avaliable to pass the splash (This is overwritten as false if the option to wait for staff DM is selected).
- Tag the channel where you want the splash embed to display (Tag channel or use `<#CHANNEL_ID>`).
- Select what message is given to users who pass splash and follow the prompt.
- Confirm creation by typing `yes`
