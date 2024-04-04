import argparse
import json
import math
import sys
import numpy as np
import os

models_list = [
  "VGG-Face", 
  "Facenet", 
  "Facenet512", 
  "OpenFace", 
  "DeepFace", 
  "DeepID", 
   "Dlib", 
  "ArcFace", 
  "SFace",
]



parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help="Dataset name",choices=["TUTFS","KDEF_cleaned","KDEF_cleaned_complete",],required=True)
parser.add_argument("-nt", "--num_thresholds", help="Number of thresholds to test", type=int,required=True)
parser.add_argument("-dc", "--cosine", help="Test with the cosine distance metric", action="store_true")
parser.add_argument("-de", "--euclidean", help="Test with the euclidean distance metric", action="store_true")
parser.add_argument("-del2", "--euclidean_l2", help="Test with the euclidean_l2 distance metric", action="store_true")
parser.add_argument("-m", "--models-mask", help="Binary mask to decide what Deep Learning models to use for face verification", type=str,required=True)
args = parser.parse_args()
args_str = " ".join(sys.argv)

if not os.path.exists("results"):
    os.makedirs("results")

dataset_name = args.input
print(dataset_name)

if not (set(args.models_mask).issubset({'0', '1'}) and bool(args.models_mask)):
    raise ValueError("Provided models mask is not binary")

if len(args.models_mask) != len(models_list):
    raise ValueError("Provided models mask is not complete. The length of the mask should be 9.")


models=[]

for (i, j) in enumerate(models_list):
    if args.models_mask[i] == "1": 
        models.append(j)

print(models)

distance_metrics = []
if args.cosine:
    distance_metrics.append("cosine")
if args.euclidean:
    distance_metrics.append("euclidean")
if args.euclidean_l2:
    distance_metrics.append("euclidean_l2")
if distance_metrics==[]:
    print("Distance metrics not provided, default to euclidean distance metric")
    distance_metrics.append('euclidean')

print(distance_metrics)

path_max_distances="max_distances_complete_no_face.json"
with open(path_max_distances, 'r') as f:
    max_distances = json.load(f)



for model in models:
    path_model="results/"+dataset_name+"/"+model
    if not os.path.exists(path_model):
        os.makedirs(path_model) 
    for metric in distance_metrics:
        path_metric="results/"+dataset_name+"/"+model+"/"+metric
        if not os.path.exists(path_metric):
            os.makedirs(path_metric)
        max_distance=math.ceil(max_distances[dataset_name][model][metric]*100)/100
        thresholds=np.linspace(0,max_distance,args.num_thresholds)
        path_matrix="matrices/"+dataset_name+"/"+model+"/"+metric+"/matrix_complete_no_face0_.json"
        with open(path_matrix, 'r') as f:
            lines = json.load(f)
        genuine_acceptances = dict()
        genuine_rejections = dict()
        false_acceptances = dict()
        false_rejections = dict()

        genuine_acceptance_rate = dict()
        genuine_rejection_rate = dict()
        false_acceptance_rate = dict()
        false_rejection_rate = dict()
        count=0
        for threshold in thresholds:
            count+=1
            print(str(count)+": "+str(threshold))
            genuine_attempts = 0
            impostor_attempts = 0
            
            genuine_acceptances[threshold]=0
            genuine_rejections[threshold]=0
            false_acceptances[threshold]=0
            false_rejections[threshold]=0
            

            for key,value in lines.items():
                key=key.split(" , ")
                identity_first=key[0].split("/")[1]
                identity_second=key[1].split("/")[1]
                if value <= threshold:
                    if identity_first==identity_second:
                        genuine_attempts+=1
                        genuine_acceptances[threshold]+=1
                    else:
                        impostor_attempts+=1 
                        false_acceptances[threshold]+=1
                else:
                    if identity_first==identity_second:
                        genuine_attempts+=1
                        false_rejections[threshold]+=1
                    else: 
                        impostor_attempts+=1
                        genuine_rejections[threshold]+=1

            genuine_acceptance_rate[threshold]=genuine_acceptances[threshold]/genuine_attempts
            genuine_rejection_rate[threshold]=genuine_rejections[threshold]/impostor_attempts
            false_acceptance_rate[threshold]=false_acceptances[threshold]/impostor_attempts
            false_rejection_rate[threshold]=false_rejections[threshold]/genuine_attempts

        results = {
            "genuine_acceptances": genuine_acceptances,
            "genuine_rejections": genuine_rejections,
            "false_acceptances": false_acceptances,
            "false_rejections": false_rejections,
            "genuine_acceptance_rate": genuine_acceptance_rate,
            "genuine_rejection_rate": genuine_rejection_rate,
            "false_acceptance_rate": false_acceptance_rate,
            "false_rejection_rate": false_rejection_rate,
            "genuine_attempts": genuine_attempts,
            "impostor_attempts": impostor_attempts,
            "args": args_str
        }

        with open(path_metric+"/"+"results_complete_no_face_"+dataset_name+"_"+model+"_"+metric+"_"+str(args.num_thresholds)+".json", "w") as output_log:
            output_log.write(json.dumps(results,indent=1))
            output_log.close()