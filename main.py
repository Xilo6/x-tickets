import discord
from discord.ext import commands
from discord.ext.commands import has_role as perms
import json
import uuid
import asyncio

intents = discord.Intents.all()
bot = discord.Bot(intents=intents)

with open("settings.json", "r") as file:
    settings = json.load(file)

@bot.event
async def on_ready():
    print(f"Successfully booted {bot.user.name}")

@bot.slash_command(description="Ticket system setup [Admins Only]")
@perms("Developer")
async def setup(ctx, category: discord.CategoryChannel, team_role: discord.Role):
    class Buttons(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label="Delete", custom_id="button-2", row=0,style=discord.ButtonStyle.danger)
        async def first_button_callback(self, button, interaction):
            member = interaction.user
            if team_role in member.roles:
                embed = discord.Embed(
                description="Closing ticket in 5 seconds"
                )
                await interaction.response.send_message(embed=embed)
                await asyncio.sleep(5)
                await interaction.channel.delete(reason="Ticket closed by user")
            else:
                await interaction.response.send_message(f"You do not have the {team_role.mention} role", ephemeral=True)

        @discord.ui.button(label="Claim",custom_id="button-4", row=0, style=discord.ButtonStyle.primary)
        async def second_button_callback(self, button, interaction):
            member = interaction.user
            if team_role in member.roles:
                channel = interaction.channel
                await channel.edit(name=f"{interaction.user.name}")
                await interaction.response.send_message("Sucessfully claimed ticket!", ephemeral=True)
            else:
                await interaction.response.send_message(f"You do not have the {team_role.mention} role", ephemeral=True)
    class Tickets(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label="Create a Ticket", custom_id="button-1", style=discord.ButtonStyle.primary, emoji="🎫")
        async def button_callback(self, button, interaction):
            ticket_id = uuid.uuid4()
            guild = interaction.guild
            ticket_channel = await guild.create_text_channel(f"{interaction.user.name}-ticket", category=category)
            await ticket_channel.set_permissions(team_role, send_messages=True, read_messages=True, add_reactions=True, embed_links=True, attach_files=False, read_message_history=True)
            await ticket_channel.set_permissions(interaction.user, send_messages=True, read_messages=True, add_reactions=True, embed_links=True, attach_files=False, read_message_history=True)
            await ticket_channel.set_permissions(guild.default_role, view_channel=False)

            embed = discord.Embed(
                description=f"Thank you for opening a ticket with `{interaction.guild.name}`, our ownership will like to thank you for opening a ticket. \n \n Please wait patiently for our staff team to respond",
                color=0x3498db
            )
            embed.set_author(name="Ticket System", icon_url="")
            await ticket_channel.send(f"{team_role.mention}, {interaction.user.mention}", embed=embed, view=Buttons())
            await interaction.response.send_message(f"Successfully created ticket, your ticket id is: {ticket_id}", ephemeral=True)

    bot.add_view(Tickets())
    bot.add_view(Buttons())
    embed = discord.Embed(
        description="Looking to purchase one of our products? If so, please click the blue button below and speak with one of our support members.\n\n• Average response time is 4 - 20 minutes.",
        color=0x3498db
    )
    embed.set_author(name="Ticket System", icon_url="")
    await ctx.send(embed=embed, view=Tickets())

bot.run(settings["Misc"]["Token"])
