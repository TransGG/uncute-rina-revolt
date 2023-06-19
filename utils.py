from Uncute_Rina import *

class PagedMessage():
    def __init__(self, client: Bot, ctx: commands.Context, pages, timeout = 180, content: str | None = None,
                 backward_button = "◀️", forward_button = "▶️"):
        self.client: Bot = client
        self.ctx: commands.Context = ctx
        self.pages: list[CustomEmbed] = pages
        self.page: int = 0
        self.timeout: int = timeout
        self.backward_button: str = backward_button
        self.forward_button: str = forward_button
        self.content = content
        self.buttons = [self.backward_button, self.forward_button] # not sure if this is necessary. Thought it could be good for dependencies
        
        self.message: revolt.Message
        #note: don't use message.content or message.embeds, it's unreliable cause it's changing all the time
    
    async def forward(self):
        if self.page+1 >= len(self.pages):
            self.page = 0 # loop-around to first page
        else:
            self.page += 1
        embed = self.pages[self.page].copy()
        if getattr(embed, "footer", False):
            embed.set_footer(text=embed.footer+"\n##### page: " + str(self.page + 1) + " / " + str(len(self.pages)))
        else:
            embed.set_footer(text="page: " + str(self.page + 1) + " / " + str(len(self.pages)))
        await self.message.edit(embeds=[embed])
        self.message.embeds = [embed]
    
    async def backward(self):
        if self.page-1 < 0:
            self.page = len(self.pages) - 1 # loop-around to last page
        else:
            self.page -= 1
        embed = self.pages[self.page].copy()
        if getattr(embed, "footer", False):
            embed.set_footer(text=embed.footer+"\n##### page: " + str(self.page + 1) + " / " + str(len(self.pages)))
        else:
            embed.set_footer(text="page: " + str(self.page + 1) + " / " + str(len(self.pages)))
        await self.message.edit(embeds=[embed])
        self.message.embeds = [embed]

    async def on_timeout(self):
        del reaction_messages[self.message.id]
        await self.message.remove_all_reactions()

    async def send(self):
        embed = self.pages[self.page].copy()
        if getattr(embed, "footer"):
            embed.set_footer(text=embed.footer+"\n##### page: " + str(self.page + 1) + " / " + str(len(self.pages)))
        else:
            embed.set_footer(text="page: " + str(self.page + 1) + " / " + str(len(self.pages)))
        self.message = await self.ctx.message.reply(content=self.content, embed=embed)
        for button in self.buttons:
            await self.message.add_reaction(button)
        if self.timeout:
            reaction_messages[self.message.id] = self
            self.client.sched.add_job(self.on_timeout, "date", run_date=datetime.now()+timedelta(minutes=self.timeout))

class PageHandling(commands.Cog):
    def __init__(self, client: Bot):
        # client.on_message_events.append(self.on_message_page)
        client.on_reaction_add_events.append(self.on_page_reaction_add)
        self.client = client

    async def on_page_reaction_add(self, message: revolt.Message, user: revolt.User, emoji_id: str):
        if user.id == self.client.user.id:
            return
        if message.id not in reaction_messages:
            return
        paged_message: PagedMessage = reaction_messages[message.id]

        if paged_message.ctx.author.id != user.id:
            return

        if emoji_id == paged_message.backward_button:
            await paged_message.backward()
        elif emoji_id == paged_message.forward_button:
            await paged_message.forward()
        else:
            return
        
        m = paged_message.message
        await m.state.http.request("DELETE", f"/channels/{m.channel.id}/messages/{m.id}/reactions/{emoji_id}", params={"user_id":user.id})

    @commands.command(usage="Pong! testing the abilities of a usage string by \n throwing stuff in it")
    async def ping(self, ctx: commands.Context, arg1: str = ""):
        embed_list = []
        embed1=CustomEmbed(colour="#00ff00")
        embed1.add_field(value="## This is the name\nThis is a green embed. This was the description.")
        embed1.add_field(name="Custom field name", value="Field value")
        embed1.add_field(name="Another field name", value="Second value")
        embed1.set_footer("This is a footer text for a custom embed.")
        embed_list.append(embed1)
        embed2=CustomEmbed(colour="#0000ff")
        embed2.add_field(value="## This is another name\nThis is a blue embed. This is the second embed description.")
        embed2.add_field(name="Very much name", value="Very value")
        embed2.add_field(name="Another very name", value="Second much value")
        embed2.set_footer("This is more foot for a embed.")
        embed_list.append(embed2)
        await PagedMessage(self.client, ctx, embed_list).send()

    # async def on_message_page(self, message: revolt.Message):
    #     print(message.content, "hii")

reaction_messages: dict[str, PagedMessage] = {}


