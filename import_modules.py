class PrintProgress:
    def __init__(self, max):
        self.progress = 0
        self.max = max

    def increment(self, name):
        print(f"[{self.progress*'#'}+{(self.max-self.progress-1)*' '}] Importing modules:   {name}{' '*(50-len(name))}\033[F")
        self.progress += 1

progress = PrintProgress(26)
progress.increment("datetime")
from datetime import datetime, timedelta, timezone # for checking if user is older than 7days (in verification
program_start = datetime.now()
if True:
    progress.increment("discord")
    import discord # It's dangerous to go alone! Take this. /ref
    progress.increment("discord/app_commands")
    from discord import app_commands # v2.0, use slash commands
    progress.increment("discord.ext/commands")
    from discord.ext import commands # required for client bot
if True:
    progress.increment("revolt")
    import revolt
    progress.increment("revolt/commands")
    from revolt.ext import commands
progress.increment("time/mktime")
from time import mktime # for unix time code
progress.increment("json")
import json # to interpret the obtained api data
progress.increment("sys")
import sys # kill switch for rina (search for :kill)
progress.increment("random")
import random # for picking a random call_cute quote
progress.increment("re")
import re #use regex to remove pronouns from people's usernames, and split their names into sections by capital letter
#          and to identify custom emojis in a text message
#          and to remove API hyperlink definitions: {#Ace=asexual}
progress.increment("requests")
import requests # for getting the equality index of countries and to grab from en.pronouns.page api (search)
progress.increment("aiohttp") # for Revolt commands now, apparently
import aiohttp
progress.increment("warnings")
import warnings #used to warn for invalid color thingy in the debug function; as well as for debug()
progress.increment("pymongo")
import pymongo # used in cmd_emojistats
progress.increment("pymongo/MongoClient")
from pymongo import MongoClient
progress.increment("motor/motor_asyncio")
import motor.motor_asyncio as motor # for making Mongo run asynchronously (during api calls)
progress.increment("asyncio")
import asyncio # lets rina take small pauses while getting emojis from MongoDB to allow room for other commands
progress.increment("matplotlib/pyplot")
import matplotlib.pyplot as plt
progress.increment("pandas")
import pandas as pd
progress.increment("apscheduler/schedulers/asyncio/AsyncIOScheduler")
from apscheduler.schedulers.asyncio import AsyncIOScheduler # for scheduling reminders
progress.increment("traceback")
import traceback
progress.increment("logging")
import logging
progress.increment("typing/TypedDict")
from typing import TypedDict, Optional
progress.increment("utils")
from utils import is_verified, is_staff, is_admin, debug, log_to_guild, executed_in_dms, safe_string, jump_msg, get_emoji_raw, custom_group,\
    PagedMessage, CustomEmbed, CustomGroup, CustomHelpCommand, CustomCommand
# progress.increment("reminders")
# from cmdg_Reminders import Reminders
# used for adding reminders when starting up the bot
# print_progress(21,31, "", end='\n')
debug(f"[{'#'*(progress.max)}] Imported modules                      ",color='green', add_time=False)
