from Uncute_Rina import *
from import_modules import *

ID_LENGTH = 5
ID_CHARS = "abcdefghijklmnopqrstuvwxyz"
def generate_id() -> str:
    """
    Generate a random ID from the pre-set constants
    """
    return ''.join(random.choices(ID_CHARS, k=ID_LENGTH))

template = {
    "owner_id":"01A38YRYFPFYYWA2E21GN3VFX4",
    "system":{
        "id":"fewnj",
        "name":"StarSystem",
        "description":"A system for All Stars",
        "tag":"🌀",
        "color":"#00ff00", # embed color
        "fronter":"enjww", # member id
        # "avatar":"",
        "members":[
            {
                "id":"enjww",
                "name":"MysticMia",
                "display_name":"Mia",
                "server_name":"Mimi",
                "description":"A girl with name",
                "pronouns":"She/her",
                "color":"#299ff0",
                "birthday": datetime(2000,12,31),
                "proxy":["M:"],
                "avatar":"https://imgur.com/enjww.png",
            },
            {...},
        ]
    },
}

class Member(TypedDict):
    id: str
    created_at: int
    name: str
    display_name: Optional[str]
    server_name: Optional[str]
    description: Optional[str]
    pronouns: Optional[str]
    colour: Optional[str] # hex color
    birthday: Optional[str]
    proxy: Optional[str]
    avatar: Optional[str]
    message_count: int

class System(TypedDict):
    id: str
    created_at: int
    name: Optional[str] # len(name) >= 2
    display_name: Optional[str]
    description: Optional[str]
    tag: Optional[str]
    colour: Optional[str] # hex color
    fronter: Optional[str]
    avatar: Optional[str]
    members: Optional[list[Member]]

class OwnerData(TypedDict):
    owner_id: str
    system: Optional[System]

# can search by ID and by name
# if none, assume there's only one.

class NotFound(Exception):
    pass


async def get_owner(ctx: commands.Context | revolt.Message = None, id: str = None) -> OwnerData:
    """
    Get the system dictionary of a person from their ID

    ### Parameters
    --------------
    ctx: :class:`commands.Context` | :class:`revolt.Message`
        The context of the command. Used for getting a default owner ID if none given
    id (optional): :class:`str`
        The id of the user to get the system dictionary for

    ### Raises
    ----------
    :class:`NotFound`
        If no results with owner id

    ### Returns
    -----------
    :class:`OwnerData`
        A dictionary with 'owner_id' and 'system' keys
    """
    if id is None:
        id = ctx.author.id
    collection: motor.core.AgnosticCollection = asyncRinaDB["pluralkit_data"]
    query = {"owner_id": id}
    data: OwnerData|None = await collection.find_one(query)
    if data is None:
        raise NotFound("No data for this owner id")
    return data

async def get_system(ctx: commands.Context | revolt.Message, id: str = None, owned=True) -> System:
    """
    Get a System from an id (or name (using ctx.author.id))

    ### Parameters
    --------------
    ctx: :class:`commands.Context` | :class:`revolt.Message`
        The context of the command. Used for getting a default owner ID for searching with name
    id (optional): :class:`str`
        The id of the system

    ### Raises
    ----------
    :class:`NotFound`
        If no data found for system id (note: if owned is True, it only checks for the system id that the owner owns)

    ### Returns
    -----------
    :class:`System`
        A System dictionary from given name or id
    """
    if id is None:
        return (await get_owner(ctx))["system"]
    
    collection: motor.core.AgnosticCollection = asyncRinaDB["pluralkit_data"]
    if owned:
        query = {"owner_id": ctx.author.id}
    else:
        query = {}
    # get owner.system.id == id
    query["system.id"] = id.lower()
    data: OwnerData|None = await collection.find_one(query)

    if data is None:
        raise NotFound("User does not have a system")
    return data["system"]

async def get_system_from_member(ctx: commands.Context | revolt.Message, name: str = None, id: str = None, owned=True, return_member=False) -> System:
    """
    Get a System from a system member's id (or name (using ctx.author.id))

    ### Parameters
    --------------
    ctx: :class:`commands.Context` | :class:`revolt.Message`
        The context of the command. Used for getting a default owner ID for searching with name
    name (optional): :class:`name`
        The name of the member (looks in ctx.author.id's system)
    id (optional): :class:`str`
        The id of the system
    owned (optional): :class:`bool`
        Whether to look for the executor's owned system or for anyone's (default: True)

    ### Raises
    ----------
    :class:`NotFound`
        If no members, no system, or no member with this id or name found

    ### Returns
    -----------
    :class:`System`
        A System dictionary from given name or id
    """
    assert name or id
    collection = asyncRinaDB["pluralkit_data"]
    error = 0
    if id:
        # get owner.system.members.id == id
        query = {"system.members":{"$elemMatch":{"id":id.lower()}}}
        if owned:
            query["owner_id"] = ctx.author.id
        data: OwnerData|None = await collection.find_one(query)
        if data is None:
            error += 1
        else:
            for member in data["system"]["members"]:
                if member["id"].lower() == id.lower():
                    if return_member:
                        return data["system"], member
                    return data["system"]
    if name:
        # get owner.system.members.name == name (case sensitive)
        query = {"owner_id": ctx.author.id,
                 "system.members":{"$elemMatch":{"name":name}}}
        data: OwnerData|None = await collection.find_one(query)
        if data is None:
            error += 1
        else:
            for member in data["system"]["members"]:
                if member["name"] == name:
                    if return_member:
                        return data["system"], member
                    return data["system"]
    if error: # no result
        raise NotFound("Member not found")
    # shouldn't happen cause it only returns positive values
    # raise NotFound("No results")

