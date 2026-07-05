# admin_panel.py - All Admin Panel Commands

import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config import OWNER_ID, MAX_DEAL_LIMIT
from database import *
from utils import *
from keyboards import *

# ============ ADMIN PANEL MAIN ============
async def admin_panel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin panel with all options"""
    user_id = update.effective_user.id
    
    # Check if user is admin or owner
    if not is_admin(user_id) and user_id != OWNER_ID:
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(
                decorate(f"{get_emoji('cross')} 𝘼𝙙𝙢𝙞𝙣 𝙥𝙖𝙣𝙚𝙡 𝙤𝙣𝙡𝙮!"),
                parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_text(
                decorate(f"{get_emoji('cross')} 𝘼𝙙𝙢𝙞𝙣 𝙥𝙖𝙣𝙚𝙡 𝙤𝙣𝙡𝙮!"),
                parse_mode=ParseMode.HTML
            )
        return
    
    # Get stats
    total_deals = len(get_all_deals())
    pending_deals = len(get_deals_by_status('pending'))
    completed_deals = len(get_deals_by_status('completed'))
    cancelled_deals = len(get_deals_by_status('cancelled'))
    on_hold_deals = len(get_deals_by_status('on_hold'))
    admins_list = get_admins()
    
    # Get current admin's limit
    admin_limit = get_admin_limit(user_id) if user_id != OWNER_ID else MAX_DEAL_LIMIT
    
    msg = f"""
{get_emoji('crown')} 𝘼𝘿𝙈𝙄𝙉 𝙋𝘼𝙉𝙀𝙇 {get_emoji('crown')}
{get_emoji('shield')} 𝙆𝘼𝙇𝙔𝙐𝙂 𝙀𝙎𝘾𝙍𝙊𝙒 𝙎𝙀𝙍𝙑𝙄𝘾𝙀

{get_emoji('money')} 𝙏𝙤𝙩𝙖𝙡 𝘿𝙚𝙖𝙡𝙨: {total_deals}
{get_emoji('clock')} 𝙋𝙚𝙣𝙙𝙞𝙣𝙜: {pending_deals}
{get_emoji('check')} 𝘾𝙤𝙢𝙥𝙡𝙚𝙩𝙚𝙙: {completed_deals}
{get_emoji('cross')} 𝘾𝙖𝙣𝙘𝙚𝙡𝙡𝙚𝙙: {cancelled_deals}
{get_emoji('warning')} 𝙊𝙣 𝙃𝙤𝙡𝙙: {on_hold_deals}

{get_emoji('shield')} 𝘼𝙙𝙢𝙞𝙣𝙨: {len(admins_list)}
{get_emoji('diamond')} 𝙔𝙤𝙪𝙧 𝙇𝙞𝙢𝙞𝙩: ₹{admin_limit}

