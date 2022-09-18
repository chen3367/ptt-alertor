import bs4
import requests
from function.bopomofo import main
from datetime import datetime
from datetime import timedelta
from itertools import zip_longest

class Board:
    def __init__(self, name, keyword = ''):
        self.name = name
        self.index = get_index(self.name, 1)
        self.href = getlatestthread(f'https://www.ptt.cc/bbs/{self.name}/index.html')
        self.keywords = [keyword] if keyword else []

def get_index(board, n):
    """
    Get the last n index on a given board
    """
    url = f'https://www.ptt.cc/bbs/{board}/index.html'
    root = readurl(url)
    last_url = root.find('a', class_ = 'btn', text = '‹ 上頁').get('href')
    start_idx = last_url.find('index') + 5
    end_idx = last_url.find('.', start_idx)
    index = last_url[start_idx:end_idx]
    return str(int(index) - int(n) + 2)

def readurl(url):
    """
    Read the content of an url
    """    
    web = requests.get(url, headers = {'cookie':'over18=1'})
    if web.status_code == 404: return False
    data = web.text
    root = bs4.BeautifulSoup(data, 'html.parser')
    return root

def getprice(url, board):
    root = readurl(url)
    content = root.find('div', class_ = 'bbs-screen bbs-content')
    text = content.text
    try:
        text = text.replace(' ', '')
        start_index = text.index('【售價】' if board == 'gamesale' else '[售價]') + 4 + int(board == 'gamesale')
        end_index = text.index('★' if board == 'gamesale' else '[', start_index)
        value = text[start_index:end_index].strip('\n')
        return '\n' + value if '\n' in value else value
    except Exception as Ex:
        return str(Ex)

def getdatabyindex(index, board, keyword, titles, prices, urls):
    url = f'https://www.ptt.cc/bbs/{board}/index{index}.html'
    root = readurl(url)

    # 404 not found
    if not root: 
        print(f'Index {index} not found')
        return titles, prices, urls
    print(f'【Successfully accessed to {board} board {index}】')

    # Find all threads meet the condition
    threads = root.find_all('div', class_ = 'r-ent')
    for thread in threads:
        title = thread.find('div', class_ = 'title')
        if not (title.a and title.a.text): continue
        title = title.a.text

        if main.in_string(keyword, title):
            href = 'https://www.ptt.cc' + thread.find('div', class_ = 'title').a.get('href')
            titles.append(title)
            urls.append(href)
            if board.lower() in ('gamesale', 'macshop'):
                price = '非販售文' if '售' not in title else getprice(href, board)
                prices.append(price)
    
    # Direct to next page
    return getdatabyindex(str(int(index) + 1), board, keyword, titles, prices, urls)

def getlatestthread(url):
    root = readurl(url)
    threads = root.find_all('div', class_ = 'r-ent')
    today_md = datetime.today().strftime('%m/%d').lstrip('0')
    ytd_md = (datetime.today() + timedelta(days=-1)).strftime('%m/%d').lstrip('0')
    
    # Filter out bulletin thread
    for thread in threads:
        date = thread.find('div', class_ = 'date').text.lstrip()
        if date not in (today_md, ytd_md):
            break
        latest_thread = thread
    latest_title = latest_thread.find('div', class_ = 'title').a.text
    latest_href = latest_thread.a.get('href')
    return latest_href

def getdataafterthread(url, href):
    root = readurl(url)
    threads = root.find_all('div', class_ = 'r-ent')

    # Recurrsivly retrieve new threads if the page is not the last page
    while root.find('a', class_ = 'btn', text = '下頁 ›') and root.find('a', class_ = 'btn', text = '下頁 ›').get('href'):
        root = readurl('https://www.ptt.cc' + root.find('a', class_ = 'btn', text = '下頁 ›').get('href'))
        threads += root.find_all('div', class_ = 'r-ent')

    # Get new post (filter by href)
    new_threads = list(filter(lambda x: x.a['href'] > href if x.a else False, threads))
    return new_threads

def getthreadsbykeywords(threads, board: Board):
    """
    Get data by which meet the keywords
    """
    titles, prices, urls = [], [], []
    for thread in threads:
        title = thread.find('div', class_ = 'title')
        if not (title.a and title.a.text): continue
        title = title.a.text

        if main.listofstr_in_string(board.keywords, title.lower()):
            href = 'https://www.ptt.cc' + thread.find('div', class_ = 'title').a.get('href')
            titles.append(title)
            urls.append(href)
            if board.name.lower() in ('gamesale', 'macshop'):
                price = '非販售文' if '售' not in title else getprice(href, board.name)
                prices.append(price)
    return titles, prices, urls

def formatted_reply(titles, prices, urls):
    reply = []
    for i, (title, price, url) in enumerate(zip_longest(titles, prices, urls)):
        reply_list = []
        reply_list.append(f'標題：{title}')
        if prices:
            reply_list.append(f'價格：{price}')
        reply_list.append(f'網址：{url}')
        reply.append('\n'.join(reply_list))
    reply = ('\n' + '-' * 80 +'\n').join(reply)
    return reply

def getdata(board, keyword, n):
    reply = []
    index = get_index(board, n)
    titles, prices, urls = getdatabyindex(index, board, keyword, [], [], [])
    return titles, prices, urls
