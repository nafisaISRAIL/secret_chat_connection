import aiofiles
import argparse
import asyncio
import json
import logging

logging.basicConfig(level=logging.DEBUG)
HOST = ''
PORT = ''


async def submit_message(personal_hash, message):
    reader, writer = await connect(personal_hash)

    for _ in range(2):
        # pass returned authorized user data
        # pass rule of message sending
        await reader.readline()

    await send_data(writer, message)

    writer.close()
    logging.info("Message was sent")


async def authorise(message, nickname=""):
    user_info = None

    info_file = await aiofiles.open("token.txt", mode="r+")
    user_info = await info_file.read()
    if user_info == "":
        user_info = await register(nickname)
        await info_file.write(user_info.decode())
        logging.info("The retreived token was saved.")
    info_file.close()
    try:
        user_info_dict = json.loads(user_info)
        await submit_message(user_info_dict["account_hash"], message)
    except asyncio.CancelledError:
        logging.error("Error occurred while token was retrieving.")


async def register(nickname=""):
    reader, writer = await connect()
    try:
        nickname_ask_message = await reader.readline()
        logging.debug(nickname_ask_message.decode())

        await send_data(writer, nickname)

        user_data = await reader.readline()
        if not user_data:
            logging.error("Unknown token. Please check it or signup again.")
            raise asyncio.CancelledError
        return user_data
    except asyncio.CancelledError:
        logging.error("New account hash could not be retreived.")
    finally:
        writer.close()
    return user_data


async def connect(token=""):
    reader, writer = await asyncio.open_connection(HOST, PORT)
    greetings = await reader.readline()
    if not greetings:
        logging.error("Greeting message was not received.")
        raise asyncio.CancelledError
    logging.debug(greetings)
    await send_data(writer, token)
    return reader, writer


async def send_data(writer, data=""):
    data = data.replace("\\n", "")
    writer.write(f"{data}\n\n".encode())
    await writer.drain()


parser = argparse.ArgumentParser(description="Message sender script")
parser.add_argument(
    "--message", dest="message", required=True, type=str)
parser.add_argument(
    "--host", dest="host", required=False, type=str, default="minechat.dvmn.org")
parser.add_argument(
    "--port", dest="port", required=False, type=int, default=5050)
parser.add_argument(
    "--nickname", dest="nickname", required=False, type=str, default="")

if __name__ == "__main__":
    args = parser.parse_args()
    globals().update({"HOST": args.host, "PORT": args.port})
    asyncio.run(authorise(message=args.message, nickname=args.nickname))
