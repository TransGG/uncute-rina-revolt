if __name__ == '__main__':
    print("Program started")
from import_modules import *

if __name__ != '__main__':
    class  Bot(revolt.Client):
        pass
else:
    debug(f"[#+   ]: Loading api keys..." + " " * 30, color="light_blue", end='\r')
    # debug(f"[+     ]: Loading server settings" + " " * 30, color="light_blue", end='\r')
    try:
        with open("api_keys.json","r") as f:
            api_keys = json.loads(f.read())
        tokens = {}
        TOKEN = api_keys['Revolt']
        for key in ['MongoDB', 'Open Exchange Rates', 'Wolfram Alpha']:
            # copy every other key to new dictionary to check if every key is in the file.
            tokens[key] = api_keys[key]
    except json.decoder.JSONDecodeError:
        raise SyntaxError("Invalid JSON file. Please ensure it has correct formatting.").with_traceback(None)
    except KeyError as ex:
        raise KeyError("Missing API key for: " + str(ex)).with_traceback(None)

    debug(f"[##+  ]: Loading database clusters..." + " " * 30, color="light_blue", end='\r')
    cluster = MongoClient(tokens['MongoDB'])
    RinaDB = cluster["RinaRevolt"]
    cluster = motor.AsyncIOMotorClient(tokens['MongoDB'])
    asyncRinaDB = cluster["RinaRevolt"]

    commanderror_cooldown = 0
    debug(f"[###+ ]: Loading version..." + " " * 30, color="light_blue", end='\r')
    # Dependencies:
    #   permissions:
    #       read messages (for commands)
    #       send messages (for command responses)
    #       add reaction (for PagedMessage)
    #       remove (other people's) reactions (for PagedMessage, if someone reacts)
    #
    #       attach files (for image of the member joining graph thing)
    #       read channel history (locate previous starboard message, for example)
    #       move users between voice channels (custom vc)
    #       # manage roles (for adding/removing table roles) (not used currently, i guess)
    #       manage channels (Global: You need this to be able to set the position of CustomVCs in a category, apparently) NEEDS TO BE GLOBAL?
    #           Create and Delete voice channels
    #       use embeds (for starboard)
    #       use (external) emojis (for starboard, if you have external starboard reaction...?)

    # dumb code for cool version updates
    fileVersion = "0.0.6.0".split(".")#"1.2.0.7".split(".")
    try:
        with open("version.txt", "r") as f:
            version = f.read().split(".")
    except FileNotFoundError:
        version = ["0"]*len(fileVersion)
    # if testing, which environment are you in?
    # 1: private dev server; 2: public dev server (TransPlace [Copy]), 3: revolt server
    testing_environment = 3
    for v in range(len(fileVersion)):
        if int(fileVersion[v]) > int(version[v]):
            version = fileVersion + ["0"]
            break
    else:
        version[-1] = str(int(version[-1])+1)
    version = '.'.join(version)
    with open("version.txt","w") as f:
        f.write(f"{version}")
    debug(f"[#### ]: Loading Bot" + " " * 30, color="light_blue", end='\r')

    # intents = discord.Intents.default()
    # intents.members = True #apparently this needs to be additionally defined cause it's not included in Intents.default()?
    # intents.message_content = True #apparently it turned off my default intent or something: otherwise i can't send 1984, ofc.
    # #setup default discord bot client settings, permissions, slash commands, and file paths

