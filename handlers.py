import re
import json
import random
import string
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode

from config import OWNER_ID, CHANNEL_USERNAME, MAX_DEAL_LIMIT
from database import *
from utils import *
from keyboards import *

# ============ CONVERSATION STATES ============
(FORM_AMOUNT, FORM_BUYER, FORM_SELLER, FORM_DEAL_DETAIL, FORM_RLS_UPI, 
 FORM_CONDITION, FORM_ESCROW_TILL) = range(7)

# ============ START COMMAND ============
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    # Check if user is owner or admin
    is_owner = user_id == OWNER_ID
    is_admin_user = is_admin(user_id)
    
    welcome_msg = f"""
{get_emoji('crown')} 𝙆𝘼𝙇𝙔𝙐𝙂 𝙀𝙎𝘾𝙍𝙊𝙒 𝙎𝙀𝙍𝙑𝙄𝘾𝙀 {get_emoji('crown')}

{get_emoji('wave')} 𝙒𝙚𝙡𝙘𝙤𝙢𝙚 {user.first_name}!

{get_emoji('shield')} 𝙎𝙖𝙛𝙚 𝙖𝙣𝙙 𝙨𝙚𝙘𝙪𝙧𝙚 𝙚𝙨𝙘𝙧𝙤𝙬 𝙙𝙚𝙖𝙡𝙨

{get_emoji('game')} /newdeal - 𝘾𝙧𝙚𝙖𝙩𝙚 𝙣𝙚𝙬 𝙙𝙚𝙖𝙡
{get_emoji('info')} /status - 𝘾𝙝𝙚𝙘𝙠 𝙙𝙚𝙖𝙡 𝙨𝙩𝙖𝙩𝙪𝙨
{get_emoji('question')} /help - 𝙃𝙚𝙡𝙥 𝙢𝙚𝙣𝙪
"""
    
    if is_owner or is_admin_user:
        welcome_msg += f"""
{get_emoji('crown')} 𝘼𝘿𝙈𝙄𝙉 𝘾𝙊𝙈𝙈𝘼𝙉𝘿𝙎
{get_emoji('shield')} /admin - 𝘼𝙙𝙢𝙞𝙣 𝙥𝙖𝙣𝙚𝙡
{get_emoji('megaphone')} /broadcast - 𝘽𝙧𝙤𝙖𝙙𝙘𝙖𝙨𝙩
{get_emoji('diamond')} /setlimit - 𝙎𝙚𝙩 𝙙𝙚𝙖𝙡 𝙡𝙞𝙢𝙞𝙩
"""
    
    if is_owner:
        welcome_msg += f"""
{get_emoji('crown')} 𝙊𝙒𝙉𝙀𝙍 𝘾𝙊𝙈𝙈𝘼𝙉𝘿𝙎
{get_emoji('check')} /approve - 𝘼𝙙𝙙 𝙖𝙙𝙢𝙞𝙣
{get_emoji('cross')} /removeadmin - 𝙍𝙚𝙢𝙤𝙫𝙚 𝙖𝙙𝙢𝙞𝙣
"""
    
    welcome_msg += f"""
{get_emoji('handshake')} @KALYUGESCROWSERVICE
"""
    
    await update.message.reply_text(
        decorate(welcome_msg),
        reply_markup=get_main_menu(),
        parse_mode=ParseMode.HTML
    )

# ============ NEW DEAL FORM ============
async def new_deal_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_admin(user_id) and user_id != OWNER_ID:
        await update.message.reply_text(
            decorate(f"{get_emoji('cross')} 𝙊𝙣𝙡𝙮 𝙖𝙙𝙢𝙞𝙣𝙨 𝙘𝙖𝙣 𝙘𝙧𝙚𝙖𝙩𝙚 𝙙𝙚𝙖𝙡𝙨!"),
            parse_mode=ParseMode.HTML
        )
        return
    
    await update.message.reply_text(
        decorate(f"{get_emoji('money')} 𝙀𝙣𝙩𝙚𝙧 𝙙𝙚𝙖𝙡 𝙖𝙢𝙤𝙪𝙣𝙩 (𝙢𝙖𝙭 ₹{MAX_DEAL_LIMIT}):"),
        parse_mode=ParseMode.HTML
    )
    return FORM_AMOUNT

