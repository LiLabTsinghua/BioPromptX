import json
import re


def normalize_value(value):
    """Normalize numerical values by removing units and symbols, keeping only the number."""
    # Keep only the numerical part (including negative signs and decimal points)
    match = re.match(r'([\-+]?\d*\.\d+|\d+)', value)
    if match:
        return match.group(0)  # Return the normalized numerical part
    return value  # If no valid number is matched, return the original value


def add_table_kinetic_params_to_paper_kinetics(paper_kinetics_file, table_kinetics_file, output_file):
    # Read the enzyme kinetic parameters file extracted from tables
    with open(table_kinetics_file, 'r', encoding='utf-8') as f:
        table_kinetics_data = json.load(f)

    # Read the enzyme kinetic parameters file extracted from the main text
    with open(paper_kinetics_file, 'r', encoding='utf-8') as f:
        paper_kinetics_data = json.load(f)

    # Iterate through the data extracted from tables
    for table_entry in table_kinetics_data:
        doi = table_entry['doi']
        table_kinetics = table_entry['Kinetic Parameters']

        # Find the corresponding main text extraction result for the DOI
        for paper_entry in paper_kinetics_data:
            if paper_entry['doi'] == doi:
                # If kinetic parameters exist in the main text extraction, append table-extracted parameters to existing ones
                if 'Kinetic Parameters' in paper_entry:
                    for param_name in ['kcat', 'Km', 'kcat/Km']:
                        for value in table_kinetics[param_name]:
                            # Normalize the parameter value (remove unit info and symbols) for checking
                            normalized_value = normalize_value(value)

                            # Check if the value already exists; if not, add it
                            if not any(normalize_value(existing_value) == normalized_value for existing_value in
                                       paper_entry['Kinetic Parameters'][param_name]):
                                paper_entry['Kinetic Parameters'][param_name].append(value)
                else:
                    # If no kinetic parameters exist in the main text extraction, add them directly
                    paper_entry['Kinetic Parameters'] = table_kinetics
                break

    # Save the modified results to a new file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(paper_kinetics_data, f, ensure_ascii=False, indent=4)


# Example usage
add_table_kinetic_params_to_paper_kinetics(
    paper_kinetics_file='/home/zhetao/Human_gene/Info_Extration/Dataset_Process/SC_doi_kinetic.json',  # Enzyme kinetic parameters file extracted from main text
    table_kinetics_file='SC_tables_result_combined.json',  # Enzyme kinetic parameters file extracted from tables
    output_file='/home/zhetao/Human_gene/Info_Extration/Dataset_Process/SC_kinetic_combined.json'  # Output file
)
