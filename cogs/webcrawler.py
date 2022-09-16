import nextcord
from nextcord.ext import tasks, commands
from nextcord.ext.commands import Bot
import bs4
import requests
from function.bopomofo import main
from function.ptt import *
from itertools import zip_longest

class Ptt(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.channels = {} # Ex: self.channels = {channelA: {'gamesale': Board('gamesale'), 'gossiping': Board('gossiping)}}
        self.fetch.start()

    def cog_unload(self):
        self.fetch.cancel()

    @commands.command(brief = 'add <版名> <關鍵字>', description = '新增自動搜尋清單')
    async def add(self, ctx, name, keyword):
        channel = ctx.channel
        name, keyword = name.lower(), keyword.lower()
        if channel not in self.channels:
            self.channels[channel] = {name: Board(name, keyword)}
            await ctx.send(f'成功加入清單(board: {name}, keyword: {keyword})')
        elif name not in self.channels[channel]:
            self.channels[channel][name] = Board(name, keyword)
            await ctx.send(f'成功加入清單(board: {name}, keyword: {keyword})')
        elif keyword not in self.channels[channel][name].keywords:
            self.channels[channel][name].keywords.append(keyword)
            await ctx.send(f'成功加入清單(board: {name}, keyword: {keyword})')
        else:
            await ctx.send(f'已在清單之中(board: {name}, keyword: {keyword})')

    @commands.command(brief = 'delete <版名> <關鍵字>', description = '刪除自動搜尋清單')
    async def delete(self, ctx, name, keyword):
        channel = ctx.channel
        name, keyword = name.lower(), keyword.lower()
        if channel not in self.channels:
            await ctx.send(f'不在清單之中(board: {name}, keyword: {keyword})')
        elif name not in self.channels[channel]:
            await ctx.send(f'不在清單之中(board: {name}, keyword: {keyword})')
        elif keyword not in self.channels[channel][name].keywords:
            await ctx.send(f'不在清單之中(board: {name}, keyword: {keyword})')
        else:
            if len(self.channels[channel][name].keywords) == 1:
                del self.channels[channel][name]
            else:
                self.channels[channel][name].keywords.remove(keyword)
            await ctx.send(f'已從清單刪除(board: {name}, keyword: {keyword})')

    @commands.command(breif = 'deleteall <版名>', description = '刪除該版所有自動搜尋關鍵字')
    async def deleteall(self, ctx, name):
        channel = ctx.channel
        name = name.lower()
        if name not in self.channels[channel]:
            await ctx.send(f'不在清單之中(board: {name})')
        else:
            del self.channels[channel][name]
            await ctx.send(f'已從清單刪除(board: {name})')
            
    @commands.command(aliases = ['list'], brief = 'list', description = '列出自動搜尋清單')
    async def list_(self, ctx):
        channel = ctx.channel
        if channel not in self.channels or not self.channels[channel]:
            await ctx.send('目前沒有清單')
        else:
            reply = ['關鍵字']
            for name, board in self.channels[channel].items():
                if board.keywords:
                    keywords = ', '.join(board.keywords)
                    reply.append(f'{name.capitalize()}: {keywords}')
            await ctx.send('\n'.join(reply))
    
    @tasks.loop(seconds=10.0)
    async def fetch(self):
        for channel in self.channels:
            for name in self.channels[channel]:
                board = self.channels[channel][name]
                url = f'https://www.ptt.cc/bbs/{name}/index{board.index}.html'
                new_threads = getdataafterthread(url, board.href)

                titles, prices, urls = getthreadsbykeywords(new_threads, board)
                reply = formatted_reply(board.name, titles, prices, urls)
                if reply:
                    print(f'Channel: {channel.name}, 看板：{name.capitalize()} 有新文章' + '\n' + reply)
                    await channel.send(f'★看板：{name.capitalize()} 有新文章' + '\n' + reply)
                board.index = get_index(board.name, 1)
                board.href = getlatestthread(url)
    
    @commands.command(hidden = True)
    async def get(self, ctx, name):
        channel = ctx.channel
        board = self.channels[channel][name]
        keywords = ', '.join(board.keywords)
        await ctx.send('\n'.join([f'Board: {board.name.capitalize()}', f'Index: {board.index}', f'href: {board.href}', f'keywords: {keywords}']))

    @commands.command(brief = 'ptt <版名> <關鍵字> <頁數>', description = '手動搜尋文章(頁數預設三頁)')
    async def ptt(self, ctx, board, keyword, n = 3):
        await ctx.send(f'★看板：{board}；關鍵字：{keyword} 搜尋中...')
        titles, prices, urls = getdata(board, keyword, n)
        reply = formatted_reply(board, titles, prices, urls)

        if not reply:
            print('No data found!')
            await ctx.send('No data found!')
        
        else:
            print(f'Successfully retrieved {len(reply)} threads!')
            print(reply)
            await ctx.send(reply)

def setup(bot: Bot):
    bot.add_cog(Ptt(bot))