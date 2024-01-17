from pony.orm import *
# from pony.orm.examples.estore import *
# from pony.orm.decompiling import decompile
from datetime import datetime

db = Database()

class User(db.Entity):
    _table_ = 'users'
    
    id = PrimaryKey(int, auto=True)
    uid = Required(str, unique=True, index=True)
    username = Required(str, unique=True, index=True)
    name = Required(unicode)
    banned = Required(bool, default=False)
    nsfw = Required(bool, default=False)
    bot_status = Required(bool, default=True)
    joined_time = Required(datetime, default=datetime.now)
    reset_factory = Optional(str)
    is_admin = Required(bool, default=False)
    
    blacklist = Set('Blacklist', reverse='user', cascade_delete=True)
    blocked_users = Set('Blacklist', reverse='blocked_user', cascade_delete=True)

class Blacklist(db.Entity):
    _table_ = 'blacklist'
    
    id = PrimaryKey(int, auto=True)
    user = Required(User, reverse='blacklist')
    blocked_user = Required(User, reverse='blocked_users')

db.bind(provider='sqlite', filename='database.sqlite', create_db=True)
db.generate_mapping(create_tables=True)