async def form_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = int(update.message.text.strip())
        if amount <= 0:
            raise ValueError
        if amount > MAX_DEAL_LIMIT:
            await update.message.reply_text(
                decorate(f"{get_emoji('cross')} 𝘼𝙢𝙤𝙪𝙣𝙩 𝙘𝙖𝙣𝙣𝙤𝙩 𝙚𝙭𝙘𝙚𝙚𝙙 ₹{MAX_DEAL_LIMIT}!"),
                parse_mode=ParseMode.HTML
            )
            return FORM_AMOUNT
        
        # Check admin limit
        user_id = update.effective_user.id
        if user_id != OWNER_ID:
            admin_limit = get_admin_limit(user_id)
            if amount > admin_limit:
                await update.message.reply_text(
                    decorate(f"{get_emoji('cross')} 𝙔𝙤𝙪𝙧 𝙙𝙚𝙖𝙡 𝙡𝙞𝙢𝙞𝙩 𝙞𝙨 ₹{admin_limit}. 𝘾𝙤𝙣𝙩𝙖𝙘𝙩 𝙤𝙬𝙣𝙚𝙧 𝙩𝙤 𝙞𝙣𝙘𝙧𝙚𝙖𝙨𝙚."),
                    parse_mode=ParseMode.HTML
                )
                return FORM_AMOUNT
        
        context.user_data['deal_data'] = {'amount': amount}
        await update.message.reply_text(
            decorate(f"{get_emoji('wave')} 𝙀𝙣𝙩𝙚𝙧 𝙗𝙪𝙮𝙚𝙧 𝙪𝙨𝙚𝙧𝙣𝙖𝙢𝙚 (𝙬𝙞𝙩𝙝 @):"),
            parse_mode=ParseMode.HTML
        )
        return FORM_BUYER
    except ValueError:
        await update.message.reply_text(
            decorate(f"{get_emoji('cross')} 𝙋𝙡𝙚𝙖𝙨𝙚 𝙚𝙣𝙩𝙚𝙧 𝙖 𝙫𝙖𝙡𝙞𝙙 𝙣𝙪𝙢𝙗𝙚𝙧!"),
            parse_mode=ParseMode.HTML
        )
        return FORM_AMOUNT

async def form_buyer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buyer = update.message.text.strip()
    if not buyer.startswith('@'):
        buyer = '@' + buyer
    context.user_data['deal_data']['buyer'] = buyer
    await update.message.reply_text(
        decorate(f"{get_emoji('shield')} 𝙀𝙣𝙩𝙚𝙧 𝙨𝙚𝙡𝙡𝙚𝙧 𝙪𝙨𝙚𝙧𝙣𝙖𝙢𝙚 (𝙬𝙞𝙩𝙝 @):"),
        parse_mode=ParseMode.HTML
    )
    return FORM_SELLER

async def form_seller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    seller = update.message.text.strip()
    if not seller.startswith('@'):
        seller = '@' + seller
    context.user_data['deal_data']['seller'] = seller
    await update.message.reply_text(
        decorate(f"{get_emoji('info')} 𝙀𝙣𝙩𝙚𝙧 𝙙𝙚𝙖𝙡 𝙙𝙚𝙩𝙖𝙞𝙡𝙨:"),
        parse_mode=ParseMode.HTML
    )
    return FORM_DEAL_DETAIL

async def form_deal_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['deal_data']['deal_detail'] = update.message.text.strip()
    await update.message.reply_text(
        decorate(f"{get_emoji('diamond')} 𝙀𝙣𝙩𝙚𝙧 𝙍𝙇𝙎 𝙐𝙋𝙄:"),
        parse_mode=ParseMode.HTML
    )
    return FORM_RLS_UPI

async def form_rls_upi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['deal_data']['rls_upi'] = update.message.text.strip()
    await update.message.reply_text(
        decorate(f"{get_emoji('clock')} 𝙀𝙣𝙩𝙚𝙧 𝙘𝙤𝙣𝙙𝙞𝙩𝙞𝙤𝙣:"),
        parse_mode=ParseMode.HTML
    )
    return FORM_CONDITION

async def form_condition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['deal_data']['condition'] = update.message.text.strip()
    await update.message.reply_text(
        decorate(f"{get_emoji('target')} 𝙀𝙣𝙩𝙚𝙧 𝙚𝙨𝙘𝙧𝙤𝙬 𝙩𝙞𝙡𝙡 (𝙚.𝙜. 𝙩𝙞𝙡𝙡 𝙩𝙧𝙖𝙣𝙨𝙛𝙚𝙧):"),
        parse_mode=ParseMode.HTML
    )
    return FORM_ESCROW_TILL

