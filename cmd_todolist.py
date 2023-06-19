from Uncute_Rina import *
from import_modules import *

class TodoList(commands.Cog):
    def __init__(self, client: Bot):
        global RinaDB
        RinaDB = client.RinaDB
        self.client = client

    @commands.command()
    async def todo(self, ctx: commands.Context, mode: str, *todo):
        """
        Add/remove/check your to-do list!
        """
        todo = ' '.join(todo) or None
        if (mode := mode.lower()) not in ["add", "remove", "check"]:
            await ctx.message.reply(f"'mode' needs to be one of the following: add, remove, check. Not '{safe_string(mode)}'")

        if mode == "add": # Add item to to-do list
            if todo is None:
                cmd_mention = self.client.get_command_mention("todo")
                await ctx.message.reply(f"This command lets you add items to your to-do list!\n"
                                        f"Type whatever you still plan to do in the `todo: ` argument, "
                                        f"and then you can see your current to-do list with {cmd_mention} "
                                        f"`mode:Check`!")
                return
            if len(todo) > 500:
                ctx.message.reply("I.. don't think having such a big to-do message is gonna be very helpful..")
                return
            collection = RinaDB["todoList"]
            query = {"user": ctx.author.id}
            search = collection.find_one(query)
            if search is None:
                list = []
            else:
                list = search["list"]
            list.append(todo)
            collection.update_one(query, {"$set":{f"list":list}}, upsert=True)
            await ctx.message.reply(f"Successfully added an item to your to-do list! ({len(list)} item{'s'*(len(list)!=1)} in your to-do list now)")
        elif mode == "remove": # Remove item from to-do list
            if todo is None:
                cmd_mention = self.client.get_command_mention("todo")
                await ctx.message.reply(f"Removing todo's with this command is done with IDs. You can see your current list "
                                        f"of todo's using {cmd_mention} `mode:Check`. \n"
                                        f"This list will start every todo-list item with a number. This is the ID you're "
                                        f"looking for. This number can be filled into the `todo: ` argument to remove it.")
                return
            try:
                todo = int(todo)
            except ValueError:
                await ctx.message.reply("To remove an item from your to-do list, you must give the id of the item you want to remove. This should be a number... You didn't give a number...")
                return
            collection = RinaDB["todoList"]
            query = {"user": ctx.author.id}
            search = collection.find_one(query)
            if search is None:
                await ctx.message.reply("There are no items on your to-do list, so you can't remove any either...")
                return
            list = search["list"]

            try:
                del list[todo]
            except IndexError:
                cmd_mention = self.client.get_command_mention("todo")
                await ctx.message.reply(f"Couldn't delete that ID, because there isn't any item on your list with that ID.. Use {cmd_mention} `mode:Check` to see the IDs assigned to each item on your list")
                return
            collection.update_one(query, {"$set":{f"list":list}}, upsert=True)
            await ctx.message.reply(f"Successfully removed '{todo}' from your to-do list. Your list now contains {len(list)} item{'s'*(len(list)!=1)}.")
        elif mode == "check":
            collection = RinaDB["todoList"]
            query = {"user": ctx.author.id}
            search = collection.find_one(query)
            if search is None:
                await ctx.message.reply("There are no items on your to-do list, so.. Good job! nothing to list here....")
                return
            list = search["list"]
            length = len(list)

            ans = []
            for id in range(length):
                ans.append(f"`{id}`: {list[id]}")
            ans = '\n'.join(ans)
            await ctx.message.reply(f"Found {length} to-do item{'s'*(length!=1)}:\n{ans}")


def setup(client):
    client.add_cog(TodoList(client))
