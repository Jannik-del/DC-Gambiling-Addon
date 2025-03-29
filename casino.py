import nextcord
from nextcord.ext import commands
import random
import json
import os


class Casino(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.data_file = "casino_data.json"
        self.role_permissions_file = "role_permissions.json"
        self.load_data()
        self.load_permissions()

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as file:
                self.data = json.load(file)
        else:
            self.data = {}

    def save_data(self):
        with open(self.data_file, "w") as file:
            json.dump(self.data, file, indent=4)

    def load_permissions(self):
        if os.path.exists(self.role_permissions_file):
            with open(self.role_permissions_file, "r") as file:
                self.role_permissions = json.load(file)
        else:
            self.role_permissions = {}

    def save_permissions(self):
        with open(self.role_permissions_file, "w") as file:
            json.dump(self.role_permissions, file, indent=4)

    def get_euro(self, user_id):
        return self.data.get(str(user_id), 100)

    def update_euro(self, user_id, amount):
        self.data[str(user_id)] = self.get_euro(user_id) + amount
        self.save_data()

    def has_permission(self, member):
        for role in member.roles:
            if str(role.id) in self.role_permissions:
                return True
        return False

    @nextcord.slash_command(name="casino", description="Spiele an der Slot-Maschine")
    async def casino(self, interaction: nextcord.Interaction, einsatz: int):
        if einsatz < 10 or einsatz > 999:
            await interaction.response.send_message("Bitte setze zwischen 10 und 999€.", ephemeral=True)
            return

        user_id = interaction.user.id
        if self.get_euro(user_id) < einsatz:
            await interaction.response.send_message("Du hast nicht genug €!", ephemeral=True)
            return

        slots = ["🍒", "🍋", "🍊", "🍉", "⭐", "💎"]
        result = [random.choice(slots) for _ in range(3)]
        win = result[0] == result[1] == result[2]
        euros = einsatz * 2 if win else -einsatz
        self.update_euro(user_id, euros)

        embed = nextcord.Embed(
            title="🎰 Slot-Maschine 🎰",
            description=f"{' '.join(result)}\n{'🎉 Gewinn! (+{}€) 🎉'.format(einsatz * 2) if win else 'Leider verloren! (-{}€)'.format(einsatz)}\nAktuelles Guthaben: {self.get_euro(user_id)}€",
            color=nextcord.Color.green() if win else nextcord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

    @nextcord.slash_command(name="glücksrad", description="Drehe das Glücksrad")
    async def glücksrad(self, interaction: nextcord.Interaction, einsatz: int):
        if einsatz < 10 or einsatz > 999:
            await interaction.response.send_message("Bitte setze zwischen 10 und 999€.", ephemeral=True)
            return

        user_id = interaction.user.id
        if self.get_euro(user_id) < einsatz:
            await interaction.response.send_message("Du hast nicht genug €!", ephemeral=True)
            return

        outcomes = [-einsatz, -einsatz // 2, 0, einsatz, einsatz * 2, einsatz * 5]
        result = random.choice(outcomes)
        self.update_euro(user_id, result)

        embed = nextcord.Embed(
            title="🎡 Glücksrad 🎡",
            description=f"Das Glücksrad wurde gedreht! \n{'🎉 Gewinn! (+{}€) 🎉'.format(result) if result > 0 else 'Leider verloren! (-{}€)'.format(abs(result))}\nAktuelles Guthaben: {self.get_euro(user_id)}€",
            color=nextcord.Color.green() if result > 0 else nextcord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

    @nextcord.slash_command(name="pay", description="Überweise Geld an einen anderen Spieler")
    async def pay(self, interaction: nextcord.Interaction, amount: int, user: nextcord.Member):
        if amount <= 0:
            await interaction.response.send_message("Der Betrag muss positiv sein.", ephemeral=True)
            return

        user_id = interaction.user.id
        if self.get_euro(user_id) < amount:
            await interaction.response.send_message("Du hast nicht genug €!", ephemeral=True)
            return

        self.update_euro(user_id, -amount)
        self.update_euro(user.id, amount)
        await interaction.response.send_message(
            f"{interaction.user.mention} hat {amount}€ an {user.mention} gesendet. Neues Guthaben: {self.get_euro(user_id)}€.")

    @nextcord.slash_command(name="euro", description="Überprüfe dein aktuelles Guthaben")
    async def euro(self, interaction: nextcord.Interaction):
        user_id = interaction.user.id
        await interaction.response.send_message(f"Du hast aktuell {self.get_euro(user_id)}€.")

    @nextcord.slash_command(name="euro_add", description="Füge Euro hinzu")
    async def euro_add(self, interaction: nextcord.Interaction, user: nextcord.Member, amount: int):
        if amount <= 0:
            await interaction.response.send_message("Der Betrag muss positiv sein.", ephemeral=True)
            return

        self.update_euro(user.id, amount)
        await interaction.response.send_message(f"{amount}€ wurden {user.mention} hinzugefügt.")

    @nextcord.slash_command(name="euro_set", description="Setze das Guthaben eines Spielers")
    async def euro_set(self, interaction: nextcord.Interaction, user: nextcord.Member, amount: int):
        if amount < 0:
            await interaction.response.send_message("Der Betrag darf nicht negativ sein.", ephemeral=True)
            return

        self.data[str(user.id)] = amount
        self.save_data()
        await interaction.response.send_message(f"Das Guthaben von {user.mention} wurde auf {amount}€ gesetzt.")

    @nextcord.slash_command(name="euro_remove", description="Entferne Euro vom Guthaben eines Spielers")
    async def euro_remove(self, interaction: nextcord.Interaction, user: nextcord.Member, amount: int):
        if amount <= 0:
            await interaction.response.send_message("Der Betrag muss positiv sein.", ephemeral=True)
            return

        self.update_euro(user.id, -amount)
        await interaction.response.send_message(f"{amount}€ wurden von {user.mention} entfernt.")


def setup(client):
    client.add_cog(Casino(client))