async def form_escrow_till(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['deal_data']['escrow_till'] = update.message.text.strip()
    
    form_data = context.user_data['deal_data']
    deal_id = generate_deal_id()
    
    # Save to database
    create_deal(deal_id, form_data, update.effective_user.id)
    add_log(deal_id, 'created', update.effective_user.id, json.dumps(form_data))
    
    # Format and send
    formatted = format_deal_form(form_data)
    buttons = get_deal_buttons(deal_id)
    
    await update.message.reply_text(
        decorate(formatted),
        reply_markup=buttons,
        parse_mode=ParseMode.HTML
    )
    
    await update.message.reply_text(
        decorate(f"{get_emoji('check')} 𝘿𝙚𝙖𝙡 𝙄𝘿: {deal_id} 𝙘𝙧𝙚𝙖𝙩𝙚𝙙 𝙨𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮!"),
        parse_mode=ParseMode.HTML
    )
    
    context.user_data.clear()
    return ConversationHandler.END

async def cancel_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        decorate(f"{get_emoji('cross')} 𝙁𝙤𝙧𝙢 𝙘𝙖𝙣𝙘𝙚𝙡𝙡𝙚𝙙."),
        parse_mode=ParseMode.HTML
    )
    context.user_data.clear()
    return ConversationHandler.END

# ============ DEAL ACTIONS ============
async def deal_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Check if user is admin or owner
    if not is_admin(user_id) and user_id != OWNER_ID:
        await query.edit_message_text(
            decorate(f"{get_emoji('cross')} 𝙊𝙣𝙡𝙮 𝙖𝙙𝙢𝙞𝙣𝙨 𝙘𝙖𝙣 𝙥𝙚𝙧𝙛𝙤𝙧𝙢 𝙩𝙝𝙞𝙨 𝙖𝙘𝙩𝙞𝙤𝙣!"),
            parse_mode=ParseMode.HTML
        )
        return
    
    data = query.data
    action, deal_id = data.split('_', 1)
    
    deal = get_deal(deal_id)
    if not deal:
        await query.edit_message_text(
            decorate(f"{get_emoji('cross')} 𝘿𝙚𝙖𝙡 𝙣𝙤𝙩 𝙛𝙤𝙪𝙣𝙙!"),
            parse_mode=ParseMode.HTML
        )
        return
    
    # Check if deal is already handled
    if deal['status'] != 'pending' and action not in ['complete']:
        await query.edit_message_text(
            decorate(f"{get_emoji('warning')} 𝙏𝙝𝙞𝙨 𝙙𝙚𝙖𝙡 𝙞𝙨 𝙖𝙡𝙧𝙚𝙖𝙙𝙮 {deal['status'].upper()}!"),
            parse_mode=ParseMode.HTML
        )
        return
    
    # Check if another admin is handling
    if deal['handled_by'] and deal['handled_by'] != user_id and deal['status'] != 'pending':
        await query.edit_message_text(
            decorate(f"{get_emoji('warning')} 𝙏𝙝𝙞𝙨 𝙙𝙚𝙖𝙡 𝙞𝙨 𝙗𝙚𝙞𝙣𝙜 𝙝𝙖𝙣𝙙𝙡𝙚𝙙 𝙗𝙮 𝙖𝙣𝙤𝙩𝙝𝙚𝙧 𝙖𝙙𝙢𝙞𝙣!"),
            parse_mode=ParseMode.HTML
        )
        return
    
    # Get current form data
    form_data = json.loads(deal['form_data'])
    
    if action == 'pay':
        update_deal_status(deal_id, 'payment_received', user_id)
        add_log(deal_id, 'payment_received', user_id)
        
        msg = format_deal_message(deal, 'payment')
        await query.edit_message_text(
            decorate(msg),
            reply_markup=get_deal_buttons(deal_id),
            parse_mode=ParseMode.HTML
        )
        
    elif action == 'hold':
        update_deal_status(deal_id, 'on_hold', user_id)
        add_log(deal_id, 'hold', user_id)
        
        msg = format_deal_message(deal, 'hold')
        await query.edit_message_text(
            decorate(msg),
            reply_markup=get_deal_buttons(deal_id),
            parse_mode=ParseMode.HTML
        )
        
    elif action == 'cancel':
        update_deal_status(deal_id, 'cancelled', user_id)
        add_log(deal_id, 'cancelled', user_id)
        
        msg = format_deal_message(deal, 'cancel')
        await query.edit_message_text(
            decorate(msg),
            parse_mode=ParseMode.HTML
        )
        
    elif action == 'complete':
        update_deal_status(deal_id, 'completed', user_id)
        add_log(deal_id, 'completed', user_id)
        
        msg = format_deal_message(deal, 'complete')
        await query.edit_message_text(
            decorate(msg),
            parse_mode=ParseMode.HTML
        )