class CustomEmbed(revolt.SendableEmbed):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.footer: str | None = None

    def add_field(self, name = None, value = None, inline = None):
        if name is None and value is None:
            raise ValueError("A 'name' or 'value' must be given")
        
        if self.description == None:
            self.description = ""
        else:
            self.description += "\n"

        if value is None:
            self.description += f"### {name}"
        elif name is None:
            self.description += f"{value}"
        else:
            self.description += f"### {value}\n{value}"

    def set_footer(self, text):
        self.footer = text

    def to_dict(self):
        if self.footer is not None:
            if self.description == None:
                self.description = ""
            else:
                self.description += "\n\n"
            self.description += f"##### {self.footer}"
        return super().to_dict()
    
    def copy(self):
        deepcopy = CustomEmbed(title=self.title, description=self.description, colour=self.colour)
        deepcopy.set_footer(self.footer)
        return deepcopy

def setup(client: Bot):
    client.add_cog(PageHandling(client))



# TODO: make make_string_safe_to_send_to_public() function to remove mentions etc.
# TODO: make all context messages reply to the original command

def is_verified(ctx: commands.Context):
    """
    Check if someone is verified

    ### Parameters:
    ctx: :class:`commands.Context`
        context with ctx.server.roles and ctx.author.roles
    
    ### Returns
    `bool` is_verified
    """
    if ctx.server_id is None:
        return False
    roles = []
    for role in ctx.server.roles:
        if role.name.lower() == "verified":
            roles.append(role)
    user_role_ids = [role.id for role in ctx.author.roles]
    role_ids = ["959748411844874240",  # Transplace: Verified
                "1109907941454258257"] # Transonance: Verified
    return len(set(roles).intersection(ctx.author.roles)) > 0 or is_staff(ctx) or len(set(role_ids).intersection(user_role_ids)) > 0

# def isVerifier(itx: discord.Interaction):
#     roles = [discord.utils.find(lambda r: r.name == 'Verifier', itx.guild.roles)]
#     return len(set(roles).intersection(itx.user.roles)) > 0 or is_admin(itx)

def is_staff(ctx: commands.Context):
    """
    Check if someone is staff

    ### Parameters
    ---------------
    ctx: :class:`commands.Context`
        context with ctx.server.roles and itx.author.roles
    
    ### Returns
    -----------
    `bool` is_staff
    """
    if ctx.server_id is None:
        return False
    
    roles = []
    for role in ctx.server.roles:
        for name_match in ["staff", "moderator", "trial mod", "sr. mod", "chat mod"]:
            if role.name.lower() in name_match:
                roles.append(role)

    user_role_ids = [role.id for role in ctx.author.roles]
    role_ids = ["1069398630944997486","981735650971775077", #TransPlace: trial ; moderator
                "1108771208931049544"] # Transonance: Staff
    return len(set(roles).intersection(ctx.author.roles)) > 0 or is_admin(ctx) or len(set(role_ids).intersection(user_role_ids)) > 0

def is_admin(ctx: commands.Context):
    """
    Check if someone is an admin

    ### Parameters
    ---------------
    ctx: :class:`discord.Interaction`
        interaction with itx.guild.roles and itx.user
    
    ### Returns
    -----------
    `bool` is_admin
    """
    if ctx.server_id is None:
        return False
    if type(ctx.author) is revolt.Member:   
        ctx.author: revolt.Member = ctx.author
    else:
        return False
    roles = []
    for role in ctx.server.roles:
        for name_match in ['full admin', 'head staff', 'admins', 'admin', 'owner']:
            if role.name.lower() in name_match:
                roles.append(role)
    user_role_ids = [role.id for role in ctx.author.roles]
    role_ids = ["981735525784358962"]  # TransPlace: Admin
    member_perms = ctx.author.get_channel_permissions(ctx.channel)
    has_admin = member_perms.manage_server and member_perms.manage_channel
    return has_admin or \
           len(set(roles).intersection(ctx.author.roles)) > 0 or \
           ctx.author.id == "01H34JM6Y9GYG5E26FX5Q2P8PW"      or \
           len(set(role_ids).intersection(user_role_ids)) > 0

