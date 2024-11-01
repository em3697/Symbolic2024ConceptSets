# Symbolic2024ConceptSets README

##ConceptSets_EdgeCases

*This file contains edge case tests to compare performance of the CODER method to the PHOEBE benchmark.*
- PHOEBE_dialysisCKD_all.csv: file contains all terms returned from an exhaustive search of "dialysis of CKD" in Atlas/Phoebe
- PHOEBE_glucose_all.csv: file contains all terms returned from and exhaustive search of "blood glucose" in Atlas/Phoebe
- dialysis_edge_cases.csv: File contains all clinically relevent terms to "dialysis of CKD" that are not returned by PHOEBE.
  - This file in specific focuses on codes of procecedures inherently related to input term i.e. cannula, av shunt, fistula, catheter
  - This file contains the edge cases the goal is to cover
- glucose_concept_codes_athena.csv: file contains all relevent concept codes realted to "blood glucose"
  - file contains overlap with the PHOEBE_glucose_all.csv file
-glucose_edge_cases.csv: File contains all clinically relevent terms to "dialysis of CKD" that are not returned by PHOEBE.
  - This file in specific focuses on codes testing inherently related to hyperglycemia/blood glucose
  - This file contains the edge cases