# ============ ADMIN PANEL ============
async def admin_panel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_admin(user_id) and user_id != OWNER_ID:
        await update.message.reply_text(
            decorate(f"{get_emoji('cross')} 𝘼𝙙𝙢𝙞𝙣 𝙥𝙖𝙣𝙚𝙡 𝙤𝙣𝙡𝙮!"),
            parse_mode=ParseMode.HTML
        )
        return
    
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        message = query.message
    else:
        message = update.message
    
    total_deals = len(get_all_deals())
    pending_deals = len(get_deals_by_status('pending'))
    completed_deals = len(get_deals_by_status('completed'))
    admins_list = get_admins()
    
    msg = f"""
{get_emoji('crown')} 𝘼𝘿𝙈𝙄𝙉 𝙋𝘼𝙉𝙀𝙇 {get_emoji('crown')}

{get_emoji('money')} 𝙏𝙤𝙩𝙖𝙡 𝘿𝙚𝙖𝙡𝙨: {total_deals}
{get_emoji('clock')} 𝙋𝙚𝙣𝙙𝙞𝙣𝙜: {pending_deals}
{get_emoji('check')} 𝘾𝙤𝙢𝙥𝙡𝙚𝙩𝙚𝙙: {completed_deals}
{get_emoji('shield')} 𝘼𝙙𝙢𝙞𝙣𝙨: {len(admins_list)}

{get_emoji('handshake')} @KALYUGESCROWSERVICE
"""
    
    await message.reply_text(
        decorate(msg),
        reply_markup=get_admin_panel_buttons(),
        parse_mode=ParseMode.HTML
    )

# ============ ADMIN PANEL CALLBACKS ============
async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if not is_admin(user_id) and user_id != OWNER_ID:
        await query.edit_message_text(
            decorate(f"{get_emoji('cross')} 𝘼𝙙𝙢𝙞𝙣 𝙤𝙣𝙡𝙮!"),
            parse_mode=ParseMode.HTML
        )
        return
    
    data = query.data
    
    if data == "admin_back":
        await admin_panel_cmd(update, context)
        return
    
    if data == "admin_deals":
        deals = get_all_deals()
        if not deals:
            msg = f"{get_emoji('info')} 𝙉𝙤 𝙙𝙚𝙖𝙡𝙨 𝙛𝙤𝙪𝙣𝙙."
        else:
            msg = f"{get_emoji('crown')} 𝘼𝙇𝙇 𝘿𝙀𝘼𝙇𝙎 {get_emoji('crown')}\n\n"
            for d in deals[:10]:
                status_emoji = "🟢" if d['status'] == 'completed' else "🟡" if d['status'] == 'pending' else "🔴"
                msg += f"{status_emoji} {d['deal_id']} - ₹{d['amount']} - {d['status'].upper()}\n"
            if len(deals) > 10:
                msg += f"\n... 𝙖𝙣𝙙 {len(deals)-10} 𝙢𝙤𝙧𝙚"
        
        await query.edit_message_text(
            decorate(msg),
            reply_markup=get_back_button(),
            parse_mode=ParseMode.HTML
        )
        
    elif data == "admin_pending":
        deals = get_deals_by_status('pending')
        if not deals:
            msg = f"{get_emoji('check')} 𝙉𝙤 𝙥𝙚𝙣𝙙𝙞𝙣𝙜 𝙙𝙚𝙖𝙡𝙨."
        else:
            msg = f"{get_emoji('clock')} 𝙋𝙀𝙉𝘿𝙄𝙉𝙂 𝘿𝙀𝘼𝙇𝙎 {get_emoji('clock')}\n\n"
            for d in deals[:10]:
                msg += f"🟡 {d['deal_id']} - ₹{d['amount']}\n"
            if len(deals) > 10:
                msg += f"\n... 𝙖𝙣𝙙 {len(deals)-10} 𝙢𝙤𝙧𝙚"
        
        await query.edit_message_text(
            decorate(msg),
            reply_markup=get_back_button(),
            parse_mode=ParseMode.HTML
        )
        
    elif data == "admin_list":
        admins = get_all_admins_with_limits()
        if not admins:
            msg = f"{get_emoji('info')} 𝙉𝙤 𝙖𝙙𝙢𝙞𝙣𝙨 𝙛𝙤𝙪𝙣𝙙."
        else:
            msg = f"{get_emoji('shield')} 𝘼𝘿𝙈𝙄𝙉 𝙇𝙄𝙎𝙏 {get_emoji('shield')}\n\n"
            for a in admins:
                is_owner_tag = "👑 " if a[0] == OWNER_ID else ""
                msg += f"{is_owner_tag}𝙸𝙳: {a[0]}\n𝙻𝚒𝚖𝚒𝚝: ₹{a[2]}\n\n"
        
        await query.edit_message_text(
            decorate(msg),
            reply_markup=get_back_button(),
            parse_mode=ParseMode.HTML
        )
        
    elif data == "admin_status":
        total = len(get_all_deals())
        pending = len(get_deals_by_status('pending'))
        completed = len(get_deals_by_status('completed'))
        cancelled = len(get_deals_by_status('cancelled'))
        on_hold = len(get_deals_by_status('on_hold'))
        
        msg = f"""
{get_emoji('target')} 𝘿𝙀𝘼𝙇 𝙎𝙏𝘼𝙏𝙐𝙎 {get_emoji('target')}

{get_emoji('money')} 𝙏𝙤𝙩𝙖𝙡: {total}
{get_emoji('clock')} 𝙋𝙚𝙣𝙙𝙞𝙣𝙜: {pending}
{get_emoji('check')} 𝘾𝙤𝙢𝙥𝙡𝙚𝙩𝙚𝙙: {completed}
{get_emoji('cross')} 𝘾𝙖𝙣𝙘𝙚𝙡𝙡𝙚𝙙: {cancelled}
{get_emoji('warning')} 𝙊𝙣 𝙃𝙤𝙡𝙙: {on_hold}

{get_emoji('handshake')} @KALYUGESCROWSERVICE
"""
        await query.edit_message_text(
            decorate(msg),
            reply_markup=get_back_button(),
            parse_mode=ParseMode.HTML
        )

