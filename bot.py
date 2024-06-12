import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import CommandStart, Command
import asyncio
from utils import *
import time
import csv
from wheel import *
from aiogram import types

API_TOKEN = "6422952891:AAFWdrhr7-2mUnsMnNCZsYYPAjB_SY-bDvM"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
paychecks = load_json('paychecks.json')

# Define states
class Form(StatesGroup):
    name = State()
    phone = State()
    kaspi = State()
    prodamus = State()
    wheel_available = State()

# Start command handler
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    current_time = int(time.time())

    telegram_id = message.from_user.id
    user_data = {
        "start_time": current_time,
        "telegram_id": str(telegram_id),
        "name": "",
        "phone": "",
        "crm_id": "",
        "payment_time" : 0# Initialize crm_id with a default value
    }

    # Load existing users
    existing_users = {}
    try:
        with open('user_data.csv', 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                existing_users[row['telegram_id']] = row
    except FileNotFoundError:
        pass

    if str(telegram_id) in existing_users:
        user_data = existing_users[str(telegram_id)]

    await state.update_data(**user_data)
    await state.set_state(Form.name)
    
    await message.reply("Please enter your name and surname:")

# Name and surname handler
@dp.message(Form.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.reply("Please share your phone number:", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Share phone number", request_contact=True)]],
        one_time_keyboard=True
    ))
    await state.set_state(Form.phone)

# Phone number handler
@dp.message(Form.phone)
async def process_phone(message: types.Message, state: FSMContext):
    if message.contact:
        await state.update_data(phone=message.contact.phone_number)

    data = await state.get_data()
    current_state = await state.get_state()

    telegram_id = data['telegram_id']

    # Load existing users
    existing_users = {}
    try:
        with open('user_data.csv', 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                existing_users[row['telegram_id']] = row
    except FileNotFoundError:
        pass

    # Check if the user already exists
    if telegram_id in existing_users:
        crm_id = existing_users[telegram_id]["crm_id"]
    else:
        info = [data["name"], "+" + data["phone"], data["start_time"]]
        crm_id = add_crm(info[0], info[1], info[2])
        await state.update_data(crm_id=crm_id)

    # Update user data
    existing_users[telegram_id] = {
        "start_time": data["start_time"],
        "telegram_id": data["telegram_id"],
        "name": data["name"],
        "phone": data["phone"],
        "state": str(current_state),
        "crm_id": crm_id
    }

    # Write updated data back to CSV
    with open('user_data.csv', 'w', newline='') as csvfile:
        fieldnames = ["start_time", "telegram_id", "name", "phone", "state", "crm_id", "payment_time"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for user in existing_users.values():
            writer.writerow(user)

    kb = [
        [types.InlineKeyboardButton(text="Kaspi", callback_data="pay_kaspi")],
        [types.InlineKeyboardButton(text="Prodamus", callback_data="pay_prodamus")]
    ]

    await message.reply("Choose the payment method:", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(lambda c: c.data in ["pay_kaspi", "pay_prodamus"])
async def payment_method_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()

    if callback_query.data == "pay_prodamus":
        await state.set_state(Form.prodamus)
        await callback_query.message.answer("https://enalika.proeducation.kz/")
        await callback_query.message.answer("Prodamus payment is not yet implemented.")
    elif callback_query.data == "pay_kaspi":
        await state.set_state(Form.kaspi)
        await callback_query.message.answer("https://pay.kaspi.kz/pay/5t1euuhq")
        await callback_query.message.answer("Please upload your PDF receipt for Kaspi payment.")

# Receipt handler
@dp.message(Form.kaspi)
async def process_receipt(message: types.Message, state: FSMContext):
    if not message.document or message.document.mime_type != "application/pdf":
        await message.reply("Send receipt")
        return

    try:
        pdf = "check.pdf"
        await bot.download(message.document, pdf)
        pdf_data = parse_pdf(pdf)
        online_data = parse_online_receipt(pdf)
    except Exception as e:
        await message.reply("Этот чек не корректен")
        print(e)
        return

    if pdf_data != online_data:
        await message.reply("Данные не соответствуют")
        return

    os.remove("check.pdf")
    await process_paycheck(message, online_data, state)

async def process_paycheck(message: types.Message, paycheck_data, state: FSMContext):
    paycheck_id = paycheck_data["check_number"]
    if paycheck_id in paychecks:
        await message.reply("Данный чек уже был отправлен")
        return

    print(f"Paycheck {paycheck_id} added")
    paycheck_data["user_id"] = message.from_user.id
    paychecks[paycheck_id] = paycheck_data
    save_json('paychecks.json', paychecks)

    data = await state.get_data()
    crm_id = data.get("crm_id")
    if crm_id:
        edit_crm(crm_id)
        await message.reply("Чек валидирован")
        await message.reply("https://t.me/+E6WNLXGZH8E3ZTli")
        await message.reply("колесо фортуны /wheel")

        # Update state to wheel_available and add payment time
        payment_time = int(time.time())
        await state.update_data(payment_time=payment_time)
        await state.set_state(Form.wheel_available)

        # Update CSV with payment time
        existing_users = {}
        try:
            with open('user_data.csv', 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    existing_users[row['telegram_id']] = row
        except FileNotFoundError:
            pass

        existing_users[data["telegram_id"]].update({"payment_time": payment_time})

        with open('user_data.csv', 'w', newline='') as csvfile:
            fieldnames = ["start_time", "telegram_id", "name", "phone", "state", "crm_id", "payment_time"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for user in existing_users.values():
                writer.writerow(user)
    else:
        await message.reply("CRM ID not found, cannot validate receipt.")

@dp.message(Command(commands=["wheel"]))
async def play_wheel_game(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if str(current_state)[5:] != "wheel_available" or current_state is None:
        await message.reply("Please validate your receipt first.")
        return

    user_data = await state.get_data()
    name = user_data.get("name", None)
    if not name:
        await message.reply("Please enter your name first. Use /start command.")
        return

    try:
        winning_item = str(play_game(prizes))
        for prize in prizes:
            if prize['name'] == winning_item:
                photo_id = prize['photo_id']
                video_id = prize['video_id']
        video = await message.reply_video(video=video_id)
        async def delete_video_later():
            await asyncio.sleep(13)
            await bot.delete_message(chat_id=message.chat.id, message_id=video.message_id)
        await asyncio.ensure_future(delete_video_later())
        await message.reply_photo(photo=photo_id)
        await message.reply(f"Поздравляем, {name}! Вы выиграли {winning_item}")
    except Exception as e:
        await message.reply("Произошла ошибка. Пожалуйста, попробуйте позже.")
        print(f"Error during game: {e}")

    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
