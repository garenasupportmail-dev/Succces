# deal_handlers.py - All Deal Management Handlers

import json
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode

from config import MAX_DEAL_LIMIT
from database import *
from utils import *
from keyboards import *

# ============ CONVERSATION STATES ============
(FORM_AMOUNT, FORM_BUYER, FORM_SELLER, FORM_DEAL_DETAIL, 
 FORM_RLS_UPI, FORM_CONDITION, FORM_ESCROW_TILL) = range(7)

# ============ NEW DEAL FORM ============
async def new_deal_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start new deal form"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id) and user_id != OWNER_ID:
        await update.message.reply_text(
            decorate(f"{get_emoji('cross')} 𝙊𝙣𝙡𝙮 𝙖𝙙𝙢𝙞𝙣𝙨 𝙘𝙖𝙣 𝙘𝙧𝙚𝙖𝙩𝙚 𝙙𝙚𝙖𝙡𝙨!"),
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END
    
    await update.message.reply_text(
        decorate(f"{get_emoji('money')} 𝙀𝙣𝙩𝙚𝙧 𝙙𝙚𝙖𝙡 𝙖𝙢𝙤𝙪𝙣𝙩 (𝙢𝙖𝙭 ₹{MAX_DEAL_LIMIT}):"),
        parse_mode=ParseMode.HTML
    )
    return FORM_AMOUNT

# ============ FORM STEPS ============
async def form_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 1: Deal amount"""
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
                    decorate(f"{get_emoji('cross')} 𝙔𝙤𝙪𝙧 𝙙𝙚𝙖𝙡 𝙡𝙞𝙢𝙞𝙩 𝙞𝙨 ₹{admin_limit}. 𝘾𝙤𝙣𝙩𝙖𝙘𝙩 𝙤𝙬𝙣𝙚𝙧."),
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
    """Step 2: Buyer username"""
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
    """Step 3: Seller username"""
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
    """Step 4: Deal details"""
    context.user_data['deal_data']['deal_detail'] = update.message.text.strip()
    await update.message.reply_text(
        decorate(f"{get_emoji('diamond')} 𝙀𝙣𝙩𝙚𝙧 𝙍𝙇𝙎 𝙐𝙋𝙄:"),
        parse_mode=ParseMode.HTML
    )
    return FORM_RLS_UPI

async def form_rls_upi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 5: RLS UPI"""
    context.user_data['deal_data']['rls_upi'] = update.message.text.strip()
    await update.message.reply_text(
        decorate(f"{get_emoji('clock')} 𝙀𝙣𝙩𝙚𝙧 𝙘𝙤𝙣𝙙𝙞𝙩𝙞𝙤𝙣:"),
        parse_mode=ParseMode.HTML
    )
    return FORM_CONDITION

async def form_condition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 6: Condition"""
    context.user_data['deal_data']['condition'] = update.message.text.strip()
    await update.message.reply_text(
        decorate(f"{get_emoji('target')} 𝙀𝙣𝙩𝙚𝙧 𝙚𝙨𝙘𝙧𝙤𝙬 𝙩𝙞𝙡𝙡 (𝙚.𝙜. 𝙩𝙞𝙡𝙡 𝙩𝙧𝙖𝙣𝙨𝙛𝙚𝙧):"),
        parse_mode=ParseMode.HTML
    )
    return FORM_ESCROW_TILL

async def form_escrow_till(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 7: Escrow till - FINAL"""
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
    """Cancel form"""
    await update.message.reply_text(
        decorate(f"{get_emoji('cross')} 𝙁𝙤𝙧𝙢 𝙘𝙖𝙣𝙘𝙚𝙡𝙡𝙚𝙙."),
        parse_mode=ParseMode.HTML
    )
    context.user_data.clear()
    return ConversationHandler.END

# ============ DEAL STATUS COMMAND ============
async def deal_status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check deal status - /status DEAL_ID"""
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
    
    # Get logs
    logs = get_logs(deal_id)
    log_text = ""
    if logs:
        log_text = "\n{get_emoji('clock')} 𝙇𝙊𝙂𝙎\n"
        for log in logs[:5]:
            log_text += f"   • {log['action']} - {log['performed_at'][:16]}\n"
    
    msg = f"""
{get_emoji('info')} 𝘿𝙀𝘼𝙇 𝙎𝙏𝘼𝙏𝙐𝙎 {get_emoji('info')}

{get_emoji('crown')} 𝘿𝙚𝙖𝙡 𝙄𝘿: {deal['deal_id']}
{status_emoji} 𝙎𝙩𝙖𝙩𝙪𝙨: {deal['status'].upper()}

{get_emoji('money')} 𝘼𝙢𝙤𝙪𝙣𝙩: ₹{deal['amount']}
{get_emoji('wave')} 𝘽𝙪𝙮𝙚𝙧: {form_data.get('buyer', 'N/A')}
{get_emoji('shield')} 𝙎𝙚𝙡𝙡𝙚𝙧: {form_data.get('seller', 'N/A')}
{get_emoji('clock')} 𝘾𝙧𝙚𝙖𝙩𝙚𝙙: {deal['created_at']}
{get_emoji('info')} 𝘿𝙚𝙩𝙖𝙞𝙡: {form_data.get('deal_detail', 'N/A')[:50]}...
{log_text}
{get_emoji('handshake')} @KALYUGESCROWSERVICE
"""
    
    await update.message.reply_text(
        decorate(msg),
        parse_mode=ParseMode.HTML
    )

# ============ DEAL ACTION HANDLER (Buttons) ============
async def deal_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle deal buttons: pay, hold, cancel, complete"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Check if user is admin or owner
    if not is_admin(user_id) and user_id != OWNER_ID:
        await query.edit_message_text(
            decorate(f"{get_emoji('cross')} 𝙊𝙣𝙡𝙮 𝙖𝙙𝙢𝙞𝙣𝙨 𝙘𝙖𝙣 𝙥𝙚𝙧𝙛𝙤𝙧𝙢 𝙩𝙝𝙞𝙨!"),
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
            decorate(f"{get_emoji('warning')} 𝘼𝙣𝙤𝙩𝙝𝙚𝙧 𝙖𝙙𝙢𝙞𝙣 𝙞𝙨 𝙝𝙖𝙣𝙙𝙡𝙞𝙣𝙜 𝙩𝙝𝙞𝙨!"),
            parse_mode=ParseMode.HTML
        )
        return
    
    # ============ PAYMENT RECEIVED ============
    if action == 'pay':
        update_deal_status(deal_id, 'payment_received', user_id)
        add_log(deal_id, 'payment_received', user_id)
        
        msg = format_deal_message(deal, 'payment')
        await query.edit_message_text(
            decorate(msg),
            reply_markup=get_deal_buttons(deal_id),
            parse_mode=ParseMode.HTML
        )
    
    # ============ HOLD DEAL ============
    elif action == 'hold':
        update_deal_status(deal_id, 'on_hold', user_id)
        add_log(deal_id, 'hold', user_id)
        
        msg = format_deal_message(deal, 'hold')
        await query.edit_message_text(
            decorate(msg),
            reply_markup=get_deal_buttons(deal_id),
            parse_mode=ParseMode.HTML
        )
    
    # ============ CANCEL DEAL ============
    elif action == 'cancel':
        update_deal_status(deal_id, 'cancelled', user_id)
        add_log(deal_id, 'cancelled', user_id)
        
        msg = format_deal_message(deal, 'cancel')
        await query.edit_message_text(
            decorate(msg),
            parse_mode=ParseMode.HTML
        )
    
    # ============ DEAL COMPLETED ============
    elif action == 'complete':
        update_deal_status(deal_id, 'completed', user_id)
        add_log(deal_id, 'completed', user_id)
        
        msg = format_deal_message(deal, 'complete')
        await query.edit_message_text(
            decorate(msg),
            parse_mode=ParseMode.HTML
        )

# ============ BUTTON CALLBACK ============
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main callback router for all buttons"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    # Deal actions (pay_, hold_, cancel_, complete_)
    if data.startswith('pay_') or data.startswith('hold_') or data.startswith('cancel_') or data.startswith('complete_'):
        await deal_action(update, context)
        return
    
    # Admin panel actions
    if data.startswith('admin_'):
        from admin_panel import admin_callback
        await admin_callback(update, context)
        return
    
    # New deal
    if data == "new_deal":
        await new_deal_cmd(update, context)
        return
    
    # Admin panel
    if data == "admin_panel":
        from admin_panel import admin_panel_cmd
        await admin_panel_cmd(update, context)
        return
    
    # Help
    if data == "help":
        from handlers import help_cmd
        await help_cmd(update, context)
        return

# ============ ERROR HANDLER ============
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Global error handler"""
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Update {update} caused error: {context.error}", exc_info=context.error)