from Uncute_Rina import *
from import_modules import *

hsv_color_list = { #in h    s    v
    "report"                          : [ 16, 100, 100],
    "customvcs"                       : [ 84,  55, 100],
    "trigger warnings"                : [240,  40, 100],
    "tone indicators"                 : [170,  40, 100],
    "trusted role"                    : [280,  40, 100],
    "selfies"                         : [120,  40, 100],
    "minimodding or correcting staff" : [340,  55, 100],
    "avoiding politics"               : [ 60,  40, 100],
    "please change topic"             : [205,  40, 100],
}
def convert_hsv_to_hex(h, s, v):
    """
    Convert an HSV color representation to a HEX color representation.

    ### Parameters
    --------------
    h: :class:`int` | :class:`float` (0 to 360)
        hue
    s: :class:`int` | :class:`float` (0 to 100)
        saturation
    v: :class:`int` | :class:`float` (0 to 100)
        value (brightness (blackness))
    
    ### Returns
    -----------
    :class:`str`
        HEX representation of the input HSV value.
    """
    # Copied from colorutils module, thank you kind person who made it open source. Otherwise I'd have to use Wikipedia
    s = s/100
    v = v/100
    c = v * s
    h /= 60
    x = c * (1 - abs((h % 2) - 1))
    m = v - c

    if h < 1:
        res = (c, x, 0)
    elif h < 2:
        res = (x, c, 0)
    elif h < 3:
        res = (0, c, x)
    elif h < 4:
        res = (0, x, c)
    elif h < 5:
        res = (x, 0, c)
    elif h < 6:
        res = (c, 0, x)
    else:
        raise Exception("Unable to convert from HSV to RGB")
    r, g, b = res
    r, g, b = round((r + m)*255, 3), round((g + m)*255, 3), round((b + m)*255, 3)
    return "#"+hex(int(r))[2:].zfill(2)+\
               hex(int(g))[2:].zfill(2)+\
               hex(int(b))[2:].zfill(2)

colours = {k: convert_hsv_to_hex(*v) for k, v in hsv_color_list.items()}

