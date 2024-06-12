import random

# List of prizes with their chances and available counts
prizes = [
    {"name": "Гайд антитрендов на лето", "chance": 40, "count": float('inf'), "photo_id": "AgACAgIAAxkBAAJSJWZpiwqEiuHVvEdnTOQhbsgYYjoVAAKJ3TEbsupRS_64Oe3JUUa-AQADAgADeQADNQQ","video_id": "BAACAgIAAxkBAAJR9GZphe2jW1nm9xh_bfav5ZZ9CKyDAAKgSwACsupRS5pEmfSSgxnCNQQ"},
    {"name": "Урок: как правильно сочетать цвета в образах?", "chance": 30, "count": float('inf'),"photo_id": "AgACAgIAAxkBAAJSKmZpix29B4wbMAsFC5g6kqwqxARwAAKK3TEbsupRS1lTThQE0XfUAQADAgADeQADNQQ","video_id": "BAACAgIAAxkBAAJSCmZphzxVjH9oZSei65Sf97O07XEcAAK-SwACsupRS9jxHFj2jperNQQ"},
    {"name": "Урок по трендам и как их прогнозировать", "chance": 20, "count": float('inf'),"photo_id": "AgACAgIAAxkBAAJSG2Zpitp-5ZkKwbltvhnrw3YZ3HakAAKH3TEbsupRS4_0KGXXDG3EAQADAgADeQADNQQ","video_id": "BAACAgIAAxkBAAJSBWZphy_luIuC3u5a_botVaLd6ENAAAK9SwACsupRS2E9HFQ7D0uCNQQ"},
    {"name": "150.000 тг и составление капсулы от меня на лето", "chance": 4, "count": 2,"photo_id": "AgACAgIAAxkBAAJSIGZpiveMO3iqcxUj4_bFIgLdpj_4AAKI3TEbsupRS2ylCGhTWvGTAQADAgADeQADNQQ","video_id": "BAACAgIAAxkBAAJR-2ZphwZB4NLzbVIf5vK8sIMZdOEVAAK7SwACsupRS5IFI4kD8ikBNQQ"},
    {"name": "Сумка Jacquemus", "chance": 2, "count": 1,"photo_id": "AgACAgIAAxkBAAJSFmZpisM64vEKwYV3DykmDArcAnciAAKG3TEbsupRSyKRwoMONySBAQADAgADeQADNQQ","video_id": "BAACAgIAAxkBAAJSAAFmaYcfBb4QZrqZQ1Kn_tmwt7s4CwACvEsAArLqUUsi1g3K50wkKDUE"},
]

def play_game(prizes):
    # Create a list of prizes according to their chances
    prize_list = []
    for prize in prizes:
        prize_list.extend([prize] * prize["chance"])
    
    while True:
        # Spin the wheel
        selected_prize = random.choice(prize_list)
        
        # Check if the prize is available
        if selected_prize["count"] > 0 or selected_prize["count"] == float('inf'):
            # Decrease the count of available prizes if not infinite
            if selected_prize["count"] != float('inf'):
                selected_prize["count"] -= 1
            return selected_prize["name"]
        else:
            # If the prize is not available, remove it from the prize list
            prize_list = [p for p in prize_list if p["name"] != selected_prize["name"]]