{get_emoji('handshake')} @KALYUGESCROWSERVICE
"""
    
    # Get message object
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        message = query.message
    else:
        message = update.message
    
    await message.reply_text(
        decorate(msg),
        reply_markup=get_admin_panel_buttons(),
        parse_mode=ParseMode.HTML
    )

# ============ ADMIN PANEL CALLBACKS ============
async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin panel button clicks"""
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
    
    # ============ BACK BUTTON ============
    if data == "admin_back":
        await admin_panel_cmd(update, context)
        return
    
    # ============ ALL DEALS ============
    if data == "admin_deals":
        deals = get_all_deals()
        if not deals:
            msg = f"{get_emoji('info')} 𝙉𝙤 𝙙𝙚𝙖𝙡𝙨 𝙛𝙤𝙪𝙣𝙙."
        else:
            msg = f"{get_emoji('crown')} 𝘼𝙇𝙇 𝘿𝙀𝘼𝙇𝙎 {get_emoji('crown')}\n\n"
            for d in deals[:10]:
                status_emoji = {
                    'pending': '🟡',
                    'payment_received': '🟢',
                    'on_hold': '🟠',
                    'completed': '✅',
                    'cancelled': '❌'
                }.get(d['status'], '🟡')
                msg += f"{status_emoji} `{d['deal_id']}` - ₹{d['amount']} - {d['status'].upper()}\n"
                msg += f"   👤 {d['buyer']} → {d['seller']}\n\n"
            if len(deals) > 10:
                msg += f"\n... 𝙖𝙣𝙙 {len(deals)-10} 𝙢𝙤𝙧𝙚"
        
        await query.edit_message_text(
            decorate(msg),
            reply_markup=get_back_button(),
            parse_mode=ParseMode.HTML
        )
        return
    
    # ============ PENDING DEALS ============
    if data == "admin_pending":
        deals = get_deals_by_status('pending')
        if not deals:
            msg = f"{get_emoji('check')} 𝙉𝙤 𝙥𝙚𝙣𝙙𝙞𝙣𝙜 𝙙𝙚𝙖𝙡𝙨."
        else:
            msg = f"{get_emoji('clock')} 𝙋𝙀𝙉𝘿𝙄𝙉𝙂 𝘿𝙀𝘼𝙇𝙎 {get_emoji('clock')}\n\n"
            for d in deals[:10]:
                msg += f"🟡 `{d['deal_id']}` - ₹{d['amount']}\n"
                msg += f"   👤 {d['buyer']} → {d['seller']}\n\n"
            if len(deals) > 10:
                msg += f"\n... 𝙖𝙣𝙙 {len(deals)-10} 𝙢𝙤𝙧𝙚"
        
        await query.edit_message_text(
            decorate(msg),
            reply_markup=get_back_button(),
            parse_mode=ParseMode.HTML
        )
        return
    
    # ============ ADMINS LIST ============
    if data == "admin_list":
        admins = get_all_admins_with_limits()
        if not admins:
            msg = f"{get_emoji('info')} 𝙉𝙤 𝙖𝙙𝙢𝙞𝙣𝙨 𝙛𝙤𝙪𝙣𝙙."
        else:
            msg = f"{get_emoji('shield')} 𝘼𝘿𝙈𝙄𝙉 𝙇𝙄𝙎𝙏 {get_emoji('shield')}\n\n"
            for a in admins:
                is_owner_tag = "👑 " if a[0] == OWNER_ID else ""
                msg += f"{is_owner_tag}𝙄𝙳: `{a[0]}`\n"
                msg += f"   𝙇𝙞𝙢𝙞𝙩: ₹{a[2]}\n\n"
        
        await query.edit_message_text(
            decorate(msg),
            reply_markup=get_back_button(),
            parse_mode=ParseMode.HTML
        )
        return
    
    # ============ DEAL STATUS SUMMARY ============
    if data == "admin_status":
        total = len(get_all_deals())
        pending = len(get_deals_by_status('pending'))
        completed = len(get_deals_by_status('completed'))
        cancelled = len(get_deals_by_status('cancelled'))
        on_hold = len(get_deals_by_status('on_hold'))
        payment_received = len(get_deals_by_status('payment_received'))
        
        msg = f"""
{get_emoji('target')} 𝘿𝙀𝘼𝙇 𝙎𝙏𝘼𝙏𝙐𝙎 {get_emoji('target')}

{get_emoji('money')} 𝙏𝙤𝙩𝙖𝙡: {total}
{get_emoji('clock')} 𝙋𝙚𝙣𝙙𝙞𝙣𝙜: {pending}
{get_emoji('check')} 𝘾𝙤𝙢𝙥𝙡𝙚𝙩𝙚𝙙: {completed}
{get_emoji('cross')} 𝘾𝙖𝙣𝙘𝙚𝙡𝙡𝙚𝙙: {cancelled}
{get_emoji('warning')} 𝙊𝙣 𝙃𝙤𝙡𝙙: {on_hold}
{get_emoji('money')} 𝙋𝙖𝙮𝙢𝙚𝙣𝙩 𝙍𝙚𝙘𝙚𝙞𝙫𝙚𝙙: {payment_received}

{get_emoji('handshake')} @KALYUGESCROWSERVICE
"""
        await query.edit_message_text(
            decorate(msg),
            reply_markup=get_back_button(),
            parse_mode=ParseMode.HTML
        )
        return

