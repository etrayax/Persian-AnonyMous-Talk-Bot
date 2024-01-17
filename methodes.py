from pyrogram       import Client, filters, errors
from pyrogram.types import Message

from models    import User, db_session, Blacklist
from assets    import Buttons
from variables import ADMIN

import asyncio
import pyromod

class Methodes:
    
    async def sendMessage(client: Client, message: Message, userid: int, tgusername: str = None, tguid: str|int = None, reply: int = 0, admin : bool = False):
        
        
        with db_session:
        
            uinfo = User.get(uid=str(userid))
            ustatus = False
            
            if uinfo.banned:
                await message.reply(f"⛔️ کاربر {uinfo.name or message.from_user.first_name}، دسترسی شما توسط بات مسدود شده و مجاز به استفاده از بات نمی باشید.")
                return
            
            if not admin:
            
                tginfo = User.get(username=tgusername) if tgusername else User.get(uid=str(tguid))
                
                if not tginfo:
                    
                    await message.reply("🕵️‍♂️ نتوستم کسی رو که می خواستی پیدا کنم 🕵️‍♂️")
                    return

                else:
                    
                    if uinfo.uid == tginfo.uid:
                        
                        await message.reply("😐 نمی تونی با خودت حرف بزنی")
                        return
                
                if not tginfo.bot_status:
                
                    await message.reply("😴 کاربر باتو خاموش کرده 😴")
                    return
                    
                elif (ustatus := Blacklist.exists(user=tginfo, blocked_user=uinfo)):
                    
                    await message.reply(f"😢 کاربر {tginfo.name} تو رو مسدود کرده")
                    return
                    
            else:
                
                if uinfo.is_admin:
                    return
                
                tginfo = User.select(lambda c:c.is_admin)

            try:
                
                placeholder = "🧨 در حال ارسال پیام ناشناس به {0} هستی.\n\nمی‌تونی هر حرف یا انتقادی که تو دلت هست رو بگی.".format(tginfo.name) \
                    if not admin else "👮‍♂️ در حال ارسال پیام به پشتیبانی می باشید.\nمشکل، اعتقاد، پیشنهاد و ... به طور کامل بنویسید."

                user_message : Message = await message.chat.ask(placeholder, timeout=60 * 10, filters=filters.user(userid))
        
            except pyromod.listen.ListenerTimeout:
                await message.reply("🤔 مثل اینکه منصرف شدی پیامتو بفرستی منم لغو اش کردم")
            
            except errors.UserIsBlocked:
                return
            
            else:
                
                if not admin:
                
                    if tginfo.nsfw and bool(user_message.text) and PersianSwear().has_swear(user_message.text):
                        await user_message.reply("🚫 پیام شما حاوی محتوا رکیک می باشد 🚫")
                        return
            
                if bool(user_message.text) and user_message.text == "/cancel":
                    
                    try:
                        await user_message.delete()
                        await client.send_message(
                            userid,
                            "فهمیدم."
                        )
                    
                    except:
                        return
                    
                    else:
                        return
                
                try:
                    
                    if bool(user_message.media_group_id):
                        await message.reply("☹️ فعلا نمی تونی مدیا گروپ بفرستی")
                    
                    else:
                        
                        if admin:
                            
                            task = []
                            
                            for user in tginfo:
                                
                                task.append(
                                    user_message.copy(
                                        int(user.uid), 
                                        reply_to_message_id=reply,
                                        reply_markup=Buttons.MessageCTRLForTG(
                                            userid,
                                            user.uid,
                                            ustatus,
                                            user_message.id,
                                            uinfo.name if not admin else None,
                                            user.is_admin
                                        )
                                    )
                                )
                                
                            await asyncio.gather(
                                *task,
                                return_exceptions=True
                            )
                        
                        else:
                        
                            msg = await user_message.copy(
                                int(tginfo.uid), 
                                reply_to_message_id=reply,
                                reply_markup=Buttons.MessageCTRLForTG(
                                    userid,
                                    tginfo.uid,
                                    ustatus,
                                    user_message.id,
                                    uinfo.name,
                                    tginfo.is_admin
                                )
                            )

                
                except errors.UserIsBlocked:
                    await message.reply("😴 کاربر باتو خاموش کرده 😴")
                
                except Exception as err:
                    await message.reply("🙏 مشکلی در روند ارسال پیام به وجود آمده است، مشکل بررسی و به زودی رفع می شود 🙏")
                    
                    task.append(
                        client.send_message(ADMIN, f"SendMessage : {err}")
                    )
                    
                        
                else:
                    
                    if not admin:
                        
                        await client.send_message(
                            userid,
                            f"🙂 پیامتو ارسال کردم",
                            reply_to_message_id=user_message.id,
                            reply_markup=Buttons.MessageCTRLForBS(
                                    int(tginfo.uid),
                                    msg.id,
                                    admin
                                )
                            )
                    
                    else:
                        
                        await client.send_message(
                            userid,
                            "🙂 پیام شما با موفقیت ارسال شد"
                        )
                        
                        
import json
from string import punctuation


class PersianSwear:
    def __init__(self):
        with open("data.json", encoding="utf-8") as file:
            self.data = json.load(file)
        self.swear_words = set(self.data["word"])

    def ignoreSY(self, text):
        translator = str.maketrans("", "", punctuation)
        return text.translate(translator)

    def filter_words(self, text, symbol="*", ignoreOT=False):
        if not self.swear_words:
            return text

        words = text.split()
        filtered_words = []
        for word in words:
            if word in self.swear_words or (
                ignoreOT and self.ignoreSY(word) in self.swear_words
            ):
                filtered_words.append(symbol)
            else:
                filtered_words.append(word)

        return " ".join(filtered_words)

    def is_empty(self):
        return not self.swear_words

    def add_word(self, word):
        self.swear_words.add(word)
        self.data["word"].append(word)

    def remove_word(self, word):
        if word in self.swear_words:
            self.swear_words.remove(word)
        if word in self.data["word"]:
            self.data["word"].remove(word)

    def is_bad(self, text, ignoreOT=False):
        if ignoreOT:
            text = self.ignoreSY(text)
        text = text.replace("\u200c", "")
        return text in self.swear_words

    def has_swear(self, text, ignoreOT=False):
        if ignoreOT:
            text = self.ignoreSY(text)
        text = text.replace("\u200c", "")
        if not self.swear_words:
            return False

        words = text.split()
        return any(word in self.swear_words for word in words)

    def tostring(self):
        return " - ".join(self.swear_words)
    
