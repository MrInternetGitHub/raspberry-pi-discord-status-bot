import discord
import psutil
import time
import subprocess
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Replace 'YOUR_BOT_TOKEN' with your actual bot token from the .env file
BOT_TOKEN = os.getenv('BOT_TOKEN')
# Replace 'YOUR_CHANNEL_ID' with your actual channel ID from the .env file
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

# Thresholds for alerts
RAM_THRESHOLD = 90.0  # Send an alert if RAM usage exceeds 90%
CPU_THRESHOLD = 90.0  # Send an alert if CPU usage exceeds 90%
TEMP_THRESHOLD = 50.0  # Send an alert if CPU temperature exceeds 50°C

# Define the intents your bot will use
intents = discord.Intents.default()

# Explicitly enable the necessary intents for this bot
intents.typing = False
intents.presences = False

# Create the discord.Client instance
client = discord.Client(intents=intents)

# Function to get CPU temperature
def get_cpu_temperature():
    try:
        temp_output = subprocess.check_output(["vcgencmd", "measure_temp"]).decode("utf-8")
        cpu_temp = float(temp_output.strip().split('=')[1][:-2])
        return cpu_temp
    except Exception as e:
        print(f"Error reading CPU temperature: {e}")
        return None

# Function to get system information as an embed
def get_system_info_embed():
    ram_usage = psutil.virtual_memory().percent
    cpu_usage = psutil.cpu_percent()
    cpu_temp = get_cpu_temperature()

    # Convert uptime to different time units
    uptime_seconds = time.time() - psutil.boot_time()
    uptime_minutes = uptime_seconds // 60
    uptime_hours = uptime_minutes // 60
    uptime_days = uptime_hours // 24
    uptime_months = uptime_days // 30  # Approximation: 30 days in a month
    uptime_years = uptime_months // 12  # Approximation: 12 months in a year

    system_info_embed = discord.Embed(
        title="System Status",
        description="Current status of the Raspberry Pi:",
        color=0x00FF00  # You can change the color code as you like
    )
    system_info_embed.add_field(name="📱RAM Usage", value=f"{ram_usage:.2f}%", inline=True)
    system_info_embed.add_field(name="💻CPU Usage", value=f"{cpu_usage:.2f}%", inline=True)
    system_info_embed.add_field(name="⏱️Uptime", value=f"{uptime_years:.0f} years, {uptime_months % 12:.0f} months, "
                                                     f"{uptime_days % 30:.0f} days, {uptime_hours % 24:.0f} hours, "
                                                     f"{uptime_minutes % 60:.0f} minutes", inline=False)
    system_info_embed.add_field(name="🌡️CPU Temperature", value=f"{cpu_temp:.2f}°C", inline=True)
    
    # Display the current time in the footer of the embed
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    system_info_embed.set_footer(text=f"Current Time: {current_time}")

    # Create alert messages if any of the thresholds are exceeded
    alerts = []
    if ram_usage > RAM_THRESHOLD:
        alerts.append(f"<@924561350716444733> 🚨 ALERT: RAM usage is at {ram_usage:.2f}%")
    if cpu_usage > CPU_THRESHOLD:
        alerts.append(f"<@924561350716444733> 🚨 ALERT: CPU usage is at {cpu_usage:.2f}%")
    if cpu_temp and cpu_temp > TEMP_THRESHOLD:
        alerts.append(f"<@924561350716444733> 🚨 ALERT: CPU temperature is at {cpu_temp:.2f}°C")

    return system_info_embed, alerts

# Main event to run the bot
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    while True:
        system_info_embed, alerts = get_system_info_embed()
        channel = client.get_channel(CHANNEL_ID)
        
        # Send the system status as an embed
        await channel.send(embed=system_info_embed)
        
        # Check and send alerts if necessary
        for alert in alerts:
            await channel.send(alert)
        
        await asyncio.sleep(60)  # Wait for 1 minute before the next update

# Main function to run the bot
def run_bot():
    client.run(BOT_TOKEN)

if __name__ == '__main__':
    run_bot()
