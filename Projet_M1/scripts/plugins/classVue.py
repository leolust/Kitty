import discord
from discord import ui

class VueKitty(ui.View):
    def __init__(self, pages):
        super().__init__()
        self.pages = pages
        self.page_courante = 0

    @ui.button(label="Précédent", style=discord.ButtonStyle.secondary)
    async def bouton_precedent(self, interaction: discord.Interaction, button: ui.Button):
        self.page_courante = len(self.pages) - 1 if self.page_courante == 0 else self.page_courante - 1
        await interaction.response.edit_message(content=self.pages[self.page_courante], view=self)

    @ui.button(label="Suivant", style=discord.ButtonStyle.secondary)
    async def bouton_suivant(self, interaction: discord.Interaction, button: ui.Button):
        self.page_courante = 0 if self.page_courante == len(self.pages) - 1 else self.page_courante + 1
        await interaction.response.edit_message(content=self.pages[self.page_courante], view=self)