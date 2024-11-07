import json

# Load the JSON data
with open('data.json') as f:
    data = json.load(f)

# Extract relevant data into a list
item_dps_data = []

# Loop through items, assuming they are in 'items' or similar
for item in data.get("items", []):
    # Adjust the key names based on actual JSON structure
    item_name = item.get("name")
    dps_increase = item.get("dps_increase_percentage")  # Substitute with actual key
    
    # Append to list if dps_increase is found
    if item_name and dps_increase:
        item_dps_data.append({
            "name": item_name,
            "dps_increase": dps_increase
        })

# Write the extracted data to a new JSON file
with open('item_dps_data.json', 'w') as outfile:
    json.dump(item_dps_data, outfile, indent=4)

print("Data successfully written to item_dps_data.json")
