from Uncute_Rina import *
from import_modules import *

class Moderation(commands.Cog):
    def __init__(self, client):
        # self.staff_command_logging_channel_id = "01H35AM97PZW3166FDGK4FAN39" # Dev server
        self.staff_command_logging_channel_id = "01H2Z0Q2PAFVZ2MPGSNG0Y7WF0" # Main server
        self.client: Bot = client
        # self.recently_banned_people = 0

    @commands.command(cls=CustomCommand, usage={
        "description":"Ban a member with a reason",
        "usage":"ban <member> [reason ...]",
        "examples":"ban 01H34JM6Y9GYG5E26FX5Q2P8PW too cute",
        "parameters":{
            "member":{
                "description":"The member mention or id of the user you want to ban",
                "type":CustomCommand.template("mention or ID")
            },
            "reason":{
                "description":"The reason for which you want to ban this user",
                "type":CustomCommand.template("str",optional=True, wrapped=True)
            }
        }
    })
    async def ban(self, ctx: commands.Context, member_id: str, *reason):
        if await executed_in_dms(ctx):
            return
        if not is_staff(ctx):
            await ctx.message.reply("You don't have the right permissions to use this command!")
            return
        for i in "<\@>":
            member_id = member_id.replace(i, "")
        reason = ' '.join(reason)
        try:
            try:
                member = await ctx.server.fetch_member(member_id)
                custom_ctx = self.client.CustomInteraction(server=member.server, server_id=member.server_id, author=member)
                if is_staff(custom_ctx):
                    await ctx.message.reply("You can't ban staff members. That's kinda sus you know...")
                    return
            except revolt.errors.HTTPError:
                member = ctx.server.get_member(member_id)
            try:
                # send them a message before the user is banned.
                ban_message = await member.send(f"You were banned from Transplace Revolt for reason:\n" +
                                                f"> {reason or '_(No reason given)_'}")
            except revolt.errors.HTTPError as ex:
                self.client.dispatch("command_error", ctx, ex)
                # curious what errors there could be while trying to send a message to the banned user
            try:
                # temporary, until server.ban() is added
                await self.client.state.http.ban_member(ctx.server.id, member_id, reason or None)
            except revolt.errors.HTTPError as ex:
                if ex.args[0] == 500:
                    await ctx.message.reply("Couldn't ban member! Error 500: Internal Server Error\nPerhaps this member is already banned.")
                if ex.args[0] == 403:
                    await ctx.message.reply("Couldn't ban member! Error 403: Forbidden\nRina does not have permissions to ban.")
                else:
                    await ctx.message.reply(f"Couldn't ban member! Error {ex.args[0]}\n")
                await ban_message.delete()
                return
        except LookupError:
            log_channel: revolt.TextChannel = ctx.server.get_channel(self.staff_command_logging_channel_id)
            await log_channel.send(f":hammer: <\@{ctx.author.id}> _banned_ out-of-server user [`{member_id}`, <@{member_id}>]" +
                            f"\n> {reason}" if reason else "\n> _(No reason given)_")
            await ctx.send("Banned out-of-server user successfully")
        else:
            log_channel: revolt.TextChannel = ctx.server.get_channel(self.staff_command_logging_channel_id)
            await log_channel.send(f":hammer: <\@{ctx.author.id}> _banned_ {member.original_name}#{member.discriminator} [`{member.id}`, <@{member.id}>]" +
                            f"\n> {reason}" if reason else "\n> _(No reason given)_")
            await ctx.send("Member banned successfully")

    @commands.command(cls=CustomCommand, usage={
        "description":"Unban a member",
        "usage":"ban <member>",
        "examples":"unban 01H34JM6Y9GYG5E26FX5Q2P8PW",
        "parameters":{
            "member":{
                "description":"The member mention or id of the user you want to unban",
                "type":CustomCommand.template("mention or ID")
            }
        }
    })
    async def unban(self, ctx: commands.Context, member_id: str):
        if await executed_in_dms(ctx):
            return
        if not is_staff(ctx):
            await ctx.message.reply("You don't have the right permissions to use this command!")
            return
        for i in "<\@>":
            member_id = member_id.replace(i, "")
        try:
            # temporary, until server.ban() is added
            await self.client.state.http.unban_member(ctx.server.id, member_id)

            log_channel: revolt.TextChannel = ctx.server.get_channel(self.staff_command_logging_channel_id)
            try:
                member = await ctx.server.fetch_member(member_id)
            except revolt.errors.HTTPError:
                member = ctx.server.get_member(member_id)
        except LookupError:
            try:
                await log_channel.send(f":cloud: <\@{ctx.author.id}> _unbanned_ user [`{member_id}`, <@{member_id}>]")
            except LookupError:
                # there's a crash if the bot tries to return the message with message.mentions, because it can't get
                # member's mention if the member isn't in the server (anymore)
                pass
        else:
            await log_channel.send(f":cloud: <\@{ctx.author.id}> _unbanned_ {member.original_name}#{member.discriminator} [`{member.id}`, <@{member.id}>]")
        await ctx.send("Unbanned user successfully")

def setup(client):
    client.add_cog(Moderation(client))
