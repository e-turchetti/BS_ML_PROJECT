import deepface1.deepface.DeepFace as DeepFace
import deepface1.deepface.commons.functions as functions
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

inputs= [
    "TUTFS_list_files.txt",
    "KDEF_cleaned_list_files.txt"
]


parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help="File containing the dataset's file paths",choices=["TUTFS_list_files.txt","KDEF_cleaned_list_files.txt","d_test_list_files.txt","TUTFS_list_files2.txt","test.txt"],required=True)
parser.add_argument("-m", "--models-mask", help="Binary mask to decide what models to use for evaluation.", type=str,required=True)
parser.add_argument("-b", "--begin", help="Line of input file to begin from", type=int, default = 0)
parser.add_argument("-l", "--limit", help="Whether to limit the  paths list to a certain length", type=int)
args = parser.parse_args()
args_str = " ".join(sys.argv)


dataset_name = args.input.split('_list_')[0]
print('Dataset: '+ dataset_name)
# models

if not (set(args.models_mask).issubset({'0', '1'}) and bool(args.models_mask)):
    raise ValueError("Provided models mask is not binary")

if len(args.models_mask) != len(models):
    raise ValueError("Provided models mask is not complete. The length of the mask should be 9.")

models_dict = {}

for (i, j) in enumerate(models):
    if args.models_mask[i] == "1": 
        models_dict[j] = DeepFace.build_model(j)
        print((i, j))

#begin and limit and open file
with open(args.input) as file:
    lines = file.readlines()

if args.begin < 0:
    raise ValueError("Line of input file to begin from should be greater or equal than 0")

if args.begin > len(lines):
    raise ValueError("Line of input file to begin from is greater than the length of the dataset")

lines = lines[args.begin : ]
lines = [line.rstrip() for line in lines]
start_line=str(args.begin)
if args.limit is not None:
    if args.limit > len(lines):
        end_line=str(args.begin+len(lines)-1)
    else: end_line=str(args.begin+args.limit-1)
    lines = lines[ : args.limit]
else:
    end_line=str(args.begin+len(lines)-1) 
    

print('Number of rapresentations: '+str(len(lines)))



enforce_detection=False
detector_backend="opencv"
align=True
normalization="base"

face_detector=FaceDetector.build_model(detector_backend)
representations=dict()
representations_noface=dict()
errors=[]

start_time = time.time()
count_comb=0
for model_name in models_dict.keys():
    representations[model_name]=dict()
    representations_noface[model_name]=dict()

    path = "representations/"+dataset_name+"/"+model_name
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
    print('Current: Model='+model_name)
    count=0
    for line in lines:
        try:
            # --------------------------------
            target_size = functions.find_target_size(model_name=model_name)

            # img pairs might have many faces
            img1_objs,face_detected = functions.extract_faces(
                img=line,
                face_detector=face_detector,
                target_size=target_size,
                detector_backend='skip',
                grayscale=False,
                enforce_detection=enforce_detection,
                align=align,
            )

            #if face_detected:
            representations[model_name][line]=[]
            #else: 
                #representations_noface[model_name][line]=[]

            for img1_content, img1_region, _ in img1_objs:
                    img1_embedding_obj = DeepFace.represent(
                        img_path=img1_content,
                        model=models_dict[model_name],
                        model_name=model_name,
                        enforce_detection=enforce_detection,
                        detector_backend="skip",
                        align=align,
                        normalization=normalization,
                    )

                    img1_representation = img1_embedding_obj[0]["embedding"]
                    #break
            # -------------------------------
                    #if face_detected:
                    representations[model_name][line].append(img1_representation)
                    #else:
                        #representations_noface[model_name][line].append(img1_representation)
        except Exception as e:
                print(e, line)

                errors.append({
                    "error": str(e),
                    "sample_path": line,
                })
                continue
        count+=1
        if count%1==0:
            print(str(count)+' rapresentations of current Model='+model_name+' done. ')
            print('Remaining: '+ str(int(len(lines)-count)))

        #if face_detected:
    with open(path+"/"+"representations_complete_no_face"+".json", "w") as output_log:
            output_log.write(json.dumps(representations[model_name],indent=0))
            output_log.close()
    with open(path+"/"+"errors_complete_no_face"+".txt", "w") as output_log:
            output_log.write(json.dumps(errors))
            output_log.close()
    '''
        else:
            with open(path+"/"+"representations_no_face"+".json", "w") as output_log:
                output_log.write(json.dumps(representations_noface[model_name],indent=0))
                output_log.close()
            with open(path+"/"+"errors_no_face"+".txt", "w") as output_log:
                output_log.write(json.dumps(errors))
                output_log.close()
    '''
end_time = time.time()
print("Total execution time (s)       : ", end_time - start_time)
