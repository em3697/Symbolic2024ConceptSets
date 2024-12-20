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


def update_concept_set_items(concept_set_id, concept_ids, descendants, other_concept_ids):
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
    if len(other_concept_ids) > 0:
        other_items = [
            {
                "includeDescendants": 0,
                "conceptSetId": concept_set_id,
                "isExcluded": 0,
                "includeMapped": 0,
                "conceptId": concept_id,
                "id": 0  # Set to 0 for new items
            }
            for concept_id in other_concept_ids
        ]

        items.extend(other_items)



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
    new_concept_set_name = f"EM VV Final4 {cohort} {type}"
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
            if row[2] == '1' and row[3] == '1':
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
        domains = ['procedures', 'tests', 'medications', 'symptoms']
        for cohort in cohorts:
            for domain in domains:
                # Get Baseline
                baseline_concept_subset = f"EM VV {cohort} ATLAS & PHOEBE"
                # Get domain specific
                domain_concept_subset = f"EM VV {cohort} {domain}"

                # Load the CSV file into a DataFrame
                csv_file = "includedConceptsFinalAll.csv"
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


# 'Dialysis for Chronic Kidney Disease', 'Cataracts','Rheumatoid arthritis', 'Sickle Cell Anemia', 'Type 1 Diabetes'
    cohorts = ['Dialysis for Chronic Kidney Disease', 'Cataracts','Rheumatoid arthritis', 'Sickle Cell Anemia', 'Type 1 Diabetes']
    domains = ['procedures', 'tests,', 'medications', 'symptoms']

    analysis(cohorts)

    for cohort in cohorts:
        print(cohort)

        # Get search results for concept
        atlas_concept_ids = atlas_search(cohort)

        # Get PHOEBE recs for the concept set
        phoebe_concept_ids = phoebe_recs(atlas_concept_ids)

        # Create cohort concept sets
        baseline_concept_set_id = new_concept_set(cohort, 'ATLAS & PHOEBE')

        # Add concepts to the set and add recs to the set WITHOUT descendants
        update_concept_set_items(baseline_concept_set_id, atlas_concept_ids, 1, phoebe_concept_ids)

        for domain in domains:
            print(domain)

            # Get cohort files
            formatted_cohort = cohort.replace(' ', '_')
            file = f"12-3 results for annotation/{formatted_cohort}_{domain}_output.csv"

            # Check that file is found
            if os.path.exists(file):
                # Read file contents
                llm_concept_names = get_relevant_concepts_csv(file)

                if len(llm_concept_names) > 0:
                    # Search for concepts
                    llm_concept_ids_to_add = get_llm_recs_search(llm_concept_names)

                    if len(llm_concept_ids_to_add) > 0:
                        # Create concept set for domain and cohort
                        concept_set_id = new_concept_set(cohort, domain)
                        update_concept_set_items(concept_set_id, llm_concept_ids_to_add, 1)

            else:
                print('FILE NOT FOUND')


    # Benchmark Evaluation
    
    # What is not captured by our recs
    diff = utils.check_differences_exported('file.csv', 'Dialysis for Chronic Kidney Disease Concepts - Anna - Additional procedures AO.csv')
    # What is not captured by ATLAS + PHOEBE
    diff_ctrl = utils.check_differences_exported('file.csv', 'Dialysis for Chronic Kidney Disease Concepts - Anna - Additional procedures AO.csv')
    # What is captured by neither
    diff_to_find = [val for val in diff if val in diff_ctrl]

    with open('dckd_concepts_llm_phoebe_missing.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(diff_to_find)
 

    overlap = utils.check_validity_exported('includedConceptsFinalAll.csv', 'Dialysis for Chronic Kidney Disease Concepts - Anna - Additional procedures AO.csv')
    overlap_ctrl = utils.check_validity_exported('mappedConceptsCtrl.csv', 'Dialysis for Chronic Kidney Disease Concepts - Anna - Additional procedures AO.csv')
    missing = utils.check_missing_concepts_llm('file.csv', 'Dialysis for Chronic Kidney Disease Concepts - Anna - Additional procedures AO.csv')

    new_concepts = []
    for i in overlap:
        if i not in overlap_ctrl:
            new_concepts.append(i)

    with open('dckd_concepts_llm_phoebe_added.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(new_concepts)

    with open('dckd_concepts_llm_missing_mapped', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(missing)
    



