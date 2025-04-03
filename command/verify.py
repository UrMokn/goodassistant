import discord
from discord import app_commands
import config

REGULAR_ROLE_ID = config.REGULAR_ROLE_ID

class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="認証する", style=discord.ButtonStyle.green, custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        role = interaction.guild.get_role(REGULAR_ROLE_ID)
        if role is None:
            await interaction.followup.send("エラー: 指定されたロールが見つかりません。", ephemeral=True)
            return

        if role in interaction.user.roles:
            await interaction.followup.send("すでに認証済みです。", ephemeral=True)
            return

        await interaction.user.add_roles(role)
        await interaction.followup.send("認証が完了しました！", ephemeral=True)

async def verify_command(interaction: discord.Interaction):
    admin_role = interaction.guild.get_role(ADMIN_ROLE_ID)
    if admin_role not in interaction.user.roles:
        await interaction.response.send_message("このコマンドを実行する権限がありません！", ephemeral=True)
        return

    embed = discord.Embed(title="認証", description="ボタンを押して認証してください。", color=discord.Color.blue())
    await interaction.channel.send(embed=embed, view=VerifyView())
    await interaction.response.send_message("認証パネルを作成しました！", ephemeral=True)

def setup(bot):
    bot.tree.command(name="verify", description="認証パネルを作成します")(verify_command)
