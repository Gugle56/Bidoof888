import discord
from discord.ext import commands
from discord import app_commands
import json
import random

TOKEN = "MTUwNDgzNjM3NjA5OTU1MzUyMg.G4-7DM.4FxJMcuPxZ43ISHZRWBE1rcLnR7RmX-zKqyNZU"

# =========================
# ตั้งค่า Bot
# =========================

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# โหลด / เซฟ Respect
# =========================

def load_data():
    try:
        with open("respect.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open("respect.json", "w") as f:
        json.dump(data, f, indent=4)

# =========================
# รายชื่อยศสี
# ใส่ชื่อยศที่มีในเซิร์ฟจริง
# =========================

roles = [
    {"name": "#ff0000", "rarity": "Common"},
    {"name": "#111314", "rarity": "Common"},
    {"name": "#54555", "rarity": "Uncommon"},
    {"name": "#fff800", "rarity": "Legendary"},
    {"name": "#009bff", "rarity": "Rare"},
    {"name": "#11404", "rarity": "Common"},
    {"name": "#d000ff", "rarity": "Epic"},
    {"name": "#23111", "rarity": "Common"},
    {"name": "#4dff00", "rarity": "Epic"},
    {"name": "#ff6d00", "rarity": "Rare"},
    {"name": "#01101", "rarity": "Common"},
    {"name": "#000bff", "rarity": "Epic"},
    {"name": "#ff009e", "rarity": "Legendary"},
    {"name": "#00ff8a", "rarity": "Rare"},
    {"name": "#012183", "rarity": "Uncommon"}
]

# =========================
# Bot Ready
# =========================

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"ออนไลน์เป็น {bot.user}")

# =========================
# /give
# =========================

@bot.tree.command(name="give", description="แจก respect")
@app_commands.describe(user="คนที่จะได้รับ respect")
async def give(interaction: discord.Interaction, user: discord.Member):

    # เช็คแอดมิน
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ คำสั่งนี้ใช้ได้เฉพาะแอดมิน",
            ephemeral=True
        )
        return

    data = load_data()

    user_id = str(user.id)

    if user_id not in data:
        data[user_id] = 0

    data[user_id] += 1

    save_data(data)

    await interaction.response.send_message(
        f"✨ give 1 respect to {user.mention}"
    )

# =========================
# /respect
# =========================

@bot.tree.command(name="respect", description="ดูจำนวน respect")
@app_commands.describe(user="คนที่ต้องการดู")
async def respect(interaction: discord.Interaction, user: discord.Member = None):

    data = load_data()

    target = user if user else interaction.user

    user_id = str(target.id)

    amount = data.get(user_id, 0)

    embed = discord.Embed(
        title="🙏 Respect",
        description=f"{target.mention} มี respect ทั้งหมด `{amount}`",
        color=discord.Color.blue()
    )

    await interaction.response.send_message(embed=embed)

# =========================
# /pray
# =========================

@bot.tree.command(name="pray", description="สุ่มยศสี")
async def pray(interaction: discord.Interaction):

    data = load_data()

    user_id = str(interaction.user.id)

    if data.get(user_id, 0) <= 0:
        await interaction.response.send_message(
            "❌ คุณมี respect ไม่พอ",
            ephemeral=True
        )
        return

    # ลบ respect 1
    data[user_id] -= 1
    save_data(data)

    # สุ่มยศ
    selected = random.choice(roles)

    role = discord.utils.get(
        interaction.guild.roles,
        name=selected["name"]
    )

    if role is None:
        await interaction.response.send_message(
            f"❌ ไม่เจอยศ {selected['name']}"
        )
        return

    # ลบยศสีเก่า
    for r in roles:
        old_role = discord.utils.get(
            interaction.guild.roles,
            name=r["name"]
        )

        if old_role in interaction.user.roles:
            await interaction.user.remove_roles(old_role)

    # เพิ่มยศใหม่
    await interaction.user.add_roles(role)

    # Embed
    embed = discord.Embed(
        title="🙏 PRAY RESULT",
        color=role.color
    )

    embed.add_field(
        name="ได้รับยศ",
        value=role.mention,
        inline=False
    )

    embed.add_field(
        name="ระดับความหายาก",
        value=selected["rarity"],
        inline=False
    )

    embed.set_footer(
        text=f"เหลือ respect {data[user_id]}"
    )

    await interaction.response.send_message(embed=embed)

# =========================

bot.run(TOKEN)