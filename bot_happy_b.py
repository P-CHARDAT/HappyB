import os
import discord
import asyncio
import datetime
from discord import app_commands
from discord.ext import commands, tasks
from datetime import datetime, timedelta, date
from dotenv import load_dotenv
from database import add_birthday, get_all_birthdays, get_birthday, update_birthday, delete_birthday


# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
BIRTHDAY_CHANNEL_ID = int(os.getenv("BIRTHDAY_CHANNEL_ID", 0))

if TOKEN is None:
    raise ValueError("❌ Bot token not found! Make sure you have a valid DISCORD_TOKEN in your .env file.")

if BIRTHDAY_CHANNEL_ID is None:
    raise ValueError("❌ BIRTHDAY_CHANNEL_ID not found! Make sure to set BIRTHDAY_CHANNEL_ID as an environment variable.")

# Bot setup
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree  # Slash commands

# Dictionary to store birthdays (in memory for now)
anniversaires = {}
reminded_users = set()  # Stores users who have already been reminded

# -------------------------------
# 🚀 Scheduled Task: Birthday Reminders
# -------------------------------
@tasks.loop(hours=24)  # Runs every 24 hours
async def birthday_reminder():
    """Check for upcoming birthdays and send reminders exactly 1 month and 2 weeks before."""
    today = datetime.now().date()
    reminder_1_month = today + timedelta(weeks=4)  # 1 month before
    reminder_2_weeks = today + timedelta(weeks=2)  # 2 weeks before

    channel = bot.get_channel(BIRTHDAY_CHANNEL_ID)
    if not channel:
        print("❌ Error: Birthday reminder channel not found.")
        return

    reminders = {"1_month": [], "2_weeks": []}
    reminded_users = {"1_month": set(), "2_weeks": set()}  # Store users who have received reminders


    for user_id, birthdate in anniversaires.items():
        birth_day, birth_month = map(int, birthdate.split("-"))

        # Convert birthday to this year
        birthday_this_year = datetime(today.year, birth_month, birth_day).date()

        # Check if the birthday is exactly 1 month ahead
        if birthday_this_year == reminder_1_month and user_id not in reminded_users["1_month"]:
            user = bot.get_user(user_id)
            user_mention = user.mention if user else f"Utilisateur inconnu ({user_id})"
            reminders["1_month"].append(f"🎂 **{user_mention}** fête son anniversaire dans **1 mois** 🎉")
            reminded_users["1_month"].add(user_id)  # Mark as reminded

        # Check if the birthday is exactly 2 weeks ahead
        if birthday_this_year == reminder_2_weeks and user_id not in reminded_users["2_weeks"]:
            user = bot.get_user(user_id)
            user_mention = user.mention if user else f"Utilisateur inconnu ({user_id})"
            reminders["2_weeks"].append(f"🎂 **{user_mention}** fête son anniversaire dans **2 semaines** 🎉")
            reminded_users["2_weeks"].add(user_id)  # Mark as reminded

    # Send messages if there are reminders
    if reminders["1_month"]:
        await channel.send("📅 **Rappel des anniversaires dans 1 mois !**\n" + "\n".join(reminders["1_month"]))
    
    if reminders["2_weeks"]:
        await channel.send("📅 **Rappel des anniversaires dans 2 semaines !**\n" + "\n".join(reminders["2_weeks"]))

# Start the reminder loop when bot is ready
@bot.event
async def on_ready():
    await bot.tree.sync()  # Sync slash commands with Discord
    print(f"✅ Bot is connected as {bot.user}")
    print(f"✅ Slash commands synchronized!")

    if not birthday_reminder.is_running():
        birthday_reminder.start()  # Start the reminder loop