# ============ DEAL STATUS COMMAND ============
async def deal_status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            decorate(f"{get_emoji('info')} 𝙐𝙨𝙖𝙜𝙚: /status 𝘿𝙀𝘼𝙇_𝙄𝘿"),
            parse_mode=ParseMode.HTML
        )
        return
    
    deal_id = context.args[0].upper()
    deal = get_deal(deal_id)
    
    if not deal:
        await update.message.reply_text(
            decorate(f"{get_emoji('cross')} 𝘿𝙚𝙖𝙡 𝙣𝙤𝙩 𝙛𝙤𝙪𝙣𝙙!"),
            parse_mode=ParseMode.HTML
        )
        return
    
    form_data = json.loads(deal['form_data'])
    status_emoji = {
        'pending': '🟡',
        'payment_received': '🟢',
        'on_hold': '🟠',
        'completed': '✅',
        'cancelled': '❌'
    }.get(deal['status'], '🟡')
    
    msg = f"""
{get_emoji('info')} 𝘿𝙀𝘼𝙇 𝙎𝙏𝘼𝙏𝙐𝙎 {get_emoji('info')}

{get_emoji('crown')} 𝘿𝙚𝙖𝙡 𝙄𝘿: {deal['deal_id']}
{status_emoji} 𝙎𝙩𝙖𝙩𝙪𝙨: {deal['status'].upper()}

{get_emoji('money')} 𝘼𝙢𝙤𝙪𝙣𝙩: ₹{deal['amount']}
{get_emoji('wave')} 𝘽𝙪𝙮𝙚𝙧: {form_data.get('buyer', 'N/A')}
{get_emoji('shield')} 𝙎𝙚𝙡𝙡𝙚𝙧: {form_data.get('seller', 'N/A')}
{get_emoji('clock')} 𝘾𝙧𝙚𝙖𝙩𝙚𝙙: {deal['created_at']}

{get_emoji('handshake')} @KALYUGESCROWSERVICE
"""
    
    await update.message.reply_text(
        decorate(msg),
        parse_mode=ParseMode.HTML
    )

