#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KALYUG ESCROW SERVICE BOT
Main entry point - connects all modules
"""

import os
import sys
import logging
import threading
import time

# ============ LOGGING ============
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============ IMPORT ALL MODULES ============
try:
    from config import BOT_TOKEN, OWNER_ID, CHANNEL_USERNAME, MAX_DEAL_LIMIT
    from database import *
    from utils import *
    from keyboards import *
    from handlers import *
    from admin_panel import *
    from deal_handlers import *
    logger.info("✅ All modules imported successfully")
except ImportError as e:
    logger.error(f"❌ Import error: {e}")
    logger.info("📁 Make sure all files are in the same directory:")
    logger.info("   - config.py")
    logger.info("   - database.py")
    logger.info("   - utils.py")
    logger.info("   - keyboards.py")
    logger.info("   - handlers.py")
    logger.info("   - admin_panel.py")
    logger.info("   - deal_handlers.py")
    sys.exit(1)

# ============ MAIN FUNCTION ============
def main():
    """Main entry point for the bot"""
    logger.info("=" * 60)
    logger.info("🚀 Starting KALYUG ESCROW SERVICE BOT...")
    logger.info("=" * 60)
    logger.info(f"👑 Owner ID: {OWNER_ID}")
    logger.info(f"📢 Channel: {CHANNEL_USERNAME}")
    logger.info(f"💰 Max Deal Limit: ₹{MAX_DEAL_LIMIT}")
    logger.info("=" * 60)
    
    # ============ CHECK BOT TOKEN ============
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN environment variable is not set!")
        logger.info("📝 Set BOT_TOKEN in Render Environment Variables")
        sys.exit(1)
    
    # ============ START FLASK (For Render Health Check) ============
    try:
        from flask import Flask
        flask_app = Flask(__name__)
        
        @flask_app.route('/')
        @flask_app.route('/health')
        def health():
            return "✅ BOT RUNNING", 200
        
        def run_flask():
            try:
                port = int(os.environ.get('PORT', 5000))
                flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
            except Exception as e:
                logger.error(f"❌ Flask error: {e}")
        
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        logger.info(f"✅ Flask server started on port {os.environ.get('PORT', 5000)}")
    except ImportError:
        logger.warning("⚠️ Flask not installed - skipping health check server")
    
    # ============ CREATE TELEGRAM APPLICATION ============
    try:
        from telegram import Update
        from telegram.ext import (
            Application, 
            CommandHandler, 
            CallbackQueryHandler, 
            MessageHandler, 
            filters, 
            ConversationHandler
        )
        
        application = Application.builder().token(BOT_TOKEN).build()
        logger.info("✅ Telegram application created")
        
        # ============ REGISTER ALL HANDLERS ============
        
        # 1. Conversation Handler (New Deal Form)
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
        application.add_handler(conv_handler)
        logger.info("✅ Added conversation handler")
        
        # 2. User Commands
        application.add_handler(CommandHandler("start", start_cmd))
        application.add_handler(CommandHandler("help", help_cmd))
        application.add_handler(CommandHandler("status", deal_status_cmd))
        application.add_handler(CommandHandler("admin", admin_panel_cmd))
        logger.info("✅ Added user commands")
        
        # 3. Owner / Admin Commands
        application.add_handler(CommandHandler("approve", approve_cmd))
        application.add_handler(CommandHandler("removeadmin", removeadmin_cmd))
        application.add_handler(CommandHandler("setlimit", setlimit_cmd))
        application.add_handler(CommandHandler("broadcast", broadcast_cmd))
        logger.info("✅ Added admin commands")
        
        # 4. Callback Query Handler (Buttons)
        application.add_handler(CallbackQueryHandler(button_callback))
        logger.info("✅ Added callback handler")
        
        # 5. Error Handler
        application.add_error_handler(error_handler)
        logger.info("✅ Added error handler")
        
        # ============ START POLLING ============
        logger.info("=" * 60)
        logger.info("✅ Bot is ready! Starting polling...")
        logger.info("=" * 60)
        
        while True:
            try:
                application.run_polling(
                    allowed_updates=Update.ALL_TYPES,
                    drop_pending_updates=True
                )
            except Exception as e:
                logger.error(f"❌ Polling crashed: {e}")
                logger.info("🔄 Restarting in 5 seconds...")
                time.sleep(5)
                
    except ImportError as e:
        logger.error(f"❌ Telegram import error: {e}")
        logger.info("📝 Install python-telegram-bot: pip install python-telegram-bot==20.7")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()