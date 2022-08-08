import asyncio
import base64
from tkinter import E

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from telebot.async_telebot import AsyncTeleBot

from functions import help
from functions import push
from functions import my
from functions import log
from functions import category
from functions import use_cdk


async def cbq_master(cbq: CallbackQuery, bot: AsyncTeleBot):
    '''
    Use to get all CallbackQuery Info and pre-deal it, distribute it to the proper function
    '''
    # 从cbq中提取data_dict
    data_dict = cbq.data
    data_dict = eval(data_dict)

    # 读取按钮类型
    bt_type:str = data_dict['button']
    if bt_type == 'help_get_use_guide':  # 获取使用文档
        await help.help_get_use_guide(cbq, bot, data_dict)

    elif bt_type.startswith('help_guide_'):  # 所有的使用文档共用这个按钮
        await help.help_get_use_guide(cbq, bot, data_dict)

    elif bt_type in ['my_become_premium','category_become_premium']:  # 成为会员
        await my.become_premium(cbq, bot, data_dict)

    elif bt_type.startswith('push_'):  # 推送消息
        await push.push_control(cbq, bot, data_dict)
    
    # 管理标签
    elif bt_type == 'category_manage_tag':
        await category.manage(cbq, bot, data_dict)
    
    # 管理标签_清空tag
    elif bt_type == 'category_clean_tag':
        await category.clean(cbq, bot, data_dict)

    elif bt_type.startswith('category_clean_tag_'):
        await category.clean_confirm(cbq, bot, data_dict)
    
    elif bt_type == 'category_set_tag_bypass':
        await category.set_tag_bypass(cbq, bot, data_dict)

    elif bt_type == 'category_cancel_tag_bypass':
        await category.cancel_tag_bypass(cbq, bot, data_dict)
    
    elif bt_type == 'category_add_ch_to_tag':
        await category.add_ch_to_tag(cbq, bot, data_dict)

    elif bt_type == 'category_remove_ch_from_tag':
        await category.del_ch_from_tag(cbq, bot, data_dict)
    
    # 生成兑换码
    elif bt_type == 'use_cdk_add_cdk':
        await use_cdk.add_cdk(cbq, bot, data_dict)

    else:
        await bot.answer_callback_query(cbq.id, '服务已关闭或还未开放')
    # 记录用户活跃
    user_id=cbq.from_user.id
    await log.log_user(user_id)