# -------------------------------
# 🚀 Slash Command Group `/anniv`
# -------------------------------
class AnnivCommand(app_commands.Group):
    """Gère les anniversaires avec des sous-commandes"""

    @app_commands.command(name="add", description="Ajoute un anniversaire")
    @app_commands.describe(
        user="Mentionnez l'utilisateur dont vous voulez enregistrer l'anniversaire",
        date="Date au format JJ-MM"
    )
    async def add(self, interaction: discord.Interaction, user: discord.Member, date: str):
        """Ajoute un anniversaire pour un utilisateur"""
        try:
            datetime.strptime(date, "%d-%m")  # Vérifier le format de la date
        except ValueError:
            await interaction.response.send_message(
                "❌ Format de date invalide. Utilisation correcte : `JJ-MM` (ex: 10-02)", ephemeral=True)
            return

        add_birthday(user.id, date)
        reminded_users.discard(user.id)  # Reset the reminder for this user
        await interaction.response.send_message(f"✅ Anniversaire de {user.mention} ajouté pour le {date} !")


    @app_commands.command(name="list", description="Affiche la liste des anniversaires enregistrés")
    async def list_birthdays(self, interaction: discord.Interaction):
        """Affiche la liste des anniversaires enregistrés"""
        birthdays = get_all_birthdays()
        if not birthdays:
            await interaction.response.send_message("📅 Aucun anniversaire enregistré.", ephemeral=True)
            return
        
        today = datetime.now().date()
        sorted_birthdays = []
        for user_id, date in birthdays:
            day, month = map(int, date.split("-"))
            
            # Convert the birthday into a date object for this year
            birthday_this_year = datetime(today.year, month, day).date()

            # If the birthday has already passed this year, set it to next year
            if birthday_this_year < today:
                birthday_this_year = datetime(today.year + 1, month, day).date()
            
            # Calculate the number of days until the next birthday
            days_until = (birthday_this_year - today).days
            
            sorted_birthdays.append((user_id, date, days_until))

        # Sort by the number of days until the birthday
        sorted_birthdays.sort(key=lambda x: x[2])

        msg = "**📅 Liste des anniversaires (triés par date la plus proche) :**\n"
        for user_id, date, days_until in sorted_birthdays:
            user = interaction.guild.get_member(user_id)
            username = user.display_name if user else f"Utilisateur inconnu ({user_id})"
            msg += f"🎂 {username} : {date} (**dans {days_until} jours**)\n"

        await interaction.response.send_message(msg)


    @app_commands.command(name="for", description="Affiche l'anniversaire d'un utilisateur")
    @app_commands.describe(user="Mentionnez l'utilisateur dont vous voulez voir l'anniversaire")
    async def birthday_for(self, interaction: discord.Interaction, user: discord.Member):
        """Affiche l'anniversaire d'un utilisateur spécifique"""
        date = get_birthday(user.id)
        if date:
            await interaction.response.send_message(f"🎂 **{user.display_name}** a son anniversaire le **{anniversaires[user.id]}** !")
        else:
            await interaction.response.send_message(f"❌ Aucun anniversaire enregistré pour **{user.display_name}**.", ephemeral=True)


    @app_commands.command(name="update", description="Met à jour l'anniversaire d'un utilisateur")
    @app_commands.describe(
        user="Mentionnez l'utilisateur dont vous voulez mettre à jour l'anniversaire",
        date="Nouvelle date au format JJ-MM"
    )
    async def update_birthday(self, interaction: discord.Interaction, user: discord.Member, date: str):
        """Met à jour un anniversaire existant"""
        if get_birthday(user.id) is None:
            await interaction.response.send_message(f"❌ Aucun anniversaire enregistré pour **{user.display_name}**.", ephemeral=True)
            return

        try:
            datetime.strptime(date, "%d-%m")
        except ValueError:
            await interaction.response.send_message(
                "❌ Format de date invalide. Utilisation correcte : `JJ-MM` (ex: 10-02)", ephemeral=True)
            return

        update_birthday(user.id, date)
        reminded_users.discard(user.id)  # Reset reminder for updated user
        await interaction.response.send_message(f"✅ Anniversaire de {user.mention} mis à jour pour le **{date}** !")

    @app_commands.command(name="delete", description="Supprime l'anniversaire d'un utilisateur")
    @app_commands.describe(user="Mentionnez l'utilisateur dont vous voulez supprimer l'anniversaire")
    async def delete_birthday(self, interaction: discord.Interaction, user: discord.Member):
        """Supprime un anniversaire enregistré"""
        if get_birthday(user.id) is None:
            await interaction.response.send_message(f"❌ Aucun anniversaire enregistré pour **{user.display_name}**.", ephemeral=True)
            return
        
        delete_birthday(user.id)
        reminded_users.discard(user.id)  # Remove user from reminded list
        await interaction.response.send_message(f"🗑️ Anniversaire de **{user.display_name}** supprimé !")

    # @app_commands.command(name="remind", description="Teste le rappel des anniversaires")
    # async def remind(self, interaction: discord.Interaction):
    #     """Permet de tester immédiatement le rappel des anniversaires"""
    #     await birthday_reminder()  # Manually call the function
    #     await interaction.response.send_message("📅 Rappel des anniversaires testé !", ephemeral=True)

# Ajouter le groupe de commandes sous `/anniv`
tree.add_command(AnnivCommand(name="anniv"))

# -------------------------------
# 🚀 Start the bot
# -------------------------------
bot.run(TOKEN)
