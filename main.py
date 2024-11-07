import json


with open('data.json') as f:
    data = json.load(f)


# "name": "1273/2602/raid-mythic/212019/639/7601/legs/", -mythic legs 955,278 dps Lightless Scanveger's Stalkings, itemID 212019
# "name": "1273/2602/raid-mythic/212454/639/0/trinket2/", -trink, queens Mandate itemID 212454
# Raid boss identifier = data.json["sim"]["profilesets"]["results"]["name"]

test_list = []

for item in data.items():
    if data['sim']['profilesets']['results'][0]['name'].startswith('1273/2602/raid-mythic/'):
        test_list.append(item)

print(test_list)
    


# with open('testing_data.json', 'w') as outfile:
#     json.dump(data, outfile, indent=4)

