import pandas as pd
from time import sleep
from tqdm import tqdm
from qwen_api import qwen_api  # Interface to call the model


# Call the model interface to determine if two gene functions are consistent
def compare_gene_functions_with_prompt(gene_function1, gene_function2):
    system_prompt = 'You are a knowledgeable assistant in molecular biology.'

    prompt = f"""
    Two gene functions are described below:\n
    Gene Function1: '''{gene_function1}'''
    Gene Function2: '''{gene_function2}'''

    Please determine if the functions described for Gene are consistent or different.

    If the functions are fully consistent, respond with 'Yes, the gene's two function descriptions are consistent'.
    If the functions are partly consistent, respond with 'Unclear, the gene's two function descriptions are not entirely consistent'.
    If the functions are entirely different, respond with 'No, the gene's two function descriptions are inconsistent'.

    Output strictly follow the example and don't output any other information.'
    """

    result = qwen_api(user_message=prompt, top_p=0.6, system_message=system_prompt)

    # Check if result is None, and handle it appropriately
    if result is None:
        return "impossible judge"  # Or return another placeholder

    return result.strip()


# Read the TSV file and call the model to judge if gene functions are consistent
def compare_gene_functions_in_tsv(input_file, output_file):
    # Read the TSV file
    df = pd.read_csv(input_file, sep='\t')

    # Assume gene function descriptions are stored in columns named 'Function [CC]' and 'Confirmed Gene Function'
    gene_function_column1 = df['Function [CC]']
    gene_function_column2 = df['Gene Function Description']

    # Create a new column to store the model's judgment results
    comparison_results = []

    # Use tqdm to display a progress bar
    for g1_func, g2_func in tqdm(zip(gene_function_column1, gene_function_column2), total=len(gene_function_column1),
                                 desc="Comparing gene functions"):
        # Check if the value in the Function column is "PubMed_ID not found", "Not found", etc.
        if g2_func in ["PubMed_ID not found", "Not found", "Not mentioned in the provided article."]:
            comparison_results.append("")  # Or use pd.NA or np.nan
        else:
            # Call the model interface to compare gene function descriptions
            result = compare_gene_functions_with_prompt(g1_func, g2_func)
            comparison_results.append(result)
            sleep(1)  # Add delay to avoid frequent API calls

    # Add the comparison results to a new column in the dataframe
    df['Function Comparison Result2'] = comparison_results

    # Save the results to a new TSV file
    df.to_csv(output_file, sep='\t', index=False)
    print(f"Comparison results saved to {output_file}")


if __name__ == '__main__':
    # Define the paths for input and output TSV files
    input_file = 'carbon_result_gene_Q30B_comparison_checked_split_function.tsv'  
    output_file = 'carbon_result_gene_Q30B_comparison_checked_split_function_result.tsv'  

    # Call the function to perform gene function comparison
    compare_gene_functions_in_tsv(input_file, output_file)
