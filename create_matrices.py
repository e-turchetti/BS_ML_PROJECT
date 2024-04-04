import deepface1.deepface.DeepFace as DeepFace
import deepface1.deepface.commons.functions as functions
import deepface1.deepface.commons.distance as dst
import json
import deepface1.deepface.detectors.FaceDetector as FaceDetector
import argparse
import sys
import time
import os


models = [
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

distance_metrics=[
    "cosine",
    "euclidean",
    "euclidean_l2"
]

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help="Dataset name",choices=["TUTFS","KDEF_cleaned","KDEF_cleaned_complete",],required=True)
parser.add_argument("-dc", "--cosine", help="Evaluate with cosine distance ", action="store_true")
parser.add_argument("-de", "--euclidean", help="Evaluate with euclidean distance ", action="store_true")
parser.add_argument("-del2", "--euclidean_l2", help="Evaluate with euclidean_l2 distance", action="store_true")
parser.add_argument("-m", "--model_name", help="Model Name", type=str,required=True)
parser.add_argument("-b", "--begin", help="Line of input file to begin from", type=int, default = 0)
args = parser.parse_args()
args_str = " ".join(sys.argv)

dataset_name = args.input
print(dataset_name)
# models
if args.model_name not in models:
    raise Exception("Invalid model")


path='representations/'+dataset_name+"/"+args.model_name+"/representations_complete_no_face.json"
isExist = os.path.exists(path)
if not isExist:
    raise Exception("Image representations from dataset "+dataset_name+" were not found for model "+args.model_name)
print(args.model_name)

#metrics
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


#begin and limit and open file
with open(path) as json_file:
   lines = json.load(json_file)
 

if args.begin < 0:
    raise ValueError("Line of input file to begin from should be greater or equal than 0")

if args.begin > len(lines.keys()):
    raise ValueError("Line of input file to begin from is greater than the length of the dataset")

if args.begin >0:

        # Trova le chiavi dei primi due elementi
    first_keys = list(lines.keys())[:int(args.begin)]

    # Creare un nuovo dizionario escludendo i primi due elementi
    lines = {k: v for k, v in lines.items() if k not in first_keys}

start_line_num=args.begin
start_line_name=list(lines.keys())[0]
    
matrix_dim=(len(lines.keys())**2 - len(lines.keys()))/2
print("Matrix dimension: "+str(int(matrix_dim)))
matrices_num=len(distance_metrics)
print("Number of matrices: "+str(matrices_num))
total_combinations=matrices_num*matrix_dim
print("Total combinations: "+str(int(total_combinations)))



matrix=dict()
errors=[]

start_time = time.time()
count_comb=0
for distance_metric in distance_metrics:

    path = "matrices/"+dataset_name+"/"+args.model_name+"/"+distance_metric
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
    print('Remaining combinations: '+str(matrices_num-count_comb))
    print('Remaining total comparisons: '+str(int(total_combinations-count_comb*matrix_dim)))
    count_comb+=1
    print(str(count_comb)+' Current: Model='+args.model_name+' , Distance='+distance_metric)

    matrix[distance_metric]=dict()  
    count=0
    count2=1
    for first_sample in lines.items():
        
        first_keys = list(lines.keys())[:count2]

    # Creare un nuovo dizionario escludendo i primi due elementi
        for second_sample in {k: v for k, v in lines.items() if k not in first_keys}.items():   
                try:
                    distances=[]
                    for x in first_sample[1]:
                        for y in second_sample[1]:
                            
                            if distance_metric == "cosine":
                                distance = dst.findCosineDistance(x, y)
                            elif distance_metric == "euclidean":
                                distance = dst.findEuclideanDistance(x,y)
                            elif distance_metric == "euclidean_l2":
                                distance = dst.findEuclideanDistance(
                                    dst.l2_normalize(x), dst.l2_normalize(y)
                                )
                            else:
                                raise ValueError("Invalid distance_metric passed - ", distance_metric)

                            distances.append(distance)

                    # -------------------------------
                    distance = min(distances)  # best distance
                    matrix[distance_metric][first_sample[0]+' , '+second_sample[0]]=distance


                except Exception as e:
                        print(e, first_sample, second_sample)
                        
                        errors.append({
                            "error": str(e),
                            "sample1_path": first_sample,
                            "sample2_path": second_sample,
                        })
                        continue
                count+=1
                if count%1==0:
                    print(str(count)+' comparisons of current combination Model='+args.model_name+' , Distance='+distance_metric+' done. ')
                    print('Remaining: '+ str(int(matrix_dim-count)))
        count2+=1
    with open(path+"/"+"matrix_complete_no_face"+str(start_line_num)+"_"+".json", "w") as output_log:
            output_log.write(json.dumps(matrix[distance_metric],indent=0))
            output_log.close()
    with open(path+"/"+"errors_complete_no_face"+str(start_line_num)+"_"+".txt", "w") as output_log:
        output_log.write(json.dumps(errors))
        output_log.close()

end_time = time.time()
print("Total execution time (s)       : ", end_time - start_time)









