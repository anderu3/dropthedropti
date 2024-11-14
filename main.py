import json
import requests
import time

# blizz API creds, DELETE BEFORE PUSH CAUSE IM TOO LAZY TO HIDE IT 
client_id = 'ebf3c5959d3f49f381fad9feef87c6f0'
client_secret = 'JXqxxT8kf5pSR2MCCiflb4cJYLGLfD7P'

# access token for bnet
auth_url = 'https://us.battle.net/oauth/token'
auth_response = requests.post(auth_url, data={'grant_type': 'client_credentials'}, auth=(client_id, client_secret))
auth_response.raise_for_status()
access_token = auth_response.json()['access_token']

# tried caching items to not request from blizz API for speed maybe but not working, i dunno, might have to retouch this further down


def get_item_details(item_id):
    if item_id in item_details_cache:
        return item_details_cache[item_id]
    
    api_url = f'https://us.api.blizzard.com/data/wow/item/{item_id}'
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'namespace': 'static-us', 'locale': 'en_US'}
    response = requests.get(api_url, headers=headers, params=params)
    response.raise_for_status()
    item_details = response.json()
    
    # cache the item details
    item_details_cache[item_id] = item_details
    return item_details


def extract_relevant_data(data):
    relevant_data = {
        "player_name": data["sim"]["players"][0]["name"],
        "player_average_dps": data["sim"]["players"][0]["collected_data"]["dps"]["mean"],
        # results is the part with the boss ID, item ID, and avg dps gained
        "results": [
            {
                "name": result["name"],
                "mean": result["mean"]
            }
            for result in data["sim"]["profilesets"]["results"]
        ]
    }
    return relevant_data

# removing commas or breaks, t
user_input = input("Enter Raidbots links separated by commas or new lines:\n")
links = []
for link in user_input.replace("\n", ",").split(","):
    stripped_link = link.strip()
    if stripped_link:
        links.append(stripped_link)

formatted_links = [f"{link}/data.json" for link in links]

# loading this into new json
master_data = []

for link in formatted_links:
    try:
        response = requests.get(link)
        response.raise_for_status()
        data = response.json()

        # extract relevant data
        relevant_data = extract_relevant_data(data)
        master_data.append(relevant_data)

        print(f"Processed data from {link}")

    except requests.exceptions.RequestException as e:
        print(f"Failed to download {link}: {e}")
    except KeyError as e:
        print(f"Failed to extract relevant data from {link}: {e}")

# writing to master.json
with open('master.json', 'w') as json_file:
    json.dump(master_data, json_file, indent=4)


print("master.json updated with data from all links")

with open('master.json') as f:
    master_data = json.load(f)

unique_item_ids = set()

for player_data in master_data:
    for result in player_data['results']:
        name = result['name']
        if name.startswith("1273/"):
            item_identifier = name.split('/')[3]
            unique_item_ids.add(item_identifier)

item_details_cache = {}

#code here to cache the items with dictionary of item_id: item_details

# with open('items.json', 'r') as json_file:
#     item_details_cache = json.load(json_file)

# TAKING THE LONGEST HERE AT ~50 SECONDS TO PROCESS ALL ITEMS, CAN DO BETTER HERE
start_time = time.time()
print(unique_item_ids)
for item_id in unique_item_ids:
    if item_id not in item_details_cache:
        item_details_cache[item_id] = get_item_details(item_id)

# IT IS A TIER PIECE WHEN THIS EXISTS:
# ["itemnumber"]["preview_item"]["set"] = True
 
end_time = time.time()
print(f"Time taken to fetch item details: {end_time - start_time} seconds")

with open('full_items.json', 'w') as json_file:
    json.dump(item_details_cache, json_file, indent=4)

boss_dict = {
    "2607": "Ulgrax",
    "2611": "Bloodbound Horror",
    "2599": "Sik'ran",
    "2609": "Rasha'nan",
    "2612": "Broodtwister",
    "2601": "Nexus Princess",
    "2608": "Silken Court",
    "2602": "Ansurek",
    "-67": "Trash Mobs"
}

# keys are values from boss_dict, values are empty currently but will be items
start_time = time.time()
boss_and_items = {boss_name: {} for boss_name in boss_dict.values()}

# just feels lengthy and unoptimized, will look into it later
for player_data in master_data:
    player_name = player_data['player_name']
    player_average_dps = player_data['player_average_dps']
    for result in player_data['results']:
        name = result['name']
        mean = result['mean']
        if name.startswith("1273/"):
            item_number = name.split('/')[3]
            print(f'Item Identifier: {item_number}')
            boss_id = name.split('/')[1]
            boss_name = boss_dict.get(boss_id, "Unknown Boss")
            item_name = item_details_cache[item_number]
            dps_increase = round(((mean / player_average_dps) - 1) * 100, 2)

            if item_number not in boss_and_items[boss_name]:
                boss_and_items[boss_name][item_number] = {
                    "item_name": item_name,
                    "dps_increase": [],
                }
            boss_and_items[boss_name][item_number]["dps_increase"].append({
                "player_name": player_name,
                "dps_increase": dps_increase
            })

# list bosses to pick
print("\nAvailable Bosses:")
for i, boss in enumerate(boss_dict.values(), 1):
    print(f"{i}. {boss}")

# need -1 cause they're numbered and indexes start a 0
boss_choice = int(input("\nSelect a boss by number: ")) - 1
selected_boss = list(boss_dict.values())[boss_choice]

# list all items for that boss and to pick
print(f"\nItems for {selected_boss}:")
items = list(boss_and_items[selected_boss].values())
for i, item in enumerate(items, 1):
    print(f"{i}. {item['item_name']}")

item_choice = int(input("\nSelect an item by number: ")) - 1
selected_item = items[item_choice]

# return top 5 dps increase for that item
print(f"\nTop 5 DPS Increasers for {selected_item['item_name']}:")
sorted_dps_increases = sorted(selected_item["dps_increase"], key=lambda x: x['dps_increase'], reverse=True)

top_five = []
seen_players = set()

for dps_increase in sorted_dps_increases:
    if dps_increase['player_name'] not in seen_players:
        top_five.append(dps_increase)
        seen_players.add(dps_increase['player_name'])
    if len(top_five) == 5:
        break

for i, dps_increase in enumerate(top_five, 1):
    print(f"{i}) {dps_increase['player_name']} {dps_increase['dps_increase']}%")