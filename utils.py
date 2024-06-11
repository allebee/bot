import os
import re
import json
import requests
import PyPDF2
from bs4 import BeautifulSoup
from pdf2image import convert_from_path
import cv2
from aiogram import types
import pandas as pd
from qreader import QReader

import requests
import time
# Replace with your new access token and subdomain
access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjlkNWY3NGJiY2JlYWNiNjE2YTUxZjAzYzc4YmQyODA0ZGRkOWRlYWQ5YWVlZTdkY2VlMDE4MTE2ZDhjZGUyMWNjNGQwNjlmNDIwZDU4YzBmIn0.eyJhdWQiOiI3MDdmYTJiOC03ZDE0LTRkNmEtYWM1Ni1jZWM1Y2VjNGUyMDAiLCJqdGkiOiI5ZDVmNzRiYmNiZWFjYjYxNmE1MWYwM2M3OGJkMjgwNGRkZDlkZWFkOWFlZWU3ZGNlZTAxODExNmQ4Y2RlMjFjYzRkMDY5ZjQyMGQ1OGMwZiIsImlhdCI6MTcxODEwMjE1MywibmJmIjoxNzE4MTAyMTUzLCJleHAiOjE3MTgxODg1NTMsInN1YiI6IjExMTQ1MzM0IiwiZ3JhbnRfdHlwZSI6IiIsImFjY291bnRfaWQiOjMxNzk0NDAyLCJiYXNlX2RvbWFpbiI6ImFtb2NybS5ydSIsInZlcnNpb24iOjIsInNjb3BlcyI6WyJwdXNoX25vdGlmaWNhdGlvbnMiLCJmaWxlcyIsImNybSIsImZpbGVzX2RlbGV0ZSIsIm5vdGlmaWNhdGlvbnMiXSwiaGFzaF91dWlkIjoiZGU0NDc4NTktNDI1Ni00ZDdkLWExYzYtNzYwNWZhYjlkZGY5In0.VWKefnLRJQe0tQ9lerUKv0OVEoHLyepI-nM_tWoApSmUJX02nIIyN_7TDY7sl1U9O2eAQbfkldFBwdwTUoatv9UO3qo23J9bw9ZOKaghxWdQ_TW4xe7ioCtYlD5_EKCEy55qoHHSsqkW1KGmVMUwIVcDiNb3ZK18AWJbUGCj7TPpKBNILM5qNLDw1USEDDmPeLETGDtE_9Aiv4qf465ZF_w0nRRVKYwVqj5gwcgR0a1OzQL0BOIdfV9mXR4F03GC88lq36ByUtNzZzNmIjlVt0PId3hJkfAmBFwfTUO-7vwLTVxD0ppVefniISykiGSLX_I6wtMLJw60D3r0zdLXhw"


def add_crm(name, phone, date):

    # Set the headers for the request
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Minimal lead creation data
    data = [{
        "name": "Zapusk",
        "_embedded":{
            "contacts":[
                {
                "first_name":name,
                "created_at":int(date),
                "updated_by":0,
                "custom_fields_values":[
                    {
                        "field_code": "PHONE",
                        "values":[
                            {
                            "enum_code":"WORK",
                            "value":phone
                            }
                        ]
                    }
                ]
                }
            ],
        },
    }]



    # Make the POST request to create the lead
    url = f'https://sanzharalibekovgmailcom8.amocrm.ru/api/v4/leads/complex'
    response = requests.post(url, headers=headers, json=data)

    # Check the response
    if response.status_code == 201:
        print("Lead created successfully.")
        print("Response:", response.json())
    else:
        print("Failed to create lead.")
        print("Status code:", response.status_code)
        print("Response:", response.json())
        
    return response.json()[0]["id"]

def edit_crm(id):
    # Replace with your new access token and subdomain
    access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjlkNWY3NGJiY2JlYWNiNjE2YTUxZjAzYzc4YmQyODA0ZGRkOWRlYWQ5YWVlZTdkY2VlMDE4MTE2ZDhjZGUyMWNjNGQwNjlmNDIwZDU4YzBmIn0.eyJhdWQiOiI3MDdmYTJiOC03ZDE0LTRkNmEtYWM1Ni1jZWM1Y2VjNGUyMDAiLCJqdGkiOiI5ZDVmNzRiYmNiZWFjYjYxNmE1MWYwM2M3OGJkMjgwNGRkZDlkZWFkOWFlZWU3ZGNlZTAxODExNmQ4Y2RlMjFjYzRkMDY5ZjQyMGQ1OGMwZiIsImlhdCI6MTcxODEwMjE1MywibmJmIjoxNzE4MTAyMTUzLCJleHAiOjE3MTgxODg1NTMsInN1YiI6IjExMTQ1MzM0IiwiZ3JhbnRfdHlwZSI6IiIsImFjY291bnRfaWQiOjMxNzk0NDAyLCJiYXNlX2RvbWFpbiI6ImFtb2NybS5ydSIsInZlcnNpb24iOjIsInNjb3BlcyI6WyJwdXNoX25vdGlmaWNhdGlvbnMiLCJmaWxlcyIsImNybSIsImZpbGVzX2RlbGV0ZSIsIm5vdGlmaWNhdGlvbnMiXSwiaGFzaF91dWlkIjoiZGU0NDc4NTktNDI1Ni00ZDdkLWExYzYtNzYwNWZhYjlkZGY5In0.VWKefnLRJQe0tQ9lerUKv0OVEoHLyepI-nM_tWoApSmUJX02nIIyN_7TDY7sl1U9O2eAQbfkldFBwdwTUoatv9UO3qo23J9bw9ZOKaghxWdQ_TW4xe7ioCtYlD5_EKCEy55qoHHSsqkW1KGmVMUwIVcDiNb3ZK18AWJbUGCj7TPpKBNILM5qNLDw1USEDDmPeLETGDtE_9Aiv4qf465ZF_w0nRRVKYwVqj5gwcgR0a1OzQL0BOIdfV9mXR4F03GC88lq36ByUtNzZzNmIjlVt0PId3hJkfAmBFwfTUO-7vwLTVxD0ppVefniISykiGSLX_I6wtMLJw60D3r0zdLXhw"


    # Set the headers for the request
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Lead update data
    data = {
        "status_id": 67455558
    }

    # Make the PATCH request to update the lead
    url = f'https://sanzharalibekovgmailcom8.amocrm.ru/api/v4/leads/{id}'
    response = requests.patch(url, headers=headers, json=data)

    # Check the response
    if response.status_code == 204:
        print("Lead updated successfully.")
    elif response.status_code == 200:
        print("Lead update partially successful.")
        print("Response:", response.json())
    else:
        print("Failed to update lead.")
        print("Status code:", response.status_code)
        print("Response:", response.json())
    return "Success"