# ============ HELP COMMAND ============
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = f"""
{get_emoji('question')} 𝙃𝙀𝙇𝙋 𝙈𝙀𝙉𝙐 {get_emoji('question')}

{get_emoji('game')} /newdeal - 𝘾𝙧𝙚𝙖𝙩𝙚 𝙣𝙚𝙬 𝙙𝙚𝙖𝙡
{get_emoji('info')} /status - 𝘾𝙝𝙚𝙘𝙠 𝙙𝙚𝙖𝙡 𝙨𝙩𝙖𝙩𝙪𝙨
{get_emoji('shield')} /admin - 𝘼𝙙𝙢𝙞𝙣 𝙥𝙖𝙣𝙚𝙡

{get_emoji('crown')} 𝙃𝙊𝙒 𝙏𝙊 𝙐𝙎𝙀
1️⃣ 𝘼𝙙𝙢𝙞𝙣 𝙘𝙧𝙚𝙖𝙩𝙚𝙨 𝙙𝙚𝙖𝙡 𝙛𝙤𝙧𝙢
2️⃣ 𝘽𝙪𝙮𝙚𝙧 & 𝙎𝙚𝙡𝙡𝙚𝙧 𝙖𝙜𝙧𝙚𝙚
3️⃣ 𝘼𝙙𝙢𝙞𝙣 𝙢𝙖𝙣𝙖𝙜𝙚𝙨 𝙙𝙚𝙖𝙡

{get_emoji('handshake')} @KALYUGESCROWSERVICE
"""
    await update.message.reply_text(
        decorate(msg),
        parse_mode=ParseMode.HTML
    )

# ============ OWNER COMMANDS ============
async def approve_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID:
        await update.message.reply_text(
            decorate(f"{get_emoji('cross')} 𝙊𝙬𝙣𝙚𝙧 𝙤𝙣𝙡𝙮!"),
            parse_mode=ParseMode.HTML
        )
        return
    
    if not context.args:
        await update.message.reply_text(
            decorate(f"{get_emoji('info')} 𝙐𝙨𝙖𝙜𝙚: /approve 𝙐𝙎𝙀𝙍_𝙄𝘿"),
            parse_mode=ParseMode.HTML
        )
        return
    
    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text(
            decorate(f"{get_emoji('cross')} 𝙄𝙣𝙫𝙖𝙡𝙞𝙙 𝙐𝙎𝙀𝙍_𝙄𝘿!"),
            parse_mode=ParseMode.HTML
        )
        return
    
    # Get user info
    try:
        chat = await context.bot.get_chat(target_id)
        name = chat.first_name or chat.username or str(target_id)
    except:
        name = str(target_id)
    
    add_admin(target_id, name, user_id)
    
    await update.message.reply_text(
        decorate(f"{get_emoji('check')} {name} 𝙖𝙙𝙙𝙚𝙙 𝙖𝙨 𝙖𝙙𝙢𝙞𝙣!"),
        parse_mode=ParseMode.HTML
    )
    
    # Notify the new admin
    try:
        await context.bot.send_message(
            target_id,
            decorate(f"{get_emoji('crown')} 𝙔𝙤𝙪 𝙝𝙖𝙫𝙚 𝙗𝙚𝙚𝙣 𝙖𝙙𝙙𝙚𝙙 𝙖𝙨 𝙖𝙣 𝙖𝙙𝙢𝙞𝙣!\n\n{get_emoji('shield')} 𝙐𝙨𝙚 /admin 𝙛𝙤𝙧 𝙥𝙖𝙣𝙚𝙡."),
            parse_mode=ParseMode.HTML
        )
    except:
        pass

async def removeadmin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID:
        await update.message.reply_text(
            decorate(f"{get_emoji('cross')} 𝙊𝙬𝙣𝙚𝙧 𝙤𝙣𝙡𝙮!"),
            parse_mode=ParseMode.HTML
        )
        return
    
    if not context.args:
        await update.message.reply_text(
            decorate(f"{get_emoji('info')} 𝙐𝙨𝙖𝙜𝙚: /removeadmin 𝙐𝙎𝙀𝙍_𝙄𝘿"),
            parse_mode=ParseMode.HTML
        )
        return
    
    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text(
            decorate(f"{get_emoji('cross')} 𝙄𝙣𝙫𝙖𝙡𝙞𝙙 𝙐𝙎𝙀𝙍_𝙄𝘿!"),
            parse_mode=ParseMode.HTML
        )
        return
    
    if target_id == OWNER_ID:
        await update.message.reply_text(
            decorate(f"{get_emoji('cross')} 𝘾𝙖𝙣𝙣𝙤𝙩 𝙧𝙚𝙢𝙤𝙫𝙚 𝙤𝙬𝙣𝙚𝙧!"),
            parse_mode=ParseMode.HTML
        )
        return
    
    remove_admin(target_id)
    
    await update.message.reply_text(
        decorate(f"{get_emoji('cross')} 𝘼𝙙𝙢𝙞𝙣 𝙧𝙚𝙢𝙤𝙫𝙚𝙙!"),
        parse_mode=ParseMode.HTML
    )