# interactions
# mentions
# remove_all_reactions 
# remove_reaction 
# replies 
# reply 
# reply_ids 
# server 
# server_id 
# state 
    from revolt.ext import commands
    class Bot(commands.CommandsClient):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        commandList: list[discord.app_commands.AppCommand]
        logChannel: revolt.TextChannel
        api_tokens = tokens
        startup_time = datetime.now() # used in /version
        RinaDB = RinaDB
        asyncRinaDB = asyncRinaDB
        prefixes = ["!"]
        # staff_server_id = 981730502987898960
        bot_owner: revolt.User # for AllowedMentions in on_appcommand_error()

        # "logging.WARNING" to remove annoying 'Scheduler started' message on sched.start()
        sched = AsyncIOScheduler(logger=logging.getLogger("apscheduler").setLevel(logging.WARNING))
        sched.start()


        # Class functions


        def get_command_mention(self, command_string: str):
            return f"`{self.prefixes[0]}{command_string}`"
            """
            Turn a string (/reminders remindme) into a command mention (</reminders remindme:43783756372647832>)

            ### Parameters
            --------------
            command_string:  :class:`str`
                Command you want to convert into a mention (without slash in front of it)
            ### Returns
            -----------
            command mention: :class:`str`
                The command mention, or input if not found
            """

            args = command_string.split(" ")+[None, None]
            command_name, subcommand, subcommand_group = args[0:3]
            # returns one of the following:
            # </COMMAND:COMMAND_ID>
            # </COMMAND SUBCOMMAND:ID>
            # </COMMAND SUBCOMMAND_GROUP SUBCOMMAND:ID>
            #              /\- is posed as 'subcommand', to make searching easier
            for command in self.commandList:
                if command.name == command_name:
                    if subcommand is None:
                        return command.mention
                    for subgroup in command.options:
                        if subgroup.name == subcommand:
                            if subcommand_group is None:
                                return subgroup.mention
                            #now it techinically searches subcommand in subcmdgroup.options
                            #but to remove additional renaming of variables, it stays as is.
                            # subcmdgroup = subgroup # hm
                            for subcmdgroup in subgroup.options:
                                if subcmdgroup.name == subcommand_group:
                                    return subcmdgroup.mention
                                    # return f"</{command.name} {subgroup.name} {subcmdgroup.name}:{command.id}>"
            return "/"+command_string
        
        async def get_guild_info(self, guild_id: revolt.Server | str, *args: str, log: list[revolt.Messageable | str] | None = None):
            """
            Get a guild's server settings (from /editguildinfo, in cmd_customvcs)

            ### Arguments:
            --------------
            guild_id: :class:`revolt.Server` or :class:`str`
                server or id from which you want to get the guild info / settings
            *args: :class:`str`
                settings (or multiple) that you want to fetch
            log (optional): :class:`list[Messageable, str]` (note: :class:`commands.Context` is a :class:`Messageable`)
                A list of [Messageable, error_message], and will reply this error message to the given channel if there's a KeyError.

            ### Returns:
            ------------
            `any` (whichever is given in the database)

            ### Raises:
            -----------
            `KeyError` if server is None, does not have data, or not the requested data.
            """
            if guild_id is None:
                raise KeyError(f"'{guild_id}' is not a valid guild or id!")
            if isinstance(guild_id, revolt.Server):
                guild_id = guild_id.id
            try:
                collection = self.RinaDB["guildInfo"]
                query = {"guild_id": guild_id}
                guild_data = collection.find_one(query)
                if guild_data is None:
                    raise KeyError(str(guild_id) + " does not have data in the guildInfo database!")
                if len(args) == 0:
                    return guild_data
                output = []
                unavailable = []
                for key in args:
                    try:
                        output.append(guild_data[key])
                    except KeyError:
                        unavailable.append(key)
                if unavailable:
                    raise KeyError("Guild " + str(guild_id) + " does not have data for: " + ', '.join(unavailable))
                if len(output) == 1: # prevent outputting [1] (one item as list) (doesn't unfold)
                    return output[0]
                return output
            except KeyError:
                if log is not None:
                    await log[0].send(log[1], ephemeral=True)
                raise


        # Class functions end
        # Command event overwriting


        async def get_prefix(self, message: revolt.Message):
            return self.prefixes
        
        on_message_events = []
        async def _on_message(self, message):
            for i in self.on_message_events:
                await i(message)

        async def process_commands(self, message: revolt.Message):
            """Processes commands, if you overwrite `Client.on_message` you should manually call this function inside the event.

            Parameters
            -----------
            message: :class:`Message`
                The message to process commands on

            Returns
            --------
            Any
                The return of the command, if any
            """
            content = message.content

            prefixes = await self.get_prefix(message)

            if isinstance(prefixes, str):
                prefixes = [prefixes]

            #edited from CommandsClient class
            has_prefix = True
            for prefix in prefixes:
                if content.startswith(prefix):
                    content = content[len(prefix):]
                    break
            else:
                # return
                has_prefix = False

            if has_prefix:
                if not content:
                    return

                view = self.get_view(message)(content)

                try:
                    command_name = view.get_next_word()
                except StopIteration:
                    return

                context_cls = self.get_context(message)

                try:
                    command = self.get_command(command_name)
                except KeyError:
                    context = context_cls(None, command_name, view, message, self)
                    return self.dispatch("command_error", context, commands.errors.CommandNotFound(command_name))

                context = context_cls(command, command_name, view, message, self)

                try:
                    self.dispatch("command", context)

                    if not await self.bot_check(context):
                        raise commands.errors.CheckError(f"the global check for the command failed")

                    if not await context.can_run():
                        raise commands.errors.CheckError(f"the check(s) for the command failed")

                    output = await context.invoke()
                    self.dispatch("after_command_invoke", context, output)

                    return output
                except Exception as e:
                    await command._error_handler(command.cog or self, context, e)
                    self.dispatch("command_error", context, e)

            else:
                await self._on_message(message)

        on_message = process_commands

        on_reaction_add_events = []

        async def on_reaction_add(self, message: revolt.Message, user: revolt.User, emoji_id: str):
            for i in self.on_reaction_add_events:
                await i(message, user, emoji_id)

        # Command event overwriting end
        # Bot commands


        @commands.command()
        async def version(self, ctx: commands.Context):
            public = is_staff(ctx)
            # get most recently pushed's version
            latest_rina = requests.get("https://raw.githubusercontent.com/TransPlace-Devs/uncute-rina-revolt/main/Uncute_Rina.py").text
            latest_version = latest_rina.split("fileVersion = \"", 1)[1].split("\".split(\".\")", 1)[0]
            for i in range(len(latest_version.split("."))):
                if int(latest_version.split(".")[i]) > int(version.split(".")[i]):
                    await ctx.send(f"Bot is currently running on v{version} (latest: v{latest_version})\n(started at {self.startup_time.strftime('%Y-%m-%dT%H:%M:%S.%f')})")
                    return
            else:
                await ctx.send(f"Bot is currently running on v{version} (latest)\n(started at {self.startup_time.strftime('%Y-%m-%dT%H:%M:%S.%f')})")


        # Bot commands end
        # Bot events


        async def on_ready(self):
            debug(f"[######  ]: Started bot"+ " "*30,color="green")
            debug(f"[######+ ]: Loading server settings"+ " "*30,color="light_blue",end='\r')
            
            try:
                self.logChannel = await self.fetch_channel("01H33X24TYG9S6GFXXZVPH3JPH")
            except (revolt.errors.HTTPError, revolt.errors.Forbidden, Exception): # "Exception" raised in revolt.channel.channel_factory()
                if testing_environment == 3:
                    self.logChannel = await self.fetch_channel("01H35AM97PZW3166FDGK4FAN39")
            
            self.bot_owner = self.get_user("01H34JM6Y9GYG5E26FX5Q2P8PW") # for mentioning me on crashes
            self.prefixes.append(self.user.mention+" ")
            debug(f"[####### ]: Loaded server settings"+" "*30,color="green")

            await self.logChannel.send(f":white_check_mark: **Started Rina** in version {version}")
            debug(f"[########] Logged in as {self.user.name}, in version {version} (in {datetime.now()-program_start})",color="green")
        
        async def on_message_kill_test(self, message):
            # kill switch, see other modules for other on_message events.
            if message.author.id == self.bot_owner.id:
                if message.content == ":kill now please stop":
                    sys.exit(0)


        # Crash event handling

        async def send_crash_message(self, error_type: str, traceback_text: str, error_source: str, color: str, ctx: commands.Context=None):
            """
            Sends crash message to Rina's logging channel

            ### Parameters
            error_type: :class:`str`
                Is it an 'Error' or an 'AppCommand Error'
            traceback_text: :class:`str`
                What is the traceback?
            error_source: :class:`str`
                Name of the error source, displayed at the top of the message. Think of event or command.
            color: :class:`str`
                Color of the embed
            ctx (optional): :class:`commands.Context`
                Context with a potential server. This might allow Rina to send the crash log to that server instead
            """

            log_guild: revolt.Server
            try:
                log_guild = self.get_server(ctx.server_id)
                vcLog = await self.get_guild_info(ctx.server_id, "vcLog")
            except (AttributeError, KeyError, LookupError): # no guild settings, or the given messageable
                try:
                    log_guild = self.get_server("01H2Y4Y97PW6584PHN1TAVN5WR")
                except (revolt.errors.HTTPError, LookupError): # LookupError if get_server, HTTPError if fetch_server
                    if testing_environment == 3:
                        log_guild = self.get_server("01H35AM97P8B5YKPVATG88JY3F")
                    else:
                        raise ValueError("testing_environment variable out of range") # (shouldn't happen anyway)

                try:
                    vcLog = await self.get_guild_info(log_guild, "vcLog")
                except KeyError:
                    await self.logChannel.send("KeyError in get_guild_info while trying to log a crash!")
                    return # prevent infinite logging loops, i guess
            
            error_caps = error_type.upper()
            debug_message = f"\n\n\n\n[{datetime.now().strftime('%H:%M:%S.%f')}] [{error_caps}]: {error_source}\n\n{traceback_text}\n"
            debug(f"{debug_message}",add_time=False)

            try:
                channel = log_guild.get_channel(vcLog)
            except LookupError:
                await self.logChannel.send(f"LookupError on get_channel of vcLog of log_guild '{log_guild.name} ({log_guild.id})'")
                return
            msg = debug_message.replace("``", "`` ")#("\\", "\\\\").replace("*", "\\*").replace("`", "\\`").replace("_", "\\_").replace("~~", "\\~\\~")
            msg = "```\n" + msg.strip() + "\n```"
            embed = revolt.SendableEmbed(colour=color, title = error_type +' Log', description=msg)
            await channel.send(f"{self.bot_owner.mention}", embed=embed)

        async def on_error(self, event: str, *_args, **_kwargs):
            # msg = '\n\n          '.join([repr(i) for i in args])+"\n\n"
            # msg += '\n\n                   '.join([repr(i) for i in kwargs])
            msg = traceback.format_exc()
            await self.send_crash_message("Error", msg, event, "rgb(255, 77, 77)")

        async def on_command_error(self, ctx: commands.Context, exception: Exception | commands.errors.CommandNotFound):
            global commanderror_cooldown
            if int(mktime(datetime.now().timetuple())) - commanderror_cooldown < 60:
                # prevent extra log (prevent excessive spam and saving myself some large mentioning chain) if within 1 minute
                return

            if isinstance(exception, commands.errors.CommandNotFound):
                cmd_mention = self.get_command_mention("update")
                cmd_mention2 = self.get_command_mention("help")
                await ctx.send(f"This command doesn't exist! Perhaps the commands are unsynced. Ask {self.bot_owner.name}#{self.bot_owner.discriminator} if she typed {cmd_mention}!\n"
                               f"Perhaps you misspelled your command. Use {cmd_mention2} to check if you used the right command!")
                return
            elif isinstance(exception, RuntimeError):
                # TODO: add help() command to Client so you can call a docstring or help command of a function easily.
                await ctx.send("RuntimeError: Your command didn't have the right input! TODO.")
                return
            else:
                if hasattr(exception, 'original'):
                    error_reply = "Error "
                    if hasattr(exception.original, 'status'):
                        error_reply += str(exception.original.status)
                        # if error.original.status == "403":
                        #     await reply(itx, f"Error 403: It seems like I didn't have permissions for this action! If you believe this is an error, please message or ping {client.bot_owner}} :)")
                    if hasattr(exception.original, 'code'):
                        error_reply += "(" + str(exception.original.code) + ")"
                    await ctx.send(error_reply + f". Please report the error and details to {self.bot_owner.name}#{self.bot_owner.discriminator} by pinging her or sending her a DM")
                else:
                    await ctx.send("Something went wrong executing your command!\n    " + repr(exception)[:1700])

            try:
                msg = f"    Executor details: {ctx.author.name} ({ctx.author.id})\n"
            except Exception as ex:
                msg = f"    Executor details: couldn't get context author details: {repr(ex)}\n"
                #   f"    command: {error.command}\n" + \
                #   f"    arguments: {error.args}\n"
            if hasattr(exception, 'original'):
                if hasattr(exception.original, 'code'):
                    msg += f"    code: {exception.original.code}\n"
                if hasattr(exception.original, 'status'):
                    msg += f"    original error: {exception.original.status}: {exception.original.text}\n\n"
                        #    f"   error response:     {error.original.response}\n\n"
            if len(traceback.format_exc()) > 16: # 'NoneType: None\n', stupid solution, but it works, i guess
                msg += traceback.format_exc()
            else:
                msg += ''.join(traceback.format_exception(exception)) # returns list of lines (with \n included)
            await self.send_crash_message("Command Error", msg, f"{ctx.command.name}", "rgb(255,121,77)", ctx=ctx)
            commanderror_cooldown = int(mktime(datetime.now().timetuple()))

        # Crash event handling end
        # Bot events end


    debug(f"[#       ]: Loaded bot" + " " * 30, color="green")
    debug(f"[#+      ]: Starting Bot...", color="light_blue", end='\r')

    async def main(token):
        async with revolt.utils.client_session() as session:
            start = datetime.now()
            logging.getLogger("revolt").setLevel(logging.WARNING)
            client = Bot(session, token)
            client.on_message_events.append(client.on_message_kill_test)
            debug(f"[##      ]: Started Bot"+" "*30,color="green")

            extensions = [
                # "cmd_addons",
                "cmd_customvcs",
                # "cmd_emojistats",
                # "cmd_getmemberdata",
                # "cmd_pronouns",
                # "cmd_qotw",
                # "cmd_tags",
                "cmd_termdictionary",
                # "cmd_todolist",
                # "cmd_toneindicator",
                # "cmdg_Reminders",
                # "cmdg_Starboard",
                "utils",
            ]
            for extID in range(len(extensions)):
                debug(f"[{'#'*extID}+{' '*(len(extensions)-extID-1)}]: Loading {extensions[extID]}"+" "*15,color="light_blue",end='\r')
                client.load_extension(extensions[extID])

            debug(f"[###     ]: Loaded extensions successfully (in {datetime.now()-start})",color="green")
            # debug(f"[###+   ]: Restarting ongoing reminders"+" "*30,color="light_blue",end="\r")
            # collection = RinaDB["reminders"]
            # query = {}
            # db_data = collection.find(query)
            # for user in db_data:
            #     try:
            #         for reminder in user['reminders']:
            #             creationtime = datetime.fromtimestamp(reminder['creationtime'])#, timezone.utc)
            #             remindertime = datetime.fromtimestamp(reminder['remindertime'])#, timezone.utc)
            #             Reminders.Reminder(client, creationtime, remindertime, user['userID'], reminder['reminder'], user, continued=True)
            #     except KeyError:
            #         pass
            debug(f"[####    ]: Finished setting up reminders"+" "*30,color="yellow")
            # debug(f"[####+  ]: Caching bot's command names and their ids",color="light_blue",end='\r')
            # commandList = await client.tree.fetch_commands()
            # client.commandList = commandList
            debug(f"[#####   ]: Cached bot's command names and their ids"+" "*30,color="yellow")
            debug(f"[#####+  ]: Starting..."+" "*30,color="light_blue",end='\r')
            await client.start()

    asyncio.run(main(TOKEN))


# todo:
# - Translator
# - (Unisex) compliment quotes
# - Add error catch for when dictionaryapi.com is down
# - make more three-in-one commands have optional arguments, explaining what to do if you don't fill in the optional argument
