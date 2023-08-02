import asyncio
import datetime
import requests
import sys
import time
import urllib
from json import load as json_load
from math import ceil, floor
from os import system


def get_now_strftime():
    time = datetime.datetime.now().strftime("%H:%M:%S.%f")
    return time


def console_select(select_dict: dict, multiple_select=False):
    print("SELECT." if not multiple_select else "SELECT (determine multiple options if you want).")
    for i, name in enumerate(select_dict.keys()):
        print("\t", f"{i+1}) {name}")
    selected = input("Enter corresponding " + ("number: " if not multiple_select else "number(s): "))
    if not multiple_select:
        selected = int(selected) - 1
        while selected not in range(len(select_dict.keys())):
            selected = int(input("Wrong choice. Enter corresponding number: ")) - 1
        return select_dict[list(select_dict.keys())[selected]]
    selecteds = [int(s) - 1 for s in selected.split()]
    while True:
        for s in selecteds:
            if s not in range(len(select_dict.keys())):
                break
        else:
            break
        selected = input("Wrong choice. Enter corresponding number(s): ")
        selecteds = [int(s) - 1 for s in selected.split()]
    return [select_dict[list(select_dict.keys())[s]] for s in selecteds]


def cal_diff_percentage(p1: float, p2: float) -> float:
    return (p1/p2 - 1) * 100


def cal_total_percentage(amount: float, total: float) -> float:
    return amount / total * 100


def clear_console():
    system("clear")


def load_configurations(filename:str="config.json") -> dict:
    confs = {}
    with open(filename) as f:
        confs = json_load(f)
    return confs


def load_autopilot_confs(filename:str="posAutopilot.json") -> dict:
    return load_configurations(filename)


def load_redis_confs(filename: str="redis.json") -> dict:
    return load_configurations(filename)


def prompt_sys_for_args():
    arguments = sys.argv[:]
    return arguments


def colorize_text(text, color):
    colors = {
        'red': "\u001b[31m",
        'yellow': "\u001b[33m",
        'blue': '\u001b[34m',
        'reset': "\u001b[0m",
        'green': "\u001b[32m",
        'purple': '\u001b[35m',
        'cyan': '\u001b[36m',
        'orange': '\u001b[38;5;202m',
        'indian_red': '\u001b[38;5;131m',
        'header' : '\033[95m',
        'cyanbg': '\033[106m',
        'pinkbg':'\033[105m',
        'bluebg':'\033[104m',
        'greybg':'\033[100m',
        'redbg':'\033[101m',
        'greenbg':'\033[102m',
        'yellowbg':'\033[103m'
    }
    return f"{colors[color]}{text}{colors['reset']}"


def truncate(number: float, decimals: int=0) -> float:
    return round(floor(number * 10**(decimals)) / 10**(decimals), decimals)


def truncate_up(number: float, decimals: int=0) -> float:
    return round(ceil(number * 10**(decimals)) / 10**(decimals), decimals)


def tg_send_message(text, tg_token: str, tg_chatid: str):
    URL = 'https://api.telegram.org/bot{token}/'.format(token=tg_token)
    tot = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(tot, tg_chatid)    
    r = requests.get(url)
    if not r.status_code == requests.codes.OK:
        raise Exception(colorize_text(r.content, 'pinkbg'))
    else:
        print(colorize_text("tg sent", 'pinkbg'))


async def batch_first_complete_coroutines(coros: list[asyncio.coroutine], timeout_time: int):
    tasks = [asyncio.create_task(coro) for coro in coros]
    potential_exceptions = []
    start = time.time()
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED, timeout=timeout_time + start - time.time())
    while done:
        for task in done:
            exception = task.exception()
            if exception is None:
                for ts in pending:
                    ts.cancel()
                return await task
            potential_exceptions.append(exception)
        if pending:
            potential_exceptions.clear()
            done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED, timeout=timeout_time + start - time.time())
        else:
            break
    if potential_exceptions:
        raise potential_exceptions[-1]
    for ts in pending:
        ts.cancel()
    raise asyncio.TimeoutError()


def print_ascii_art():
    with open("configs/lovita_ascii.txt") as f:
        print(f.read())


def is_passed_from(secs: int, last_epoch: float):
    now_epoch = time.time()
    return now_epoch - last_epoch > secs


def wait_until(end_timestamp):
    while True:
        diff = end_timestamp - time.time()
        if diff < 0: return
        time.sleep(diff/2)
        if diff <= 0.1: return