async def get_owner_from_system(ctx: commands.Context | revolt.Message, name: str = None, id: str = None) -> OwnerData:
    """
    Get the system dictionary of a person from a server's ID or name

    ### Parameters
    --------------
    ctx: :class:`commands.Context` | :class:`revolt.Message`
        The context to get the ctx.author.id's system for getting the system name
    name (optional): :class:`name`
        The name of the system (looks in ctx.author.id's system) (case sensitive)
    id (optional): :class:`str`
        The id of the system

    ### Raises
    ----------
    :class:`NotFound`
        If no system with this name or id found

    ### Returns
    -----------
    :class:`System`
        A System dictionary from given name or id
    """
    assert name or id
    collection = asyncRinaDB["pluralkit_data"]
    error = 0
    if id:
        query = {"system.id":id.lower()}
        data: OwnerData|None = await collection.find_one(query)
        if data is None:
            error += 1
    if name and not error:
        query = {"owner_id": ctx.author.id, 
                 "system.name":name}
        data: OwnerData|None = await collection.find_one(query)
        if data is None:
            error += 1
    if error: # no result
        raise NotFound("System not found")
    return data


############################
 #     Util functions     # 
############################

async def check_system(ctx: commands.Context, system_name_or_id: str) -> OwnerData | None:
    """
    Check if a user has a system (with this name/id)

    ### Parameters
    --------------
    ctx: :class:`commands.Context`
        The context of the user whose system to check, and who to reply to if no results.
    system_name_or_id: :class:`str`
        The name or id of the system to look for

    ### Output
    ----------
    Sends message to user if no system found

    ### Returns
    -----------
    :class:`NoneType`
        If no system found, replies message to user.
    :class:`OwnerData`
        dictionary with owner_id and system that matches given name or id
    """
    try:
        owner = await get_owner(ctx)
    except NotFound:
        await ctx.message.reply("You don't have a system yet, so you can't change/view its properties either!")
        return
    if owner["system"]["id"].lower() != system_name_or_id.lower() and \
        owner["system"].get("name", "").lower() != system_name_or_id.lower():
        await ctx.message.reply("The system id you provided was not the same as the system you own. Perhaps you mistyped something?\n"
                                f"- System name: {safe_string(owner['system']['name'])}\n"
                                f"- System id: {owner['system']['id']}\n"
                                f"- Given name or id: {safe_string(system_name_or_id)}")
        return
    return owner

async def check_member(ctx: commands.Context, member_name_or_id: str, return_system=False) -> Member | tuple[Member, System] | None:
    try:
        system = await get_system_from_member(ctx, name=member_name_or_id, id=member_name_or_id)
    except NotFound:
        await ctx.message.reply("I couldn't find that member in your system!")
        return
    
    for member in system["members"]:
        if member["id"] == member_name_or_id:
            break
    else:
        for member in system["members"]:
            if member["name"] == member_name_or_id:
                break
        else:
            raise Exception("This shouldn't happen...?") # but it does help resolve 'unbound' typing check
    if return_system:
        return (member, system)
    else:
        return member

