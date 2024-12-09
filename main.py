import pandas as pd
import claude_lib
import test_model as coder
import json
import utils


# Cataracts
# utils.get_similarities('ConceptSets_EdgeCases/Big20/cataract-umls-terms.json', 'Cataracts')
# utils.get_differences('ConceptSets_EdgeCases/Big20/cataracts_PHOEBE_initial.csv', 'Cataracts')

# Type 1 Diabetes
# utils.get_similarities('ConceptSets_EdgeCases/Big20/type-1-diabetes-terminology.json', 'Type 1 Diabetes')

# Rheumatoid Arthritis
# utils.get_similarities('ConceptSets_EdgeCases/Big20/rheumatoid-arthritis-detailed-terminology.json', 'Rheumatoid arthritis')
# utils.get_differences('ConceptSets_EdgeCases/Big20/RA_PHOEBE_initial.csv', 'Rheumatoid arthritis')

# Sickle Cell
# utils.get_similarities('ConceptSets_EdgeCases/Big20/sickle-cell-comprehensive-terminology.json', 'Sickle Cell Anemia')
# utils.get_differences('ConceptSets_EdgeCases/Big20/SickleCellAnemia_PHOEBE_initial.csv', 'Sickle Cell Anemia')

# Dialysis for Chronic Kidney Disease
# utils.get_similarities('ConceptSets_EdgeCases/Big20/dialysis-precise-umls-terms.json', 'Dialysis for Chronic Kidney Disease')

# cataracts = {
# 'comorbidities': 'Cataracts_comorbidities_output.csv',
# 'diagnostic_tests': 'Cataracts_diagnostic_tests_output.csv',
# 'medications_detailed': 'Cataracts_medications_detailed_output.csv',
# 'medications': 'Cataracts_medications_not_detailed_output.csv',
# 'procedures': 'Cataracts_procedures_output.csv',
# 'progress_note': 'Cataracts_progress_note_keywords_output.csv',
# 'surgical_parameters_detailed': 'Cataracts_surgical_parameters_detailed_output.csv',
# 'surgical_parameters': 'Cataracts_surgical_parameters_not_detailed_output.csv',
# 'symptoms': 'Cataracts_symptoms_output.csv',
# 'to_remove': 'Cataracts_to_remove.csv',
# }

# utils.write_csv_to_sheets('1Wy6nSB73m0etmYJIPdocQJylF_y-18YfMcfAKkP54t4', cataracts, '/Users/em3697/Downloads/aou-ehr-ops-curation-test-2a2138f19033.json')

overlap = utils.check_validity('ConceptSets_EdgeCases/RD_mapped_UMLS.csv', 'Dialysis for Chronic Kidney Disease Concepts - Anna - Additional procedures AO.csv')

# sim = utils.get_similarities('ConceptSets_EdgeCases/dialysis_llmterms_2.json', 'dialysis for chronic kidney disease')

import requests

# Base URL
base_url = "https://discovery.dbmi.columbia.edu/atlas/dev/WebApi/concepset/"

# Make GET request
try:
    # Basic authentication

    response = requests.get(base_url)
    
    # Check if request was successful
    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print(f"Request failed with status code: {response.status_code}")
        
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")


# # Load reference set and group by first column
# reference_df = pd.read_csv('ConceptSets_EdgeCases/reference_sets.csv')
# ##grouped_df = reference_df.groupby('concept set')
# eskd_reference_df = reference_df[reference_df['concept set'] == 'end stage kidney disease']
# eskd_reference_concepts = eskd_reference_df['Name'].to_list()

# # PHOEBE sim
# ckd_phoebe_df = pd.read_csv('ConceptSets_EdgeCases/Phoebe_dialysisCKD_initial_full.csv')
# ckd_phoebe_concepts = ckd_phoebe_df['Name'].to_list()

# phoebe_sim = coder.find_similarities('dialysis for chronic kidney disease', ckd_phoebe_concepts)
# removal = [t for t in phoebe_sim if t[1] < 0]
# utils.write_tuples_to_csv("dialysis_for_chronic_kidney_disease_to_remove.csv", removal)


# # Evaluate gold standard similarity
# sim_reference = coder.find_similarities('end stage kidney disease', eskd_reference_concepts)


# # Load file of current PHOEBE output
# eskd_phoebe_df = pd.read_csv('ConceptSets_EdgeCases/endstagerenal_phoebe_output.csv')
# eskd_phoebe_concepts = eskd_phoebe_df['Name'].to_list()

# # Evaluate PHOEBE concept list
# sim_phoebe = coder.find_similarities('end stage kidney disease', eskd_phoebe_concepts)

# # Append output concepts to CODER concept list
# coder_concept_list = eskd_phoebe_concepts


# # Set up LLM api
# # claude = claude_lib.setup_claude_client('')

# # Run LLM prompt to get back concept sets
# # response = claude_lib.send_message(
# #             claude,
# #             "",
# #             model="claude-3-opus-20240229",
# #             max_tokens=1000
# #         )

# # Process results
# with open('ConceptSets_EdgeCases/dialysis-terms-json.json', 'r', encoding='utf-8') as file:
#     llm_output = json.load(file)

# # Run coder on returned LLM concept list compared to concept output or input term

# # PROCEDURES
# sim_procedures = coder.find_similarities('dialysis for chronic kidney disease', llm_output['procedures'])
# utils.write_tuples_to_csv("dialysis_for_chronic_kidney_disease_procedures_output.csv", sim_procedures)

# # TESTS
# sim_tests = coder.find_similarities('dialysis for chronic kidney disease', llm_output['dialysis_specific_tests'])
# utils.write_tuples_to_csv("dialysis_for_chronic_kidney_disease_tests_output.csv", sim_tests)

# # MEDICATIONS
# meds = llm_output['medications']
# med_list = []
# for elem in meds:
#     concept = elem['name'] + ' ' + elem['dosage']
#     med_list.append(concept)
# sim_meds = coder.find_similarities('dialysis for chronic kidney disease', med_list)
# utils.write_tuples_to_csv("dialysis_for_chronic_kidney_disease_med_dosage_output.csv", sim_meds)

# med_list_names = []
# for elem in meds:
#     concept = elem['name']
#     med_list_names.append(concept)
# sim_meds_names = coder.find_similarities('dialysis for chronic kidney disease', med_list_names)
# utils.write_tuples_to_csv("dialysis_for_chronic_kidney_disease_med_output.csv", sim_meds_names)




# Check whether any of these concepts are in the PHOEBE output

# Append to CODER concept list
# for i, elem in sim:
#     if elem > 0.5:
#         coder_concept_list.append(llm_output['procedures'][i])


# Remove duplicate concepts from concept list
# coder_concept_set = set(coder_concept_list)

# Run coder on input term and concept list


# Evaluate results


