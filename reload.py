import nextcord
from nextcord.ext import commands

class Reload(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nextcord.slash_command(name="reload", description="Lädt alle Cogs neu.")
    async def reload(self, interaction: nextcord.Interaction):
        """
        Reloads all cogs for the bot.
        """
        reloaded_cogs = []
        failed_cogs = []

        for extension in list(self.client.extensions.keys()):
            try:
                self.client.reload_extension(extension)
                reloaded_cogs.append(extension)
            except Exception as e:
                failed_cogs.append(f"{extension}: {e}")

        if reloaded_cogs:
            success_message = f"✅ Erfolgreich neu geladen:\n- " + "\n- ".join(reloaded_cogs)
        else:
            success_message = "⚠️ Keine Cogs wurden neu geladen."

        if failed_cogs:
            failure_message = f"❌ Fehler beim Neuladen:\n- " + "\n- ".join(failed_cogs)
        else:
            failure_message = "🎉 Alle Cogs wurden erfolgreich neu geladen!"

        await interaction.response.send_message(
            embed=nextcord.Embed(
                title="🔄 Reload Command",
                description=f"{success_message}\n\n{failure_message}",
                color=nextcord.Color.green() if not failed_cogs else nextcord.Color.red(),
            ),
            ephemeral=True
        )

def setup(client):
    client.add_cog(Reload(client))