import os

def filter_umls_files(umls_dir, output_dir, source_vocabularies):
    """
    Filters MRCONSO.RRF, MRREL.RRF, and MRSTY.RRF files based on a list of acceptable source vocabularies.
    
    Parameters:
    - umls_dir: Path to the directory containing the UMLS files (MRCONSO.RRF, MRREL.RRF, MRSTY.RRF).
    - output_dir: Path to the output directory where the filtered files will be saved.
    - source_vocabularies: List of acceptable source vocabularies (SAB).
    """
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Define file paths
    mrconso_file = os.path.join(umls_dir, "MRCONSO.RRF")
    mrrel_file = os.path.join(umls_dir, "MRREL.RRF")
    mrsty_file = os.path.join(umls_dir, "MRSTY.RRF")

    # Define output file paths
    filtered_mrconso_file = os.path.join(output_dir, "MRCONSO.RRF")
    filtered_mrrel_file = os.path.join(output_dir, "MRREL.RRF")
    filtered_mrsty_file = os.path.join(output_dir, "MRSTY.RRF")
    
    # Filter MRCONSO.RRF
    print("Filtering MRCONSO.RRF...")
    with open(mrconso_file, "r", encoding="utf-8") as infile, \
         open(filtered_mrconso_file, "w", encoding="utf-8") as outfile:
        for line in infile:
            fields = line.strip().split("|")
            if fields[11] in source_vocabularies:  # SAB is the 12th column (index 11)
                outfile.write(line)
    print("Filtered MRCONSO.RRF written to:", filtered_mrconso_file)

    # Filter MRREL.RRF
    print("Filtering MRREL.RRF...")
    with open(mrrel_file, "r", encoding="utf-8") as infile, \
         open(filtered_mrrel_file, "w", encoding="utf-8") as outfile:
        for line in infile:
            fields = line.strip().split("|")
            if fields[8] in source_vocabularies:  # SAB is the 9th column (index 8)
                outfile.write(line)
    print("Filtered MRREL.RRF written to:", filtered_mrrel_file)

    # Filter MRSTY.RRF (No SAB column in MRSTY.RRF, only filter based on existing CUIs)
    print("Filtering MRSTY.RRF based on CUIs from MRCONSO.RRF...")
    valid_cuis = set()
    with open(filtered_mrconso_file, "r", encoding="utf-8") as infile:
        for line in infile:
            fields = line.strip().split("|")
            valid_cuis.add(fields[0])  # CUI is the 1st column (index 0)
    
    with open(mrsty_file, "r", encoding="utf-8") as infile, \
         open(filtered_mrsty_file, "w", encoding="utf-8") as outfile:
        for line in infile:
            fields = line.strip().split("|")
            if fields[0] in valid_cuis:  # CUI is the 1st column (index 0)
                outfile.write(line)
    print("Filtered MRSTY.RRF written to:", filtered_mrsty_file)


# Example usage
umls_dir = "."  # Replace with your UMLS directory
output_dir = "UMLS"     # Directory to save the filtered files
source_vocabularies = ['ICD10CM', 'ICD9CM', 'MTHSPL', 'LNC', 'ICD10PCS', 'CDCREC', 'MTHCMSFRF', 'SOP', 'ATC', 'NUCCHCPT', 'RxNorm', 'CPT', 'SNOMED', 'HCPCS', 'MTHICD9']  # Add your source vocabularies here

filter_umls_files(umls_dir, output_dir, source_vocabularies)
