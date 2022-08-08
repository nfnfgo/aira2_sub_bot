import time
import asyncio

import aiomysql
from telebot.types import User, Message, CallbackQuery, BotCommand

from services.sql import SQLPool


# 用户类
class UserStatus():
    # 关于用户类的全局变量
    users_status_info = {}

    def __init__(self, info: int | str | Message | CallbackQuery):
        '''
        Initialize a user and autoly read status through id, message or callbackquery.

        Notice: self.status_info will be an empty dictionary if user has no available status
        '''
        self.status_info = {}
        # 依次根据下方顺序尝试获取User的ID（唯一识别标记）
        if (isinstance(info, int)) or (isinstance(info, str)):
            self.id = int(info)
        elif (isinstance(info, Message)) or (isinstance(info, CallbackQuery)):
            self.id = info.from_user.id
        else:
            raise Exception('Failed to initialize a user since no available id data')
        # 尝试读取用户目前状态并写入 user_status （如果用户目前存在状态的话）
        self.status_info = self.get_status_info()

    def __await__(self, message: Message = None, id: int | str = None, call: CallbackQuery = None):
        return self.__init().__await__()

    # 提供await方法（虽然一个异步操作都没有）
    async def __init(self, message: Message = None, id: int | str = None, call: CallbackQuery = None):
        # 依次根据下方顺序尝试获取User的ID（唯一识别标记）
        if id is not None:
            self.id = int(id)
        elif message is not None:
            self.id = int(message.from_user.id)
        elif call is not None:
            self.id = int(call.from_user.id)
        else:
            raise Exception('Failed to initialize a user since no available id data')

    # 从列表中读取用户的 status_info （如果存在）并写入实例
    def get_status_info(self, key=None):
        '''
        Get Users Status By reading users_status_info
        Return None when user has no status

        Paras:
        self: a StatusUser class instance
        key: default=None, if None, return whole self.status_info dict, if key is specified, 
        return a list that first item would be the info stored and second is the timestamp 
        when it has been set.
        '''
        try:
            self.status_info = self.users_status_info[self.id]
        except:
            self.status_info = {}

        # 如果用户并没有status，则创建空字典，方便后期写入
        if key is None:
            return self.status_info

        # 如果用户指定了查询某个键的值，对其进行返回
        try:
            value_list = self.status_info[key]
            return value_list
        except:
            raise Exception('user.py: Failed to get status_info value list. Maybe key is invalid')

    def set_status_info(self, dict):
        '''
        Set a user status.
        You can pass a key with empty str or None to delete it, and if it doesn't exist, raise exception

        Paras:
        dict: dict type. key should be the status key, value should be the data info that you want 
        to store. timestamp is not needed since it would be added automatically
        '''
        timestamp = time.time()
        for item in dict.items():
            if (item[1] is None) or (item[1] == ''):
                try:
                    del self.status_info[item[0]]
                except Exception as e:
                    print('service/user.py: Failed to del a status_key.', e)
                continue
            self.status_info[item[0]] = [item[1], time.time()]
        self.users_status_info[self.id] = self.status_info

    def del_status_info(self):
        '''Delete **all** the status of a bot.
        Cautions: This Method doesn't means delete some single keys
        (if you need that please use set_status_info).
        Instead it will delete the whole status_info dictionary 
        of this user, and delete it from users_status_info global list
        '''
        try:
            del self.users_status_info[self.id]
        except Exception as e:
            print('service/user.py Failed to delete a whole user status_info', e)

    async def is_bot_admin(self, admin_level: int = None) -> int | bool:
        '''
        (Asynchronous) A Fucntion to check the user's account status. 
        (Such as Admin SuperAdmin ... )

        Return a int nums without any other paras. It would be the 
        status midium int number in the database

        Paras:
        admin_level=None: Should be int, return True if this user's 
        level is higher than admin_level input
        '''
        # 开始读取数据库
        asyncsql = SQLPool()
        pool = await asyncsql.create()
        async with pool.acquire() as conn:
            conn:aiomysql.Connection=conn
            async with conn.cursor() as cursor:
                cursor:aiomysql.Cursor=cursor
                await conn.commit()
                await cursor.execute('''SELECT status FROM `users` WHERE `id`=%s''', (self.id,))
                result = await cursor.fetchone()
                if result is None:
                    return False
                else:
                    if admin_level is None:
                        return result[0]
                    else:
                        return result[0] >= admin_level
        
    # 用户身份过期时间查询
    async def expired_time(self,return_bool=False) -> int|bool:
        '''
        检查用户身份的过期时间，理论上过期之后会恢复到普通身份

        Paras:
        return_bool: 返回是否过期的Bool值而非准确的int时间戳，True为过期，False为没有过期
        '''
        # 开始读取数据库
        asyncsql = SQLPool()
        pool = await asyncsql.create()
        async with pool.acquire() as conn:
            conn:aiomysql.Connection=conn
            async with conn.cursor() as cursor:
                cursor:aiomysql.Cursor=cursor
                await conn.commit()
                await cursor.execute('''SELECT expire_time FROM users WHERE id=%s''', (self.id,))
                res = await cursor.fetchone()
        res=res[0]
        if return_bool == True:
            return int(time.time())>res
        return int(res)