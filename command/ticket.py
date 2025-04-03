import discord
from discord import app_commands
import config

LOG_CHANNEL_ID = config.LOG_CHANNEL_ID
ADMIN_ROLE_ID = config.ADMIN_ROLE_ID
CATEGORY_SUPPORT_ID = config.CATEGORY_SUPPORT_ID
CATEGORY_APPEAL_ID = config.CATEGORY_APPEAL_ID
CATEGORY_YT_ID = config.CATEGORY_YT_ID

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="チケットの種類を選んでください",
        custom_id="ticket_select",
        options=[
            discord.SelectOption(label="サポート", description="サポート用のチケットを作成", emoji="🛠"),
            discord.SelectOption(label="報告", description="ユーザー報告用のチケットを作成", emoji="🚨"),
            discord.SelectOption(label="YTランク", description="YouTubeランク申請用のチケットを作成", emoji="🎥"),
        ],
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        category_map = {
            "サポート": (CATEGORY_SUPPORT_ID, "サポートチケットが作成されました！"),
            "報告": (CATEGORY_APPEAL_ID, "報告チケットが作成されました！"),
            "YTランク": (CATEGORY_YT_ID, "チャンネルURLと証拠画像を送信してください"),
        }

        selected_option = select.values[0]
        category_id, ticket_message = category_map[selected_option]

        category = interaction.guild.get_channel(category_id)
        if not category:
            await interaction.response.send_message("チケットカテゴリが見つかりません！管理者に連絡してください。", ephemeral=True)
            return

        ticket_name = f"ticket-{interaction.user.name.lower().replace(' ', '-')}"
        
        existing_channel = discord.utils.get(interaction.guild.text_channels, name=ticket_name)
        if existing_channel:
            await interaction.response.send_message("すでに開いているチケットがあります！", ephemeral=True)
            return
        
        admin_role = interaction.guild.get_role(ADMIN_ROLE_ID)
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        ticket_channel = await interaction.guild.create_text_channel(name=ticket_name, category=category, overwrites=overwrites)

        view = CloseTicketView()
        embed = discord.Embed(title="🎫 チケット", description=ticket_message, color=discord.Color.green())
        embed.add_field(name="ユーザー", value=interaction.user.mention, inline=False)
        await ticket_channel.send(embed=embed, view=view)
        await interaction.response.send_message(f"{ticket_channel.mention} にチケットを作成しました！", ephemeral=True)

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="チケットを閉じる", style=discord.ButtonStyle.red, custom_id="close_ticket_button")
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        
        if not log_channel:
            await interaction.response.send_message("ログチャンネルが見つかりません！管理者に連絡してください。", ephemeral=True)
            return

        embed = discord.Embed(title="🎫┃チケットが閉じられました", description=f"{interaction.channel.name} が閉じられました。", color=discord.Color.red())
        embed.add_field(name="閉じたユーザー", value=interaction.user.mention, inline=False)
        await log_channel.send(embed=embed)
        await interaction.response.send_message("チケットを閉じます...", ephemeral=True)
        await interaction.channel.delete()

async def ticket_command(interaction: discord.Interaction):
    admin_role = interaction.guild.get_role(ADMIN_ROLE_ID)
    if admin_role not in interaction.user.roles:
        await interaction.response.send_message("このコマンドを実行する権限がありません！", ephemeral=True)
        return

    embed = discord.Embed(
        title="🎫 チケット作成",
        description="以下のメニューからチケットの種類を選んでください！",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed, view=TicketView())

def setup(bot):
    bot.tree.command(name="ticket", description="チケットメニューを表示")(ticket_command)
