from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from variables      import BOT_USERNAME


class Messages:
    
    def welcome(name: str) -> str:
    
        return f"""❤️‍🔥 کاربر {name} عزیز، خوش اومدی 

🔸 با استفاده از این بات می تونی به طور کاملا ناشناس به دیگران پیام ارسال/دریافت 🤫 کنی، اما قابلیت بات محدود به ارسال دریافت پیام نیست و کلی قابلیت دیگه رو می تونی به طور کاملا رایگان استفاده کنی

🙂 برای شروع از دستور /settings استفاده کن """

    
    def UserSettings(userid: str|int, username: str, name: str, joined_time: str, nsfw_check: bool = False, bot_status: bool = True) -> str:
        return f"""🆔 شناسه کاربری : {userid}
🕵️‍♂️ نام کاربری : {username}
☃️ نام نمایشی : {name}

♻️ وضعیت بات : {'فعال' if bot_status else 'خاموش'}
🔰 سیستم تشخیص NSFW : {'فعال' if nsfw_check else 'خاموش'}

💎 لینک : 
⚙️ https://t.me/{BOT_USERNAME}?start={username}
    
"""

    def UserSettingsForAdmin(userid: str|int, username: str, name: str, joined_time: str, nsfw_check: bool = False, user_status: bool = False, bot_status: bool = True, factory_code: str = None, is_admin : bool = False):
        return f"""🆔 ID : {userid}
👤 Username : {username}
🕵🏻 name : {name}

☃️ User Status : {'Active' if not user_status else 'Deactive'}
♻️ Bot Status : {'Active' if bot_status else 'Deactive'}
🔰 NSFW Check : {'Active' if nsfw_check else 'Deactive'}

⏰ Joined Time : {joined_time:%Y-%m-%d | %H:%M:%S}
🌀 Reset Factory Code : {factory_code}
👮‍♂️ Admin : {'Yes' if is_admin else 'No'}

💎 User Link : 
⚙️ https://t.me/{BOT_USERNAME}?start={username}
"""


class Buttons:
    
    def UserPanelSettings(bot_status: bool, nsfw: bool):
        
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🕵️‍♂️ تغییر نام 🕵️‍♂️", callback_data="change_name"),
            ],
            [
                InlineKeyboardButton("♻️ خاموش کردن بات ♻️" if bot_status else "🔩 فعال کردن بات 🔩", callback_data="change_botstatus")
            ],
            [
                InlineKeyboardButton("👮‍♂️ خاموش کردن NSFW 👮‍♂️" if nsfw else "🎛 فعال کردن NSFW 🎛", callback_data="change_nsfw")
            ],
            [
                InlineKeyboardButton("⚙️ ایجاد لینک جدید ⚙️", callback_data="change_username")
            ],
            [
                InlineKeyboardButton("❌ بستن پنل ❌", callback_data="close")
            ],
        ])
        
    def UserPanelSettingsForAdmin(tguid: str|int, banned: bool = False, bot_status: bool = True, nsfw_check: bool = False, is_admin : bool = False):
        
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🕵🏻 Change Name 🕵🏻", callback_data=f"change_{tguid}_name")
            ],
            [
                InlineKeyboardButton("👤 Change Username 👤", callback_data=f"change_{tguid}_username")
            ],
            [
                InlineKeyboardButton(
                    "🌀 UnBan User 🌀" if banned else"⛔️ Ban User ⛔️",
                    callback_data=f"change_{tguid}_userstatus"
                ),
                
                InlineKeyboardButton(
                    "❌ Deactive Bot ❌" if bot_status else "♻️ Active Bot ♻️", 
                    callback_data=f"change_{tguid}_botstatus"
                )
            ],
            [
                InlineKeyboardButton(
                    "🚫 Deactive NSFW 🚫" if nsfw_check else "🔰 Active NSFW 🔰",
                    callback_data=f"change_{tguid}_nsfw"
                ),
                InlineKeyboardButton(
                    "👮‍♂️ Promoted to Admin 👮‍♂️" if not is_admin else "👤 Restricted 👤",
                    callback_data=f"change_{tguid}_admin"
                )
            ]
        ])
    
    def MessageCTRLForTG(uid: str|int, tguid: str|int, blocked: bool, reply: str|int, name: str = None, is_admin: bool = False):
        
        
        if is_admin:
            
            return InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(name, callback_data="status_" + str(uid)),
                ],
                [
                    InlineKeyboardButton("⛔️ Ban User ⛔️", callback_data="ban_" + str(uid)),
                ],
                [
                    InlineKeyboardButton("📬 Reply 📬", callback_data="send_" + str(uid) + "_" + str(reply))
                ]
            ])  
            
        
        else:
            
            return InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(name, callback_data="status_" + str(uid)),
                ],
                [
                    InlineKeyboardButton(
                        "❌ بلاک ❌" if not blocked else "✅ آنبلاک ✅", callback_data="block_" + str(uid)
                    ),
                ],
                [
                    InlineKeyboardButton("📬 پاسخ 📬", callback_data="send_" + str(uid) + "_" + str(reply))
                ]
            ])
            
        
    def MessageCTRLForBS(tguid: str|int, target_message: int|str, is_admin : bool = False):
        
        if is_admin:
            
            return InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📬 Reply 📬", callback_data="send_" + str(tguid) + "_" + str(target_message))
                ],
                [
                    InlineKeyboardButton("❌ UnSend ❌", callback_data="del_" + str(tguid) + "_" + str(target_message))
                ],
                [
                    InlineKeyboardButton("🕵️‍♂️ User Status 🕵️‍♂️", callback_data="status_" + str(tguid)),
                ]
            ])
        
        else:
            return InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📬 ریپلای 📬", callback_data="send_" + str(tguid) + "_" + str(target_message)),
                ],
                [
                    InlineKeyboardButton("❌ حذف پیام ❌", callback_data="del_" + str(tguid) + "_" + str(target_message))
                ],
            ])
        
        
        