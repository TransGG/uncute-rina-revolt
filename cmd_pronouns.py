from Uncute_Rina import *
from import_modules import *

class Pronouns(commands.Cog):
    def __init__(self, client: Bot):
        global RinaDB
        RinaDB = client.RinaDB
        self.client = client

        # # setting ContextMenu here, because apparently you can't use that decorator in classes..?
        # self.ctx_menu_user = app_commands.ContextMenu(
        #     name='Pronouns',
        #     callback=self.pronouns_ctx_user,
        # )
        # self.ctx_menu_message = app_commands.ContextMenu(
        #     name='Pronouns',
        #     callback=self.pronouns_ctx_message,
        # )
        # self.client.tree.add_command(self.ctx_menu_user)
        # self.client.tree.add_command(self.ctx_menu_message)

    async def get_pronouns(self, ctx: commands.Context, user: revolt.Member | revolt.User):
        """
        Get the pronouns of a user depending on their roles

        ### Parameters
        --------------
        ctx: :class:`commands.Context`
            Context of the command- where to reply to
        user: :class:`revolt.Member` (or :class:`revolt.User`)
            The member to get roles from. If not a member, only outputs custom pronouns
        
        ### Output
        ----------
        Sends to ctx.message.reply
            The (custom) pronouns of the given user
        """
        collection = RinaDB["members"]
        query = {"member_id": user.id}
        data = collection.find_one(query)
        warning = ""
        if data is None:
            pronouns = []
        else:
            pronouns = data['pronouns']
        if len(pronouns) == 0:
            cmd_mention = self.client.get_command_mention("pronouns")
            warning = f"\nThis person hasn't added custom pronouns yet! (They need to use {cmd_mention} `mode:Add` `argument:<pronoun>` to add one)"

        list = []
        for pronoun in pronouns:
            if pronoun.startswith(":"):
                p = pronoun[1:]
                if p[-1] == "s":
                    pronoun = pronoun + " = " + ', '.join([p, p, p + "'", p + "'", p + "self"])
                else:
                    pronoun = pronoun + " = " + ', '.join([p, p, p+"'s", p+"'s", p+"self"])
            elif len(pronoun) > 500:
                pronoun = pronoun[:500]
            list.append("-> " + pronoun)

        if type(user) is discord.User:
            await ctx.message.reply("This person isn't in the server (anymore), so I can't see their pronouns from their roles!\n" +
                                    "So if they had custom pronouns, here's their list:\n"+'\n'.join(list)+warning, ephemeral=True, allowed_mentions=discord.AllowedMentions.none())
            return

        roles = []
        lowered_list = [i.lower() for i in list]
        pronoun_roles = ["he/him", "she/her", "they/them", "it/its", "any pronouns"]
        for role in user.roles:
            if role.name.lower() == "ask pronouns" and len(list) == 0:
                roles.append("This person has the 'Ask Pronouns' role, so ask them if they have different pronouns.")
            if role.name.lower() in pronoun_roles and role.name.lower() not in lowered_list:
                roles.append("=> " + role.name+" (from role)")
        list += roles

        if len(list) == 0:
            cmd_mention = self.client.get_command_mention("pronouns")
            await ctx.message.reply(f"This person doesn't have any pronoun roles and hasn't added any custom pronouns. Ask them to "
                                    f"add a role in #self-roles, or to use {cmd_mention} `mode:Add` `argument:<pronoun>`\nThey might "
                                    f"also have pronouns mentioned in their About Me.. I can't see that sadly, so you'd have to check yourself.")
        else:
            await ctx.message.reply(f"{user.nickname or user.name} ({user.id}) uses these pronouns:\n" + '\n'.join(list)+warning)
    
    # async def pronoun_autocomplete(self, itx: discord.Interaction, current: str):
    #     if itx.namespace.mode == 1:
    #         results = []
    #         for member in itx.guild.members:
    #             if member.nick is not None:
    #                 nick = current.lower() in member.nick.lower()
    #             else:
    #                 nick = False
    #             if current.lower() in member.name.lower():
    #                 name = str(member)
    #                 results.append(app_commands.Choice(name=name, value=member.mention))
    #             elif nick:
    #                 name = f"{member.nick}     ({member})"
    #                 results.append(app_commands.Choice(name=name, value=member.mention))
    #             if len(results) >= 10:
    #                 return results
    #         return results
    #     if itx.namespace.mode == 2:
    #         def get_pronouns():
    #             part = [
    #                 "She",
    #                 "Her",
    #                 "He",
    #                 "Him",
    #                 "They",
    #                 "Them",
    #                 "It",
    #                 "Its",
    #             ]
    #             part_loose = [
    #                 "Any",
    #                 "Any pronouns",
    #                 "Ask",
    #                 "Ask for pronouns",
    #                 "Hee/hee"
    #             ]
    #             results = []
    #             sections = current.lower().split("/")
    #             if len(sections) < 2:
    #                 suggestions = part_loose
    #                 for x in part:
    #                     for y in part:
    #                         suggestions.append(x+"/"+y)
    #                 for suggestion in suggestions:
    #                     if current.lower() in suggestion.lower():
    #                         results.append(suggestion)
    #             for pronoun_part in part_loose:
    #                 if current.lower() in pronoun_part.lower():
    #                     results.append(pronoun_part)
    #             for pronoun_part in part:
    #                 if sections[-1].lower() in pronoun_part.lower():
    #                     suggestion = "/".join(sections[:-1])+"/"+pronoun_part
    #                     results.append(suggestion)
    #             results.append(current)
    #             return results

    #         _results = get_pronouns()
    #         _temp = []
    #         results = []

    #         for result in _results:
    #             if result not in _temp:
    #                 results.append(app_commands.Choice(name=result, value=result))
    #                 _temp.append(result)
    #             if len(results) >= 10:
    #                 break
    #         return results
    #     if itx.namespace.mode == 3:
    #         staff_overwrite = False
    #         data = None
    #         if is_staff(itx) and " |" in current:
    #             sections = current.split(" |")
    #             if len(sections) == 2:
    #                 try:
    #                     user_id = int(sections[0])
    #                     collection = RinaDB["members"]
    #                     query = {"member_id": user_id}
    #                     data = collection.find_one(query)
    #                     staff_overwrite = True
    #                     current = sections[1].strip()
    #                 except ValueError:
    #                     pass
    #         if not staff_overwrite:
    #             # find results in database
    #             collection = RinaDB["members"]
    #             query = {"member_id": itx.user.id}
    #             data = collection.find_one(query)
    #         if data is None:
    #             return []
    #         else:
    #             pronouns = data['pronouns']

    #         if len(pronouns) == 0:
    #             return []
    #         if staff_overwrite:
    #             return [
    #                 app_commands.Choice(name=pronouns[index], value=str(index))
    #                 for index in range(len(pronouns)) if pronouns[index].lower().startswith(current.lower())
    #             ]
    #         return [
    #             app_commands.Choice(name=pronoun, value=pronoun)
    #             for pronoun in pronouns if pronoun.lower().startswith(current.lower())
    #         ]
    #     if itx.namespace.mode == 4:
    #         return [
    #             app_commands.Choice(name="This mode doesn't need an argument", value="None")
    #         ]
    #     return []

    @commands.command(name="pronouns", cls=CustomCommand, usage={
        "description":"Check, add, or remove (custom) pronouns!",
        "usage":"pronouns <mode> [argument...]",
        "examples":["pronouns check",
                    "pronouns add fae/faer/faer/faers/faerself",
                    "pronouns add :star",
                    "pronouns remove 0",
                    "pronouns help"],
        "parameters":{
            "mode":{
                "description":"Do you want to add/remove pronouns or just check them?",
                "type": CustomCommand.template("str",pre_defined=True, case_sensitive=False),
                "accepted values":"\"check\", \"add\", \"remove\", \"help\"",
            },
            "argument":{
                "description":"The pronoun you want to add, id of the one you want to remove, or user to check",
                "type": [CustomCommand.template("str", wrapped=True),
                         CustomCommand.template("int"),
                         CustomCommand.template("mention or ID", optional=True)],
                "additional info":["If you're checking pronouns or using the help feature, you can leave this blank",
                                   "To remove a custom pronoun, you fill in the ID, found by using mode:check",
                                   "To check someone else's pronoun, mention them or give their user-ID"]
            }
        }
    })
    async def pronouns_command(self, ctx: commands.Context, mode: str, *argument: str):
        argument = ' '.join(argument) if argument else None
        mode = mode.lower()

        if mode == "check": # Check
            if argument is not None:
                user = argument
                for i in "<\@>": # backslashes because you can ping someone without mentioning them if you use <\@ABC>
                    user = user.replace(i,"")
                try:
                    user_id = user
                except ValueError:
                    await ctx.message.reply("You need to give a valid user to get their pronouns!")
                    return
                user = ctx.server.get_member(user_id)
                if user is None:
                    user = ctx.client.get_user(user_id)
                    if user is None:
                        await ctx.message.reply("I couldn't find a user with that ID! Did you mention the right person? Perhaps they're not in the server anymore")
            else:
                user = ctx.author
            await self.get_pronouns(ctx, user)
        elif mode == "add": # Add
            if argument is None:
                await ctx.message.reply("You can add pronouns here. For example, \"she/her\", or \":Alex\". For more information about pronouns, "
                                        "or if you want to try out your own pronouns, check out <https://en.pronouns.page/pronouns>")
                return
            pronoun = argument
            warning = ""
            if not ("/" in pronoun or pronoun.startswith(":")):
                warning = "Warning: Others may not be able to know what you mean with these pronouns (it doesn't use an `x/y` or `:x` format)\n"
            collection = RinaDB["members"]
            query = {"member_id": ctx.author.id}
            data = collection.find_one(query)
            if data is None:
                # see if this user already has data, if not, add empty
                pronouns = []
            else:
                pronouns = data['pronouns']
            if pronoun in pronouns:
                await ctx.message.reply("You have already added this pronoun! You can't really put multiple of the same pronouns, that's be unnecessary..")
                return
            if len(pronouns) > 20:
                await ctx.message.reply("Having this many pronouns will make it difficult for others to pick one! Remove a few before adding a new one!")
                return
            if len(pronoun) > 90:
                await ctx.message.reply("Please make your pronouns shorter in length, or use this command multiple times / split up the text")
                return
            if pronoun.startswith(":") and len(pronoun) < 2:
                await ctx.message.reply("Please make your ':' pronoun more than 0 letters long...")
                return
            pronouns.append(pronoun)
            collection.update_one(query, {"$set": {f"pronouns": pronouns}}, upsert=True)
            cmd_mention = self.client.get_command_mention("pronouns")
            await ctx.message.reply(warning + f"Successfully added `{pronoun}`. Use {cmd_mention} `mode:Check` to see your custom pronouns, and use "
                                              f"{cmd_mention} `mode:Remove` `argument:pronoun` to remove one")
        elif mode == "remove": # Remove
            collection = RinaDB["members"]
            query = {"member_id": ctx.author.id}
            data = collection.find_one(query)
            if data is None:
                # see if this user already has data, if not, add empty
                cmd_mention = self.client.get_command_mention("pronouns")
                await ctx.message.reply(f"You haven't added pronouns yet! Use {cmd_mention} `mode:Add` `argument:<pronoun>` to add one!")
                return

            if argument is None:
                cmd_mention = self.client.get_command_mention("pronouns")
                await ctx.message.reply(f"You can remove pronouns with this command. Check the pronouns you have with the {cmd_mention} `mode:Check` command."
                                        f"If you have a pronoun you want to remove, write the pronoun in the 'argument' section of the command.")
                return
            pronoun = argument
            pronouns = data['pronouns']
            if pronoun not in pronouns:
                if is_staff(ctx):
                    # made possible with the annoying user '27', alt of Error, trying to break the bot :\
                    try:
                        member_id, pronoun = pronoun.split(" | ", 1)
                        query = {"member_id": int(member_id)}
                        data = collection.find_one(query)
                        if data is None:
                            # see if this user already has data, if not, add empty
                            cmd_mention = self.client.get_command_mention("pronouns")
                            await ctx.message.reply(f"This person hasn't added pronouns yet! Tell them to use {cmd_mention} `mode:Add` `argument:<pronoun>` "
                                                    f"to add one!")
                            return
                        pronouns = data['pronouns']
                        del pronouns[int(pronoun) - 1]
                    except ValueError:
                        cmd_mention = self.client.get_command_mention("pronouns")
                        await ctx.message.reply(f"If you are staff, and wanna remove a pronoun, then type `argument:USERID | PronounYouWannaRemove` "
                                                f"like {cmd_mention} `mode:Remove` `argument:4491185284728472 | 1`\nThe pronoun/item you wanna remove "
                                                f"will be in order of the pronouns, starting at 1 at the top. So if someone has 3 pronouns and you "
                                                f"wanna remove the second one, type '2'.")
                        return
                else:
                    cmd_mention = self.client.get_command_mention("pronouns")
                    await ctx.message.reply(f"You haven't added this pronoun yet, so I can't really remove it either! "
                                            f"Use {cmd_mention} `mode:Add` `argument:<pronoun>` to add one, or {cmd_mention} `mode:Check` "
                                            f"to see what pronouns you have added")
                    return
            else:
                pronouns.remove(pronoun)
            collection.update_one(query, {"$set": {f"pronouns": pronouns}}, upsert=True)
            await ctx.message.reply(f"Removed `{pronoun}` successfully!")
        elif mode == "help": # help
            cmd_mention = self.client.get_command_mention("pronouns")
            await ctx.message.reply(f"There are multiple ways to get a user's pronouns. The simplest of all is clicking their role. "
                                    f"However, sometimes the selection of roles is not enough to tell others your pronouns. In that "
                                    f"case, you can use {cmd_mention} `mode:Check` to see their pronouns.\n"
                                    f"\n"
                                    f"When adding a pronoun (using {cmd_mention} `mode:Add`), it will autocomplete potential pronoun "
                                    f"combinations.\n"
                                    f"Removing added pronouns (using {cmd_mention} `mode:Remove`) is made easy by the autocompletion "
                                    f"of your already-added pronouns.\n"
                                    f"\n"
                                    f"You can also use the context menu buttons on users or messages to see the message author's "
                                    f"pronouns. You can find these by right-clicking the message or user, hover over 'Apps', and "
                                    f"click 'Pronouns'.")

    # async def pronouns_ctx_user(self, itx: discord.Interaction, user: discord.User):
    #     await self.get_pronouns(itx, user)

    # async def pronouns_ctx_message(self, itx: discord.Interaction, message: discord.Message):
    #     await self.get_pronouns(itx, message.author)

def setup(client):
    # client.add_command(getMemberData)
    client.add_cog(Pronouns(client))
