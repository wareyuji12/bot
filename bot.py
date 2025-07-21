import discord
from discord.ext import commands
import os
import asyncio

# Bot configuration
AUTHORIZED_USERS = [1318623756436115511, 739402097535221821]
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "MTM5NjgxNjg0NzM4MjM4NDY3MA.G1sd0e.XHDxmv1LKNsLqeyEQbC1jgWdYVoAhOh2LshJNI")

# Bot setup with necessary intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

class RobloxBusinessBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='!',  # Prefix for text commands (not used for slash commands)
            intents=intents,
            help_command=None
        )
    
    async def setup_hook(self):
        """Called when the bot is starting up"""
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"Failed to sync commands: {e}")
    
    async def on_ready(self):
        """Called when the bot is ready"""
        print(f'{self.user} has connected to Discord!')
        print(f'Bot is in {len(self.guilds)} guilds')

# Create bot instance
bot = RobloxBusinessBot()

def is_authorized(interaction: discord.Interaction) -> bool:
    """Check if the user is authorized to use restricted commands"""
    return interaction.user.id in AUTHORIZED_USERS

@bot.tree.command(name="ticketsetup", description="Set up the ticket system (Authorized users only)")
async def ticket_setup(interaction: discord.Interaction):
    """Set up the ticket system with a create ticket embed"""
    
    # Check if user is authorized
    if not is_authorized(interaction):
        await interaction.response.send_message(
            "❌ **Access Denied**\nYou are not authorized to use this command.", 
            ephemeral=True
        )
        return
    
    # Create the ticket embed
    embed = discord.Embed(
        title="Please create a ticket in either the Purchasing or Support department. Once the ticket is created, kindly state what you need.",
        color=0x0099ff  # Blue color
    )
    
    # Create the button view
    view = TicketView()
    
    # Send confirmation to user first
    await interaction.response.send_message("✅ **Ticket setup created**", ephemeral=True)
    
    # Post the embed completely anonymously by sending directly to the channel
    await interaction.channel.send(embed=embed, view=view)

@bot.tree.command(name="say", description="Send a message through the bot (Authorized users only)")
async def say_command(interaction: discord.Interaction, message: str):
    """Send a message through the bot"""
    
    # Check if user is authorized
    if not is_authorized(interaction):
        await interaction.response.send_message(
            "❌ **Access Denied**\nYou are not authorized to use this command.", 
            ephemeral=True
        )
        return
    
    # Validate message content
    if not message.strip():
        await interaction.response.send_message(
            "❌ **Error**\nMessage cannot be empty.", 
            ephemeral=True
        )
        return
    
    # Send confirmation to the user first
    await interaction.response.send_message(
        f"✅ **Message Sent**", 
        ephemeral=True
    )
    
    # Send the actual message completely anonymously by sending directly to the channel
    await interaction.channel.send(message)

@bot.tree.command(name="sendltc", description="LTC address for ltc payment method")
async def send_ltc(interaction: discord.Interaction):
    """Send LTC address for payment"""
    
    # Check if user is authorized
    if not is_authorized(interaction):
        await interaction.response.send_message(
            "❌ **Access Denied**\nYou are not authorized to use this command.", 
            ephemeral=True
        )
        return
    
    # Create LTC address embed
    ltc_embed = discord.Embed(
        title="💰 LTC Payment Address",
        description="**LTC Address:**\n`LYSce9g7XDwydsyWKDL7Sjt8D9PKuL2FfP`",
        color=0x345d9d  # LTC blue color
    )
    
    ltc_embed.add_field(
        name="💳 Payment Method",
        value="Litecoin (LTC)",
        inline=True
    )
    
    ltc_embed.add_field(
        name="⚠️ Important",
        value="Only send LTC to this address",
        inline=True
    )
    
    ltc_embed.set_footer(text="Copy the address above for payment")
    
    # Send confirmation to user first
    await interaction.response.send_message("✅ **LTC address sent**", ephemeral=True)
    
    # Post the LTC embed completely anonymously by sending directly to the channel
    await interaction.channel.send(embed=ltc_embed)



