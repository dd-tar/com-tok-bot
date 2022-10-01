import json
import logging
import os
from datetime import datetime, timedelta
from aiogram.utils.deep_linking import get_start_link, decode_payload
from hexbytes import HexBytes
from eth_account.messages import defunct_hash_message
from web3 import Web3
from aiogram.utils.markdown import hlink
from aiogram.types import ChatType
from aiogram import Bot, Dispatcher, executor, types
import helpers
from welcome import welcome_text

logging.basicConfig(level=logging.INFO)

print(os.getenv("TELEGRAM_API_TOKEN"))
API_TOKEN = str(os.getenv("TELEGRAM_API_TOKEN"))  # "t:ok-en" - if running locally
INFURA_ID = os.getenv("WEB3_INFURA_PROJECT_ID")
INFURA_PROVIDER = f"https://rinkeby.infura.io/v3/{INFURA_ID}"  # "your_infura_id" - if running locally
ERC20_BALANCE_ABI = "contract_abi/ERC20Balance.json"
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'], chat_type=[ChatType.GROUP, ChatType.SUPERGROUP, ChatType.PRIVATE])
async def send_welcome(message: types.Message):
    """Sends welcome/help msg and handles join & mint deeplinks"""

    args = message.get_args()
    print("args:")
    print(args)
    payload = decode_payload(args).split(" ")
    print("payload:")
    print(payload)
    if payload[0] == '':

        await bot.send_message(
            chat_id=message.chat.id,
            text=welcome_text,
            parse_mode="Markdown"
        )
        return

    # /mint and /join_group deeplinks:
    if len(payload) == 3:
        print("len payload == 3")
        if payload[0] == "m":
            msg = f"/mint_tokens {payload[1]} {payload[2]}"
            print("throwing to mint_tokens")
            msg1 = message
            msg1.text = msg
            await mint_tokens(msg1)
            return

    if len(payload) == 2:
        if payload[0] == "j":
            msg = f"/join_group {payload[1]} {ZERO_ADDRESS}"
            print("throwing to join_group_by_id")
            msg1 = message
            msg1.text = msg
            await join_group_by_id(msg1)
            return


@dp.message_handler(commands=['create_token'], chat_type=ChatType.PRIVATE)
async def create_token(message: types.Message):
    """Returns a link to sign the transaction of token creation with given params
         in the MetaMask extension"""
    # params: name, symbol, price
    print("started create")
    params = str.split(message.text, ' ')
    if len(params) != 4:
        await bot.send_message(message.from_user.id, "Invalid number of arguments.")
    else:
        if not (await helpers.check_string(params[1]) and helpers.check_string(params[2])):
            await bot.send_message(message.from_user.id, "Wrong arguments: Token name and symbol should contain "
                                                         "latin letters, numbers and underscore characters only")
        else:
            is_price = await helpers.is_float(params[3])
            if is_price:
                _name = params[1]
                _symbol = params[2]
                _price = params[3]
                link = await helpers.get_create_token_link(_name, _symbol, _price)
                answer_message = hlink(f'Tap to sign the {_name} ({_symbol}) token creation transaction '
                                       f'Starting {_symbol} price will be set to {_price} native tokens of the network',
                                       link)

                await bot.send_message(message.from_user.id, answer_message)
            else:
                await bot.send_message(message.from_user.id, "Wrong arguments: price should be a number")


@dp.message_handler(commands=['mint_tokens'], chat_type=ChatType.PRIVATE)
async def mint_tokens(message: types.Message):
    """Returns a link to sign the transaction of token mint with given params
        in the MetaMask extension"""
    # params: token_address, amount
    print("mint_tokens")
    print("params:" + message.text)

    params = str.split(message.text, ' ')
    print(len(params))
    if len(params) != 3:
        await bot.send_message(message.from_user.id, "Invalid number of arguments.")
    else:
        is_addr = False
        try:
            is_addr = await helpers.is_address(params[1])
        except Exception as e:
            await bot.send_message(message.from_user.id, "Wrong address: " + e.args[0])

        if is_addr:
            if await helpers.is_float(params[2]):
                _token_address = params[1]
                _amount = params[2]

                link = await helpers.get_mint_token_link(_token_address, _amount)

                answer_message = hlink(f'Tap to mint {_amount} tokens of {_token_address} token contract', link)

                await bot.send_message(message.from_user.id, answer_message)
            else:
                await bot.send_message(message.from_user.id, "Wrong amount: amount should be a number")


@dp.message_handler(commands=['change_token_price'], chat_type=ChatType.PRIVATE)
async def change_token_price(message: types.Message):
    """Returns a link to sign the transaction of token mint with given params
        in the MetaMask extension"""
    # params: token_address, amount
    params = str.split(message.text, ' ')
    print("change_price")
    if len(params) != 3:
        await bot.send_message(message.from_user.id, "Invalid number of arguments.")
        print("len")
    else:
        is_addr = False
        try:
            is_addr = await helpers.is_address(params[1])
        except Exception as e:
            await bot.send_message(message.from_user.id, "Wrong address: " + e.args[0])

        if is_addr:
            flt = await helpers.is_float(params[2])
            if flt:
                _token_address = params[1]
                _new_price = params[2]

                link = await helpers.get_change_price_link(_token_address, _new_price)

                answer_message = hlink(f'Tap to sign the transaction to change the price of the {_token_address} token '
                                       f'to {_new_price}', link)

                await bot.send_message(message.from_user.id, answer_message)
            else:
                await bot.send_message(message.from_user.id, f"Wrong price: Price should be a number")


