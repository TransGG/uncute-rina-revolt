from Uncute_Rina import *

class PagedMessage:
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

class PageHandling(commands.Cog[Bot]):
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

reaction_messages: dict[str, PagedMessage] = {}


class CustomEmbed(revolt.SendableEmbed):
    def __init__(self, *args, **kwargs):
        """
        Represents an embed that can be sent in a message, you will never receive this, you will receive :class:`Embed`.

        Attributes
        -----------
        title: Optional[:class:`str`]
            The title of the embed

        description: Optional[:class:`str`]
            The description of the embed

        media: Optional[:class:`str`]
            The file inside the embed, this is the ID of the file, you can use :meth:`Client.upload_file` to get an ID.

        icon_url: Optional[:class:`str`]
            The url of the icon url

        colour: Optional[:class:`str`]
            The embed's accent colour, this is any valid `CSS color <https://developer.mozilla.org/en-US/docs/Web/CSS/color_value>`_

        color: Optional[:class:`str`]
            Alias for colour

        url: Optional[:class:`str`]
            URL for hyperlinking the embed's title
        """
        if "color" in kwargs:
            kwargs["colour"] = kwargs["color"]
            del kwargs["color"]
        super().__init__(*args, **kwargs)
        self.footer: str | None = None

    def add_field(self, name = None, value = None, inline = None):
        if name is None and value is None:
            raise ValueError("A 'name' or 'value' must be given")
        
        if self.description in [None, ""]:
            self.description = ""
        else:
            self.description += "\n"

        if value is None:
            self.description += f"### {name}"
        elif name is None:
            self.description += f"{value}"
        else:
            self.description += f"### {name}\n{value}"

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

class UsageDict(TypedDict):
    usage: Optional[str]
    parameters: Optional[dict[str, dict[str, str | list[str]]]]
    examples: Optional[str | list[str]]
    # {"term":{"description":"str","accepted values":["str","str","str"]}}

class CustomCommand(commands.Command):
    """Class for holding info about a command.

    ### Parameters
    ----------
    callback: Callable[..., Coroutine[Any, Any, Any]]
        The callback for the command
    name: :class:`str`
        The name of the command
    aliases (optional): :class:`str`
        The aliases of the command. (default: None)
    parent (optional): :class:`Group`
        The parent of the command if this command is a subcommand. (default: None)
    cog (optional): :class:`Cog`
        The cog the command is apart of. (default: None)
    usage (optional): :class:`str` | :class:`dict`
        The usage string for the command. (default: None)
    """
    def __init__(self, callback, name: str, aliases: list[str], usage: str | UsageDict | None = None):
        if usage is None:
            usage = UsageDict()
        elif type(usage) is str:
            usage = UsageDict({"usage":usage})
        elif type(usage) is dict and \
             type(usage) is not UsageDict:
            usage = UsageDict(usage)
        else:
            print(type(usage))
            raise
        super().__init__(callback, name, aliases, usage)
        self._error_handler = type(self).error_handler
    
    @staticmethod
    def template(type, optional: str | None = None, kwarg: str | None = None, pre_defined: bool = False, 
                 wrapped: bool | None = None, case_sensitive: bool | None = None):
        """
        Get pre-built string for command usage parameter "Type"

        ### Parameters
        type: :class:`str`
            one of: "word", "str", "list[str]", "list[int]", "int", "mention or ID", or else
        optional: :class:`bool` | None
            Whether the command is optional (default: None)
        kwarg: :class:`str` | `None`
            The name of the parameter if it's a keyword argument (default: None)
        pre_defined (optional): :class:`bool`
            Whether the parameter has pre-defined variables you have to pick from (default: False)
        wrapped (optional): :class:`bool` | `None`
            Whether you can pass multiple words to the parameter without quotation marks (default: None)
        case_sensitive (optional): :class:`bool` | `None`
            Whether the parameter is case-sensitive (default: None)
        """
        parts = []
        if pre_defined:
            parts.append("pre-defined")
        if case_sensitive:
            parts.append("case-sensitive")
        if kwarg:
            parts.append(f"keyword argument (`{kwarg}=...`):")
        if optional:
            parts.append("(optional)")


        if type == "word":
            parts.append("string (word)")
        elif type == "str":
            parts.append("string (word or words)")
        elif type == "list[str]":
            parts.append("list of strings (word or words, separated by a comma)")
        elif type == "list[int]":
            parts.append("list of numbers (separated by a comma)")
        elif type == "int":
            parts.append("number")
        elif type == "mention or ID":
            parts.append("mention (or ID)")
        else:
            parts.append(type)
        # any, ID, subcommand, emoji
            
        
        if wrapped:
            parts.append("(no quotes necessary)")
        if wrapped is False:
            parts.append("(surrounded by quotes if you want multiple words)")
        if case_sensitive == False:
            parts.append("(case-insensitive)")
        
        return ' '.join(parts)

    async def error_handler(self, ctx: commands.Context, error: Exception):
        #This should handle replying to the author and log to console.
        ctx.client.dispatch("command_error", ctx, error)
        # traceback.print_exception(type(error), error, error.__traceback__)

