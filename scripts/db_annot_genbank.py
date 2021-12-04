from Bio import SeqIO
import json
import os

gb = "/mnt_sdc/operons/16Sref/bacteria.16SrRNA.gbff"

dict_db = {}
for seq_record in SeqIO.parse(gb, "genbank"):
    results = []
    result = {}
    result["Rank"] = "species"
    result["ScientificName"] = seq_record.description.split("16S")[0]
    results.append(result)
    result = {}
    result["Rank"] = "genus"
    result["ScientificName"] = seq_record.annotations["taxonomy"][-1]
    results.append(result)
    
    newdict = {"LineageEx" : results}
    dict_db[seq_record.id] = newdict
    
#store dictionary of taxa results as json
json_path = os.path.splitext(gb)[0]+".json"
try:
    with open(json_path, 'w') as f:
        json.dump(dict_db, f)
    print(len(dict_db),"entries successfully written at",json_path)
except Exception as e:
    print(str(e)+"Error: failed to store as json at path:",json_path)