class TicketView(discord.ui.View):
    """View class for ticket creation button"""
    
    def __init__(self):
        super().__init__(timeout=None)  # Persistent view
    
    @discord.ui.button(
        label="Create Ticket", 
        style=discord.ButtonStyle.green, 
        emoji="🎫"
    )
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle ticket creation button click"""
        
        guild = interaction.guild
        user = interaction.user
        
        # Check if we're in a guild
        if not guild:
            await interaction.response.send_message(
                "❌ **Error**\nTickets can only be created in servers.",
                ephemeral=True
            )
            return
        
        # Check if user already has a ticket
        existing_channel = discord.utils.get(guild.channels, name=f"ticket-{user.name.lower()}")
        if existing_channel:
            await interaction.response.send_message(
                f"❌ **You already have an active ticket!**\nPlease use {existing_channel.mention}",
                ephemeral=True
            )
            return
        
        # Create ticket channel
        ticket_name = f"ticket-{user.name.lower()}"
        
        # Set up permissions for the ticket channel
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),  # Hide from everyone
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),  # Allow ticket creator
        }
        
        # Add permissions for authorized users (admins)
        for user_id in AUTHORIZED_USERS:
            admin_user = guild.get_member(user_id)
            if admin_user:
                overwrites[admin_user] = discord.PermissionOverwrite(
                    read_messages=True, 
                    send_messages=True, 
                    manage_messages=True,
                    manage_channels=True
                )
        
        # Add permissions for users with Administrator permission
        for member in guild.members:
            if isinstance(member, discord.Member) and member.guild_permissions.administrator:
                overwrites[member] = discord.PermissionOverwrite(
                    read_messages=True, 
                    send_messages=True, 
                    manage_messages=True,
                    manage_channels=True
                )
        
        try:
            # Create the ticket channel
            ticket_channel = await guild.create_text_channel(
                name=ticket_name,
                overwrites=overwrites,
                reason=f"Ticket created by {user.name}"
            )
            
            # Create welcome embed for the ticket channel
            welcome_embed = discord.Embed(
                title="🎫 Support Ticket Created",
                description=f"Hello {user.mention}! Welcome to your support ticket.\n\nPlease provide the following information to help us assist you:",
                color=0x0099ff
            )
            
            welcome_embed.add_field(
                name="",
                value="1. **Please clearly state what you need, including any specific issues or concerns. If your request involves the External team or Purchasing, be sure to mention that as well so it can be directed properly.**",
                
                inline=False
            )
            
            welcome_embed.add_field(
                name=" Response Time:",
                value="Our team will respond within 24 hours",
                inline=True
            )
            
            welcome_embed.add_field(
                name=" Privacy:",
                value="Only you and admins can see this channel",
                inline=True
            )
            
            welcome_embed.set_footer(
                text=f"Ticket ID: {user.id}-{interaction.created_at.strftime('%Y%m%d%H%M')}"
            )
            
            # Add close button to the ticket
            close_view = CloseTicketView()
            
            # Send welcome message in ticket channel
            await ticket_channel.send(
                content=f"{user.mention} Welcome to your ticket!",
                embed=welcome_embed,
                view=close_view
            )
            
            # Respond to the user
            await interaction.response.send_message(
                f"✅ **Ticket Created!**\nYour ticket has been created: {ticket_channel.mention}",
                ephemeral=True
            )
            
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ **Error**\nI don't have permission to create channels. Please contact an administrator.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                "❌ **Error**\nFailed to create ticket. Please try again later.",
                ephemeral=True
            )
            print(f"Error creating ticket: {e}")

class CloseTicketView(discord.ui.View):
    """View class for closing tickets"""
    
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(
        label="Close Ticket",
        style=discord.ButtonStyle.red,
        emoji="🔒"
    )
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle ticket closing"""
        
        # Check if we're in a guild channel
        if not interaction.guild or not isinstance(interaction.channel, discord.TextChannel):
            await interaction.response.send_message(
                "❌ **Error**\nThis command can only be used in server text channels.",
                ephemeral=True
            )
            return
        
        # Check if user is authorized or the ticket creator
        channel_name = interaction.channel.name
        if channel_name and channel_name.startswith("ticket-"):
            ticket_user = channel_name.replace("ticket-", "")
            is_ticket_owner = interaction.user.name.lower() == ticket_user
            
            # Check if user is admin
            is_admin = is_authorized(interaction)
            if isinstance(interaction.user, discord.Member):
                is_admin = is_admin or interaction.user.guild_permissions.administrator
            
            if not (is_ticket_owner or is_admin):
                await interaction.response.send_message(
                    "❌ **Access Denied**\nOnly the ticket creator or admins can close this ticket.",
                    ephemeral=True
                )
                return
            
            # Create confirmation embed
            confirm_embed = discord.Embed(
                title="🔒 Ticket Closing",
                description=f"**Closed by:** {interaction.user.mention}\n**Reason:** Ticket resolved",
                color=0xff0000,
                timestamp=interaction.created_at
            )
            
            await interaction.response.send_message(embed=confirm_embed)
            
            # Wait a moment then delete the channel
            await asyncio.sleep(3)
            await interaction.channel.delete(reason=f"Ticket closed by {interaction.user.name}")
            
        else:
            await interaction.response.send_message(
                "❌ **Error**\nThis command can only be used in ticket channels.",
                ephemeral=True
            )

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore unknown commands
    
    print(f"Command error: {error}")

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    """Handle slash command errors"""
    if isinstance(error, discord.app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"❌ **Cooldown**\nThis command is on cooldown. Try again in {error.retry_after:.2f} seconds.",
            ephemeral=True
        )
    elif isinstance(error, discord.app_commands.MissingPermissions):
        await interaction.response.send_message(
            "❌ **Insufficient Permissions**\nYou don't have permission to use this command.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "❌ **Error**\nAn unexpected error occurred. Please try again later.",
            ephemeral=True
        )
        print(f"Slash command error: {error}")

async def run_bot():
    """Run the bot"""
    try:
        await bot.start(BOT_TOKEN)
    except discord.LoginFailure:
        print("❌ Failed to login. Please check your bot token.")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
