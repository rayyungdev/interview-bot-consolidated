import discord
from discord.ext import commands
from numpy.random import randint
from discord.ext import tasks

'''
    When the user first enters the server: 
        - A new text channel and a new role is created.
            - User is added to this role
            - This is done so that role is unique. 

'''
text_channel_name = 'interview-channel-'
welcome_response = "I'm Raymond-Bot. I will be representing Raymond during this interview. \nI am made with an Intent Classification model, a model commonly used for FAQ Chatbots!\nIf you want more information about how I was built, checkout my blog at: _https://rayyungdev.github.io_"

class server_setup(commands.Cog, description = 'Server Moderation'):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, ctx):
        print('User: ', ctx, ' has joined')
        role_name = str(randint(1,9999))
        text_channel = text_channel_name+role_name
        permission_overwrites = {
            'read_messages' : True, 
            'send_messages' : True, 
            'read_message_history' : True
        }
        
        await ctx.guild.create_role(name = role_name, permissions = discord.Permissions.none())
        overwrites = {ctx : discord.PermissionOverwrite(**permission_overwrites)}
        channel = await ctx.guild.create_text_channel(text_channel, overwrites = overwrites)
        await channel.send(f"Hi <@{ctx.id}>\n" + welcome_response)

    @commands.Cog.listener()
    async def on_member_remove(self, ctx):
        test = await ctx.guild.fetch_roles()
        for role in test: 
            role_name = role.name
            if len(role.members) == 0:
                channel_name = text_channel_name + role_name
                channel = discord.utils.get(ctx.guild.channels, name = channel_name)
                if channel is not None:
                    await channel.delete()
                    await role.delete()
    
async def setup(client):
    await client.add_cog(server_setup(client))