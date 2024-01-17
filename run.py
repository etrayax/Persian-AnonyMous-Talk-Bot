from pyrogram       import Client, filters, errors, enums
from pyrogram.types import *

# Database
from models import User, Blacklist, db_session, commit

from assets     import Messages, Buttons
from methodes   import Methodes
from variables  import ADMIN, BOT_USERNAME, API_HASH, API_ID, TOKEN
from hashlib    import md5
from random     import random

import asyncio
import pyromod

app = Client(
    "Talk",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN
)

@app.on_message(filters.private & filters.text)
async def OnCommand(client: Client, message: Message):
    
    cmd = message.text.split()
    
    
    with db_session:

        if not (uinfo := User.get(uid=str(message.from_user.id))):

            uinfo = User(
                uid=str(message.from_user.id),
                username=md5(f"{message.from_user.id}{random() % 10000}".encode()).hexdigest()[:15],
                name=message.from_user.first_name,
                is_admin=message.from_user.id == ADMIN
            )
            
            commit()

        elif uinfo.banned:
            await message.reply(f"⛔️ کاربر {uinfo.name or message.from_user.first_name}، دسترسی شما توسط بات مسدود شده و مجاز به استفاده از بات نمی باشید.")
            return
        
        if cmd[0].startswith("/start") and cmd.__len__() == 1:
            
            await message.reply(Messages.welcome(uinfo.name or message.from_user.first_name))
            
            
        elif cmd[0].startswith("/start") and cmd.__len__() == 2:
            
            await Methodes.sendMessage(
                client, 
                message,
                message.from_user.id, 
                cmd[1],
            )
        
                
        elif cmd[0].startswith("/link"):
            
            await message.reply(
                f"😀 لینک شما : https://t.me/{BOT_USERNAME}?start={uinfo.username}",
            )
                
        elif cmd[0].startswith("/support"):
            
            await Methodes.sendMessage(
                client, 
                message,
                message.from_user.id, 
                admin=True
            )
            
        elif cmd[0].startswith("/status") and cmd.__len__() == 3 and (c := User.get(uid=str(message.from_user.id))) and c.is_admin:
            
            user_information = User.get(uid=cmd[2]) if cmd[1] == "id" else User.get(username=cmd[2]) if cmd[1] == "username" else None
                
            if user_information:
                
                await message.reply(
                    Messages.UserSettingsForAdmin(
                        user_information.uid,
                        user_information.username,
                        user_information.name,
                        user_information.joined_time,
                        user_information.nsfw,
                        user_information.banned,
                        user_information.bot_status,
                        user_information.reset_factory,
                        user_information.is_admin
                    ),
                    reply_markup=Buttons.UserPanelSettingsForAdmin(
                        user_information.uid,
                        user_information.banned,
                        user_information.bot_status,
                        user_information.nsfw,
                        user_information.is_admin
                    )
                )
            
            else:
                await message.reply("☹️ نتونستم کسی رو با این مشخصات پیدا کنم")
            
        elif cmd[0].startswith("/generate"):
            
            uinfo.username = md5(f"{message.from_user.id}{random() % 10000}".encode()).hexdigest()[:15]
            
            await message.reply(f"✅ لینک شما با موفقیت تغییر یافت.\n😀 لینک شما : https://t.me/{BOT_USERNAME}?start={uinfo.username}")
            
            commit()
            
        elif cmd[0].startswith("/settings"):
            
            user_information = Messages.UserSettings(
                uinfo.uid,
                uinfo.username,
                uinfo.name,
                uinfo.joined_time,
                uinfo.nsfw,
                uinfo.bot_status,
            )
            
            reply_markup = Buttons.UserPanelSettings(
                uinfo.bot_status,
                uinfo.nsfw
            )
            
            await message.reply(user_information, reply_markup=reply_markup)
            
        elif cmd[0].startswith("/sendall") and (cmd.__len__() >= 2 or bool(message.reply_to_message_id)) and uinfo.is_admin:
            
            tasks = []
            
            page_size = 20
            page_number = 1
            while True:
                records = User.select().page(page_number, page_size)
                
                if not records:
                    break
                for record in records:
                    
                    tasks.append(
                        client.send_message(
                            record.uid,
                            " ".join(cmd[1:]) if not bool(message.reply_to_message_id) else message.reply_to_message.text
                        )
                    )
                
                await asyncio.gather(
                    *tasks,
                    return_exceptions=True
                )
                
                await asyncio.sleep(5)
                page_number += 1
                
        elif cmd[0].startswith("/send") and (cmd.__len__() >= 3 or bool(message.reply_to_message_id)) and uinfo.is_admin:
            
            try:
                
                await client.send_message(
                    int(cmd[1]),
                    " ".join(cmd[2:]) if not bool(message.reply_to_message_id) else message.reply_to_message.text
                )

                await message.reply("😉 حله.")
                
            except:
                await message.reply("☹️ نتونستم پیامو ارسال کنم")
            
        elif cmd[0].startswith("/members") and message.from_user.id == ADMIN:
            
            await message.reply(f"❄️ Members : {User.select().count()}")
        
