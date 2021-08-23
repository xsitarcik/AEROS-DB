import pandas as pd
import json
import os
import numpy as np
import argparse
import gzip

#loads taxonomy information for the database
def load_db(path):
    with gzip.open(path, 'rb') as f:
    	db_dict = json.load(f)
    return db_dict

#returns taxonomy frequency counts from input reads
def classify_reads(pafs,out_path,db,MIN_LENGTH,MIN_SCORE_PERCENTILE,rank):
    #in: pafs – path to files in .paf format
    #in: db – taxonomy information corresponding to the database used
    #in: MIN_LENGTH – alignments lower than this are filtered out
    #in: MIN_SCORE_PERCENTILE – the minimum percentile for alignment score
    #in: rank – string denoting the classification level

    dicts = []
    colnames_rename = {}
    idx = 0
    for f in pafs:
        colnames_rename[idx] = f.split("/")[-1].split(".")[0]
        idx = idx + 1
        df = pd.read_csv(f,sep='\t',header=None,usecols=[0,1,5,10,14])
        df.rename(columns = {0:"Query name",1:'Query len', 5:'SEQID',
                                  10:'Alignment block',14:"as tag"}, inplace = True)
        df["grscore"] = [float(i.split(":")[2]) for i in df["as tag"].values]
        df["score"] = df["grscore"]/df['Query len']
        
        #get taxonomy information using loaded dict
        df["type"] = [parse_dicts(db[i],rank) for i in df["SEQID"].values]
        df = df.drop(["as tag","SEQID"], axis = 1)
        df = df.sort_values("score").drop_duplicates('Query name', keep='last')
	  
	  #filtering of mapping outputs
        filtered = df[df["Alignment block"] > MIN_LENGTH]
        MIN_SCORE = np.percentile(filtered["score"].values,MIN_SCORE_PERCENTILE)
        filtered = filtered[filtered["score"] > MIN_SCORE]
        out = (filtered["type"].value_counts()/len(filtered["type"])*100).sort_values(ascending=False).to_dict()
        dicts.append(out)
    df = pd.DataFrame.from_dict(dicts).transpose()
    df = df.rename(columns = colnames_rename)
    df = df[sorted(df.columns)]

    if out_path is not None:
    	df.to_csv(out_path, index = True, header=True)
    else:
    	display(df)

# parse_taxonomy information according to used classification level
def parse_dicts(dicts,rank):
    out = ""
    for a in dicts["LineageEx"]:
        if a['Rank']==rank:
            out = a["ScientificName"]
    if out == "":
        return dicts["ScientificName"]
    else:
        return out

def load_args():
    """
    Parses input args and returns parsed config
    """
    
    try:
        parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description="operons-db-use")
        parser.add_argument('-p','--pafs_list', nargs='+', dest='pafs_list', required=True, help='path to PAF file(s)')
        parser.add_argument('-r','--rank', dest='rank', required=True, help='lineage rank used for classification')
        parser.add_argument('-o','--output', dest='out_path', default=None, help='path where to store output')
        parser.add_argument('-m','--min_length', dest='min_length', default=2999, help='Minimum aligned block length to use')
        parser.add_argument('-s','--min_score', dest='min_score', default=80, help='Percentage of the best aligned reads to use')
        args = parser.parse_args()
    except argparse.ArgumentTypeError as e:
        print("Error when parsing input",e.message)
        exit(-1)
                
    return args

#load input args
args = load_args()

#load DB and assign taxonomy
print("Assigning taxonomy with the following settings:")
print("Minimum aligned block length:",args.min_length)
print("Percentage of the best aligned reads used for taxonomy:",args.min_score)

db_dict = load_db("progenome_db.json.gz")
classify_reads(args.pafs_list,args.out_path,db_dict,args.min_length,args.min_score,args.rank)


