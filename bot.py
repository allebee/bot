import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import CommandStart, Command
from aiogram.types import contact, document
import asyncio
from utils import *
import time
import csv
from wheel import *
import aiogram
import aiogram
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
    # Get current timestamp for start time
    current_time = int(time.time())

    # Open CSV file in read mode
    try:
        with open('user_data.csv', 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            existing_users = [row for row in reader]  # List of dictionaries from CSV
    except FileNotFoundError:
        existing_users = []  # Empty list if file doesn't exist

    # Find user by Telegram ID
    telegram_id = message.from_user.id
    matching_user = next((user for user in existing_users if user['telegram_id'] == str(telegram_id)), None)

    # Update user data if it exists, otherwise create a new entry
    if matching_user:
        user_data = matching_user
    else:
        user_data = {
            "start_time": current_time,
            "telegram_id": telegram_id,
            "name": "",  # Placeholder, will be filled in process_name
            "phone": "",  # Placeholder, will be filled in process_phone
        }

    # Update state with user data
    await state.update_data(**user_data)

    await state.set_state(Form.name)
    await message.reply("Please enter your name and surname:")

# Name and surname handler (similar logic applies to process_phone)
@dp.message(Form.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.reply("Please share your phone number:", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Share phone number", request_contact=True)]],
        one_time_keyboard=True
    ))
    await state.set_state(Form.phone)


# Phone number handler
# Phone number handler
# Phone number handler
@dp.message(Form.phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)

    # Get all user data, including current state
    data = await state.get_data()
    current_state = await state.get_state()  
    # Get current state object
    info = [data["name"],"+"+data["phone"],data["start_time"]]
    id = add_crm(info[0],info[1],info[2])
    print(id)
    data["crm_id"] = id
    # Open CSV file in write mode (may create or overwrite)
    with open('user_data.csv', 'w', newline='') as csvfile:
        fieldnames = ["start_time", "telegram_id", "name", "phone", "state", "crm_id"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write header
        writer.writeheader()

        # Find matching user again (in case data changed during conversation)
        telegram_id = data['telegram_id']
        existing_users = []  # Empty list to store non-matching users

        # Open CSV file in read mode (separate for existing users)
        with open('user_data.csv', 'r') as csvfile_read:
            reader = csv.DictReader(csvfile_read)
            for row in reader:
                if row['telegram_id'] != str(telegram_id):
                    existing_users.append(row)

        # Write existing users
        for user in existing_users:
            writer.writerow(user)

        # Update data with current state (string representation)
        data['state'] = str(current_state)

        # Write updated user data
        writer.writerow(data)

    kb = [
        [types.InlineKeyboardButton(text="Kaspi", callback_data="pay_kaspi")],
        [types.InlineKeyboardButton(text="Prodamus", callback_data="pay_prodamus")]
    ]

    await message.reply("Choose the payment method:", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb))




@dp.callback_query(lambda c: c.data in ["pay_kaspi", "pay_prodamus"])
async def payment_method_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()  # Acknowledge the callback

    if callback_query.data == "pay_prodamus":
        await state.set_state(Form.prodamus)
        await callback_query.message.answer("https://enalika.proeducation.kz/")
        await callback_query.message.answer("Prodamus payment is not yet implemented.")
    elif callback_query.data == "pay_kaspi":
        # Prompt for PDF receipt instead of opening the URL directly
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


async def process_paycheck(message, paycheck_data, state):
    paycheck_id = paycheck_data["check_number"]
    if paycheck_id in paychecks:
        await message.reply("Данный чек уже был отправлен")
        return

    print(f"Paycheck {paycheck_id} added")
    paycheck_data["user_id"] = message.from_user.id
    paychecks[paycheck_id] = paycheck_data
    save_json('paychecks.json', paychecks)
    await message.reply("Чек валидирован")
    await message.reply("https://t.me/+E6WNLXGZH8E3ZTli")
    await message.reply("колесо фортуны /wheel")
    
    await state.set_state("wheel_available")
    
    # await state.clear()

@dp.message(Command(commands=["wheel"]))
async def play_wheel_game(message: types.Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state != "wheel_available":
        await message.reply("Please validate your receipt first.")
        return
    user_data = await state.get_data()
    name = user_data.get("name", None)

    if not name:
        await message.reply("Please enter your name first. Use /start command.")
        return

    try:
        # Determine winning item (replace with your game logic)
        winning_item = str(play_game())
        print(f"{winning_item}.MOV")
        # Send fortune wheel video (replace with actual video logic)
        await message.reply_photo(photo="https://pbs.twimg.com/profile_images/1676625773611081728/k05BA1j1_400x400.jpg")

        # Announce the result with user's name
        await message.reply(f"Поздравляем, {name}! Вы выиграли {winning_item}")

    except Exception as e:
        # Handle potential errors during game logic or video sending
        await message.reply("Произошла ошибка. Пожалуйста, попробуйте позже.")
        print(f"Error during game: {e}")

    await state.clear()  # Clear state afte

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