async def setlimit_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID:
        await update.message.reply_text(
            decorate(f"{get_emoji('cross')} 𝙊𝙬𝙣𝙚𝙧 𝙤𝙣𝙡𝙮!"),
            parse_mode=ParseMode.HTML
        )
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            decorate(f"{get_emoji('info')} 𝙐𝙨𝙖𝙜𝙚: /setlimit <𝙖𝙢𝙤𝙪𝙣𝙩> <𝙪𝙨𝙚𝙧_𝙞𝙙>\n\n𝙀𝙭𝙖𝙢𝙥𝙡𝙚: /setlimit 5000 123456789\n𝙈𝙖𝙭: 12000"),
            parse_mode=ParseMode.HTML
        )
        return
    
    try:
        limit = int(context.args[0])
        target_id = int(context.args[1])
        
        if limit < 0:
            await update.message.reply_text(
                decorate(f"{get_emoji('cross')} 𝘾𝙖𝙣𝙣𝙤𝙩 𝙗𝙚 𝙣𝙚𝙜𝙖𝙩𝙞𝙫𝙚!"),
                parse_mode=ParseMode.HTML
            )
            return
        
        if limit > MAX_DEAL_LIMIT:
            limit = MAX_DEAL_LIMIT
            await update.message.reply_text(
                decorate(f"{get_emoji('warning')} 𝙈𝙖𝙭 𝙡𝙞𝙢𝙞𝙩 𝙞𝙨 {MAX_DEAL_LIMIT}. 𝙎𝙚𝙩𝙩𝙞𝙣𝙜 𝙩𝙤 {MAX_DEAL_LIMIT}."),
                parse_mode=ParseMode.HTML
            )
        
        if not is_admin(target_id):
            await update.message.reply_text(
                decorate(f"{get_emoji('cross')} 𝙐𝙨𝙚𝙧 𝙞𝙨 𝙣𝙤𝙩 𝙖𝙣 𝙖𝙙𝙢𝙞𝙣! 𝙐𝙨𝙚 /approve 𝙛𝙞𝙧𝙨𝙩."),
                parse_mode=ParseMode.HTML
            )
            return
        
        set_admin_limit(target_id, limit)
        
        try:
            chat = await context.bot.get_chat(target_id)
            name = chat.first_name or chat.username or str(target_id)
        except:
            name = str(target_id)
        
        await update.message.reply_text(
            decorate(f"{get_emoji('check')} {name} 𝙙𝙚𝙖𝙡 𝙡𝙞𝙢𝙞𝙩 𝙨𝙚𝙩 𝙩𝙤 ₹{limit}"),
            parse_mode=ParseMode.HTML
        )
        
        try:
            await context.bot.send_message(
                target_id,
                decorate(f"{get_emoji('crown')} 𝙔𝙤𝙪𝙧 𝙙𝙚𝙖𝙡 𝙡𝙞𝙢𝙞𝙩 𝙝𝙖𝙨 𝙗𝙚𝙚𝙣 𝙨𝙚𝙩 𝙩𝙤 ₹{limit}"),
                parse_mode=ParseMode.HTML
            )
        except:
            pass
            
    except ValueError:
        await update.message.reply_text(
            decorate(f"{get_emoji('cross')} 𝙄𝙣𝙫𝙖𝙡𝙞𝙙 𝙖𝙢𝙤𝙪𝙣𝙩!"),
            parse_mode=ParseMode.HTML
        )

