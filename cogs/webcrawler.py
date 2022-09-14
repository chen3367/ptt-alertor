import nextcord
from nextcord.ext import tasks, commands
from nextcord.ext.commands import Bot
import bs4
import requests
from function.bopomofo import main
from function.ptt import *
from collections import defaultdict
from itertools import zip_longest

class Ptt(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.boards = {} # Ex: self.boards = {'gamesale': Board('gamesale'), 'gossiping': Board('gossiping')}
        self.channels = []
        self.fetch.start()

    def cog_unload(self):
        self.fetch.cancel()
    
    @commands.command(aliases = ['啟動'], description = '在目前頻道開啟Ptt Alertor')
    async def start(self, ctx):
        channel = ctx.channel
        if channel in self.channels:
            await ctx.send('頻道已在啟動清單中')
        else:
            self.channels.append(channel)
            await ctx.send(f'成功加入啟動清單, channel name: {channel}')

    @commands.command(aliases = ['關閉'], description = '關閉目前頻道的Ptt Alertor')
    async def stop(self, ctx):
        channel = ctx.channel
        if channel not in self.channels:
            await ctx.send('頻道不在啟動清單中')
        else:
            self.channels.remove(channel)
            await ctx.send(f'成功移除啟動清單, channel name: {channel}')

    @commands.command(aliases = ['新增'], brief = '新增 <版名> <關鍵字>', description = '新增自動搜尋清單')
    async def add(self, ctx, name, keyword):
        name, keyword = name.lower(), keyword.lower()
        if name in self.boards.keys() and keyword in self.boards[name].keywords:
            await ctx.send(f'已在清單之中(board: {name}, keyword: {keyword})')
        else:
            if name not in self.boards:
                self.boards[name] = Board(name)
            self.boards[name].keywords.append(keyword)
            await ctx.send(f'成功加入清單(board: {name}, keyword: {keyword})')

    @commands.command(aliases = ['刪除'], brief = '刪除 <版名> <關鍵字>', description = '刪除自動搜尋清單')
    async def delete(self, ctx, name, keyword):
        name, keyword = name.lower(), keyword.lower()
        if not (name in self.boards.keys() and keyword in self.boards[name].keywords):
            await ctx.send(f'不在清單之中(board: {name}, keyword: {keyword})')
        else:
            self.boards[name].keywords.remove(keyword)
            if not self.boards[name].keywords:
                del self.boards[name]
            await ctx.send(f'成功刪除清單(board: {name}, keyword: {keyword})')
    
    @commands.command(aliases = ['清單'], brief = '清單', description = '列出自動搜尋清單')
    async def list_(self, ctx):
        if not self.boards or all(not board.keywords for board in self.boards.values()):
            await ctx.send('目前沒有清單')
        else:
            reply = ['關鍵字']
            for board in self.boards.values():
                if board.keywords:
                    keywords = ', '.join(board.keywords)
                    reply.append(f'{board.name}: {keywords}')
            await ctx.send('\n'.join(reply))
    
    @tasks.loop(seconds=10.0)
    async def fetch(self):
        for name in self.boards:            
            board = self.boards[name]
            url = f'https://www.ptt.cc/bbs/{name}/index{board.index}.html'
            new_threads = getdataafterthread(url, board.href)

            titles, prices, urls = getthreadsbykeywords(new_threads, board)
            reply = formatted_reply(board.name, titles, prices, urls)
            if reply:
                for channel in self.channels:
                    await channel.send(f'★看板：{name} 有新文章' + '\n' + reply)
            board.index = get_index(board.name, 1)
            board.href = getlatesthref(url)
    
    @commands.command(hidden = True)
    async def getboardinfo(self, ctx, name):
        board = self.boards[name]
        keywords = ', '.join(board.keywords)
        await ctx.send('\n'.join([f'Board: {board.name}', f'Index: {board.index}', f'href: {board.href}', f'keywords: {keywords}']))

    @commands.command(brief = 'ptt <board> <keyword> <n_pages>', description = 'Retrieve titles and urls from ptt by keyword, default n_pages = 3')
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