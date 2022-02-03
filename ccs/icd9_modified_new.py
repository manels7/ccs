import os
import re
import pandas as pd
from toolz.dicttoolz import merge

import json

def _get_icd9_codes(filename, code_type):
    assert code_type in ['dx', 'px']
    file_path = os.path.join("./resources/", filename)
    # file_path = os.path.join("./resources/", 'ccs_multi_dx_tool_2015.csv')
    df = pd.read_csv(file_path)

    #To be able to access the dataframe columns more easily. Procedures have 3 CCS levels and Diagnosis have 4 levels
    if code_type == 'dx':
        df = df.rename(columns={"'ICD-9-CM CODE'": "ICD9", "'CCS LVL 1'": "CCS1", "'CCS LVL 1 LABEL'": "CCS1LABEL", "'CCS LVL 2'": "CCS2",
            "'CCS LVL 2 LABEL'": "CCS2LABEL", "'CCS LVL 3'": "CCS3", "'CCS LVL 3 LABEL'": "CCS3LABEL", "'CCS LVL 4'": "CCS4", "'CCS LVL 4 LABEL'": "CCS4LABEL"})
    elif code_type == "px":
        df = df.rename(columns={"'ICD-9-CM CODE'": "ICD9", "'CCS LVL 1'": "CCS1", "'CCS LVL 1 LABEL'": "CCS1LABEL", "'CCS LVL 2'": "CCS2",
            "'CCS LVL 2 LABEL'": "CCS2LABEL", "'CCS LVL 3'": "CCS3", "'CCS LVL 3 LABEL'": "CCS3LABEL",})

    #Regex to find labels with the ccs code at the end which have a structure of [xxx.]
    # regex = re.compile("\[[0-9.]{1,6}\]") # This regex struggles in the case of [259. and 260.] CCS code
    regex = re.compile("\[[0-9]{1,3}.*\]")
    
    icdToCcsMapping = {}
    ccsToDefinitionMapping = {}
    ccsToDefinitionMapping["0"] = ""

    for row in df.itertuples():
        if row.CCS3LABEL.endswith("]"):
            match = regex.search(row.CCS3LABEL)
        elif row.CCS2LABEL.endswith("]"):
            match = regex.search(row.CCS2LABEL)
        elif row.CCS1LABEL.endswith("]"):
            match = regex.search(row.CCS1LABEL)
        # Procedure codes do not have 4 CCS levels but only 3
        elif code_type == "dx":
            if row.CCS4LABEL.endswith("]"):
                match = regex.search(row.CCS4LABEL)

        #If there was a valid match, procede
        if match:
            if code_type == "dx":
                icd9Code = "D_" + row.ICD9[1:-1].strip()
                ccsCode  = "D_" + match.group(0)[1:-2]
                if len(ccsCode) > 5: ccsCode = ccsCode[:5] #If we have the case of [259. and 260], we trim it to simplify have only 259
            elif code_type == "px":
                icd9Code = "P_" + row.ICD9[1:-1].strip()
                ccsCode  = "P_" + match.group(0)[1:-2]

            ccsDefinition = match.string[:match.start()]
            icdToCcsMapping[icd9Code] = ccsCode
            if ccsCode not in ccsToDefinitionMapping.keys():
                ccsToDefinitionMapping[ccsCode] = ccsDefinition

    return icdToCcsMapping, ccsToDefinitionMapping

dx_codes, dx_text_mapping = _get_icd9_codes('ccs_multi_dx_tool_2015.csv', 'dx')
print("Diagnosis file processed")
px_codes, px_text_mapping = _get_icd9_codes('ccs_multi_pr_tool_2015.csv', 'px')
print("Procedures file processed")

with open("output/dx_icdccs_codes.json", "w") as file:
    json.dump(dx_codes, file)
with open("output/px_icdccs_codes.json", "w") as file:
    json.dump(px_codes, file)
with open("output/dx_ccs_text.json", "w") as file:
    json.dump(dx_text_mapping, file)
with open("output/px_ccs_text.json", "w") as file:
    json.dump(px_text_mapping, file)

merged_codes = merge(dx_codes, px_codes)
merged_texts = merge(dx_text_mapping, px_text_mapping)

# with open("output/merged_icdccs_codes.json", "w") as file:
with open("../../../data/extended/preprocessing/ICDandCCSmappings/merged_icdccs_codes.json", "w") as file:
    json.dump(merged_codes, file)
    
# with open("output/merged_ccs_text.json", "w") as file:
with open("../../../data/extended/preprocessing/ICDandCCSmappings/merged_ccs_text.json", "w") as file:
    json.dump(merged_texts, file)