def debug(text="", color="default", add_time=True, end="\n", advanced=False):
    """
    Log a message to the console

    ### Parameters
    ---------------
    text: :class:`str`
        The message you want to send to the console
    color (optional): :class:`str`
        The color you want to give your message ('red' for example)
    add_time (optional): :class:`bool`
        If you want to start the message with a '[23:59:59.000001] [INFO]:'
    end (optional): :class:`str`
        What to end the end of the message with (similar to print(end=''))
    advanced (optional) :class:`bool`
        Whether to interpret `text` as advanced text (like minecraft in-chat colors). Replaces "&4" to red, "&l" to bold, etc. and "&&4" to a red background.
    """

    colors = {
        "default":"\033[0m",
        "black":"\033[30m",
        "red":"\033[31m",
        "lime":"\033[32m",
        "green":"\033[32m",
        "yellow":"\033[33m",
        "blue":"\033[34m",
        "magenta":"\033[35m",
        "purple":"\033[35m",
        "cyan":"\033[36m",
        "gray":"\033[37m",
        "lightblack":"\033[90m",
        "darkgray":"\033[90m",
        "lightred":"\033[91m",
        "lightlime":"\033[92m",
        "lightgreen":"\033[92m",
        "lightyellow":"\033[93m",
        "lightblue":"\033[94m",
        "lightmagenta":"\033[95m",
        "lightpurple":"\033[95m",
        "lightcyan":"\033[96m",
        "aqua":"\033[96m",
        "lightgray":"\033[97m",
        "white":"\033[97m",
    }
    detailColor = {
        "&0" : "40",
        "&8" : "40",
        "&1" : "44",
        "&b" : "46",
        "&2" : "42",
        "&a" : "42",
        "&4" : "41",
        "&c" : "41",
        "&5" : "45",
        "&d" : "45",
        "&6" : "43",
        "&e" : "43",
        "&f" : "47",
        "9" : "34",
        "6" : "33",
        "5" : "35",
        "4" : "31",
        "3" : "36",
        "2" : "32",
        "1" : "34",
        "0" : "30",
        "f" : "37",
        "e" : "33",
        "d" : "35",
        "c" : "31",
        "b" : "34",
        "a" : "32",
        "l" : "1",
        "o" : "3",
        "n" : "4",
        "u" : "4",
        "r" : "0",
    }
    color = color.replace(" ","").replace("-","").replace("_","")
    if advanced:
        for _detColor in detailColor:
            while "&"+_detColor in text:
                _text = text
                text = text.replace("m&"+_detColor,";"+detailColor[_detColor]+"m",1)
                if _text == text:
                    text = text.replace("&"+_detColor,"\033["+detailColor[_detColor]+"m",1)
        color = "default"
    else:
        try:
            # is given color a valid option?
            colors[color]
        except KeyError:
            warnings.warn("Invalid color given for debug function: "+color, SyntaxWarning)
            color = "default"
    if add_time:
        time = f"{colors[color]}[{datetime.now().strftime('%H:%M:%S.%f')}] [INFO]: "
    else:
        time = colors[color]
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logger = logging.getLogger()
    print = logger.info
    if end.endswith("\n"):
        end = end[:-2]
    print(f"{time}{text}{colors['default']}"+end.replace('\r','\033[F'))

async def log_to_guild(client: Bot, guild: revolt.Server, msg: str):
    """
    Log a message to a server's logging channel (vcLog)

    ### Parameters
    --------------
    client: :class:`Uncute_Rina.Bot`
        The bot class with `client.get_command_info()`
    guild: :class:`revolt.Server`
        Server of the logging channel
    msg: :class:`str`
        Message you want to send to this logging channel
    """
    try:
        log_channel_id = await client.get_guild_info(guild, "vcLog")
    except KeyError:
        msg = "__**THIS MESSAGE CAUSES THE CRASH BELOW**__\n"+msg
        await client.logChannel.send(msg)
        raise
    log_channel = guild.get_channel(log_channel_id)
    if log_channel is None:
        debug("Exception in log_channel:\n"
              "    guild: "+repr(guild)+"\n"
              "    log_channel_id: "+str(log_channel_id),color="orange")
        return
    return await log_channel.send(msg)

async def executed_in_dms(ctx: commands.Context = None, 
                          message: revolt.Message = None,
                          channel: revolt.ServerChannel= None):
    """
    Make a command guild-only by telling people in DMs that they can't use the command

    ### Parameters
    ---------------
    ctx: :class:`commands.context`
        The context to check if it was used in a server - and to reply to
    message: :class:`discord.Message` (used for events)
        The message to check if it was used in a server
    channel: :class:`revolt.ServerChannel`
        The channel to check if it was used in a server

    ### Returns
    ------------
    :class:`bool` if command was executed in DMs (for 'if ... : continue')

    (:class:`revolt.Message` is sent to the executor)
    """
    assert len([i for i in [ctx, message, channel] if i is not None]) == 1, ValueError("Give an itx, message, or channel, not multiple!")
    id_object: revolt.Message | commands.Context | revolt.ServerChannel = next(i for i in [ctx, message, channel] if i is not None)
    if id_object.server_id is None:
        if type(id_object) == revolt.Message:
            # Technically you could check if `channel` is DMChannel, but server_id==None should catch this too.
            await id_object.channel.send("This command is unavailable in DMs", ephemeral=True)
            return True
        await id_object.send("This command is unavailable in DMs", ephemeral=True)
        return True
    return False