class CustomGroup(commands.Group):
    def __init__(self, callback, name: str = None, aliases: list[str] = [], usage: str|dict = None):
        """Class for holding info about a group command.

        Parameters
        ----------
        name: :class:`str`
            The name of the command
        callback: Callable[..., Coroutine[Any, Any, Any]]
            The callback for the group command
        aliases: list[:class:`str`]
            The aliases of the group command
        usage: :class:`str` | :class:`dict[str, str | dict[str, dict[str, str|list[str]]]]`
            Command usage
        """
        if usage is None:
            usage = UsageDict()
        elif type(usage) is str:
            usage = UsageDict({"usage":usage})
        elif type(usage) is dict and \
             type(usage) is not UsageDict:
            usage = UsageDict(usage)
        else:
            print(type(usage))
            raise
        super().__init__(callback=callback, name = name or callback.__name__, aliases=aliases)
        self.usage = usage
        self._error_handler = type(self).error_handler

    def command(self, *, name = None, aliases: list[str] = None, cls = CustomCommand, usage: str | None = None):
        """A decorator that turns a function into a :class:`Command` and registers the command as a subcommand.

        Parameters
        -----------
        name: Optional[:class:`str`]
            The name of the command, this defaults to the functions name
        aliases: Optional[list[:class:`str`]]
            The aliases of the command, defaults to no aliases
        cls: type[:class:`Command`]
            The class used for creating the command, this defaults to :class:`Command` but can be used to use a custom command subclass
        usage: Optional[:class:`str`]
            The usage string for the command
        Returns
        --------
        Callable[Callable[..., Coroutine], :class:`Command`]
            A function that takes the command callback and returns a :class:`Command`
        """
        def inner(func):
            command = cls(func, name or func.__name__, aliases or [], usage=usage)
            command.parent = self
            self.subcommands[command.name] = command
            return command

        return inner

    async def error_handler(self, ctx: commands.Context, error: Exception):
        # Reply to the author and log to console
        ctx.client.dispatch("command_error", ctx, error)


