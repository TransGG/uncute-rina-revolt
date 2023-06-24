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
        "fronter":"enjww",
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
    color: Optional[str] # hex color
    birthday: Optional[str]
    proxy: Optional[str]
    avatar: Optional[str]
    message_count: int

class System(TypedDict):
    id: str
    created_at: int
    name: Optional[str] # len(name) >= 2
    description: Optional[str]
    tag: Optional[str]
    color: Optional[str] # hex color
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


async def get_owner(ctx: commands.Context = None, id: str = None) -> OwnerData:
    """
    Get the system dictionary of a person from their ID

    ### Parameters
    --------------
    ctx: :class:`commands.Context`
        The context of the command. Used for getting a default owner ID if none given
    id (optional): :class:`str`
        The id of the user to get the system dictionary for

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
        raise NotFound("Not found")
    return data

async def get_system(ctx: commands.Context, id: str = None, owned=True) -> System:
    """
    Get a System from an id (or name (using ctx.author.id))

    ### Parameters
    --------------
    ctx: :class:`commands.Context`
        The context of the command. Used for getting a default owner ID for searching with name
    id (optional): :class:`str`
        The id of the system

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

async def get_system_from_member(ctx: commands.Context, name: str = None, id: str = None, owned=True) -> System:
    """
    Get a System from a system member's id (or name (using ctx.author.id))

    ### Parameters
    --------------
    ctx: :class:`commands.Context`
        The context of the command. Used for getting a default owner ID for searching with name
    name (optional): :class:`name`
        The name of the member (looks in ctx.author.id's system)
    id (optional): :class:`str`
        The id of the system
    owned (optional): :class:`bool`
        Whether to look for the executor's owned system or for anyone's (default: True)

    ### Returns
    -----------
    :class:`System`
        A System dictionary from given name or id
    """
    # assert bool(name) ^ bool(id) # name xor id given
    collection = asyncRinaDB["pluralkit_data"]
    if owned:
        query = {"owner_id": ctx.author.id}
    else:
        query = {}
    if id:
        # get owner.system.members.id == id
        query["system.members"] = {"$elemMatch":{"id":id.lower()}}
        data: OwnerData|None = await collection.find_one(query)
        if data is None:
            raise NotFound("Member not found")
        for member in data["system"]:
            if member["id"].lower() == id.lower():
                return data["system"]
    if name:
        if not owned:
            query = {"owner_id": ctx.author.id}
        # get owner.system.members.name == name (case insensitive)
        query["system.members"] = {"$elemMatch":{"name":name.lower()}}
        data: OwnerData|None = await collection.find_one(query)
        if data is None:
            raise NotFound("Member not found")
        for member in data["system"]["members"]:
            if member["name"].lower() == name.lower():
                return data["system"]
    raise NotFound("No results")

async def get_owner_from_system(name: str = None, id: str = None) -> OwnerData:
    """
    Get the system dictionary of a person from a server's ID or name

    ### Parameters
    --------------
    name (optional): :class:`name`
        The name of the member (looks in ctx.author.id's system)
    id (optional): :class:`str`
        The id of the system
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
        query = {"system.name":name.lower()}
        data: OwnerData|None = await collection.find_one(query)
        if data is None:
            error += 1
    if error: # no result
        raise NotFound("System not found")
    return data

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
            embed = CustomEmbed(title=f"Members of `{system['id']}`", description=description)
            members = 0
            pages = []
            for member in system.get("members", []):
                name = member["name"] + (f" ({member['display_name']})" if member["display_name"] else "")
                description = "**ID**: " + member["id"]
                for key in member:
                    if key in ["name", "id", "display_name", "created_at"]:
                        continue
                    description += f"\n**{key.capitalize()}**: {member[key].capitalize()}"
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


    @system_cmds.command(cls=CustomCommand, name="new", usage={
        "description":"Make a new system.",
        "usage":"system new [name...]",
        "examples":["system new Star System",
                    "system new"],
        "parameters":{
            "name":{
                "description":"The name of your new system",
                "type": CustomCommand.template("str", wrapped=True),
            }
        }
    })
    async def new_system(self, ctx: commands.Context, *name: str):
        name = ' '.join(name)
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
        
        await asyncRinaDB["pluralkit_data"].update_one(OwnerData(owner_id=ctx.author.id), 
                                      {"$set": {"system": system}}, upsert=True)
        if name:
            await ctx.message.reply(f"Created your system (named `{safe_string(name)}`) successfully! (id: `{system_id}`)")
        else:
            await ctx.message.reply(f"Created your system (unnamed) successfully! (id: `{system_id}`)")

    @system_cmds.command(cls=CustomCommand, name="delete", usage={
        "description":"Delete your system.",
        "usage":"system delete <system_id>",
        "examples":"system delete wtmlo",
        "parameters":{
            "system_id":{
                "description":"The id of your system (for safety reasons)",
                "type": CustomCommand.template("str"),
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

    #############################
     #     Member commands     # 
    #############################

    async def member_command(self, ctx: commands.Context, name: str):
        name = ' '.join(name)
        await ctx.message.reply("NotImplementedError: \"This command has not been implemented yet\"")
        try:
            ...
        except NotFound:
            ...

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
                                      {"$set": {"system":system}}, upsert=True)
        if display_name:
            await ctx.message.reply(f"Successfully added a member ({safe_string(display_name)} (`{safe_string(name)}`)) to your system! (member_id: `{member['id']}`)")
        else:
            await ctx.message.reply(f"Successfully added a member (`{safe_string(name)}`) to your system! (member_id: `{member['id']}`)")

    @member_cmds.command(cls=CustomCommand, name="delete", usage={
        "description":"Delete a member from your system",
        "usage":"member delete <member_id>",
        "examples":"member delete johnsmith",
        "parameters":{
            "member_id":{
                "description":"The id of the member you want to delete",
                "type": CustomCommand.template("str"),
            }
        }
    })
    async def delete_member(self, ctx: commands.Context, member_id: str):
        try:
            system = await get_system_from_member(ctx, id=member_id)
        except (NotFound, KeyError):
            await ctx.message.reply("Couldn't find this member in your system!")
            return
        members = system["members"]
        for member_index in range(len(members)):
            if members[member_index]["id"] == member_id:
                member = members[member_index]
                del members[member_index]
        system["members"] = members
        # await ctx.message.reply("The system id you provided was not the same as the system you own. Perhaps you mistyped something?\n"
        #                         f"- System id: {owner['system']['id'].lower()}\n"
        #                         f"- Given id: {system_id.lower()}")
        # return
        await asyncRinaDB["pluralkit_data"].update_one(OwnerData(owner_id=ctx.author.id), 
                                      {"$set": {"system":system["members"]}}, upsert=True)
        await ctx.message.reply(f"Removed member (name:`{member.name}`, id: `{member_id}`) from your system successfully.")

    ############################
     #     Message Events     # 
    ############################

    async def on_message_pk(self, message: revolt.Message):
        pass


def setup(client):
    client.add_cog(PluralKit(client))