def load_json(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_json(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)


def parse_pdf(pdf_path):
    text = extract_text_from_pdf(pdf_path)

    return {
        "price": extract_price_from_pdf_text(text)[:-2:],
        "check_number": extract_check_number_from_pdf_text(text),
        "name": extract_name_from_pdf_text(text)
    }


def extract_text_from_pdf(pdf_path):
    # Open the PDF file
    with open(pdf_path, 'rb') as file:
        # Create a PDF reader object
        reader = PyPDF2.PdfReader(file)

        # Initialize a variable to store the extracted text
        text = ""

        # Iterate over all the pages in the PDF
        for page_num in range(len(reader.pages)):
            # Get the page
            page = reader.pages[page_num]

            # Extract text from the page
            text += page.extract_text() + "\n"

    return text


def extract_price_from_pdf_text(text):
    # Use regex to find the price in the text
    price_pattern = r'\d{1,3}(?: \d{3})* ₸'
    match = re.search(price_pattern, text)
    if match:
        return match.group(0)
    return None


def extract_check_number_from_pdf_text(text):
    # Use regex to find the check number starting with QR
    match = re.search(r'QR\d+', text)
    return match.group(0) if match else None


def extract_name_from_pdf_text(text):
    # Use regex to find the name of the person
    match = re.search(r'ФИО плательщика (.+)', text)
    return match.group(1).strip() if match else None


def parse_online_receipt(pdf):
    link = extract_qr_code_from_pdf(pdf)
    html = fetch_html(link)
    return parse_html(html)


def fetch_html(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Find price
    price_element = soup.find('span', class_='amount-value')
    price = price_element.get_text(strip=True) if price_element else None

    # Find check number
    check_number_element = soup.find('div', class_='name', text=lambda x: x and '№ чека' in x)
    check_number = check_number_element.find_next('div', class_='value').get_text(
        strip=True) if check_number_element else None

    # Find name of the person
    name_element = soup.find('div', class_='name', text=lambda x: x and 'ФИО плательщика' in x)
    name = name_element.find_next('div', class_='value').get_text(strip=True) if name_element else None

    return {
        "price": price[:-1:],
        "check_number": check_number,
        "name": name
    }


def extract_qr_code_from_pdf(pdf_path):
    # Convert PDF to images
    images = convert_from_path(pdf_path)

    # Initialize QR Code detector
    qcd = cv2.QRCodeDetector()

    for image in images:
        # Save image temporarily to disk
        temp_image_path = "/Users/user/Desktop/dev/zapusk/Screenshot 2024-06-11 at 21.34.49.png"
        image.save(temp_image_path)

        # Read the saved image
        image = cv2.imread(temp_image_path)

        # Create a QReader instance
        qreader = QReader()

        # Get the image (as RGB)
        image = cv2.cvtColor(cv2.imread(temp_image_path), cv2.COLOR_BGR2RGB)

        # Use the detect_and_decode function to get the decoded QR data
        decoded_texts = qreader.detect_and_decode(image=image)
        
        os.remove(temp_image_path)
        # Print the results
        for text in decoded_texts:
            return text

    return None


async def send_whitelist(message: types.Message, bot, whitelist):
    print(f"Sending whitelist to {message.from_user.username}")
    await generate_and_send_whitelist_excel(message, bot, whitelist)


async def generate_and_send_whitelist_excel(message: types.Message, bot, whitelist):
    # Create a DataFrame from the whitelist
    df = pd.DataFrame(list(whitelist.keys()), columns=["Username"])

    # Save the DataFrame to an Excel file
    file_path = "whitelist.xlsx"
    df.to_excel(file_path, index=False)

    # Send the Excel file
    await bot.send_document(message.chat.id, types.FSInputFile(file_path))

    # Remove the file after sending
    os.remove(file_path)