@app.on_callback_query()
async def OnCallBackQuery(client: Client, update: CallbackQuery):
    
    method = update.data.split("_")
    
    if not method:
        return
    
    match method[0]:
        
        case "change":
            
            with db_session:
                
                index = 1
                c = None
                
                if method.__len__() == 3:
                    
                    if ((c := User.get(uid=method[1])) and c.is_admin and update.from_user.id != ADMIN) or int(method[1]) == ADMIN:
                        return
                    
                    index = 2
                
                uinfo = User.get(uid=str(update.from_user.id)) if method.__len__() < 3 else c
                
                if update.from_user.id != ADMIN:
                    
                    if uinfo.banned:
                        return
                
                if not uinfo:
                    return
                
                match method[index]:
                    
                    case 'name':
                
                        try:


                            while \
                            (
                                name := await update.message.chat.ask(
                                    "⚙️ خب الان اسم کی می خوای تنظیم کنی رو ارسال کن این اسم توسط دیگران قابل مشاهده است.\n\n⚠️ شروع اسم نباید با عدد باشه و از کاراکتر های ویژه استفاده نشه، حداقل طول اسم 4 حداکثر طول 40 کاراکتر ", 
                                    timeout=30, 
                                    filters=filters.user(update.from_user.id)
                                )
                            )   and not name.text[0].isalpha() \
                                or not name.text.isalnum() \
                                or not len(name.text) <= 40  or not len(name.text) >= 4 \
                                or name.text == uinfo.name:
                                    
                                    if name.text == "/cancel":
                                    
                                        try:
                                            await client.send_message(
                                                update.from_user.id,
                                                "فهمیدم."
                                            )
                                        
                                        except errors.MessageIdInvalid:
                                            ...
                                        
                                        return
                                    else:
                                        continue
                                        
                        except pyromod.listen.ListenerTimeout:
                            return
                        
                        else:
                            
                            old_name = uinfo.name
                            uinfo.name = name.text
                            
                            commit()
                                
                            try:
                                await name.reply(f"✅ نام شما با موفقیت از {old_name} به {uinfo.name} تغییر یافت.")
                            
                            except:
                                ...
                        
                        return
                       
                    case 'nsfw':
                        
                        uinfo.nsfw = not uinfo.nsfw
                            
                        commit()

                        try:                    
                            await update.answer("✅ با موفقیت فعال شد ✅" if uinfo.nsfw else "❌ با موفقیت غیرفعال شد ❌")
                            
                        except:
                            return
                    
                    case 'botstatus':
                        
                        uinfo.bot_status = not uinfo.bot_status
                        
                        commit()
                        
                        try:                    
                            await update.answer("✅ با موفقیت فعال شد ✅" if uinfo.bot_status else "❌ با موفقیت غیرفعال شد ❌")
                        
                        except:
                            return

                    case 'username':
                        
                        uinfo.username = md5(f"{update.from_user.id}{random() % 10000}".encode()).hexdigest()[:15]
            
                        await update.answer("✅ با موفقیت تغییر یافت.")
            
                        commit()
                        
                        
                    case 'userstatus':
                        
                        uinfo.banned = not uinfo.banned
            
                        await update.answer("⛔️ دیگه نمی تونه از بات استفاده کنه" if uinfo.banned else "🙂 می تونه دوباره از بات استفاده کنه")
                        
                        commit()
                        
                    case 'admin':
                        
                        if update.from_user.id == ADMIN:
                        
                            uinfo.is_admin = not uinfo.is_admin
                
                            await update.answer("😉 الان ادمینه." if uinfo.is_admin else "🫠 دیگه ادمین نیست.")
                
                            commit()
                        
                        else:
                            return
                            
                user_information = Messages.UserSettings(
                    uinfo.uid,
                    uinfo.username,
                    uinfo.name,
                    uinfo.joined_time,
                    uinfo.nsfw,
                    uinfo.bot_status,
                ) if method.__len__() < 3 else Messages.UserSettingsForAdmin(
                    uinfo.uid,
                    uinfo.username,
                    uinfo.name,
                    uinfo.joined_time,
                    uinfo.nsfw,
                    uinfo.banned,
                    uinfo.bot_status,
                    uinfo.reset_factory,
                    uinfo.is_admin
                )
                
                reply_markup = Buttons.UserPanelSettings(
                    uinfo.bot_status,
                    uinfo.nsfw
                ) if method.__len__() < 3 else Buttons.UserPanelSettingsForAdmin(
                    uinfo.uid,
                    uinfo.banned,
                    uinfo.bot_status,
                    uinfo.nsfw,
                    uinfo.is_admin
                )
                
                try:
                    await client.edit_message_text(
                        update.from_user.id,
                        update.message.id,
                        user_information,
                        reply_markup=reply_markup,
                    )
                
                except errors.MessageIdInvalid:
                    
                    await client.send_message(
                        update.from_user.id,
                        user_information,
                        reply_markup=reply_markup
                    )
                
                except errors.MessageNotModified:
                    return

        case 'send':
            
            await Methodes.sendMessage(
                client, 
                update.message,
                update.from_user.id, 
                tguid=method[1],
                reply=int(method[2])
            )
        
        
        case 'del':
            
            try:
                await client.delete_messages(
                    int(method[1]),
                    int(method[2])
                )

                try:
                    await update.message.edit(
                        "😎 حذفش کردم"
                    )
                    
                except errors.EditBotInviteForbidden:
                    await update.message.reply(
                        "😎 حذفش کردم"
                    )
                
            except:
                
                try:
                    await update.message.edit(
                        "🫠 تلاشم کردم ولی نشد"
                    )
                    
                except errors.MessageIdInvalid:
                    await update.message.reply(
                        "🫠 تلاشم کردم ولی نشد"
                    )
        
        
        case 'block':
            
            with db_session:
                
                uinfo = User.get(uid=str(update.from_user.id))
                
                if uinfo.banned:
                    return
                
                if uinfo and method[1].isnumeric():
                    
                    tginfo = User.get(uid=method[1])
                    
                    if not tginfo:
                        await update.answer("☹️ نتونستم پیداش کنم ☹️")
                    
                    if tginfo.is_admin:
                        return
                    
                    else:
                        
                        if Blacklist.exists(user=uinfo, blocked_user=tginfo):
                            
                            Blacklist.get(user=uinfo, blocked_user=tginfo).delete()
                            await update.answer("🙂 آنبلاکش کردم ")
                            await update.message.reply(
                                f"🙂 کاربر {tginfo.name} از بلاک خارج شد",
                                reply_markup=InlineKeyboardMarkup([
                                    [
                                        InlineKeyboardButton("❌ بلاک ❌", callback_data=f"block_{tginfo.uid}")
                                    ]
                                ])
                            )
                            
                        else:
                            
                            Blacklist(
                                user=uinfo, 
                                blocked_user=tginfo
                            )
                            
                            await update.answer("😎 بلاکش کردم ")
                            await update.message.reply(
                                f"😌 کاربر {tginfo.name} بلاکش کردم، دیگه نمی تونه پیام ارسال کنه.",
                                reply_markup=InlineKeyboardMarkup([
                                    [
                                        InlineKeyboardButton("✅ آنبلاک ✅", callback_data=f"block_{tginfo.uid}")
                                    ]
                                ])
                            )
                commit()
            
        case 'ban':
                        
            if update.from_user.id == ADMIN:

                with db_session:
                    
                    tginfo = User.get(uid=method[1])
                    
                    if not tginfo or int(tginfo.uid) == update.from_user.id:
                        await update.answer("☹️ نتونستم پیداش کنم ☹️")
                        
                    tginfo.banned = not tginfo.banned
        
                    await update.answer("⛔️ دیگه نمی تونه از بات استفاده کنه" if tginfo.banned else "🙂 می تونه از بات استفاده کنه")

                    await update.message.reply(
                            f"⛔️ کاربر {tginfo.name} دیگه نمی تونه از بات استفاده کنه"\
                            if tginfo.banned \
                            else f"🙂 کاربر {tginfo.name} می تونه از بات استفاده کنه",
                            reply_markup=InlineKeyboardMarkup([
                                [
                                    InlineKeyboardButton(
                                        "♻️ UnBan ♻️" if tginfo.banned else "⛔️ Ban ⛔️",
                                        f"change_{tginfo.uid}_ban"
                                    )
                                ]
                            ])
                        )
                        
                        
                    commit()
            


        case "status":
             
            with db_session:

                if (c := User.get(uid=str(update.from_user.id))) and c.is_admin:
                
                    user_information = User.get(uid=method[1])
                    
                    if user_information:
                        
                        await client.send_message(
                            update.from_user.id,
                            Messages.UserSettingsForAdmin(
                                user_information.uid,
                                user_information.username,
                                user_information.name,
                                user_information.joined_time,
                                user_information.nsfw,
                                user_information.banned,
                                user_information.bot_status,
                                user_information.reset_factory,
                                user_information.is_admin
                            ),
                            reply_markup=Buttons.UserPanelSettingsForAdmin(
                                user_information.uid,
                                user_information.banned,
                                user_information.bot_status,
                                user_information.nsfw,
                                user_information.is_admin
                            )
                        )
                        
                    else:
                        await update.answer("☹️ نتونستم پیداش کنم")
        
        case "close":
            
            try:
                await update.message.delete()
                
            except errors.MessageIdInvalid:
                await update.answer("😔 تلاشم کردم ولی حذف نشد")
                
app.run()