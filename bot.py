import os
import discord
from discord.ext import commands
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import math
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('token')
CHANNEL_ID = int(os.getenv('id'))  # Ensure this is an integer

# Initialize bot with command prefix
bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())

# Function to get the size of the video file
def get_file_size(file_path):
    return os.path.getsize(file_path) / (1024 * 1024)  # Size in MB

# Function to split the video into parts if it exceeds the size limit
def split_video(file_path, size_limit_mb=20):
    from moviepy.editor import VideoFileClip

    clips = []
    video = VideoFileClip(file_path)
    duration = video.duration
    num_parts = math.ceil(get_file_size(file_path) / size_limit_mb)
    part_duration = duration / num_parts

    for i in range(num_parts):
        start_time = i * part_duration
        end_time = start_time + part_duration
        part_path = f"{file_path}_part_{i + 1}.mp4"
        ffmpeg_extract_subclip(file_path, start_time, end_time, targetname=part_path)
        clips.append(part_path)

    video.close()
    return clips

# Function to send video files to the Discord channel
async def send_videos(channel, folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".mp4"):
            file_path = os.path.join(folder_path, filename)
            if get_file_size(file_path) > 23:
                parts = split_video(file_path)
                for part in parts:
                    await channel.send(file=discord.File(part))
                    os.remove(part)  # Delete the part file after sending
            else:
                await channel.send(file=discord.File(file_path))
            os.remove(file_path)  # Delete the original file after sending

# Event when bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    channel = bot.get_channel(CHANNEL_ID)
    folder_path = './rec'  # Replace with the path to your videos folder
    await send_videos(channel, folder_path)
    await bot.close()  # Close the bot after sending videos

# Command to add a message to wanted.txt
@bot.command(name='addmsg')
async def add_message(ctx, *, message: str):
    with open('wanted.txt', 'a') as f:
        f.write(message + '\n')
    await ctx.send(f'Message added to wanted.txt: {message}')

if __name__ == '__main__':
    bot.run(TOKEN)
