# from clinvoc.icd9 import ICD9PCS, ICD9CM
#from . import resources
import os
import re
from clinvoc.icd9 import ICD9CM, ICD9PCS
import pandas as pd
from toolz.dicttoolz import merge

import pickle

# '''
# Single category parsing
# '''
icd9cm_vocab = ICD9CM(use_decimals=False)
icd9pcs_vocab = ICD9PCS(use_decimals=False)

def _get_icd9_codes(filename, code_type):
    assert code_type in ['dx', 'px']
    vocab = icd9cm_vocab if code_type == 'dx' else icd9pcs_vocab
    file_path = os.path.join("./resources/", filename)
    df = pd.read_csv(file_path)
    code_column = df.columns[0]
    
    result = {}
    for item, row in df.iterrows():
        key = (re.sub('\[[^\]]*\]', '', row[0]).strip(), re.sub('\[[^\]]*\]', '', row[3]).strip())
        icd9, ccs = key
        #print(icd9, ccs)
        if code_type == "dx": icd9 = "D" +  icd9.replace("\'","")
        elif code_type == "px": icd9 = "P" + icd9.replace("\'","")
        
        while (len(icd9)<6): icd9 += " "
        
        ccs = ccs.replace(".","").replace("\'","")
        while (len(ccs)<6): ccs += " "
       # print(icd9, ccs)
        
        #key = (re.sub('\[[^\]]*\]', '', row[2]).strip(), re.sub('\[[^\]]*\]', '', row[4]).strip(), re.sub('\[[^\]]*\]', '', row[6]).strip(), vocab.vocab_domain, vocab.vocab_name)
#         if not key[2]:
#             key = key[:2] + key[1:2] + key[3:]
        #if icd9 not in result:
        #    result[icd9] = set()
        result[icd9] = ccs
    return result

dx_code_sets_dict = _get_icd9_codes('ccs_multi_dx_tool_2015.csv', 'dx')
print("Diagnosis file processed")
px_code_sets_dict = _get_icd9_codes('ccs_multi_pr_tool_2015.csv', 'px')
print("Procedures file processed")
code_sets_dict = merge(dx_code_sets_dict, px_code_sets_dict)

with open('icd9_to_ccs_dict.pkl', 'wb') as pickle_file:
    pickle.dump(code_sets_dict, pickle_file)
