import discord
from discord.ext import commands
import sys
from asyncio import sleep
import csv
from bot_model.mybot import *
from bot_model.utils import * 


'''
    So how will this bot work in terms of Discord?
    
    Before we do that, let's understand how I want the bot to work
        - Need a way for users to let me know if a question was misclassified
            - Use !misclassified to use add the last question to the database. 
'''
raymond_bot = interview_bot()
added_response = "\n\n_If you think my response was misclassified, use the command_ `!misclassified` _to add your question to the database\nIf you're done with the interview please use the command `!finished` to end your session_"

class Raymond_Bot(commands.Cog, description = 'Hello World'):
    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if not message.content.startswith('!'):
            userinput = message.content
            response = raymond_bot.respond(userinput)
            await message.channel.send(response[0] + added_response)

    @commands.command(brief = "use this command if the question was misclassified")
    async def misclassified(self, ctx):
        last_message = [message async for message in ctx.channel.history(limit=3)]
        question = last_message[2].content #We'll create a method to add this to a yaml file later. 
        question_add(question)
        response = '_Thanks for letting me know!_'
        await ctx.channel.send(response)

    @commands.command(brief = "Use this command when you're done with the interview. You will be removed from the server")
    async def finished(self, ctx):
        if ctx.author.guild_permissions.administrator:
            print('Finished Function Works')
        else:
            await ctx.channel.send('Thank you for taking the time to interview me!\nYou will be now be removed from the server in 10 seconds.\nFeel free to comeback and interview me again!\n -_Raymond Yung_')
            await sleep(10)
            await ctx.author.kick()

    @commands.command(brief = "Admin Command to delete Chat History")
    @commands.has_guild_permissions(manage_messages = True)
    async def delete(self, ctx, amount = None):
        await ctx.channel.purge(limit = amount)
        return

async def setup(client):
    await client.add_cog(Raymond_Bot(client))