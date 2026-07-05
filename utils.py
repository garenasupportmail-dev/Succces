import random
import json
from config import PREMIUM_EMOJIS

def get_emoji(name):
    if name in PREMIUM_EMOJIS:
        data = PREMIUM_EMOJIS[name]
        return f'<tg-emoji emoji-id="{data["id"]}">{data["fallback"]}</tg-emoji>'
    return ""

def get_random_emoji():
    names = list(PREMIUM_EMOJIS.keys())
    return get_emoji(random.choice(names))

def decorate(text):
    lines = text.split('\n')
    out = []
    for line in lines:
        if line.strip():
            out.append(f"{get_random_emoji()} {line} {get_random_emoji()}")
        else:
            out.append(line)
    return '\n'.join(out)

def format_deal_form(form_data):
    return f"""
{get_emoji('crown')} 𝙆𝘼𝙇𝙔𝙐𝙂 𝙀𝙎𝘾𝙍𝙊𝙒 𝘿𝙀𝘼𝙇 𝙁𝙊𝙍𝙈 {get_emoji('crown')}

{get_emoji('money')} 𝘿𝙀𝘼𝙇 𝘼𝙈𝙊𝙐𝙉𝙏 :- {form_data.get('amount', 'N/A')}

{get_emoji('wave')} 𝘽𝙐𝙔𝙀𝙍𝙎 :- {form_data.get('buyer', 'N/A')}

{get_emoji('shield')} 𝙎𝙀𝙇𝙇𝙀𝙍 :- {form_data.get('seller', 'N/A')}

{get_emoji('info')} 𝘿𝙀𝘼𝙇 𝘿𝙀𝙏𝘼𝙄𝙇 :- {form_data.get('deal_detail', 'N/A')}

{get_emoji('diamond')} 𝙍𝙇𝙎 𝙐𝙋𝙄 :- {form_data.get('rls_upi', 'N/A')}

{get_emoji('clock')} 𝘾𝙊𝙉𝘿𝙄𝙏𝙄𝙊𝙉 :- {form_data.get('condition', 'N/A')}

{get_emoji('target')} 𝙀𝙎𝘾𝙍𝙊𝙒 𝙏𝙄𝙇𝙇 :- {form_data.get('escrow_till', 'N/A')}

{get_emoji('warning')} 𝙀𝙎𝘾𝙍𝙊𝙒 𝙁𝙀𝙀𝙎 𝙄𝙎 𝙉𝙊𝙉 - 𝙍𝙀𝙁𝙐𝙉𝘿𝘼𝘽𝙇𝙀 𝙉𝙊 𝙈𝘼𝙏𝙏𝙀𝙍 𝙄𝙁 𝙏𝙃𝙀 𝘿𝙀𝘼𝙇 𝙂𝙀𝙏𝙎 𝘾𝘼𝙉𝘾𝙀𝙇𝙇𝙀𝘿.

{get_emoji('megaphone')} 𝙍𝙂 : @KALYUGESCROWSERVICE
"""

def format_deal_message(deal, action):
    form_data = json.loads(deal['form_data'])
    buyer = form_data.get('buyer', '').replace('@', '')
    seller = form_data.get('seller', '').replace('@', '')
    
    if action == 'payment':
        return f"""
{get_emoji('check')} 𝙋𝘼𝙔𝙈𝙀𝙉𝙏 𝙍𝙀𝘾𝙀𝙄𝙑𝙀𝘿 {get_emoji('check')}

{get_emoji('wave')} @{buyer}
{get_emoji('shield')} @{seller}

{get_emoji('money')} 𝘿𝙚𝙖𝙡 𝘼𝙢𝙤𝙪𝙣𝙩: {deal['amount']}

{get_emoji('rocket')} 𝘾𝙤𝙣𝙩𝙞𝙣𝙪𝙚 𝙮𝙤𝙪𝙧 𝙙𝙚𝙖𝙡!

{get_emoji('handshake')} @KALYUGESCROWSERVICE
"""
    elif action == 'cancel':
        return f"""
{get_emoji('cross')} 𝘿𝙀𝘼𝙇 𝘾𝘼𝙉𝘾𝙀𝙇𝙇𝙀𝘿 {get_emoji('cross')}

{get_emoji('wave')} @{buyer}
{get_emoji('shield')} @{seller}

{get_emoji('warning')} 𝘿𝙚𝙖𝙡 𝙝𝙖𝙨 𝙗𝙚𝙚𝙣 𝙘𝙖𝙣𝙘𝙚𝙡𝙡𝙚𝙙!

{get_emoji('handshake')} @KALYUGESCROWSERVICE
"""
    elif action == 'hold':
        return f"""
{get_emoji('clock')} 𝘿𝙀𝘼𝙇 𝙊𝙉 𝙃𝙊𝙇𝘿 {get_emoji('clock')}

{get_emoji('info')} 𝘿𝙚𝙖𝙡 𝙄𝘿: {deal['deal_id']}

{get_emoji('wave')} @{buyer}
{get_emoji('shield')} @{seller}

{get_emoji('handshake')} @KALYUGESCROWSERVICE
"""
    elif action == 'complete':
        return f"""
{get_emoji('diamond')} 𝘿𝙀𝘼𝙇 𝘾𝙊𝙈𝙋𝙇𝙀𝙏𝙀𝘿 {get_emoji('diamond')}

{get_emoji('wave')} @{buyer}
{get_emoji('shield')} @{seller}

{get_emoji('crown')} 𝙏𝙝𝙖𝙣𝙠𝙨 𝙛𝙤𝙧 𝙙𝙚𝙖𝙡𝙞𝙣𝙜!

{get_emoji('handshake')} @KALYUGESCROWSERVICE
"""
    return ""