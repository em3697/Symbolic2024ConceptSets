import requests
import json
import test_model
import claude_lib
import utils
import csv
import os
import pandas as pd
from itertools import islice

# Base URL for the API
# demo - https://atlas-demo.ohdsi.org/WebAPI
# discovery - https://discovery.dbmi.columbia.edu/WebAPI
BASE_URL = "https://atlas-demo.ohdsi.org/WebAPI"

# Replace with your Concept Set ID and API token
#CONCEPT_SET_ID = 12345
API_TOKEN = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJlbGlzZSBsYXVyZW4gbWludG8iLCJTZXNzaW9uLUlEIjoiY2M5ZTJiYTAtMmNiNS00M2E5LTllN2EtMTQ3OWYyNTU2NTJjIiwiZXhwIjoxNzMzNzk5NjM3fQ.f_7hxrxlkJzLmVYvn7T90VvlkCyJx5wYN6vOsALDhYTxxTjKuS8Z0tDkjWAkVjQH1YOeuoVXcHAI6TBSakDL6Q"

# Headers for authentication and content type
HEADERS = {
    # "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def chunked_iterable(iterable, size):
    """Yield chunks of the iterable of the given size."""
    it = iter(iterable)
    while chunk := list(islice(it, size)):
        yield chunk


def export(concept_set_id):
    # discovery: CUMC_inpatient_and_outpatient_2023q4r1
    constructed_endpoint = f"{BASE_URL}/conceptset/{concept_set_id}/export/"
    print(constructed_endpoint)
    response = requests.get(constructed_endpoint, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def lookup_concept_names(concept_ids):
    
    response = requests.post(f"{BASE_URL}/vocabulary/lookup/identifiers/", headers=HEADERS, json=concept_ids)
    
    if response.status_code == 200:
        concepts = response.json()
        concept_names = [concept['CONCEPT_NAME'] for concept in concepts]
        return concept_names
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None
    
def recommend(concepts):
    # conceptset/{id}/recommend
    # vocabulary/{sourceKey}/lookup/recommended
    # /conceptset/1885577/recommend
    # discovery - CUMC_inpatient_and_outpatient_2023q4r1
    response = requests.post(f"{BASE_URL}/vocabulary/ATLASPROD/lookup/recommended/", headers=HEADERS, json=concepts)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def search(concept_search_string):
    formatted_string = concept_search_string.replace(' ', '+')
    # discovery: CUMC_inpatient_and_outpatient_2023q4r1
    # demo: ATLASPROD
    constructed_endpoint = f"{BASE_URL}/vocabulary/ATLASPROD/search?query={formatted_string}"
    print(constructed_endpoint)
    response = requests.get(constructed_endpoint, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def get_concept_set(concept_set_id):
    """Retrieve the concept set details."""
    response = requests.get(f"{BASE_URL}/{concept_set_id}/", headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def get_concept_set_items(concept_set_id):
    response = requests.get(f"{BASE_URL}/conceptset/exportlist?conceptsets={concept_set_id}", headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


def update_concept_set_items(concept_set_id, concept_ids, descendants):
    """Update the concept set items with the provided concept IDs."""
    print('*. Add concepts')
    # Prepare the body
    items = [
        {
            "includeDescendants": descendants,
            "conceptSetId": concept_set_id,
            "isExcluded": 0,
            "includeMapped": 0,
            "conceptId": concept_id,
            "id": 0  # Set to 0 for new items
        }
        for concept_id in concept_ids
    ]

    # Send PUT request to update items
    response = requests.put(
        f"{BASE_URL}/conceptset/{concept_set_id}/items/",
        headers=HEADERS,
        json=items
    )

    if response.status_code == 200:
        print("Concept set items updated successfully.")
        print('*. Completed')
    else:
        print(f"Error: {response.status_code} - {response.text}")

def get_concept_set_items(concept_set_id):
    """Update the concept set items with the provided concept IDs."""
    
    # Send GET request to update items
    response = requests.get(
        f"{BASE_URL}/conceptset/{concept_set_id}/items/",
        headers=HEADERS
    )

    if response.status_code == 200:
        print("Concept set items gotten successfully.")
        items = response.json()
        ids = [item['conceptId'] for item in items]
        return ids
    else:
        print(f"Error: {response.status_code} - {response.text}")

def create_concept_set(name, description="", tags=None):
    """
    Create a new concept set in the database.
    :param name: The name of the new concept set.
    :param description: A description of the concept set (optional).
    :param tags: List of tags to associate with the concept set (optional).
    :return: The ID of the newly created concept set.
    """
    body = {
        "name": name,
        "description": description,
        "tags": tags or []  # Default to empty list if no tags are provided
    }
    
    response = requests.post(f"{BASE_URL}/conceptset/", headers=HEADERS, json=body)
    
    if response.status_code == 200:
        concept_set = response.json()
        print(f"Concept set created successfully with ID: {concept_set['id']}")
        return concept_set["id"]
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def new_concept_set(cohort, type):
    print('1. creating concept set')
    new_concept_set_name = f"EM VV 31 {cohort} {type}"
    new_concept_set_description = f"This concept set is for the {cohort} and is a concept set for {type}"
    new_concept_set_tags = [
        {
            "name": "Test Tag",
            "hasWriteAccess": True,
            "icon": "test-icon",
            "multiSelection": False,
            "permissionProtected": False,
            "color": "blue",
            "type": "CUSTOM",
            "description": "A tag for testing",
            "count": 0,
            "id": 0,
            "groups": [],
            "allowCustom": True,
            "showGroup": False,
            "mandatory": False
        }
    ]
    
    # Step 1: Create the new concept set
    new_concept_set_id = create_concept_set(
        name=new_concept_set_name,
        description=new_concept_set_description,
        tags=new_concept_set_tags
    )
    print('1. Completed')
    return new_concept_set_id

def atlas_search(cohort):
    print('2. Atlas search')
    # Step 2: Search for term
    search_results = search(cohort)

    # Step 3: Filter search results by vocabulary (CPT4, ICD10, ICD9Proc, SNOMED, and LOINC)
    search_data = search_results
    vocabs = ['CPT4', 'ICD10', 'ICD9Proc', 'SNOMED', 'LOINC']
    filtered_search = []
    concept_ids = []
    concept_names = []
    if search_data:
        for item in search_data:
            if item['VOCABULARY_ID'] in vocabs:
                filtered_search.append(item)
                concept_ids.append(item['CONCEPT_ID'])
                concept_names.append(item['CONCEPT_NAME'])
    print('2. Completed')
    return concept_ids

def phoebe_recs(concept_ids):
    print('3. Get PHOEBE concepts')
    vocabs = ['CPT4', 'ICD10', 'ICD9Proc', 'SNOMED', 'LOINC']
    recommended_concepts = recommend(concept_ids)

    filtered_phoebe_recs = []
    phoebe_concept_names = []
    phoebe_concepts = []
    if recommended_concepts:
        for item in recommended_concepts:
            if item['VOCABULARY_ID'] in vocabs:
                filtered_phoebe_recs.append(item)
                phoebe_concepts.append(item['CONCEPT_ID'])
                phoebe_concept_names.append(item['CONCEPT_NAME'])
    print('3. Completed')
    return phoebe_concepts


def get_relevant_concepts_csv(file):
    print('4. Get relevant concepts')
    concept_names = []
    with open(file, 'r') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            if row[2] == '1':
                concept_names.append(row[0])
    print('4. Completed')
    return concept_names

def get_llm_recs_search(llm_concept_names):
    print('5. Search LLM Recs')
    new_concept_ids = []
    for concept in llm_concept_names:
        search_results = search(concept)
        # filter for standard, valid, and vocabulary
        # Define your target vocabularies
        vocabs = ['CPT4', 'ICD10', 'ICD9Proc', 'SNOMED', 'LOINC']
        # Filter the list using a list comprehension
        filtered_concepts = [
            concept for concept in search_results 
            if (concept['STANDARD_CONCEPT'] == 'S' and 
                concept['INVALID_REASON'] == 'V' and 
                concept['VOCABULARY_ID'] in vocabs)
        ]
        if len(filtered_concepts) > 0:
            for result in filtered_concepts:
                new_concept_ids.append(result['CONCEPT_ID'])
    print('5. Completed')
    return new_concept_ids

def analysis(cohorts):
    # Find concepts
    with open('analysis_results.csv', 'w', newline='') as file:
        # Create a CSV writer object
        writer = csv.writer(file)

        # Write the header row (optional)
        writer.writerow(['Cohort', 'Domain', 'Added Concept Count', 'Concept Count To Remove'])
        domains = ['procedures']
        for cohort in cohorts:
            for domain in domains:
                # Get Baseline
                baseline_concept_subset = f"EM VV {cohort} ATLAS & PHOEBE"
                # Get domain specific
                domain_concept_subset = f"EM VV {cohort} {domain}"

                # Load the CSV file into a DataFrame
                csv_file = "includedConceptsAll.csv"
                df = pd.read_csv(csv_file)

                # Filter rows where 'Name' column equals a specific value
                baseline_filtered_rows = df[df['Name'] == baseline_concept_subset]
                domain_filtered_rows = df[df['Name'] == domain_concept_subset]

                if len(baseline_filtered_rows) > 0 and len(domain_filtered_rows) > 0:

                    # Find domain specifics not in baseline
                    additions = utils.check_domain_additions(baseline_filtered_rows, domain_filtered_rows)
                    additions_count = len(additions)

                    # Check for coder removal

                    # Parameters
                    chunk_size = 100  # Adjust this based on your system's memory and performance
                    to_remove_count = 0

                    for chunk in chunked_iterable(additions, chunk_size):
                        similarity_phoebe = test_model.find_similarities(cohort, chunk)
                        to_remove = [t for t in similarity_phoebe if t[1] < 0]
                        to_remove_count += len(to_remove)
                        
                    # Write the data row
                    writer.writerow([cohort, domain, additions_count, to_remove_count])


# Main logic
if __name__ == "__main__":

    # # What is not captured by our recs
    # diff = utils.check_differences_exported('mappedConcepts.csv', 'Dialysis for Chronic Kidney Disease Concepts - Anna - Additional procedures AO.csv')
    # # What is not captured by ATLAS + PHOEBE
    # diff_ctrl = utils.check_differences_exported('mappedConceptsCtrl.csv', 'Dialysis for Chronic Kidney Disease Concepts - Anna - Additional procedures AO.csv')
    # # What is captured by neither
    # diff_to_find = [val for val in diff if val in diff_ctrl]

    # # with open('dckd_concepts_llm_phoebe_missing.csv', 'w', newline='') as csvfile:
    # #     writer = csv.writer(csvfile)
    # #     writer.writerow(diff_to_find)
 

    # overlap = utils.check_validity_exported('mappedConcepts.csv', 'Dialysis for Chronic Kidney Disease Concepts - Anna - Additional procedures AO.csv')
    # overlap_ctrl = utils.check_validity_exported('mappedConceptsCtrl.csv', 'Dialysis for Chronic Kidney Disease Concepts - Anna - Additional procedures AO.csv')
    # new_concepts = []
    # for i in overlap:
    #     if i not in overlap_ctrl:
    #         new_concepts.append(i)


# 'Cataracts','Rheumatoid arthritis', 'Sickle Cell Anemia', 'Type 1 Diabetes', 'Dialysis for Chronic Kidney Disease'
    cohorts = ['Cataracts','Rheumatoid arthritis', 'Sickle Cell Anemia', 'Type 1 Diabetes', 'Dialysis for Chronic Kidney Disease']
    domains = ['procedures']

    analysis(cohorts)

    for cohort in cohorts:
        print(cohort)

        # Get search results for concept
        atlas_concept_ids = atlas_search(cohort)

        # Get PHOEBE recs for the concept set
        phoebe_concept_ids = phoebe_recs(atlas_concept_ids)

        # Create cohort concept sets
        baseline_concept_set_id = new_concept_set(cohort, 'ATLAS & PHOEBE')

        # Add concepts to the set
        update_concept_set_items(baseline_concept_set_id, atlas_concept_ids, 1)

        # Add recs to the set WITHOUT descendants
        update_concept_set_items(baseline_concept_set_id, phoebe_concept_ids, 0)

        for domain in domains:
            print(domain)

            # Get cohort files
            formatted_cohort = cohort.replace(' ', '_')
            file = f"12-3 results for annotation/{formatted_cohort}_{domain}_output.csv"

            # Check that file is found
            if os.path.exists(file):
                # Create concept set for domain and cohort
                concept_set_id = new_concept_set(cohort, domain)

                # Read file contents
                llm_concept_names = get_relevant_concepts_csv(file)

                if len(llm_concept_names) > 0:
                    # Search for concepts
                    llm_concept_ids_to_add = get_llm_recs_search(llm_concept_names)

                    if len(llm_concept_ids_to_add) > 0:
                        update_concept_set_items(concept_set_id, llm_concept_ids_to_add, 1)

            else:
                print('FILE NOT FOUND')
                exit()


    # # What is not captured by our recs
    # diff = utils.check_differences_exported('mappedConcepts.csv', 'Dialysis for Chronic Kidney Disease Concepts - Anna - Additional procedures AO.csv')
    # # What is not captured by ATLAS + PHOEBE
    # diff_ctrl = utils.check_differences_exported('mappedConceptsCtrl.csv', 'Dialysis for Chronic Kidney Disease Concepts - Anna - Additional procedures AO.csv')
    # # What is captured by neither
    # diff_to_find = [val for val in diff if val in diff_ctrl]

    # with open('dckd_concepts_llm_phoebe_missing.csv', 'w', newline='') as csvfile:
    #     writer = csv.writer(csvfile)
    #     writer.writerow(diff_to_find)
 

    # overlap = utils.check_validity_exported('mappedConcepts.csv', 'Dialysis for Chronic Kidney Disease Concepts - Anna - Additional procedures AO.csv')
    # overlap_ctrl = utils.check_validity_exported('mappedConceptsCtrl.csv', 'Dialysis for Chronic Kidney Disease Concepts - Anna - Additional procedures AO.csv')

    # new_concepts = []
    # for i in overlap:
    #     if i not in overlap_ctrl:
    #         new_concepts.append(i)

    # with open('dckd_concepts_llm_phoebe_added.csv', 'w', newline='') as csvfile:
    #     writer = csv.writer(csvfile)
    #     writer.writerow(new_concepts)


    
    # construct LLM Recs Concept Set
    # new_concept_set_name = "EM VV Dialysis for Chronic Kidney Disease - LLM Recs"
    # new_concept_set_description = "This uses prompt 3 llm output with all initial concepts and PHOEBE reccomendations as well as LLM reccomendations and descendants"
    # new_concept_set_tags = [
    #     {
    #         "name": "Test Tag",
    #         "hasWriteAccess": True,
    #         "icon": "test-icon",
    #         "multiSelection": False,
    #         "permissionProtected": False,
    #         "color": "blue",
    #         "type": "CUSTOM",
    #         "description": "A tag for testing",
    #         "count": 0,
    #         "id": 0,
    #         "groups": [],
    #         "allowCustom": True,
    #         "showGroup": False,
    #         "mandatory": False
    #     }
    # ]
    
    # # Step 1: Create the new concept set
    # new_concept_set_id_llm = create_concept_set(
    #     name=new_concept_set_name,
    #     description=new_concept_set_description,
    #     tags=new_concept_set_tags
    # )


    # Load CKD recs
    # with open('ConceptSets_EdgeCases/Big20/dialysis-precise-umls-terms.json') as f:
    #     llm_data = json.load(f)

    # # Add to concept set with
    # new_concept_ids = []

    # vocabs = ['CPT4', 'ICD10', 'ICD9Proc', 'SNOMED', 'LOINC']
    # filtered_search = []
    # concept_ids = []
    # concept_names = []
    # for item in search_data:
    #     if item['VOCABULARY_ID'] in vocabs:

    # for item in llm_data:
    #     for concept in llm_data[item]:
    #         concept_name = concept['term'] #'term', 'conceptId', 'vocabulary'
    #         # Search concept and add all descendants to the concept set
    #         search_results = search(concept_name)
    #         for result in search_results:
    #             if result['VOCABULARY_ID'] in vocabs:
    #             #test_model.find_similarities(concept_name, )
    #                 new_concept_ids.append(result['CONCEPT_ID'])
    # update_concept_set_items(new_concept_set_id_llm, new_concept_ids, 1)



    # Create a new concept set
    # new_concept_set_name = "EM VV Dialysis for Chronic Kidney Disease - ATLAS, PHOEBE, and LLM Recs"
    # new_concept_set_description = "This uses prompt 3 llm output with all initial concepts and PHOEBE reccomendations as well as LLM reccomendations and descendants"
    # new_concept_set_tags = [
    #     {
    #         "name": "Test Tag",
    #         "hasWriteAccess": True,
    #         "icon": "test-icon",
    #         "multiSelection": False,
    #         "permissionProtected": False,
    #         "color": "blue",
    #         "type": "CUSTOM",
    #         "description": "A tag for testing",
    #         "count": 0,
    #         "id": 0,
    #         "groups": [],
    #         "allowCustom": True,
    #         "showGroup": False,
    #         "mandatory": False
    #     }
    # ]
    
    # # Step 1: Create the new concept set
    # new_concept_set_id = create_concept_set(
    #     name=new_concept_set_name,
    #     description=new_concept_set_description,
    #     tags=new_concept_set_tags
    # )

    # new_concept_set_name_ctrl = "EM VV Dialysis for Chronic Kidney Disease - ATLAS, PHOEBE"
    # new_concept_set_description_ctrl = "This uses prompt 3 llm output with all initial concepts and PHOEBE reccomendations"
    # new_concept_set_tags_ctrl = [
    #     {
    #         "name": "Test Tag",
    #         "hasWriteAccess": True,
    #         "icon": "test-icon",
    #         "multiSelection": False,
    #         "permissionProtected": False,
    #         "color": "blue",
    #         "type": "CUSTOM",
    #         "description": "A tag for testing",
    #         "count": 0,
    #         "id": 0,
    #         "groups": [],
    #         "allowCustom": True,
    #         "showGroup": False,
    #         "mandatory": False
    #     }
    # ]
    
    # # Step 1: Create the new concept set
    # new_concept_set_id_ctrl = create_concept_set(
    #     name=new_concept_set_name_ctrl,
    #     description=new_concept_set_description_ctrl,
    #     tags=new_concept_set_tags_ctrl
    # )

    # new_concept_set_id = 1885579
    # new_concept_set_id_ctrl = 1885580


    # # Step 2: Search for term
    # input_term = 'Dialysis for Chronic Kidney Disease'
    # search_results = search(input_term)

    # # Step 3: Filter search results by vocabulary (CPT4, ICD10, ICD9Proc, SNOMED, and LOINC)
    # search_data = search_results
    # vocabs = ['CPT4', 'ICD10', 'ICD9Proc', 'SNOMED', 'LOINC']
    # filtered_search = []
    # concept_ids = []
    # concept_names = []
    # for item in search_data:
    #     if item['VOCABULARY_ID'] in vocabs:
    #         filtered_search.append(item)
    #         concept_ids.append(item['CONCEPT_ID'])
    #         concept_names.append(item['CONCEPT_NAME'])

    # # Step 4: Add concepts to the set
    # update_concept_set_items(new_concept_set_id, concept_ids, 1)
    # update_concept_set_items(new_concept_set_id_ctrl, concept_ids, 1)

    # Step 5: CODER++ exclusion
    # similarity = test_model.find_similarities(input_term, concept_names)
    # removal = [t for t in similarity if t[1] < 0]
    # concepts_removed = [t for t in similarity if t[1] > 0]

    # Step 6: Add PHOEBE recommendations
    # recommended_concepts = recommend(concept_ids)

    # filtered_phoebe_recs = []
    # phoebe_concept_names = []
    # phoebe_concepts = []
    # for item in recommended_concepts:
    #     if item['VOCABULARY_ID'] in vocabs:
    #         filtered_phoebe_recs.append(item)
    #         phoebe_concepts.append(item['CONCEPT_ID'])
    #         phoebe_concept_names.append(item['CONCEPT_NAME'])


    # # Step 7: CODER++ exclusion
    # similarity_phoebe = test_model.find_similarities(input_term, phoebe_concept_names)
    # phoebe_removal = [t for t in similarity_phoebe if t[1] < 0]
    # phoebe_concepts_removed = [t for t in similarity_phoebe if t[1] > 0]

    # update_concept_set_items(new_concept_set_id, phoebe_concepts, 1)
    # update_concept_set_items(new_concept_set_id_ctrl, phoebe_concepts, 1)
    # Could remove 100 unnecessary reccomendations here

    # Check how many concepts could be irrelevant
    # items = get_concept_set_items(new_concept_set_id)


    # Step 8: Run LLM for term
#     query = f'''As a clinical trial coordinator, I need to gather all clinically relevant procedures, tests, medications, and associated symptoms related to the term {input_term}.
# Please provide a comprehensive list of UMLS terms that I should look for in patient charts that may indicate the diagnosis related to this term, ensuring a high level of detail and specificity in the response. Please include terms from CPT4, ICD10, ICD9Proc, SNOMED, and LOINC.
# Please include the procedures, specific tests and medications. Focus on the core medical terminology without descriptive modifiers like 'training', 'placement', or 'insertion'.  With each term return the full string, concept ID, and the specific vocabulary it comes from. The more specific ones are better. Please organize in a comma separated list no need to maintain headers.
# Remove white space and all cpt codes and abbreviations in parentheses from output and return it in json format. Make sure each item returned by the json has the same format. Return the json formatted as a dictionary of key value pairs where the top level key is the category (“procedures”, “tests”, “medications”, etc.) and within the value is a list of dictionaries where each dictionary is a concept from the top level key category. Include at least 10 in each section. Do not return anything other than the JSON formatted data.
# '''
    
#     llm_suggestions = claude_lib.run_query(query).replace('\n', '')
#     print(llm_suggestions)

#     # Step 9: Input each llm concept into atlas search and include all descendants
#     llm_data = json.loads(llm_suggestions)
    # with open('ConceptSets_EdgeCases/Big20/sickle-cell-comprehensive-terminology.json') as f:
    #     llm_data = json.load(f)
        
    # new_concept_ids = []

    # for item in llm_data:
    #     for concept in llm_data[item]:
    #         concept_name = concept['term'] #'term', 'conceptId', 'vocabulary'
    #         # Search concept and add all descendants to the concept set
    #         search_results = search(concept_name)
    #         for result in search_results:
    #             #test_model.find_similarities(concept_name, )
    #             new_concept_ids.append(result['CONCEPT_ID'])
    # update_concept_set_items(new_concept_set_id, new_concept_ids, 1)


    # Step 10: Compare overlap of llm to anna's output
    # exported = export(new_concept_set_id)
    # exported_ctrl = export(new_concept_set_id_ctrl)


    # items = get_concept_set_items(new_concept_set_id)
    # lookup = lookup_concept_names(items)
    # # 398207 concepts
    # # 95372 items
    # items_ctrl = get_concept_set_items(new_concept_set_id_ctrl)
    # lookup_ctrl = lookup_concept_names(items_ctrl)
    # # 1,
    # # 1393 items

    # # Analysis - Check initial overlap with Anna's set
    # # 
    # overlap = utils.check_validity_concept_items(lookup, 'Dialysis for Chronic Kidney Disease Concepts - Anna - Additional procedures AO.csv')
    # overlap_ctrl = utils.check_validity_concept_items(lookup_ctrl, 'Dialysis for Chronic Kidney Disease Concepts - Anna - Additional procedures AO.csv')

    # # Analysis - Check how this changes over multiple calls

    # # Analysis - Check how many concepts in each may be irrelevant
    # # try running this in batches

    # similarity = test_model.find_similarities(input_term, lookup)
    # removal = [t for t in similarity if t[1] < 0]
    # cleaned = [t for t in similarity if t[1] > 0]

    # similarity_ctrl = test_model.find_similarities(input_term, lookup_ctrl)
    # removal_ctrl = [t for t in similarity_ctrl if t[1] < 0]
    # cleaned_ctrl = [t for t in similarity_ctrl if t[1] > 0]
    # print()
    # Analysis - Check if there's any change in overlap when you remove irrelevant ones

    # Analysis - What are we still missing


    # overlap = utils.check_validity('mappedConcepts.csv', 'Dialysis for Chronic Kidney Disease Concepts - Anna - Additional procedures AO.csv')
    # missing = utils.check_missing_concepts_llm('mappedConcepts.csv', 'Dialysis for Chronic Kidney Disease Concepts - Anna - Additional procedures AO.csv')
    # with open('dckd_concepts_llm_missing_mapped', 'w', newline='') as csvfile:
    #         writer = csv.writer(csvfile)
    #         writer.writerow(missing)

    



