import os
import json
import re

# split paper
def slice_paper_content(paper_text, max_words=200):
    sentences = re.split(r'(?<=[.!?]) +', paper_text)  # Split by the space following a period, question mark, or exclamation point
    slices = []
    current_slice = []
    word_count = 0

    for sentence in sentences:
        sentence_word_count = len(sentence.split())

        if word_count + sentence_word_count > max_words:
            if current_slice:  
                slices.append(' '.join(current_slice))
            current_slice = [sentence]
            word_count = sentence_word_count
        else:
            current_slice.append(sentence)
            word_count += sentence_word_count

    if current_slice:
        slices.append(' '.join(current_slice))

    return slices


input_json = "carbon_paper.json" 
output_json = "sliced200_carbon_paper.json"

with open(input_json, "r", encoding="utf-8") as f:
    data = json.load(f)

# Processing JSON data organized by DOI
result = {
    "NER result": []
}

# Iterate through each paper in the JSON
for paper in data:
    pubmed_id = paper.get("PubMed_ID")  # get PubMed ID
    paper_content = paper.get("content")  # get full paper

    if not paper_content:
        continue  

    # split content
    sliced_content = []
    slices = slice_paper_content(paper_content)

    for slice_text in slices:
        sliced_content.append({"text": slice_text})

    # get result
    result["NER result"].append({
        "PubMed_ID": pubmed_id,  # PubMed ID <- DOI
        "content": paper_content,
        "paper result": sliced_content
    })


with open(output_json, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=4)

if not result["NER result"]:
    print("⚠️ Warning: No results found. Check the input data.")
else:
    print(f"✅ Processing complete. Results saved to {output_json}.")
