import json
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

datasets=[
    #"TUTFS",
    "KDEF_cleaned"
    #"KDEF_cleaned_complete"
]
d=dict()
for dataset in datasets:
    d[dataset]=dict()
    for model in models:
        d[dataset][model]=dict()
        for metric in distance_metrics:
            path="matrices/"+dataset+"/"+model+"/"+metric+"/"+"matrix_complete_no_face0_.json"
            with open(path) as json_file:
                lines = json.load(json_file)
            values=list(lines.values())
            m=max(values)
            d[dataset][model][metric]=m
with open("max_distances_complete_no_face.json", "a") as output_log:
    output_log.write(json.dumps(d,indent=2))
    output_log.close()
