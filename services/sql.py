# About asyncio https://aiomysql.readthedocs.io/en/latest/pool.html
# https://www.cnblogs.com/traditional/p/12290776.html

import asyncio
from glob import glob

import aiomysql

import config



# thread poo
gb_pool = None

class SQLPool():
    '''
    A Base Pool clase used by this program, instead of the built-in class Pool of aiomysql, 
    this class provide the common function for program

    The pool will be global for all SQLPool instance once created. And it's impossible to 
    use this class to create two different single pool. In this case, it will sure that there 
    are only one pool actived at the same time when program is running.

    Different to pool. Cursor and Conn(Connection) are instance-limited. Each SQLPool instance 
    can has most 1 conn and cursor each time.(Actually in this class a cursor is tightly 
    bound together, in common you shouldn't operate the conn, conn will be distribute or 
    delete autoly when you create or delete cursor)

    Common used:
    create, get_cursor, release_cursor
    '''
    # initialize
    
    pool: aiomysql.Pool = None

    def __init__(self) -> None:
        '''
        Actually don't do anything.
        Use await SQLPool.create to create a available pool.
        '''
        # print('services/sql.py: Notice, you should use await Pool.create method to create a pool.')
        self.cursor: aiomysql.Cursor = None
        self.conn: aiomysql.Connection = None

    # provide await
    def __await__(self):
        return self.create().__await__()

    # create thread pool
    async def create(self, force=False) -> aiomysql.Pool:
        '''
        (Asynchronous) Create a pool.
        Remember to use await to call this function
        Paras:
        force: (Bool)(=False) If True, pool will be recreated even if it has a exsiting pool.
        '''
        global gb_pool
        # create lock, prevent create many times in same time
        pool_creating_lock = asyncio.Lock()
        # if it's a existing pool, and froce=False, than skip creating and retrun existing pool
        if (gb_pool is not None) and (force == False):
            self.pool = gb_pool
            return self.pool
        if self.pool is not None:
            await self.delete()
        await pool_creating_lock.acquire()
        print('Start to creating a new pool')
        try:
            self.pool = await aiomysql.create_pool(
                echo=True,
                host=config.sql.host,
                port=config.sql.port,
                user=config.sql.user,
                password=config.sql.password,
                db=config.sql.db
            )
            gb_pool = self.pool
        except Exception as e:
            print('sql.py: Failed to create pool')
            print(e)
        finally:
            pool_creating_lock.release()
        return self.pool

    # delete pool
    async def delete(self, wait=False) -> None:
        '''
        (Asynchronous) Delete the thread pool
        Paras:
        wait: If true, start a coroutine and waiting for all connection to close actually
        '''
        global gb_pool
        # set a lock, to prevent del function to be called lots of time in same time
        pool_del_lock = asyncio.Lock()
        # Wait for actual close if wait is True
        if wait:
            async with pool_del_lock:
                await self.pool.wait_closed()
            return
        self.pool.close()
        self.pool = None
        gb_pool = self.pool

    # distribute a cursor
    async def get_cursor(self) -> aiomysql.Cursor:
        '''
        (Asynchronous) 
        Get a cursor from exsiting pool.
        Will Automatically create a pool or conn if not existing
        '''
        # create a pool if not existing
        if self.pool is None:
            await self.create()

        self.conn = self.pool.acquire()
        self.cursor = self.conn.cursor()
        return self.cursor

    async def release_cursor(self) -> None:
        await self.cursor.close()
        self.cursor = None
        self.pool.release(self.conn)
        self.conn = None


# ------------------------------------------------------------------
# 创建pool
async def create_pool():
    if gb_pool is None:
        print('active creating')
        asyncsql = SQLPool()
        await asyncsql.create()