@dp.message_handler(commands=['add_community_token'], chat_type=[ChatType.GROUP, ChatType.SUPERGROUP])
async def add_community_token(message: types.Message):
    """
    This handler will add address of the token to db in association with chat_id
    """
    # params: token_address
    params = str.split(message.text, ' ')
    print("add_group_token")
    if len(params) != 2:
        await bot.send_message(message.chat.id, "Invalid number of arguments.")
        print("len")
    else:
        chat = message.chat.id
        if await helpers.check_group_token_exists(chat):
            await bot.send_message(chat, "Token is already set  for your community")
        else:
            is_addr = False
            try:
                is_addr = await helpers.is_address(params[1])
            except Exception as e:
                await bot.send_message(chat, "Wrong address: " + e.args[0])

            if is_addr:
                caller = await bot.get_chat_member(chat, message.from_user.id)
                is_admin = caller.is_chat_admin() or caller.is_chat_owner()

                if not is_admin:
                    await bot.send_message(chat, "Only the chat administrator or owner can set the community token")
                else:
                    inserted = await helpers.add_group_token(params[1], chat)
                    await bot.send_message(chat, f"A community token with the address {inserted[1]} "
                                                 f"is set for this group")


@dp.message_handler(commands=['delete_community_token'], chat_type=[ChatType.GROUP, ChatType.SUPERGROUP])
async def delete_comm_token(message: types.Message):
    params = str.split(message.text, ' ')
    print("delete_token")
    if len(params) != 1:
        await bot.send_message(message.chat.id, "Invalid number of arguments.")
        print("len")
    else:
        chat = message.chat.id
        caller = await bot.get_chat_member(chat, message.from_user.id)
        is_admin = caller.is_chat_admin() or caller.is_chat_owner()

        if not is_admin:
            await bot.send_message(chat, "Only the chat administrator or owner can delete community token")
        else:
            # check if community actually has a token
            if not await helpers.check_group_token_exists(chat):
                await bot.send_message(chat, "Token is not set  for your community")
            else:
                delete = await helpers.delete_group_token(chat)
                await bot.send_message(chat, "Community token was successfully deleted")


@dp.message_handler(commands=['get_community_token_address'], chat_type=[ChatType.GROUP, ChatType.SUPERGROUP])
async def get_token(message: types.Message):
    params = str.split(message.text, ' ')
    print("get_token")
    if len(params) != 1:
        await bot.send_message(message.chat.id, "Invalid number of arguments.")
        print(len(params))
    else:
        chat = message.chat.id
        if not await helpers.check_group_token_exists(chat):
            await bot.send_message(chat, "Token is not set for your community")
        else:
            group_token = await helpers.get_group_token(chat)
            await bot.send_message(chat, f"Your community token address: {group_token[1]}")


@dp.message_handler(commands=['join_group'], chat_type=ChatType.PRIVATE)
async def join_group_by_id(message: types.Message):
    # params: chat_id, user_address
    # check if you have community token of <address> contract
    # using 0 address as a 2nd argument for deep link

    params = str.split(message.text, ' ')
    print("join_group")
    if len(params) != 3:
        await bot.send_message(message.from_user.id, "Invalid number of arguments.")
        return

    if params[2] == ZERO_ADDRESS:
        command = f"/join_group {params[1]} {ZERO_ADDRESS}"
        await bot.send_message(message.from_user.id, f"Please use the following command to pass a token check and"
                                                     f" join community chat: \n\n`{command}`\n\n_Use your address instead "
                                                     f"of the zero-address._", parse_mode="Markdown")
        return

    chat_id = params[1]
    try:
        int(chat_id)
    except ValueError:
        await bot.send_message(message.from_user.id, "Chat ID should be a digit")
        return

    # check if bot has this group in db
    if not await helpers.check_group_token_exists(f"{chat_id}"):
        print(f"chat id: {chat_id}")
        await bot.send_message(message.from_user.id, "Chat with this ID is not registered")
        return

    member = await bot.get_chat_member(chat_id, message.from_user.id)

    if not (member.status == "left"):
        print(member)
        chat = await bot.get_chat(chat_id)
        print(chat)
        await bot.send_message(message.from_user.id, "You are already a member of this group")
        return

    print(member)
    ###
    print("is not member")
    try:
        is_addr = await helpers.is_address(params[2])
        user_address = params[2]
    except Exception as e:
        await bot.send_message(message.from_user.id, "Wrong address: " + e.args[0]) # User not found
        return

    if is_addr:
        # SAVE ADDRESS - USER_ID - CHAT ID
        req_exists = await helpers.get_approve_request(str(user_address), f"{chat_id}")
        print(f"appr exists: {req_exists}")
        if not (req_exists == "-1" or len(req_exists) == 0):
            await bot.send_message(message.from_user.id, "The request to join the group has already been registered"
                                                         " and is awaiting signature confirmation.")
            return

        await helpers.save_approve_request(user_address, message.from_user.id, chat_id)
        link = await helpers.get_verify_address_link(user_address, chat_id)
        answer_message = hlink(f'In order to confirm that the entered address belongs to you, please'
                               f' tap this text to sign the confirmation message. \nI will check that the signer\'s'
                               f' address matches the address you entered in this command.', link)
        await bot.send_message(message.from_user.id, answer_message)
        return


