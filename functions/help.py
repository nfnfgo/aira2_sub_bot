import asyncio
import time

from telebot.types import Message, InlineKeyboardMarkup, CallbackQuery
from telebot.async_telebot import AsyncTeleBot

from services import button
from services.bot_command import send_to
from functions import guide_doc
from functions import log
from functions import deeplink
import config
from services.user import UserStatus


# ----------------------------------------------------------------
# 初始化主动发送消息部分


# 定义Introduction消息
info_text = f'''<strong>频道信息聚合姬</strong>
<strong>版本：</strong>1.1.0 <em>Beta</em>
<strong>简介：</strong> 一个可以帮助你将不同公共频道的信息聚合在一起的好用Bot~
<strong>通知/反馈频道：</strong> @{config.bot.channel_username}
<a href="https://telegra.ph/%E9%A2%91%E9%81%93%E4%BF%A1%E6%81%AF%E8%81%9A%E5%90%88%E5%A7%AC-07-30"><b>机器人介绍/使用手册</b></a>

内测免费一个月会员兑换码: <code>2KKMR3HAZGMMTA5498UAFE24C</code>'''


# 发送help信息
async def help(message: Message, bot: AsyncTeleBot):
    if (message.text != '/help') and (message.text != '/start'):
        if message.text.startswith('/start'):
            # 此时说明收到的消息应该是deeplink，将消息传给deeplink处理中心
            await deeplink.home(message, bot)
            return
    if message.chat.type != 'private':
        await bot.reply_to(message, '请私聊机器人查看帮助信息')
    await send_to(message, bot, info_text, reply_markup=gen_help_home_markup(), disable_web_page_preview=True)
    await log.log_user(message)


# help信息按钮
def gen_help_home_markup():
    # 定义各个按钮的信息
    help_get_use_guide_info = {'button': 'help_get_use_guide'}
    help_become_vip_info = {'button': 'help_become_vip'}
    help_contact_us_info = {'button': 'help_contact_us_info'}
    return button.gen_markup([
        ['获取使用帮助', help_get_use_guide_info],
        ['成为会员', help_become_vip_info],
        ['联系我们', help_contact_us_info]])


# -------------------------------------------------------------------
# 接受Guide消息并处理


# 定义guide通用的不同类型指令切换查看的按钮
def gen_guide_button(is_admin: bool = False):
    help_guide_bot_info = {'button': 'help_guide_bot'}
    help_guide_func_info = {'button': 'help_guide_func'}
    help_guide_user_info = {'button': 'help_guide_user'}
    help_guide_other_info = {'button': 'help_guide_other'}
    help_guide_admin_info = {'button': 'help_guide_admin'}
    if is_admin == False:
        return button.gen_markup([
            ['基本指令', help_guide_bot_info],
            ['功能设置', help_guide_func_info],
            ['用户设置', help_guide_user_info],
            ['其他指令', help_guide_other_info]])
    if is_admin == True:
        return button.gen_markup([
            ['基本指令', help_guide_bot_info],
            ['功能设置', help_guide_func_info],
            ['用户设置', help_guide_user_info],
            ['其他指令', help_guide_other_info],
            ['管理指令', help_guide_admin_info]])


# Callback 获取使用帮助
async def help_get_use_guide(cbq: CallbackQuery, bot: AsyncTeleBot, data_dict: dict):
    # 判断用户是否为管理员
    user_status = UserStatus(cbq)
    is_admin = False
    if await user_status.is_bot_admin(3) == True:
        is_admin = True
    # 如果用户直接用命令呼出
    if isinstance(cbq, Message):
        message: Message = cbq
        # 判断对话类型
        if message.chat.type != 'private':
            await bot.reply_to(message, '请私聊机器人进行进一步操作')
        await send_to(cbq, bot, guide_doc.home, reply_markup=gen_guide_button(is_admin=is_admin),disable_web_page_preview=True)
        return
    # 如果用户使用callback形式调用
    await bot.answer_callback_query(cbq.id, '')
    if data_dict['button'] == 'help_get_use_guide' or isinstance(cbq, Message):
        await send_to(cbq, bot, guide_doc.home, reply_markup=gen_guide_button(is_admin=is_admin), disable_web_page_preview=True)
    # --- 通过 if 实现不同按钮内容切换
    if data_dict['button'] == 'help_guide_bot':
        await bot.edit_message_text(guide_doc.home, cbq.from_user.id, cbq.message.message_id, reply_markup=gen_guide_button(is_admin=is_admin), disable_web_page_preview=True)
    elif data_dict['button'] == 'help_guide_func':
        await bot.edit_message_text(guide_doc.func, cbq.from_user.id, cbq.message.message_id, reply_markup=gen_guide_button(is_admin=is_admin))
    elif data_dict['button'] == 'help_guide_user':
        await bot.edit_message_text(guide_doc.user, cbq.from_user.id, cbq.message.message_id, reply_markup=gen_guide_button(is_admin=is_admin))
    elif data_dict['button'] == 'help_guide_other':
        await bot.edit_message_text(guide_doc.other, cbq.from_user.id, cbq.message.message_id, reply_markup=gen_guide_button(is_admin=is_admin))
    elif data_dict['button'] == 'help_guide_admin':

        await bot.edit_message_text(guide_doc.admin, cbq.from_user.id, cbq.message.message_id, reply_markup=gen_guide_button(is_admin=is_admin))
