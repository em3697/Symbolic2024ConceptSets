import csv
import json
import pandas as pd
import claude_lib
import test_model as coder
import utils

from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
import csv

def write_csv_to_sheets(spreadsheet_id, csv_files, credentials_path):
    """
    Write multiple CSV files to different tabs in a Google Sheet.
    
    Parameters:
    spreadsheet_id (str): The ID of the Google Sheet (from the URL)
    csv_files (dict): Dictionary with sheet names as keys and CSV file paths as values
    credentials_path (str): Path to your Google Sheets API credentials JSON file
    
    Returns:
    bool: True if successful, False if there was an error
    """
    try:
        # Set up credentials and service
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        service = build('sheets', 'v4', credentials=credentials)
        sheets = service.spreadsheets()

        # Get existing sheet names
        sheet_metadata = sheets.get(spreadsheetId=spreadsheet_id).execute()
        existing_sheets = {sheet['properties']['title'] for sheet in sheet_metadata.get('sheets', [])}

        for sheet_name, csv_path in csv_files.items():
            # Read CSV file
            with open(csv_path, 'r', encoding='utf-8') as file:
                csv_data = list(csv.reader(file))
            
            if not csv_data:
                print(f"Warning: CSV file {csv_path} is empty")
                continue

            # Create new sheet if it doesn't exist
            if sheet_name not in existing_sheets:
                request_body = {
                    'requests': [{
                        'addSheet': {
                            'properties': {
                                'title': sheet_name
                            }
                        }
                    }]
                }
                sheets.batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body=request_body
                ).execute()
                print(f"Created new sheet: {sheet_name}")
            else:
                # Clear existing content if sheet exists
                range_name = f"{sheet_name}!A1:ZZ"
                sheets.values().clear(
                    spreadsheetId=spreadsheet_id,
                    range=range_name
                ).execute()

            # Write data to sheet
            range_name = f"{sheet_name}!A1"
            body = {
                'values': csv_data
            }
            sheets.values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            print(f"Successfully wrote data to sheet: {sheet_name}")

            # Auto-resize columns
            request_body = {
                "requests": [{
                    "autoResizeDimensions": {
                        "dimensions": {
                            "sheetId": get_sheet_id(sheets, spreadsheet_id, sheet_name),
                            "dimension": "COLUMNS",
                            "startIndex": 0,
                            "endIndex": len(csv_data[0])
                        }
                    }
                }]
            }
            sheets.batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=request_body
            ).execute()

        return True

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False



def get_sheet_id(sheets, spreadsheet_id, sheet_name):
    """Helper function to get the sheet ID for a given sheet name"""
    sheet_metadata = sheets.get(spreadsheetId=spreadsheet_id).execute()
    for sheet in sheet_metadata.get('sheets', []):
        if sheet['properties']['title'] == sheet_name:
            return sheet['properties']['sheetId']
    return None



def write_tuples_to_csv(file_path, data):
    """
    Write a list of tuples to a CSV file with two columns.
    
    Parameters:
        file_path (str): Path to the output CSV file
        data (list): List of tuples to be written to the CSV file
    """
    try:
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for item in data:
                writer.writerow(item)
        print(f"Data written to CSV file: {file_path}")
    except Exception as e:
        raise Exception(f"Error writing to CSV file: {str(e)}")
        

def get_similarities(llm_output_path, input_concept):

    concept_var = input_concept.replace(' ', '_')

    with open(llm_output_path, 'r') as file:
        llm_data = json.load(file)

    for key, value in llm_data.items():
        if isinstance(value, list):
            if all(isinstance(item, dict) for item in value):

                terms = [item['term'] for item in value]
                
                # pass list to coder to get similarity output
                sim = coder.find_similarities(input_concept, terms)

                # write similarity to a csv
                utils.write_tuples_to_csv(f"{concept_var}_{key}_output.csv", sim)
                print(f'output {key} csv')

            else:
                print(f"Key '{key}' has a list with mixed data types.")
        else:
            print(f"Key '{key}' has a non-list value: {value}")


    return


def get_differences(phoebe_output_path, input_concept):

    concept_var = input_concept.replace(' ', '_')

    # PHOEBE sim
    phoebe_df = pd.read_csv(phoebe_output_path)
    phoebe_concepts = phoebe_df['Name'].to_list()

    phoebe_sim = coder.find_similarities(input_concept, phoebe_concepts)
    removal = [t for t in phoebe_sim if t[1] < 0]
    utils.write_tuples_to_csv(f"{concept_var}_to_remove.csv", removal)

    return
def check_differences_exported(UMLS_mapped_output_path, anna_recs_path):
    umls_mapped_df = pd.read_csv(UMLS_mapped_output_path)
    umls_mapped_concepts = umls_mapped_df['Concept Name'].to_list()

    recs_df = pd.read_csv(anna_recs_path)
    recs_concepts = recs_df['name'].to_list()
    overlap = [value for value in recs_concepts if value not in umls_mapped_concepts]
    return overlap

def check_validity_exported(UMLS_mapped_output_path, anna_recs_path):
    umls_mapped_df = pd.read_csv(UMLS_mapped_output_path)
    umls_mapped_concepts = umls_mapped_df['Concept Name'].to_list()

    recs_df = pd.read_csv(anna_recs_path)
    recs_concepts = recs_df['name'].to_list()
    overlap = [value for value in recs_concepts if value in umls_mapped_concepts]
    return overlap

def check_validity(UMLS_mapped_output_path, anna_recs_path):
    umls_mapped_df = pd.read_csv(UMLS_mapped_output_path)
    umls_mapped_concepts = umls_mapped_df['Name'].to_list()

    recs_df = pd.read_csv(anna_recs_path)
    recs_concepts = recs_df['name'].to_list()
    overlap = [value for value in recs_concepts if value in umls_mapped_concepts]
    return overlap

def check_validity_concept_items(items, anna_recs_path):
    recs_df = pd.read_csv(anna_recs_path)
    recs_concepts = recs_df['name'].to_list()
    overlap = [value for value in recs_concepts if value in items]
    return overlap

def check_missing_concepts_llm(output_path, anna_recs_path):
    umls_mapped_df = pd.read_csv(output_path)
    umls_mapped_concepts = umls_mapped_df['Concept Name'].to_list()

    recs_df = pd.read_csv(anna_recs_path)
    recs_concepts = recs_df['name'].to_list()
    missing = [value for value in recs_concepts if value not in umls_mapped_concepts]
    return missing

def check_validity_api(exported_concepts, anna_recs_path):
    pass