class PluralKit(commands.Cog):
    def __init__(self, client: Bot):
        global asyncRinaDB
        client.on_message_events.append(self.on_message_pk)
        asyncRinaDB = client.asyncRinaDB
        self.pk_data = asyncRinaDB["pluralkit_data"]
        self.client = client


    #############################
     #     System commands     # 
    #############################

    async def system_command(self, ctx: commands.Context):
        try:
            owner: OwnerData = await get_owner(ctx)
            system = owner["system"]
            if system is None:
                raise NotFound
            
            description = "" if system.get("members") else "This system has no members"
            display_name = ((system.get("display_name") or system.get("name") or "") + f" ({system['id']})").strip()
            embed = CustomEmbed(title=f"Members of {display_name}", description=description,
                                colour=system.get("colour", None))

            members = 0
            pages = []
            for member in system.get("members", []):
                name = member.get("display_name", None)
                if name is None:
                    name = member["name"]
                else:
                    name += " (" + member["name"] + ")"

                description = "**ID**: `" + member["id"] + "`"
                for key in member:
                    if key in ["name", "id", "display_name", "created_at", "avatar"]:
                        continue
                    description += f"\n**{key.capitalize()}**: {str(member[key]).capitalize()}"
                
                embed.add_field(name=name, value=description)
                members += 1
                if members % 3 == 0: # 3 members per page
                    pages.append(embed)
                    embed = CustomEmbed(title=f"Members of `{system['id']}`", description="")
            if pages:
                await PagedMessage(self.client, ctx, pages).send()
            else:
                await ctx.message.reply(embed=embed)
                
        except NotFound:
            cmd_mention = self.client.get_command_mention("system new")
            await ctx.message.reply(f"You do not have a system registered. To create one, use {cmd_mention}.")
            return

    system_cmds = CustomGroup(callback=system_command, name="system", usage={
        "description":"View or modify your system",
        "usage":"system [subcommand] ...",
        "parameters":{
            "subcommand":{
                "description":"The modification you want to apply",
                "type": CustomCommand.template("subcommand", pre_defined=True, optional=True),
                # "accepted values":"\"new\""
            }
        }
    })


    @system_cmds.command(cls=CustomCommand, name="view", usage={
        "description":"View a system",
        "usage":"system view <system_id>",
        "examples":"system view xrzme",
        "parameters":{
            "system_id":{
                "description":"The id of the server you want to view",
                "type": CustomCommand.template("ID")
            }
        }
    })
    async def view_system(self, ctx: commands.Context, system_id: str):
        try:
            system: System = await get_system(ctx, id=system_id, owned=False)
            
            description = "" if system.get("members") else "This system has no members"
            display_name = ((system.get("display_name") or system.get("name") or "") + f" ({system['id']})").strip()
            embed = CustomEmbed(title=f"Members of {display_name}", description=description,
                                colour=system.get("colour", None))

            members = 0
            pages = []
            for member in system.get("members", []):
                name = member.get("display_name", None)
                if name is None:
                    name = member["name"]
                else:
                    name += " (" + member["name"] + ")"

                description = "**ID**: `" + member["id"] + "`"
                for key in member:
                    if key in ["name", "id", "display_name", "created_at", "avatar"]:
                        continue
                    description += f"\n**{key.capitalize()}**: {str(member[key]).capitalize()}"
                
                embed.add_field(name=name, value=description)
                members += 1
                if members % 3 == 0: # 3 members per page
                    pages.append(embed)
                    embed = CustomEmbed(title=f"Members of `{system['id']}`", description="")
            if pages:
                await PagedMessage(self.client, ctx, pages).send()
            else:
                await ctx.message.reply(embed=embed)
                
        except NotFound:
            await ctx.message.reply(f"Could not find any system with id `{safe_string(system_id)}`!")

    @system_cmds.command(cls=CustomCommand, name="new", usage={
        "description":"Make a new system.",
        "usage":"system new [name] [display_name...]",
        "examples":["system new starsystem Star System",
                    "system new"],
        "parameters":{
            "name":{
                "description":"The name of your new system",
                "type": CustomCommand.template("str", case_sensitive=True, wrapped=False),
                "additional info": [
                    "It's recommended to make this 1 word, because you can use it for all other commands",
                    "You're better off setting the display name to multiple words rather than the system name.",
                    "Use `system rename` to rename a system and `system displayname` to change the display name"
                ]
            },
            "display_name":{
                "description":"The name of your new system",
                "type": CustomCommand.template("str", wrapped=True),
                "note":"If you want a display name, you also have to give `name` a value, due to the way command input is read."
            }
        }
    })
    async def new_system(self, ctx: commands.Context, name: str = None, *display_name: str):
        display_name = ' '.join(display_name)
        try:
            owner = await get_owner(id=ctx.author.id)
            if owner["system"]:
                cmd_mention = self.client.get_command_mention("system")
                cmd_mention2 = self.client.get_command_mention("system delete")
                await ctx.message.reply(f":x: You already have a system registered. To view it, type {cmd_mention}. If you'd "
                                        f"like to delete your system and start anew, type {cmd_mention2}"
                                        # ", or if you'd like to unlink this account from it, type pk;unlink"
                                        "."
                                        )
                return
        except NotFound:
            pass
        while True:
            system_id = generate_id()
            try:
                await get_system(ctx, id=system_id, owned=False)
            except NotFound:
                break
        system = System(created_at=mktime(datetime.now().timetuple()), id=system_id)
        if name:
            system["name"] = name
        if display_name:
            system["display_name"] = display_name
        
        await asyncRinaDB["pluralkit_data"].update_one(OwnerData(owner_id=ctx.author.id), 
                                      {"$set": {"system": system}}, upsert=True)
        if display_name: 
            # Code could be simplified but this is probably the easiest to comprehend
            await ctx.message.reply(f"Created your system ({safe_string(display_name)} (`{safe_string(name)}`)) successfully! (id: `{system_id}`)")
        elif name:
            await ctx.message.reply(f"Created your system (`{safe_string(name)}`) successfully! (id: `{system_id}`)")
        else:
            await ctx.message.reply(f"Created your system (unnamed) successfully! (id: `{system_id}`)")

    @system_cmds.command(cls=CustomCommand, name="delete", usage={
        "description":"Delete your system.",
        "usage":"system delete <system_id>",
        "examples":"system delete wtmlo",
        "parameters":{
            "system_id":{
                "description":"The id of your system (for safety reasons)",
                "type": CustomCommand.template("ID"),
            }
        }
    })
    async def delete_system(self, ctx: commands.Context, system_id: str):
        try:
            owner = await get_owner(ctx)
            owner["system"]
        except (NotFound, KeyError):
            await ctx.message.reply("You don't have a system yet, so you can't remove one either!")
            return
        if owner["system"]["id"].lower() != system_id.lower():
            await ctx.message.reply("The system id you provided was not the same as the system you own. Perhaps you mistyped something?\n"
                                     f"- System id: {owner['system']['id'].lower()}\n"
                                    f"- Given id: {system_id.lower()}")
            return
        await asyncRinaDB["pluralkit_data"].delete_one(OwnerData(owner_id=ctx.author.id))
        await ctx.message.reply(f"Deleted your system (id: `{system_id}`) successfully.")

    @system_cmds.command(cls=CustomCommand, name="rename", usage={
        "description":"Rename your system.",
        "usage":"system rename <system> <new_name>",
        "examples":["system rename mia MysticMia",
                    "system rename wtmlo MysticMia"],
        "parameters":{
            "system":{
                "description":"The id or name of your system",
                "type": CustomCommand.template("str"),
            },
            "new_name":{
                "description":"The new name for your system",
                "type": CustomCommand.template("str", wrapped=False),
            }
        }
    })
    async def rename_system(self, ctx: commands.Context, system: str, name: str):
        if not (owner := await check_system(ctx, system)):
            return
        old_name = owner["system"].get("name", "unnamed")
        owner["system"]["name"] = name
        await asyncRinaDB["pluralkit_data"].update_one(OwnerData(owner_id=ctx.author.id), 
                {"$set": {"system": owner["system"]}})
        await ctx.message.reply(f"Renamed your system from `{safe_string(old_name)}` to `{safe_string(name)}` successfully.")

    @system_cmds.command(cls=CustomCommand, name="displayname", usage={
        "description":"Change the display name of your system.",
        "usage":"system displayname <system> <display_name>",
        "examples":["system displayname mia MysticMia",
                    "system displayname wtmlo MysticMia"],
        "parameters":{
            "system":{
                "description":"The id or name of your system",
                "type": CustomCommand.template("str"),
            },
            "display_name":{
                "description":"The new displayname for your system",
                "type": CustomCommand.template("str", optional=True, wrapped=True),
                "accepted value":"Leave blank to reset (will then show system name or id instead of displayname)"
            }
        }
    })
    async def change_system_displayname(self, ctx: commands.Context, system: str, *display_name: str):
        display_name = ' '.join(display_name)
        if not (owner := await check_system(ctx, system)):
            return
        old_display_name = owner["system"].get("display_name", "unnamed")
        if display_name:
            owner["system"]["display_name"] = display_name
            await asyncRinaDB["pluralkit_data"].update_one(OwnerData(owner_id=ctx.author.id), 
                    {"$set": {"system": owner["system"]}}, upsert=True)
            await ctx.message.reply(f"Changed your system's display name from **{safe_string(old_display_name)}** to **{safe_string(display_name)}** successfully.")
        else:
            if "display_name" in owner["system"]:
                del owner["system"]["display_name"]
                await asyncRinaDB["pluralkit_data"].update_one(OwnerData(owner_id=ctx.author.id), 
                        {"$set": {"system": owner["system"]}}, upsert=True)
            await ctx.message.reply(f"Reset your system's display name (from **{safe_string(old_display_name)}**) successfully.")

    @system_cmds.command(cls=CustomCommand, name="description", usage={
        "description":"Change the description of your system.",
        "usage":"system description <system> [description...]",
        "examples":["system description Galaxia A cool description for this system.",
                    "system description wtmlo Super cool description."],
        "parameters":{
            "system":{
                "description":"The id or name of your system",
                "type": CustomCommand.template("str"),
            },
            "description":{
                "description":"The new description for your system",
                "type": CustomCommand.template("str", optional=True, wrapped=True),
                "additional info":[
                    "Leave blank to clear",
                    "Due to commands not allowing newlines, type [[\"\\n\"]] at the beginning of each new line if you want to add newlines"
                ]
            }
        }
    })
    async def change_system_description(self, ctx: commands.Context, system: str, *description: str):
        description = ' '.join(description).replace("[[\\n]]", "\n")
        if not (owner := await check_system(ctx, system)):
            return
        if description:
            owner["system"]["description"] = description
            await asyncRinaDB["pluralkit_data"].update_one(OwnerData(owner_id=ctx.author.id), 
                    {"$set": {"system": owner["system"]}}, upsert=True)
            await ctx.message.reply(f"Changed your system's description successfully.")
        else:
            if "description" in owner["system"]:
                del owner["system"]["description"]
                await asyncRinaDB["pluralkit_data"].update_one(OwnerData(owner_id=ctx.author.id), 
                        {"$set": {"system": owner["system"]}}, upsert=True)
            await ctx.message.reply(f"Reset your system's description successfully.")

    @system_cmds.command(cls=CustomCommand, name="colour", aliases=["color"], usage={
        "description":"Change the color of your system.",
        "usage":"system colour <system> [colour]",
        "examples":["system colour Galaxia #044932",
                    "system colour wtmlo #ff0088"],
        "parameters":{
            "system":{
                "description":"The id or name of your system",
                "type": CustomCommand.template("str"),
            },
            "colour":{
                "description":"The new colour for your system",
                "type": CustomCommand.template("str", optional=True, case_sensitive=False),
                "Accepted values":"Must be a hex colour code (#000000 for black, #FFFFFF for white)",
                "additional info":"Leave blank to clear"
            }
        }
    })
    async def change_system_colour(self, ctx: commands.Context, system: str, colour: str):
        colour = colour.lower()
        if not colour.startswith("#") or len(colour) != 7:
            await ctx.message.reply("Invalid colour given! Please give a hex color code like \"#00ff00\" or \"#ffffff\"")
        if not all([char in "0123456789abcdef" for char in colour[1:]]):
            await ctx.message.reply("Your colour contained invalid characters! A color should only contain numbers and letters from 0-9 and a-f")
        if not (owner := await check_system(ctx, system)):
            return
        
        if colour:
            owner["system"]["colour"] = colour
            await asyncRinaDB["pluralkit_data"].update_one(OwnerData(owner_id=ctx.author.id), 
                    {"$set": {"system": owner["system"]}}, upsert=True)
            await ctx.message.reply(f"Changed your system's colour successfully.")
        else:
            if "colour" in owner["system"]:
                del owner["system"]["colour"]
                await asyncRinaDB["pluralkit_data"].update_one(OwnerData(owner_id=ctx.author.id), 
                        {"$set": {"system": owner["system"]}}, upsert=True)
            await ctx.message.reply(f"Reset your system's colour successfully.")

    @system_cmds.command(cls=CustomCommand, name="tag", usage={
        "description":"Change the tag of your system.",
        "usage":"system tag <system> [tag]",
        "examples":["system tag Galaxia 🌀",
                    "system tag wtmlo 01H34CB442REBZGJMTZXDMJTTC",
                    "system tag wtmlo :01H34CB442REBZGJMTZXDMJTTC:"],
        "parameters":{
            "system":{
                "tag":"The id or name of your system",
                "type": CustomCommand.template("str"),
            },
            "tag":{
                "tag":"The new tag for your system",
                "type": CustomCommand.template("emoji (or ID)", optional=True),
            }
        }
    })
    async def change_system_tag(self, ctx: commands.Context, system: str, tag: str):
        tag = tag.replace(":", "")
        if not (owner := await check_system(ctx, system)):
            return
        if tag:
            owner["system"]["tag"] = tag
            await asyncRinaDB["pluralkit_data"].update_one(OwnerData(owner_id=ctx.author.id), 
                    {"$set": {"system": owner["system"]}}, upsert=True)
            await ctx.message.reply(f"Changed your system's tag successfully.")
        else:
            if "tag" in owner["system"]:
                del owner["system"]["tag"]
                await asyncRinaDB["pluralkit_data"].update_one(OwnerData(owner_id=ctx.author.id), 
                        {"$set": {"system": owner["system"]}}, upsert=True)
            await ctx.message.reply(f"Reset your system's tag successfully.")


    #############################
     #     Member commands     # 
    #############################

    async def member_command(self, ctx: commands.Context, member_str: str):
        cmd_mention = self.client.get_command_mention("member view")
        cmd_mention2 = self.client.get_command_mention("help")
        await ctx.message.reply(f"Use {cmd_mention} `<member>` to see a member's information\n"
                                f"Use {cmd_mention2} `member` to learn more about this command and its subcommands")

    member_cmds = CustomGroup(callback=member_command, name="member", usage={
        "description":"View or modify a member of your system",
        "usage":"member [subcommand or name] ...",
        "parameters":{
            "subcommand or name":{
                "description":"The modifications you want to apply, or the member you want to check",
                "type": [CustomCommand.template("subcommand", pre_defined=True, optional=True),
                         CustomCommand.template("str")]
            }
        }
    })

    
    @member_cmds.command(cls=CustomCommand, name="view", usage={
        "description":"View a member in your system.",
        "usage":"member view <member>",
        "examples":"member view johnsmith",
        "parameters":{
            "member":{
                "description":"The name or id of this member",
                "type": CustomCommand.template("str"),
            },
        }
    })
    async def view_member(self, ctx: commands.Context, member_str: str):
        if not (_temp := await check_member(ctx, member_str, return_system=True)):
            return
        
        member, system = _temp

        embed = CustomEmbed(title=f"viewing member '{member['id']}'")
        if member.get('colour'):
            embed.colour = member["colour"]
        
        name = member.get("display_name", None)
        if name is None:
            name = member["name"]
        else:
            name += " (" + member["name"] + ")"
        description = ""
        for key in member:
            if key in ["name", "id", "display_name", "created_at"]:
                continue
            description += f"\n**{key.capitalize()}**: {str(member[key]).capitalize()}"

        embed.add_field(name=name, value=description.strip() or None)
        embed.set_footer(f"System ID: `{system['id']}`")
        await ctx.message.reply(embed=embed)

    @member_cmds.command(cls=CustomCommand, name="new", usage={
        "description":"Create a new member in your system.",
        "usage":"member new <name> [display_name...]",
        "examples":["member new johnsmith John Smith",
                    "member new \"John Andrew Smith\" John Smith"],
        "parameters":{
            "name":{
                "description":"The name of this member",
                "type": CustomCommand.template("str", wrapped=False),
                "additional info": [
                    "It's recommended to make this 1 word, because you use it for all other commands",
                    "You're better off setting the display name to multiple words rather than the member name.",
                    "Use `member rename` to rename a member and `member displayname` to change their display name"
                ]
            },
            "display_name":{
                "description":"The display name of this member",
                "type": CustomCommand.template("str", optional=True, wrapped=True),
            }
        }
    })
    async def new_member(self, ctx: commands.Context, name: str, *display_name: str):
        display_name = ' '.join(display_name)
        try:
            system = await get_system_from_member(ctx, name=name)
            cmd_mention = self.client.get_command_mention("member rename")
            cmd_mention2 = self.client.get_command_mention("member displayname")
            await ctx.message.reply("Warning: you already have a member with this name. When searching, the first one gets selected. "
                                    "This might lead you to edit the wrong member if you edit them by name instead of id. I personally "
                                    "suggest changing the name slightly, and then setting the display name to the name you want to use. "
                                    "That way, there's no confusion about which member is which, if you do try to edit the member with "
                                    "their name.\n"
                                    f"Use {cmd_mention} to rename a member and {cmd_mention2} to change a member's display name.")
            # I intentionally don't have a return statement here. I think it should be fine without.
            # (top 10 things said before disaster)
        except NotFound:
            pass
        while True:
            member_id = generate_id()
            try:
                await get_system_from_member(ctx, id=member_id, owned=False)
            except NotFound:
                break
        system = await get_system(ctx)
        member = Member(created_at=mktime(datetime.now().timetuple()), id=member_id, name=name)
        if display_name:
            member["display_name"] = display_name
        members = system["members"] if system.get("members") else []
        members.append(member)
        system["members"] = members

        await asyncRinaDB["pluralkit_data"].update_one(OwnerData(owner_id=ctx.author.id), 
                                      {"$set": {"system":system}})
        if display_name:
            await ctx.message.reply(f"Successfully added a member (**{safe_string(display_name)}** (`{safe_string(name)}`)) to your system! (member_id: `{member['id']}`)")
        else:
            await ctx.message.reply(f"Successfully added a member (`{safe_string(name)}`) to your system! (member_id: `{member['id']}`)")

    @member_cmds.command(cls=CustomCommand, name="delete", usage={
        "description":"Delete a member from your system",
        "usage":"member delete <member_id>",
        "examples":"member delete johnsmith",
        "parameters":{
            "member_id":{
                "description":"The id of the member you want to delete",
                "type": CustomCommand.template("ID"),
            }
        }
    })
    async def delete_member(self, ctx: commands.Context, member_id: str):
        try:
            system = await get_system_from_member(ctx, id=member_id)
        except (NotFound, KeyError):
            await ctx.message.reply("Couldn't find this member in your system! Make sure to give the ID of the member you want to delete (for safety purposes)")
            return
        members = system["members"]
        for member_index in range(len(members)):
            if members[member_index]["id"] == member_id:
                member = members[member_index]
                del members[member_index]
        system["members"] = members
        if "fronter" in system:
            del system["fronter"]
        # await ctx.message.reply("The system id you provided was not the same as the system you own. Perhaps you mistyped something?\n"
        #                         f"- System id: {owner['system']['id'].lower()}\n"
        #                         f"- Given id: {system_id.lower()}")
        # return
        await asyncRinaDB["pluralkit_data"].update_one(OwnerData(owner_id=ctx.author.id), 
                                      {"$set": {"system":system}})
        await ctx.message.reply(f"Removed member (name:`{member['name']}`, id: `{member_id}`) from your system successfully.")

    @member_cmds.command(cls=CustomCommand, name="rename", usage={
        "description":"Rename a member in your system.",
        "usage":"member rename <member> <new_name>",
        "examples":["member rename mia MysticMia",
                    "member rename wtmlo MysticMia"],
        "parameters":{
            "member":{
                "description":"The id or name of this member",
                "type": CustomCommand.template("str"),
            },
            "new_name":{
                "description":"The new name for this member",
                "type": CustomCommand.template("str", wrapped=False),
            }
        }
    })
    async def rename_member(self, ctx: commands.Context, member_str: str, name: str):
        if not (_temp := await check_member(ctx, member_str, return_system=True)):
            return
        member, system = _temp
        for member_index in range(len(system["members"])):
            if system["members"][member_index]["id"] == member["id"]:
                break
        else:
            raise Exception("This shouldn't happen...")
        
        old_name = system["members"][member_index]["name"]
        system["members"][member_index]["name"] = name
        await asyncRinaDB["pluralkit_data"].update_one(OwnerData(owner_id=ctx.author.id), 
                {"$set": {"system": system}})
        await ctx.message.reply(f"Renamed this member from `{safe_string(old_name)}` to `{safe_string(name)}` successfully.")

    @member_cmds.command(cls=CustomCommand, name="displayname", usage={
        "description":"Change the display name of a member in your system.",
        "usage":"member displayname <member> [display_name]",
        "examples":["member displayname mia MysticMia",
                    "member displayname wtmlo MysticMia"],
        "parameters":{
            "member":{
                "description":"The id or name of this member",
                "type": CustomCommand.template("str"),
            },
            "display_name":{
                "description":"The new display name for this member",
                "type": CustomCommand.template("str", wrapped=True, optional=True),
                "accepted value":"Leave blank to reset (will then show member name instead of displayname)"
            }
        }
    })
    async def change_member_displayname(self, ctx: commands.Context, member_str: str, *display_name: str):
        display_name = ' '.join(display_name)
        if not (_temp := await check_member(ctx, member_str, return_system=True)):
            return
        member, system = _temp
        for member_index in range(len(system["members"])):
            if system["members"][member_index]["id"] == member["id"]:
                break
        else:
            raise Exception("This shouldn't happen...")
        
        old_display_name = system["members"][member_index].get("display_name", "No display name")
        if display_name:
            system["members"][member_index]["display_name"] = display_name
        else:
            del system["members"][member_index]["display_name"]

        await asyncRinaDB["pluralkit_data"].update_one(OwnerData(owner_id=ctx.author.id), 
                {"$set": {"system": system}})
        if display_name:
            await ctx.message.reply(f"Changed this member's display name from **{safe_string(old_display_name)}** to **{safe_string(display_name)}** successfully.")
        else:
            await ctx.message.reply(f"Reset this member's display name successfully.")

    @member_cmds.command(cls=CustomCommand, name="avatar", usage={
        "description":"Change the avatar of a member in your system.",
        "usage":"member avatar <member> [avatar_url]",
        "examples":["member displayname mia https://imgur.com/reeee.png",
                    "member displayname wtmlo "],
        "parameters":{
            "member":{
                "description":"The id or name of this member",
                "type": CustomCommand.template("str"),
            },
            "avatar_url":{
                "description":"The new avatar for this member",
                "type": CustomCommand.template("str", wrapped=True, optional=True),
                "accepted value":"Leave blank to reset (will then show default avatar)"
            }
        }
    })
    async def change_member_avatar(self, ctx: commands.Context, member_str: str, avatar: str):
        if not (_temp := await check_member(ctx, member_str, return_system=True)):
            return
        member, system = _temp
        for member_index in range(len(system["members"])):
            if system["members"][member_index]["id"] == member["id"]:
                break
        else:
            raise Exception("This shouldn't happen...")
        
        system["members"][member_index]["avatar"] = avatar
        await asyncRinaDB["pluralkit_data"].update_one(OwnerData(owner_id=ctx.author.id), 
                {"$set": {"system": system}})
        if avatar:
            await ctx.message.reply(f"Changed this member's avatar successfully.")
        else:
            await ctx.message.reply(f"Reset this member's avatar successfully.")


    ################################
     #     Autoproxy commands     # 
    ################################

    async def autoproxy_command(self, ctx: commands.Context):
        try:
            system = await get_system(ctx)
        except NotFound:
            cmd_mention = self.client.get_command_mention("system new")
            await ctx.message.reply(f"Make a system so you can set an autoproxy. Use {cmd_mention} to make a system")
            return
        if "members" not in system:
            cmd_mention = self.client.get_command_mention("member new")
            await ctx.message.reply(f"Add a member so you can set an autoproxy. Use {cmd_mention} to add a member to your system")
            return
        if "fronter" not in system:
            cmd_mention = self.client.get_command_mention("autoproxy set")
            await ctx.message.reply(f"Autoproxy is currently off. Use {cmd_mention} set autoproxy to a system member")    
            return
        cmd_mention = self.client.get_command_mention("autoproxy off")
        await ctx.message.reply(f"Autoproxy is currently set to `{system['fronter']}`. Use {cmd_mention} reset autoproxy")    

    autoproxy_cmds = CustomGroup(callback=autoproxy_command, name="autoproxy", aliases=["ap"], usage={
        "description":"autoproxy something something",
        "usage":"autoproxy [subcommand] ...",
        "parameters":{
            "subcommand":{
                "description":"The type of autoproxy you want to activate",
                "type": [CustomCommand.template("subcommand", pre_defined=True, optional=True)]
            }
        }
    })

    @autoproxy_cmds.command(cls=CustomCommand, name="set",usage={
        "description":"Sets your system's autoproxy to a specific member",
        "usage":"autoproxy set <member>",
        "examples":"autoproxy set johnsmith",
        "parameters":{
            "member":{
                "description":"The name or id of this member",
                "type": CustomCommand.template("str"),
            },
        }
    })
    async def set_autoproxy(self, ctx: commands.Context, member_str: str):
        try:
            system, member = await get_system_from_member(ctx, name=member_str, id=member_str, return_member=True)
        except NotFound:
            await ctx.message.reply("I couldn't find that member in your system!")
            return
        
        system["fronter"] = member["id"]
        display_name = ""
        if member.get("display_name"):
            display_name = "**"+member["display_name"]+"**"
        elif member.get("name"):
            display_name = "`"+member["name"]+"`"
        if display_name:
            display_name += " (`"+member["id"]+"`)"
        else:
            display_name += member["id"]

        await asyncRinaDB["pluralkit_data"].update_one(OwnerData(owner_id=ctx.author.id), 
                                      {"$set": {"system":system}})
        await ctx.message.reply(f"Autoproxy set to {display_name}")
    
    @autoproxy_cmds.command(cls=CustomCommand, name="off",usage={
        "description":"Turns off autoproxy",
        "usage":"autoproxy off",
        "examples":"autoproxy off",
    })
    async def unset_autoproxy(self, ctx: commands.Context):
        try:
            system = await get_system(ctx)
        except NotFound:
            await ctx.message.reply("You don't have a system, so you can't turn off any autoproxy either!")
            return
        
        if system["fronter"]:
            del system["fronter"]
        else:
            await ctx.message.reply(f"Autoproxy was already off :)")

        await asyncRinaDB["pluralkit_data"].update_one(OwnerData(owner_id=ctx.author.id), 
                                      {"$set": {"system":system}})
        await ctx.message.reply(f"Disabled autoproxy successfully")
    
    

    ############################
     #     Message Events     # 
    ############################

    async def on_message_pk(self, message: revolt.Message):
        try:
            system = await get_system(message)
        except NotFound:
            return
        if system.get("fronter"):
            for member_index in range(len(system["members"])):
                if system["members"][member_index]["id"] == system["fronter"]:
                    member = system["members"][member_index]
                    break
            else:
                raise Exception("This shouldn't happen...") # but lets raise it anyway \o/
            
            attachments: list[revolt.File] = [
                revolt.File(
                    await file.read(),
                    filename=file.filename, # if filename.startswith("SPOILER_"), it automatically spoilers.
                ) for file in message.attachments
            ]             

            replies: list[revolt.MessageReply] = []
            for reply_id in message.reply_ids:
                for replymsg in message.replies:
                    if replymsg.id == reply_id:
                        replies.append(revolt.MessageReply(replymsg))
                        break
                else:
                    replymsg = await message.channel.fetch_message(reply_id)
                    revolt.MessageReply(replymsg)
            
            await message.delete() # done after attachments and replies because otherwise api can't fetch data

            if "tag" in system:
                system_tag = " [" + system["tag"] + "]"
            else:
                system_tag = ""

            masquerade = revolt.Masquerade(name=member.get("display_name") or member["name"] + system_tag,
                                           avatar=member.get("avatar") or "https://avatars.githubusercontent.com/u/57727799")
            system["members"][member_index]["message_count"] = system["members"][member_index].get("message_count", 0) + 1
            await asyncRinaDB["pluralkit_data"].update_one(OwnerData(owner_id=message.author.id), 
                    {"$set": {"system": system}})
            # avi = self.client.http.fetch_default_avatar(message.author.id)
            await message.channel.send(content=message.content, masquerade=masquerade,replies=replies or None,
                                       attachments=attachments or None)


def setup(client):
    client.add_cog(PluralKit(client))