class Tags:
    async def tag_message(self, ctx: commands.Context, embed: discord.Embed):
        """
        Send a tag message (un)publicly or (un)anonymously, given an embed.
        
        ### Parameters
        ctx: :class:`commands.Context`
            The interaction to reply to
        """
        await ctx.send(embed=embed)


    async def send_report_info(self, tag_name: str, context: commands.Context | discord.TextChannel, client, additional_info: None | list[str, int]=None, public=False, anonymous=True):
        # additional_info = [message.author.name, message.author.id]
        embed = CustomEmbed(
            color=colours["report"]) #a more saturated red orange color
        embed.add_field(
            name='Reporting a message or scenario',
            value="Unfortunately reporting is currently disabled. DM staff or ping them if you have an issue.\n"
            "(On revolt, this means you have to send a friend request first)"
            # "Hi there! If anyone is making you uncomfortable, or you want to "
            # "report or prevent a rule-breaking situation, you can `Right Click "
            # "Message > Apps > Report Message` to notify our staff confidentially. "
            # "You can also create a mod ticket in <#995343855069175858> or DM a staff " # channel-id = #contact-staff
            # "member."
            )
        embed.set_image(url="https://i.imgur.com/jxEcGvl.gif")
        if isinstance(context, commands.Context):
            pass# await self.tag_message(tag_name, context, client, public, anonymous, embed)
        else:
            if additional_info is not None:
                embed.set_footer(text=f"Triggered by {additional_info[0]} ({additional_info[1]})")
            await context.send(embed=embed)

    async def send_customvc_info(self, tag_name: str, ctx: commands.Context, client: Bot, public, anonymous):
        vc_hub = await client.get_guild_info(ctx.server, "vcHub")

        cmd_mention = client.get_command_mention('editvc')
        cmd_mention2 = client.get_command_mention('vctable about')
        embed = CustomEmbed(
            color=colours["customvcs"], # greenish lime-colored
        )
        embed.add_field(
            name="TransPlace's custom voice channels (vc)",
            value=f"In our server, you can join <#{vc_hub}> to create a custom vc. You "
                  f"are then moved to this channel automatically. You can change the name and user "
                  f"limit of this channel with the {cmd_mention} command. When everyone leaves the "
                  f"channel, the channel is deleted automatically."
                  f"You can use {cmd_mention2} for additional features.")
        await self.tag_message(ctx, embed)

    async def send_triggerwarning_info(self, tag_name: str, ctx: commands.Context, client, public, anonymous):
        embed = CustomEmbed(
            color=colours["trigger warnings"], #bluer than baby blue ish. kinda light indigo
        )
        embed.add_field(
            name="Using trigger warnings correctly",
            value="Content or trigger warnings (CW and TW for short) are notices placed before a "
                  "(section of) text to warn the reader of potential traumatic triggers in it. Often, "
                  "people might want to avoid reading these, so a warning will help them be aware of "
                  "it.\n"
                  "You can warn the reader in the beginning or the middle of the text, and spoiler the "
                  "triggering section like so: \"TW: !!guns!!: !!The gun was fired.!!\".\n"
                  "\n"
                  r"You can spoiler messages with a double exclamation mark `!!text!!`." "\n"
                  "Some potential triggers include (TW: triggers): abuse, bugs/spiders, death, "
                  "dieting/weight loss, injections, self-harm, transmed/truscum points of view or "
                  "transphobic content.")
        await self.tag_message(ctx, embed)

    async def send_toneindicator_info(self, tag_name: str, ctx: commands.Context, client: Bot, public, anonymous):
        embed = CustomEmbed(
            color=colours["tone indicators"], # tealish aqua
        )
        embed.add_field(
            name="When to use tone indicators?",
            value="Tone indicators are a useful tool to clarify the meaning of a message.\n"
                  "Occasionally, people reading your comment may not be certain about the tone of "
                  "a message. Is it meant as positive feedback, a joke, or sarcasm?\n"
                  "\n"
                  "For example, you may playfully tease a friend. Without tone indicators, the "
                  "message may come across as rude or mean, but adding “/lh” (meaning light-"
                  "hearted) helps clarify that it was meant in good fun.\n"
                  "\n"
                  "Some tone indicators have multiple definitions depending on the context. For "
                  "example: \"/m\" can mean 'mad' or 'metaphor'. You can look up tone indicators by "
                  f"their tag or definition using {client.get_command_mention('toneindicator')}."
        )
        await self.tag_message(ctx, embed)

    async def send_trustedrole_info(self, tag_name: str, ctx: commands.Context, client, public, anonymous):
        embed = CustomEmbed(
            color=colours["trusted role"], # magenta
        )
        embed.add_field(
            name="The trusted role (and selfies)",
            value="The trusted role is the role we use to add an extra layer of protection to some "
                  "aspects of our community. Currently, this involves the selfies channel, but may be "
                  "expanded to other channels in future.\n"
                  "\n"
                  "You can obtain the trusted role by sending 500 messages or after gaining the "
                  "equivalent XP from voice channel usage. If you rejoin the server you can always "
                  "ask for the role back too!"
        )
        await self.tag_message(ctx, embed)

    async def send_selfies_info(self, tag_name: str, ctx: commands.Context, client, public, anonymous):
        embed = CustomEmbed(
            color=colours["selfies"], # magenta
        )
        embed.add_field(
            name="Selfies and the #selfies channel",
            value="For your own and other's safety, the selfies channel is hidden behind the "
                        "trusted role. This role is granted automatically when you've been active in "
                        "the server for long enough. We grant the role after 500 messages or 9 hours "
                        "in VC or a combination of both.\n"
                        "\n"
                        "The selfies channel automatically deletes all messages after 7 days to ensure "
                        "the privacy and safety of our members."
        )
        await self.tag_message(ctx, embed)

    async def send_minimodding_info(self, tag_name: str, ctx: commands.Context, client, public, anonymous):
        embed = CustomEmbed(
            color=colours["minimodding or correcting staff"],  # bright slightly reddish pink
        )
        embed.add_field(
            name="Correcting staff or minimodding",
            value="If you have any input on how members of staff operate, please open a ticket to "
                        "properly discuss."
                        "\n"
                        "Please do not interfere with moderator actions, as it can make situations worse. It can be seen as "
                        "harassment, and you could be warned."
        )
        await self.tag_message(ctx, embed)
        
    async def send_avoidpolitics_info(self, tag_name: str, ctx: commands.Context, client, public, anonymous):
        embed = CustomEmbed(
            color=colours["avoiding politics"], # yellow
        )
        embed.add_field(
            name="Please avoid political discussions!",
            value="A member has requested that we avoid political discussions in this chat, we kindly "
                        "ask that you refrain from discussing politics in this chat to maintain a positive and "
                        "uplifting environment for all members.\n"
                        "Our community focuses on highlighting the positive aspects of the trans "
                        "community. Political discussions often detract from this goal and create "
                        "negative air and conflict among members.\n"
                        "\n"
                        "If you continue discussing politics, a moderator may need to take action and mute "
                        "you. Thank you for your cooperation."
        )
        await self.tag_message(ctx, embed, public_footer=True)

    async def send_chat_topic_change_request(self, tag_name: str, ctx: commands.Context,  client,public, anonymous):
        embed = CustomEmbed(
            color=colours["please change topic"],
        )
        embed.add_field(
            name="Please change chat topic",
            value="A community member has requested a change of topic as the current one is making them "
                        "uncomfortable. Please refrain from continuing the current line of discussion and find "
                        "a new topic."
        )
        await self.tag_message(ctx, embed)

class TagFunctions(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(cls=CustomCommand, usage={
        "description":"Look up something through a tag",
        "usage":"tag <tag...>",
        "examples":["tag report","tag trigger warnings"],
        "parameters":{
            "tag":{
                "description":"What tag do you want more information about?",
                "type": CustomCommand.template("str", pre_defined=True, wrapped=True, case_sensitive=False),
                "accepted values":"report, customvc, tone indicators, minimodding or correcting staff, avoid politics, change topic"
            }
        }
    })
    async def tag(self, ctx: commands.Context, *tag: str):
        t = Tags()
        tag_functions = {
            "report" : t.send_report_info,
            "customvc" : t.send_customvc_info,
            # "trigger warnings" : t.send_triggerwarning_info,
            "tone indicators" : t.send_toneindicator_info,
            # "trusted role" : t.send_trustedrole_info,
            # "selfies channel info" : t.send_selfies_info,
            "minimodding or correcting staff" : t.send_minimodding_info,
            "avoid politics" : t.send_avoidpolitics_info,
            "change topic" : t.send_chat_topic_change_request,
        }
        tag = ' '.join(tag).lower()
        if tag in tag_functions:
            await tag_functions[tag](tag, ctx, self.client, public=True, anonymous=False)
        if tag == "":
            self.dispatch("command_error", ctx, RuntimeError)
            return
        else:
            await ctx.message.reply("No tag found with this name! Please pick one of the following:\n- "
                                    ', '.join(tag_functions))

def setup(client):
    client.add_cog(TagFunctions(client))