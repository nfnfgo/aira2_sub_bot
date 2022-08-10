# https://aria2.github.io/manual/en/html/aria2c.html#terminology
# https://docs.aiohttp.org/en/stable/

import asyncio
import json
import random
import time
from unittest import result

import aiohttp

import config

# Define some const
alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


# 一个简单的用于发送请求的函数
async def aria_request(method, param_list: list = [], full_res: bool = False):
    '''Serve ALL aria functions. Give an aria2 request method and some required data.

    Params:
    method: An aria2-supported method. Needn't include 'aria2'. Example: addUri
    json: the data you want to send. No need to send Secret since it will be added 
    into the request automatically.
    full_res: Default False. Return a full data_dict including id, rpc info etc. 
    if False, return only a list-type result.

    Return: A responese type object'''
    # Initialize the variables & Read the configure from config dir
    aria_url = f'http://{config.aria.ip}:6800/jsonrpc'
    method = f'aria2.{method}'
    param_list = [f'token:{config.aria.secret}'] + param_list
    data_dict = {
        'id': f'{str(int(time.time()))}_{random.choice(alphabet)}{random.choice(alphabet)}',
        'jsonrpc': '2.0',
        'method': method,
        'params': param_list}
    # Start a request to server.
    async with aiohttp.ClientSession() as session:
        async with session.post(aria_url, json=data_dict) as res:
            data_dict = await res.json()
            if full_res == True:
                return data_dict
            result = data_dict['result']
            return result


async def tell_active(full_res: bool = False, keys: list = []):
    '''Aria2 tellActive method

    Params:
    full_res: Check aria_request function doc for more info'''
    res_data = await aria_request('tellActive', [keys], full_res=full_res)
    return res_data


async def tell_stopped(offset: int, num: int, full_res: bool = False, keys: list = []):
    '''Aria2 tellStopped method

    Params:
    offset: If you want to check time_desc, use negative integers such as -1,-2. Else, use positive.
    num: Specifies how many records return.
    full_res: Default False. Check aria_request function doc for more info
    keys: Default ALL. If specified. Only return info with the key input before'''
    res_data = await aria_request('tellStopped', [offset, num]+[keys], full_res=full_res)
    return res_data


async def add_uri(uri: str | list, waiting=False) -> list:
    '''Aria2 addUri method

    Params:
    uri: URL point to file you want to download. Support Magnet Link.

    Notice: You can only pass one Magnet link at a time

    Return: A list include all res_data of input file 
    which's structure is [[res_data_1],[res_data_2],...]
    '''
    # If uri is a string type, change it to list
    if isinstance(uri, str):
        uri_list = [uri]
    else:
        uri_list = uri
    # start to iterately deal with all uri
    res_data_list = []
    for uri in uri_list:
        res_data = await aria_request('addUri')
        res_data_list.append(res_data)
    return res_data_list