@dp.message_handler(chat_type=ChatType.PRIVATE)  # commands=['approve_join_deeplink'],
async def approve_join_deeplink(chat_id, user_address, signature):
    # decoding of the signature
    w3 = Web3()
    txt_message = "I am an owner of this address and I want to join {} group".format(chat_id)
    message_hash = defunct_hash_message(text=txt_message)  # msg
    hex_signature = HexBytes(signature)
    decoded_address = w3.eth.account.recoverHash(message_hash, signature=hex_signature)
    print(F"message_hash: {message_hash}")
    print("decoded addr: " + decoded_address)

    # check if user_addr is the same as in join_group_by_id
    appr_req = await helpers.get_approve_request(user_address, chat_id)

    print(f'APP REQ: {appr_req}')
    if len(appr_req) == 0 or appr_req == -1:
        print("There is no approve request with such user_address & chat_id")
        return
    user_id = appr_req[0][0]
    print(f'USER ID: {user_id}')

    # delete approve
    await helpers.delete_approve_request(user_address, chat_id)

    # check if address has group tokens
    gt = await helpers.get_group_token(chat_id)
    token_address = gt[1]
    print("TOKEN ADDRESS: " + token_address)
    approved = await is_token_owner(user_address, token_address)
    if not approved:
        await bot.send_message(user_id, f"Your request to join the group was rejected: \n_You should have at least 1 "
                                        f"community token of_ `{token_address}`  _smart-contract to join the group_",
                                        parse_mode="Markdown")
        return
    print('approved token owner')
    # send deeplink to join
    expire_date = datetime.now() + timedelta(minutes=2)
    link = await bot.create_chat_invite_link(chat_id, expire_date, 1)
    await bot.send_message(user_id, "The check has been successfully passed!\n This is your link to join the group: \n"
                           + link.invite_link)


async def is_token_owner(user_address, token_address) -> bool:
    with open(ERC20_BALANCE_ABI, 'r') as f:
        _abi = json.load(f)

    web3 = Web3(Web3.HTTPProvider(INFURA_PROVIDER))

    erc20_contract = web3.eth.contract(address=token_address, abi=_abi)
    is_owner = erc20_contract.functions.balanceOf(user_address).call()
    print(f"is owner: {is_owner}")
    if is_owner >= 1e18:
        return True
    return False


@dp.message_handler(commands=['get_mint_deeplink'], chat_type=[ChatType.GROUP, ChatType.SUPERGROUP])
async def get_mint_deeplink(message: types.Message):
    params = str.split(message.text, ' ')
    print("get_mint_deeplink")
    if len(params) != 2:
        await bot.send_message(message.chat.id, "Invalid number of arguments.")
        return

    # get group token token_address, amount
    try:
        token_address = await helpers.get_group_token(message.chat.id)
    except:
        await bot.send_message(message.chat.id, "Invalid arguments.")
        return


    link = await get_start_link(f"m {token_address[1]} {params[1]}", encode=True)
    await bot.send_message(message.chat.id, "Send this deeplink to invite people to mint your token: \n" + link)
    return


@dp.message_handler(commands=['get_join_deeplink'], chat_type=[ChatType.GROUP, ChatType.SUPERGROUP])
async def get_join_deeplink(message: types.Message):
    params = str.split(message.text, ' ')
    print("join_group")
    if len(params) != 1:
        await bot.send_message(message.chat.id, "Invalid number of arguments.")
        return

    print("get_join_deeplink")
    # check bot is admin
    bt = await bot.get_chat_member(message.chat.id, bot.id)
    is_admin = bt.is_chat_admin()
    if not is_admin:
        await bot.send_message(message.chat.id, "Please, promote me to admin. I need permission to invite users "
                                                "to create this deeplink.")
        return
    if not bt['can_invite_users']:
        await bot.send_message(message.chat.id, "Please, give me a permission to invite users.\n"
                                                "Otherwise I won't be able to create a link to join the chat.")
        return
    params = str.split(message.text, ' ')

    if len(params) != 1:
        await bot.send_message(message.chat.id, "Invalid number of arguments.")
        return

    #check that chat has a comm token
    if not await helpers.check_group_token_exists(message.chat.id):
        await bot.send_message(message.chat.id, "Token is not set  for your community")
        return

    link = await get_start_link(f"j {message.chat.id}", encode=True)
    await bot.send_message(message.chat.id, "Send this link to invite the user to pass a token check "
                                            "and join this chat: \n" + link)
    return


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