# ============ SETLIMIT COMMAND (Owner Only) ============
async def setlimit_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set deal limit for an admin - /setlimit 5000 123456789"""
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID:
        await update.message.reply_text(
            decorate(f"{get_emoji('cross')} 𝙊𝙬𝙣𝙚𝙧 𝙤𝙣𝙡𝙮!"),
            parse_mode=ParseMode.HTML
        )
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            decorate(f"{get_emoji('info')} 𝙐𝙨𝙖𝙜𝙚: /setlimit <𝙖𝙢𝙤𝙪𝙣𝙩> <𝙪𝙨𝙚𝙧_𝙞𝙙>\n\n"
                     f"𝙀𝙭𝙖𝙢𝙥𝙡𝙚: /setlimit 5000 123456789\n"
                     f"𝙈𝙖𝙭 𝙡𝙞𝙢𝙞𝙩: {MAX_DEAL_LIMIT}"),
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
        
        # Notify the admin
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

# ============ APPROVE COMMAND (Owner Only) ============
async def approve_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add admin - /approve USER_ID"""
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
    
    # Check if already admin
    if is_admin(target_id):
        await update.message.reply_text(
            decorate(f"{get_emoji('warning')} 𝙐𝙨𝙚𝙧 𝙞𝙨 𝙖𝙡𝙧𝙚𝙖𝙙𝙮 𝙖𝙣 𝙖𝙙𝙢𝙞𝙣!"),
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

# ============ REMOVE ADMIN COMMAND (Owner Only) ============
async def removeadmin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove admin - /removeadmin USER_ID"""
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
    
    if not is_admin(target_id):
        await update.message.reply_text(
            decorate(f"{get_emoji('warning')} 𝙐𝙨𝙚𝙧 𝙞𝙨 𝙣𝙤𝙩 𝙖𝙣 𝙖𝙙𝙢𝙞𝙣!"),
            parse_mode=ParseMode.HTML
        )
        return
    
    remove_admin(target_id)
    
    await update.message.reply_text(
        decorate(f"{get_emoji('cross')} 𝘼𝙙𝙢𝙞𝙣 𝙧𝙚𝙢𝙤𝙫𝙚𝙙!"),
        parse_mode=ParseMode.HTML
    )

# ============ BROADCAST COMMAND (Admin Only) ============
async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast message to all deals - /broadcast MESSAGE"""
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
        
        # Try to send to buyer
        try:
            if buyer.isdigit():
                await context.bot.send_message(
                    chat_id=int(buyer),
                    text=decorate(f"{get_emoji('megaphone')} 𝘽𝙍𝙊𝘼𝘿𝘾𝘼𝙎𝙏\n\n{msg_text}\n\n{get_emoji('handshake')} @KALYUGESCROWSERVICE"),
                    parse_mode=ParseMode.HTML
                )
                sent += 1
        except:
            failed += 1
        
        # Try to send to seller
        try:
            if seller.isdigit():
                await context.bot.send_message(
                    chat_id=int(seller),
                    text=decorate(f"{get_emoji('megaphone')} 𝘽𝙍𝙊𝘼𝘿𝘾𝘼𝙎𝙏\n\n{msg_text}\n\n{get_emoji('handshake')} @KALYUGESCROWSERVICE"),
                    parse_mode=ParseMode.HTML
                )
                sent += 1
        except:
            failed += 1
    
    await update.message.reply_text(
        decorate(f"{get_emoji('check')} 𝙎𝙚𝙣𝙩: {sent} | {get_emoji('cross')} 𝙁𝙖𝙞𝙡𝙚𝙙: {failed}"),
        parse_mode=ParseMode.HTML
    )