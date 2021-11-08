import gzip #for opening gz
import re #for regex search
from Bio import SeqIO #load large fasta efficiently

def create_aeros-db(path):
    db = {}
    
    handle = gzip.open(path, "rt")            
    for record in SeqIO.parse(handle, "fasta"):
        fa = str(record.seq)
                
        #flag for telling if operon was found on template strand
        found = False
                
        #skip if contig is shorter than 3000
        if len(fa)>3000:
                    
            #split on primer sequence
            after_primer_temp = re.split("AG[A,G]GTTTGAT[C,T][A,C,T]TGGCTCAG", fa)
            if len(after_primer_temp)>1:                        
                #in the second sequence, i.e. sequence after primer sequence
                #search for the second primer
                for subseq in after_primer_temp[1:]:    
                    final = re.split("AGTTT[A,G,T]ACTGGGG[C,T]GGT", subseq)
                            
                    #store sequence as operon sequence only in these cases
                    if len(final)>1 and len(final[0])>3000 and len(final[0])<8000:
                        db[str(record.id)] = final[0]
                        found = True
                        break

            #check reverse in case operon for template was not found
            if found is False:
                after_primer_rev = re.split("CTGAGCCA[A,G,T][A,G]ATCAAAC[C,T]CT", fa)
                #in the sequence before, i.e. sequence before primer sequence
                #search for the second primer as it is reverse strand
                if len(after_primer_rev)>1:
                    for subseq in after_primer_rev[:-1]:    
                        final = re.split("ACC[A,G]CCCCAGT[A,C,T]AAACT", subseq)
                        if len(final)>1 and len(final[-1])>3000 and len(final[-1])<8000:
                            db[str(record.id)] = final[-1]
                            break        
    handle.close()
    
    #store operon sequences 
    with open("aeros-db.fa","w") as f:
        for i in db:
            f.write(">"+i+"\n")
            f.write(db[i])
            f.write("\n")  

#call the function
create_aeros-db("freeze12.contigs.representatives.fasta.gz")
