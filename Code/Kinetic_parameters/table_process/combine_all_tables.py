import json

# Input JSON file
input_file = 'SC_tables_result.json'  # Please replace with the actual file path
output_file = 'SC_tables_result_combined.json'

# Load input data
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Store the final merged data
merged_data = []

# Iterate through data related to each DOI
for article in data:
    for doi, tables in article.items():
        # Create a new entry
        entry = {
            "doi": doi,
            "Kinetic Parameters": {
                "kcat": [],
                "Km": [],
                "kcat/Km": []
            }
        }

        # Ensure tables is a dictionary type
        if isinstance(tables, dict):
            # Iterate through each table
            for table_id, table_content in tables.items():
                # Extract the table title to classify the table
                if table_id.endswith("Kinetic Parameters"):
                    # Assuming Kinetic Parameters data appears in this format
                    if isinstance(table_content, dict):
                        for param_type in ["kcat", "Km", "kcat/Km"]:
                            # Merge each Kinetic Parameters item
                            if param_type in table_content:
                                entry["Kinetic Parameters"][param_type].extend(table_content[param_type])

            # Add the merged entry to the result list
            merged_data.append(entry)
        else:
            # If no tables are found, log the DOI and skip
            print(f"No tables found for DOI: {doi}")

# Output to the new file
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(merged_data, f, ensure_ascii=False, indent=4)

print(f"Processing complete. Merged data has been saved to {output_file}")
