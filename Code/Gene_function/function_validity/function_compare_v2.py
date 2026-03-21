import pandas as pd
from time import sleep
from tqdm import tqdm
from qwen_api import qwen_api 


# Check gene function consistency
def compare_gene_functions_with_prompt(gene_function1, gene_function2):
    system_prompt = 'You are a knowledgeable assistant in molecular biology.'

    prompt = f"""
    Two gene functions are described below:\n
    Gene Function1: '''{gene_function1}'''
    Gene Function2: '''{gene_function2}'''

    Please determine if the functions described for Gene are consistent or different. 

    Please give me a consistent score between two functional descriptions.
    Different score means different consistence:
    0：The two function descriptions are completely inconsistent.
    2.5: The two function descriptions are less partially consistent.
    5: The two function descriptions are partially consistent.
    7.5: The two function descriptions are mostly consistent.
    10: The two function descriptions are completely consistent.

    Only output score(0, 2.5, 5, 7.5, 10) between two functional descriptions, don't output any other score and any redundant information.
    """

    result = qwen_api(user_message=prompt, top_p=0.6, system_message=system_prompt)

    # Check if result is None, and handle it appropriately
    if result is None:
        return "impossible judge"  

    return result.strip()


# compare functions from tsv
def compare_gene_functions_in_tsv(input_file, output_file):
    # read tsv
    df = pd.read_csv(input_file, sep='\t')

    gene_function_column1 = df['Function [CC]']
    gene_function_column2 = df['Gene Function Description']

    comparison_results = []

    for g1_func, g2_func in tqdm(zip(gene_function_column1, gene_function_column2), total=len(gene_function_column1),
                                 desc="Comparing gene functions"):
        # check Function "PubMed_ID not found" or "Not found"
        if g2_func in ["PubMed_ID not found", "Not found", "Not mentioned in the provided article."]:
            comparison_results.append("")  
        else:
            # compare function
            result = compare_gene_functions_with_prompt(g1_func, g2_func)
            comparison_results.append(result)
            sleep(1)  

    df['Function Comparison Result3'] = comparison_results

    df.to_csv(output_file, sep='\t', index=False)
    print(f"Comparison results saved to {output_file}")


if __name__ == '__main__':

    input_file = 'carbon_result_gene_DS32_comparison_checked_split_function_result.tsv' 
    output_file = 'carbon_result_gene_DS32_comparison_checked_split_function_result.tsv' 

    compare_gene_functions_in_tsv(input_file, output_file)