class CustomHelpCommand(commands.help.HelpCommand):
    def get_short_command_description(self, command: CustomCommand):
        """
        Get short description of a given command (first or second line)
        
        ### Parameters
        --------------
        command: :class:`commands.Command`
            The command to get the short descrpition of

        ### Returns
        -----------
        first line of description, if not empty. Else
        second line of description, if not empty. Else
        empty string
        """
        if "description" in command.usage:
            return command.usage["description"]
        if desc := command.description:
            if desc := desc.split("\n")[0]:
                # get first line of description
                pass
            elif len(split_desc := command.description.split("\n")) > 1 and (desc := split_desc[1]):
                # get second line of description if there is more than 1 line in the description, and store it in `desc`
                pass
            else:
                desc = self.trim_attribute(command)
        else:
            desc = "No description"
        return desc.strip()
    
    def trim_attribute(self, parent, _type: str = "description"):
        """
        Get / trim a string (docstring) from a command attribute

        ### Parameters
        --------------
        command: :class:`commands.Command`
            The command to get the description of
        type (optional): :class:`str`
            The attribute to use (default: "description", can be "usage" too)
        """
        # largely copied from PEP-0257
        attr = getattr(parent, _type)
        if not attr:
            return "No description"
        lines = attr.split("\n")

        # Determine minimum indentation (first line doesn't count):
        indent = sys.maxsize
        for line in lines[1:]:
            stripped = line.lstrip()
            if stripped:
                indent = min(indent, len(line) - len(stripped))
        # Remove indentation (first line is special):
        trimmed = [lines[0].strip()]
        for line in lines[1:]:
            trimmed.append(line[indent:])
        # Strip off blank lines before and after description:
        while trimmed and not trimmed[-1]:
            trimmed.pop()
        while trimmed and not trimmed[0]:
            trimmed.pop(0)
        # add 2-space indent
        return '\n'.join(trimmed)

    async def create_global_help(self, ctx: commands.Context, commands: dict[commands.Cog | None, list[CustomCommand]]):
        # lines = ["```"]
        # for cog, cog_commands in commands.items():
        #     cog_lines: list[str] = []
        #     cog_lines.append(f"{cog.qualified_name if cog else 'No cog'}:")

        #     for command in cog_commands:
        #         desc = self.get_short_command_description(command)
        #         cog_lines.append(f"  {command.name} - {desc}")

        #     lines.append("\n".join(cog_lines))

        # lines.append("```")
        m = ctx.client.get_command_mention
        return f"""Hi there! This bot has a whole bunch of commands. Let me introduce you to some:
{m('add_poll_reactions')}: Add an up-/downvote emoji to a message (for voting)
{m('help')}: See this help page. Use {m('help')} `<command>` for more info about a command.
###### {m('compliment')}: Rina can compliment others (matching their pronoun role)
{m('convert_unit')}: Convert a value from one to another! Distance, speed, currency, etc.
{m('dictionary')}: Search for an lgbtq+-related or dictionary term!
###### {m('equaldex')}: See LGBTQ safety and rights in a country (with API)
###### {m('math')}: Ask Wolfram|Alpha for math or science help
###### {m('nameusage gettop')}: See how many people are using the same name
{m('pronouns')}: See someone's pronouns or edit your own
###### {m('qotw')} and {m('developer_request')}: Suggest a Question Of The Week or Bot Suggestion to staff
{m('reminder reminders')}: Make or see your reminders
{m('roll')}: Roll some dice with a random result
{m('tag')}: Get information about some of the server's extra features
{m('todo')}: Make, add, or remove items from your to-do list
{m('toneindicator')}: Look up which tone tag/indicator matches your input (eg. /srs)

Make a custom voice channel by joining "Join to create VC" (use {m('tag')} `tag:customvc` for more info)
{m('editvc')}: edit the name or user limit of your custom voice channel
{m('vctable about')}: Learn about making your voice chat more on-topic!
"""

    async def create_command_help(self, ctx: commands.Context, command: CustomCommand):
        # ## Dictionary command
        # ### Usage
        # `!dictionary <term...> source=[source]`
        # For usage help, use !help usage.
        #
        # ### Parameters
        # `term`
        # - Description: This is your search query. What do you want to look for?
        # - Type: string (word or words)
        # ---
        # `source`
        # - Description: Where do you want to search? Online? Custom Dictionary?
        # - Type: number
        # - Accepted values:
        #     - Source should be a number from `1` to `8`:
        #     - Source `2` checks the custom dictionary
        #     - Source `4` checks en.pronouns.page
        #     - Source `6` checks dictionaryapi.dev
        #     - Source `8` checks UrbanDictionary.com
        #     - Source `1` (default) will go through sources `2`, `4`, `6`, and `8`, until it finds a result."
        # - Default: `1`
        #
        # ### Aliases
        # (none, actually)
        #
        # ### Examples
        # `!dictionary fantasy`
        # `!dictionary high heels`
        if type(command) is not CustomCommand and type(command) is not CustomGroup:
            return f"Wrong class (must be CustomCommand or CustomGroup, not {command.__class__})"
        lines = []
        prefix = (await ctx.client.get_prefix(ctx.message))[0]
        if type(command) is CustomCommand:
            lines.append(f"## '{command.name.capitalize()}' command")
        if type(command) is CustomGroup:
            lines.append(f"## '{command.name.capitalize()}' group command")
        usage: UsageDict = command.usage

        if "description" in usage:
            lines.append(usage["description"])

        if "usage" in usage:
            lines.append("")
            lines.append(f"### Usage\n"
                        f"`{prefix}{usage.get('usage')}`\n"
                        f"For usage help, use !help usage.")

        if "parameters" in usage:
            lines.append("")
            lines.append("### Parameters")
            for param in usage["parameters"]:
                lines.append(f"`{param}`")
                for detail in usage["parameters"][param]:
                    if type(value := usage["parameters"][param][detail]) is str:
                        lines.append(f"- {detail.capitalize()}: {value}")
                    elif type(value) is list:
                        lines.append(f"- {detail.capitalize()}:")
                        for item in value:
                            lines.append(f"  - {item}")
                if len(usage["parameters"]) > 1:
                    lines.append(f"---") # otherwise you get a weird indent..
        
        if command.aliases:
            lines.append("")
            lines.append(f"### Aliases\n"
                         f"{', '.join(command.aliases)}")

        if "examples" in usage:
            lines.append("")
            if type(usage["examples"]) is str:
                lines.append(f"### Example\n`{usage['examples']}`")
            elif type(usage["examples"]) is list:
                if len(usage["examples"]) == 1:
                    lines.append(f"### Example\n`{usage['examples'][0]}`")
                elif len(usage["examples"]) > 1:
                    lines.append(f"### Examples")
                    for example in usage["examples"]:
                        lines.append(f"`{prefix}{example}`")

        return "\n".join(lines)

    async def create_group_help(self, ctx: commands.Context, group: CustomGroup):
        cmd_lines = await self.create_command_help(ctx, command=group)
        lines = []
        if group.commands:
            lines.append("")
            lines.append("### Subcommands")
        
        for command in group.commands:
            command: CustomCommand
            desc = self.get_short_command_description(command)
            if 'usage' in command.usage:
                lines.append(f"- `{command.usage['usage']}`\n  - Description: {desc}")
            else:
                lines.append(f"- `{command.name}`\n  - Description: {desc}")
        
        cmd_lines += "\n"+ "\n".join(lines)
        return cmd_lines

    async def create_cog_help(self, ctx: commands.Context, cog: commands.Cog):
        lines = ["```"]
        lines.append(f"{cog.qualified_name}:")

        for command in cog.commands:
            desc = self.get_short_command_description(command)
            lines.append(f"  {command.name} - {desc}")

        lines.append("```")
        return "\n".join(lines)

    async def handle_no_command_found(self, ctx: commands.Context, name: str):
        if name == "usage":
            return ("The usage layout of commands is as follows:\n"
                    "- `<argument>` is a required argument\n"
                    "- `[argument]` is an optional argument\n"
                    "- `argument=[argument]` is an optional keyword argument. To set it, use `argument=1` or `argument:1`, for example\n"
                    "- `<argument...>` is a required wrapped argument. This means that you can use this parameter without needing any "
                    "quotation marks. This and any following words will be seen as part of the same argument\n"
                    "- `[argument...]` is an optional wrapped argument. Identical to the one above, but this one does not need to be given (it's optional)\n"
                    "- `...` is usually used in command groups, when there are sub commands that require different arguments")
        if name.lower() == "pluralkit":
            cmd_mention = ctx.client.get_command_mention("system new")
            cmd_mention2 = ctx.client.get_command_mention("member new")
            cmd_mention3 = ctx.client.get_command_mention("autoproxy set")
            cmd_mention4 = ctx.client.get_command_mention("help")
            return (f"Simply said, PluralKit is a Discord bot that lets people send messages under different names and avatars\n"
                    f"I made a simple recreation of it, for the purposes of letting people with DID, etc. create systems and members."
                    f"Due to Revolt limitations, these messages will show up with the [BRIDGE] tag.\n"
                    f"\n"
                    f"To start, type {cmd_mention}. Add members with {cmd_mention2}.\n"
                    f"Autoproxy system members with {cmd_mention3} `<member>`.\n"
                    f"For any more help, type {cmd_mention3} `<command>`, where command is the first word of one of the previously "
                    f"mentioned commands. Enjoy :)")
        
        return f"Command `{name}` not found."

    async def handle_no_cog_found(self, ctx: commands.Context, name: str):
        return f"Cog `{name}` not found. (not sure when this would be called. Please ping {Bot.bot_owner.mention} so I learn :D)"



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

def safe_string(string: str):
    index = 0
    while index < len(string):
        if string[index] == "@":
            # if matching (regex) /[^\\]+@/g (@ followed by no backslash)
            if index != 0 and string[index-1] != "\\":
                string = string[:index] + '\\' + string[index:]
                index += 1 # increment 1 because string length got 1 longer
        index += 1
    return string

def jump_msg(message: revolt.Message):
    # https://app.revolt.chat/server/serverid/channel/channelid/messageid
    try:
        return f"https://app.revolt.chat/server/{message.server.id}/channel/{message.channel.id}/{message.id}"
    except LookupError: # not in server
        return f"https://app.revolt.chat/channel/{message.channel.id}/{message.id}"

def get_emoji_raw(client: Bot, emoji_str: str):
    emoji_str = emoji_str.replace(":","")
    if not any([char in "abcdefghijklmnopqrstuvwxyz" for char in emoji_str]):
        # check if all characters in the emoji_str are either numbers or uppercase letters
        return emoji_str
    else:
        # return unicode emoji, maybe
        try:
            return client.emojis[emoji_str]
        except:
            return None
