import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os

# .envファイルを読み込む
load_dotenv()

# 環境変数から設定を取得
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
MUSIC_FOLDER = os.getenv("MUSIC_FOLDER_PATH")

# ボットの設定
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# スラッシュコマンドのセットアップ
class MusicBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="join", description="ボイスチャンネルに参加します。")
    async def join(self, interaction: discord.Interaction):
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            await channel.connect()
            await interaction.response.send_message("ボイスチャンネルに接続しました！")
        else:
            await interaction.response.send_message("ボイスチャンネルに接続してください。", ephemeral=True)

    @app_commands.command(name="play", description="音楽を再生します。ファイル名を指定してください。")
    async def play(self, interaction: discord.Interaction, filename: str):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        file_path = os.path.join(MUSIC_FOLDER, filename)  # 環境変数からフォルダを取得

        if voice_client and voice_client.is_connected():
            if os.path.isfile(file_path):
                voice_client.stop()  # 再生中の音楽を停止
                voice_client.play(discord.FFmpegPCMAudio(file_path))
                await interaction.response.send_message(f"再生中: {filename}")
            else:
                await interaction.response.send_message("指定されたファイルが見つかりません。", ephemeral=True)
        else:
            await interaction.response.send_message("ボットがボイスチャンネルに接続していません。", ephemeral=True)

    @app_commands.command(name="leave", description="ボイスチャンネルから退出します。")
    async def leave(self, interaction: discord.Interaction):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()
            await interaction.response.send_message("ボイスチャンネルから切断しました！")
        else:
            await interaction.response.send_message("ボイスチャンネルに接続していません。", ephemeral=True)

async def setup(bot):
    await bot.add_cog(MusicBot(bot))
    await bot.tree.sync()  # スラッシュコマンドをサーバーに同期

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

bot.run(TOKEN)
