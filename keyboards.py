from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_deal_buttons(deal_id):
    keyboard = [
        [
            InlineKeyboardButton("💰 Payment Received", callback_data=f"pay_{deal_id}"),
            InlineKeyboardButton("⏸️ Hold Deal", callback_data=f"hold_{deal_id}")
        ],
        [
            InlineKeyboardButton("❌ Cancel Deal", callback_data=f"cancel_{deal_id}"),
            InlineKeyboardButton("✅ Deal Completed", callback_data=f"complete_{deal_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_panel_buttons():
    keyboard = [
        [InlineKeyboardButton("📊 All Deals", callback_data="admin_deals")],
        [InlineKeyboardButton("📋 Pending Deals", callback_data="admin_pending")],
        [InlineKeyboardButton("👥 Admins List", callback_data="admin_list")],
        [InlineKeyboardButton("📈 Deal Status", callback_data="admin_status")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="admin_back")]
    ])

def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📝 New Deal Form", callback_data="new_deal")],
        [InlineKeyboardButton("👑 Admin Panel", callback_data="admin_panel")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)