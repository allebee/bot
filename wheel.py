import random

# Initial counts for the items
items = {
    "Лук в гости": float('inf'),    # Infinite
    "Лук на спорт": float('inf'),   # Infinite
    "Гайд по стилю": float('inf'),  # Infinite
    "Разбор гардероба": 5,          # Only 5 items
    "Модная вещь": 3                # Only 3 items
}

def get_probabilities(items):
    # Calculate the total number of finite items
    finite_total = sum(count for count in items.values() if count != float('inf'))
    
    # Calculate the probabilities for each item
    probabilities = {}
    for item, count in items.items():
        if count == float('inf'):
            probabilities[item] = 1 / (finite_total + 3) # 3 is the number of infinite items
        else:
            probabilities[item] = count / (finite_total + 3)
    
    # Normalize probabilities to sum to 1
    total_probability = sum(probabilities.values())
    for item in probabilities:
        probabilities[item] /= total_probability
    return probabilities

def choose_item(items):
    probabilities = get_probabilities(items)
    items_list = list(items.keys())
    probabilities_list = [probabilities[item] for item in items_list]
    chosen_item = random.choices(items_list, probabilities_list, k=1)[0]
    return chosen_item

def update_items(items, chosen_item):
    if items[chosen_item] != float('inf'):
        items[chosen_item] -= 1
        if items[chosen_item] < 0:
            items[chosen_item] = 0
    return items

# Function to play the game
def play_game():
    chosen_item = choose_item(items)
    print(f"Congratulations! You won: {chosen_item}")
    update_items(items, chosen_item)
    # print("Updated items:", items)
    return chosen_item