# ============ BROADCAST ============
async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_admin(user_id) and user_id != OWNER_ID:
        await update.message.reply_text(
            decorate(f"{get_emoji('cross')} 𝘼𝙙𝙢𝙞𝙣 𝙤𝙣𝙡𝙮!"),
            parse_mode=ParseMode.HTML
        )
        return
    
    if not context.args:
        await update.message.reply_text(
            decorate(f"{get_emoji('info')} 𝙐𝙨𝙖𝙜𝙚: /broadcast <𝙢𝙚𝙨𝙨𝙖𝙜𝙚>"),
            parse_mode=ParseMode.HTML
        )
        return
    
    msg_text = " ".join(context.args)
    deals = get_all_deals()
    sent = 0
    failed = 0
    
    await update.message.reply_text(
        decorate(f"{get_emoji('bolt')} 𝘽𝙧𝙤𝙖𝙙𝙘𝙖𝙨𝙩𝙞𝙣𝙜 𝙩𝙤 {len(deals)} 𝙙𝙚𝙖𝙡𝙨..."),
        parse_mode=ParseMode.HTML
    )
    
    for deal in deals:
        form_data = json.loads(deal['form_data'])
        buyer = form_data.get('buyer', '').replace('@', '')
        seller = form_data.get('seller', '').replace('@', '')
        
        try:
            # Send to buyer
            try:
                await context.bot.send_message(
                    chat_id=int(buyer) if buyer.isdigit() else None,
                    text=decorate(f"{get_emoji('megaphone')} 𝘽𝙍𝙊𝘼𝘿𝘾𝘼𝙎𝙏\n\n{msg_text}\n\n{get_emoji('handshake')} @KALYUGESCROWSERVICE"),
                    parse_mode=ParseMode.HTML
                )
                sent += 1
            except:
                failed += 1
            
            # Send to seller
            try:
                await context.bot.send_message(
                    chat_id=int(seller) if seller.isdigit() else None,
                    text=decorate(f"{get_emoji('megaphone')} 𝘽𝙍𝙊𝘼𝘿𝘾𝘼𝙎𝙏\n\n{msg_text}\n\n{get_emoji('handshake')} @KALYUGESCROWSERVICE"),
                    parse_mode=ParseMode.HTML
                )
                sent += 1
            except:
                failed += 1
                
        except:
            failed += 1
    
    await update.message.reply_text(
        decorate(f"{get_emoji('check')} 𝙎𝙚𝙣𝙩: {sent} | {get_emoji('cross')} 𝙁𝙖𝙞𝙡𝙚𝙙: {failed}"),
        parse_mode=ParseMode.HTML
    )

# ============ BUTTON CALLBACK ============
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith('pay_') or data.startswith('hold_') or data.startswith('cancel_') or data.startswith('complete_'):
        await deal_action(update, context)
        return
    
    if data.startswith('admin_'):
        await admin_callback(update, context)
        return
    
    if data == "new_deal":
        await new_deal_cmd(update, context)
        return
    
    if data == "admin_panel":
        await admin_panel_cmd(update, context)
        return
    
    if data == "help":
        await help_cmd(update, context)
        return

# ============ ERROR HANDLER ============
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error: {context.error}", exc_info=context.error)

# ============ MAIN ============
def main():
    logger.info("🚀 Starting KALYUG ESCROW BOT...")
    
    # Start Flask
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info(f"✅ Flask server started on port {os.environ.get('PORT', 5000)}")
    
    # Create application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # ============ CONVERSATION HANDLER ============
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("newdeal", new_deal_cmd),
            CallbackQueryHandler(button_callback, pattern="^new_deal$")
        ],
        states={
            FORM_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, form_amount)],
            FORM_BUYER: [MessageHandler(filters.TEXT & ~filters.COMMAND, form_buyer)],
            FORM_SELLER: [MessageHandler(filters.TEXT & ~filters.COMMAND, form_seller)],
            FORM_DEAL_DETAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, form_deal_detail)],
            FORM_RLS_UPI: [MessageHandler(filters.TEXT & ~filters.COMMAND, form_rls_upi)],
            FORM_CONDITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, form_condition)],
            FORM_ESCROW_TILL: [MessageHandler(filters.TEXT & ~filters.COMMAND, form_escrow_till)],
        },
        fallbacks=[CommandHandler("cancel", cancel_form)],
        per_message=True
    )
    
    # ============ COMMAND HANDLERS ============
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("status", deal_status_cmd))
    app.add_handler(CommandHandler("admin", admin_panel_cmd))
    
    # Owner commands
    app.add_handler(CommandHandler("approve", approve_cmd))
    app.add_handler(CommandHandler("removeadmin", removeadmin_cmd))
    app.add_handler(CommandHandler("setlimit", setlimit_cmd))
    app.add_handler(CommandHandler("broadcast", broadcast_cmd))
    
    # Callback handler
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Error handler
    app.add_error_handler(error_handler)
    
    logger.info("=" * 50)
    logger.info("👑 KALYUG ESCROW SERVICE BOT")
    logger.info(f"👤 Owner ID: {OWNER_ID}")
    logger.info(f"📢 Channel: {CHANNEL_USERNAME}")
    logger.info(f"💰 Max Deal Limit: ₹{MAX_DEAL_LIMIT}")
    logger.info("✅ Bot is ready!")
    logger.info("=" * 50)
    
    # Start polling
    while True:
        try:
            app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
        except Exception as e:
            logger.error(f"❌ Polling crashed: {e}")
            logger.info("🔄 Restarting in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    main()