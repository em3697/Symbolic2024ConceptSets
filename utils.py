import csv

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
        
    