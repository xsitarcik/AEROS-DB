from Bio import Entrez,SeqIO
import json
import re
import os

def add_taxa(db_path):  
    newdict = {}
    ids, full_ids = [], []
    
    #prepare list of taxonomy ids for querying NCBI
    with open(db_path,"r") as handle:
        for record in SeqIO.parse(handle, "fasta"):
            ids.append(str(record.id).split(".")[0])
            full_ids.append(str(record.id))

    Entrez.email = "sitarcik7@uniba.sk"
    start = 0

    #query NCBI DB in batches of 10,000 
    while start+10000<len(full_ids):
        used_ids = ids[start:start+10000]
        used_full_ids = full_ids[start:start+10000]
        handle = Entrez.efetch(db="taxonomy", id=used_ids, retmode="xml")
        record = Entrez.read(handle)
        handle.close()
        idx = 0
        
        #store results in dictionary
        for org in used_full_ids:
            newdict[org]=record[idx]
            idx = idx + 1
        start = start + 10000
    
    used_ids = ids[start:]
    used_full_ids = full_ids[start:]
    handle = Entrez.efetch(db="taxonomy", id=used_ids, retmode="xml")
    record = Entrez.read(handle)
    handle.close()
    idx = 0
    for org in used_full_ids:
        newdict[org]=record[idx]
        idx = idx + 1
    
    #store dictionary of taxa results as json
    jsonpath = os.path.splitext(path)[0]+".json"
    try:
        with open(jsonpath, 'w') as f:
            json.dump(newdict, f)
        print(len(newdict),"entries successfully written at",jsonpath)
    except:
        print("Error: failed to store as json at path:",jsonpath)

#call the function
add_taxa("aeros-db.fa")
