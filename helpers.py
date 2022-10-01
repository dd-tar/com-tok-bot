import re
import db
from db import conn

dao_factory_address = "..."
BASE_URI = "http://127.0.0.1:3000/"

CREATE_TOKEN = "create_token/"
MINT_TOKEN = "mint_token/"
CHANGE_PRICE = "change_price/"
VERIFY_ADDRESS = "verify_address/"


async def is_address(address: str) -> (bool, str):
    if address == dao_factory_address:
        raise ValueError('The address should not be the address of the factory contract')
    if address[:2] != "0x":
        raise ValueError('Address should start with 0x')

    adr = address[2:]
    # throws exception if the string is not convertible to a hexadecimal number
    bts = bytearray.fromhex(adr)

    if len(bts) != 20:
        raise ValueError("The address must be 20 bytes")

    return True, "Wow, you go good!"


async def is_float(price: str) -> bool:
    try:
        float(price)
        return True
    except ValueError:
        return False


async def check_string(s: str):
    return bool(re.match("^[A-Za-z0-9_]*$", s))


async def get_create_token_link(_name, _symbol, _price) -> str:
    return '{}{}{}/{}/{}'.format(BASE_URI, CREATE_TOKEN, _name, _symbol, _price)


async def get_mint_token_link(_token_address, _amount) -> str:
    return '{}{}{}/{}'.format(BASE_URI, MINT_TOKEN, _token_address, _amount)


async def get_change_price_link(_token_address, _new_price) -> str:
    return '{}{}{}/{}'.format(BASE_URI, CHANGE_PRICE, _token_address, _new_price)


async def get_verify_address_link(_user_address, _chat_id) -> str:
    return '{}{}{}/{}'.format(BASE_URI, VERIFY_ADDRESS, _user_address, _chat_id)


async def add_group_token(address: str, chat_id: str) -> ():
    inserted_row_id = db.insert("community_chat", {
        "id": chat_id,
        "gt": address
    })
    res = await get_group_token(chat_id)

    return res


async def get_group_token(chat_id: str) -> ():
    cursor = db.get_cursor()
    sql_select_query = f"select * from community_chat where id = {chat_id}"
    cursor.execute(sql_select_query)
    record = cursor.fetchall()
    print("record: " + str(record))
    return record[0][0], record[0][1]


async def check_group_token_exists(chat_id: str) -> bool:
    cursor = db.get_cursor()
    sql_select_query = f"select exists(select * from community_chat where id = {chat_id})"
    cursor.execute(sql_select_query)
    record = cursor.fetchall()
    print(f"check_group_token_exists: {record}")
    return bool(record[0][0])


async def delete_group_token(chat_id) -> bool:
    db.delete("community_chat", chat_id)
    return True


async def save_approve_request(_user_addr, _user_id, _chat_id):
    addr = _user_addr[2:]
    db.insert("approve", {
        "user_address": addr,
        "id": _user_id,
        "chat_id": _chat_id
    })


async def get_approve_request(_user_addr: str, _chat_id: str) -> ():
    print("get_approve_request")
    cursor = db.get_cursor()
    #try:
    blob = _user_addr[2:]
    print("blob: " + blob)
    print("chat id: " + _chat_id)
    cursor.execute("""SELECT id FROM approve WHERE user_address=? AND chat_id=?""", (blob, _chat_id))
    record = cursor.fetchall()
    print(f"get_approve_request: {record}")
    return record
    #except:
    #    return "-1"


async def delete_approve_request(_user_addr, _chat_id):
    print("delete_approve_request")
    cursor = db.get_cursor()
    blob = _user_addr[2:]
    cursor.execute("""DELETE FROM approve WHERE user_address=? AND chat_id=?""", (blob, _chat_id))
    conn.commit()
