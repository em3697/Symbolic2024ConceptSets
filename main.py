import pandas as pd
import claude_lib
import test_model as coder
import json
import utils

# Load reference set and group by first column
reference_df = pd.read_csv('ConceptSets_EdgeCases/reference_sets.csv')
##grouped_df = reference_df.groupby('concept set')
eskd_reference_df = reference_df[reference_df['concept set'] == 'end stage kidney disease']
eskd_reference_concepts = eskd_reference_df['Name'].to_list()

# Evaluate gold standard similarity
sim_reference = coder.find_similarities('end stage kidney disease', eskd_reference_concepts)

# Load file of current PHOEBE output
eskd_phoebe_df = pd.read_csv('ConceptSets_EdgeCases/endstagerenal_phoebe_output.csv')
eskd_phoebe_concepts = eskd_phoebe_df['Name'].to_list()

# Evaluate PHOEBE concept list
sim_phoebe = coder.find_similarities('end stage kidney disease', eskd_phoebe_concepts)

# Append output concepts to CODER concept list
coder_concept_list = eskd_phoebe_concepts


# Set up LLM api
# claude = claude_lib.setup_claude_client('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')

# Run LLM prompt to get back concept sets
# response = claude_lib.send_message(
#             claude,
#             "",
#             model="claude-3-opus-20240229",
#             max_tokens=1000
#         )

# Process results
with open('ConceptSets_EdgeCases/dialysis-terms-json.json', 'r', encoding='utf-8') as file:
    llm_output = json.load(file)

# Run coder on returned LLM concept list compared to concept output or input term

# PROCEDURES
sim_procedures = coder.find_similarities('dialysis for chronic kidney disease', llm_output['procedures'])
utils.write_tuples_to_csv("dialysis_for_chronic_kidney_disease_procedures_output.csv", sim_procedures)

# TESTS
sim_tests = coder.find_similarities('dialysis for chronic kidney disease', llm_output['dialysis_specific_tests'])
utils.write_tuples_to_csv("dialysis_for_chronic_kidney_disease_tests_output.csv", sim_tests)

# MEDICATIONS
meds = llm_output['medications']
med_list = []
for elem in meds:
    concept = elem['name'] + ' ' + elem['dosage']
    med_list.append(concept)
sim_meds = coder.find_similarities('dialysis for chronic kidney disease', med_list)
utils.write_tuples_to_csv("dialysis_for_chronic_kidney_disease_med_dosage_output.csv", sim_meds)

med_list_names = []
for elem in meds:
    concept = elem['name']
    med_list_names.append(concept)
sim_meds_names = coder.find_similarities('dialysis for chronic kidney disease', med_list_names)
utils.write_tuples_to_csv("dialysis_for_chronic_kidney_disease_med_output.csv", sim_meds_names)

# Check whether any of these concepts are in the PHOEBE output

# Append to CODER concept list
# for i, elem in sim:
#     if elem > 0.5:
#         coder_concept_list.append(llm_output['procedures'][i])


# Remove duplicate concepts from concept list
# coder_concept_set = set(coder_concept_list)

# Run coder on input term and concept list


# Evaluate results


