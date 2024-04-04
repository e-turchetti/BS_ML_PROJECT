from sklearn.metrics import auc
import plotly.express as px
import json
import plotly.graph_objects as go   
import numpy as np 
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
    "TUTFS",
    "KDEF_cleaned",
    "KDEF_cleaned_complete"
]

def plot_roc_curve(dataset,model,metric,thresholds):
    path="results/"+dataset+"/"+model+"/"+metric+"/"+"results_"+dataset+"_"+model+"_"+metric+"_"+str(thresholds)+".json"
    with open(path) as json_file:
        lines = json.load(json_file)
    far=list(lines['false_acceptance_rate'].values())
    gar=list(lines['genuine_acceptance_rate'].values())

    fig = px.area(
    x=far, y=gar,
    title=f'<b>ROC Curve (AUC={auc(far, gar):.4f})</b><br><br><sup>Dataset: <b>{dataset}</b> Model: <b>{model}</b> Metric: <b>{metric}</b> </sup>',
    labels=dict(x='False Acceptance Rate', y='Genuine Acceptance Rate'),
    width=700, height=500,
)
    fig.add_shape(
    type='line', line=dict(dash='dash'),
    x0=0, x1=1, y0=0, y1=1
)
    fig.update_layout( title_x=0.5)

    #fig.update_yaxes(scaleanchor="x", scaleratio=1)
    #fig.update_xaxes(constrain='domain')
    #fig.show()
    fig.write_image("results/"+dataset+"/"+model+"/"+metric+"/"+"roc_curve.png")



def aucs_file(datasets,models,metrics,thresholds):
    d=dict()
    for dataset in datasets:
        d[dataset]=dict()
        for metric in metrics:
            d[dataset][metric]=dict()
            for model in models:
                path="results/"+dataset+"/"+model+"/"+metric+"/"+"results_complete_no_face_"+dataset+"_"+model+"_"+metric+"_"+str(thresholds)+".json"
                with open(path) as json_file:
                    lines = json.load(json_file)
                far=list(lines['false_acceptance_rate'].values())
                gar=list(lines['genuine_acceptance_rate'].values())
                area=auc(far,gar)
                d[dataset][metric][model]=area

    with open("results/aucs_complete_no_face.json", "w") as output_log:
        output_log.write(json.dumps(d,indent=2))
        output_log.close()

#1
'''
for dataset in datasets:
    for model in models:
        for metric in distance_metrics:
            plot_roc_curve(dataset,model,metric,500)
'''
#2
#aucs_file(datasets,models,distance_metrics,500)
def plot_det_curve(dataset,model,metric,thresholds):
    path="results/"+dataset+"/"+model+"/"+metric+"/"+"results_"+dataset+"_"+model+"_"+metric+"_"+str(thresholds)+".json"
    with open(path) as json_file:
        lines = json.load(json_file)
    far=list(lines['false_acceptance_rate'].values())
    frr=list(lines['false_rejection_rate'].values())

    # Creazione della curva
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=far, y=frr, mode='lines', name='DET Curve',marker={'color': 'rgb(94, 191, 174)'}))

    # Impostazioni del layout
    fig.update_layout(
        title=f'<b>DET Curve</b><br><br><sup>Dataset: <b>{dataset}</b> Model: <b>{model}</b> Metric: <b>{metric}</b> </sup>',
        xaxis=dict(title='False Positive Rate (FPR)',type='log',range=[-3.5,0],tickvals=[0.001, 0.01, 0.1,1],tickfont=dict(color=' rgb(40, 80, 70)'),title_font=dict(color=' rgb(40, 80, 70)')),
        yaxis=dict(title='Miss Rate (FNR)',type='log',tickvals=[0.001, 0.01, 0.1,1],tickfont=dict(color=' rgb(40, 80, 70)'),title_font=dict(color='rgb(40, 80, 70)')),
        title_x=0.5,
        width=700, height=500,
        plot_bgcolor='rgba(127, 255, 232,0.2)',
        title_font=dict(color=' rgb(40, 80, 70)')
        
    )


    # Visualizza il grafico
    #fig.write_image("results/"+dataset+"/"+model+"/"+metric+"/"+"det_curve.png")
    fig.show()


def plot_far_frr_curves(dataset, model, metric, thresholds):
    path="results/"+dataset+"/"+model+"/"+metric+"/"+"results_no_face_"+dataset+"_"+model+"_"+metric+"_"+str(thresholds)+".json"
    with open(path) as json_file:
        lines = json.load(json_file)
    far=list(lines['false_acceptance_rate'].values())
    thr=list(lines['false_acceptance_rate'].keys())
    thr = [eval(i) for i in thr]
    frr=list(lines['false_rejection_rate'].values())


    # Calculate Equal Error Rate (EER)
    eer = None
    eer_threshold = None
    min_diff = float('inf')
    for i in range(len(thr)):
        diff = abs(far[i] - frr[i])
        if diff < min_diff:
            min_diff = diff
            eer = (far[i] + frr[i]) / 2
            eer_threshold = thr[i]

    print(eer_threshold)

    # Create the plot
    fig = go.Figure()

    # Plot FAR curve
    fig.add_trace(go.Scatter(x=thr, y=far, mode='lines', name='False Acceptance Rate', line=dict(color='rgb(130, 82, 200)')))
    
    # Plot FRR curve
    fig.add_trace(go.Scatter(x=thr, y=frr, mode='lines', name='False Rejection Rate', line=dict(color='rgb(255, 102, 178)')))



    # Plot EER point
    if eer_threshold is not None:
        fig.add_trace(go.Scatter(x=[eer_threshold], y=[eer], mode='markers', name='EER', marker=dict(color='rgb(51, 0, 55)', size=10)))
        fig.add_trace(go.Scatter(y=[eer, eer], x=[0, eer_threshold], mode='lines', name='EER Line', line=dict(color='rgb(51, 0, 55)', width=1, dash='dot'),showlegend = False))  
        fig.add_trace(go.Scatter(x=[eer_threshold, eer_threshold], y=[0, eer], mode='lines', name='EER Line', line=dict(color='rgb(51, 0, 55)', width=1, dash='dot'),showlegend = False))    # Layout settings
    #eer_threshold=f'<b>{eer_threshold}/b>'
    fig.update_layout(
        title=f'<b>FAR and FRR Curves with EER</b><br><br><sup>Dataset: <b>{dataset}</b> Model: <b>{model}</b> Metric: <b>{metric}</b> </sup>',
        xaxis=dict(title='Thresholds',tickvals=[min(thr),eer_threshold,max(thr)],tickfont=dict(color='rgb(55, 0, 61)'),title_font=dict(color='rgb(55, 0, 61)')),
        yaxis=dict(title='Rate',range=[0,1],tickvals=[0,0.2,0.4,eer,0.6,0.8,1],tickfont=dict(color='rgb(55, 0, 61)'),title_font=dict(color='rgb(55, 0, 61)')),
        title_x=0.2,
        width=700, height=500,
        plot_bgcolor='rgba(230, 204, 255,0.15)',
        title_font=dict(color='rgb(55, 0, 61)')
    )

    # Show the plot
    #fig.show()
    fig.write_image("results/"+dataset+"/"+model+"/"+metric+"/"+"far_frr_no_face_curve.png")


def eer_file(datasets,models,metrics,thresholds):
    d=dict()
    for dataset in datasets:
        d[dataset]=dict()
        for metric in metrics:
            d[dataset][metric]=dict()
            for model in models:
                d[dataset][metric][model]=dict()
                path="results/"+dataset+"/"+model+"/"+metric+"/"+"results_complete_no_face_"+dataset+"_"+model+"_"+metric+"_"+str(thresholds)+".json"
                with open(path) as json_file:
                    lines = json.load(json_file)
                far=list(lines['false_acceptance_rate'].values())
                thr=list(lines['false_acceptance_rate'].keys())
                thr = [eval(i) for i in thr]
                frr=list(lines['false_rejection_rate'].values())
                eer = None
                eer_threshold = None
                min_diff = float('inf')
                for i in range(len(thr)):
                    diff = abs(far[i] - frr[i])
                    if diff < min_diff:
                        min_diff = diff
                        eer = (far[i] + frr[i]) / 2
                        eer_threshold = thr[i]
                d[dataset][metric][model]['threshold']=eer_threshold
                d[dataset][metric][model]['eer']=eer

    with open("results/eer_complete_no_face.json", "w") as output_log:
        output_log.write(json.dumps(d,indent=3))
        output_log.close()

#eer_file(datasets,models,distance_metrics,500)


dataset='KDEF_cleaned_complete'
metric='euclidean'


def plot_det_curve1(dataset,metric,thresholds,models):
    fig = go.Figure()
    for model in models:
        path="results/"+dataset+"/"+model+"/"+metric+"/"+"results_"+dataset+"_"+model+"_"+metric+"_"+str(thresholds)+".json"
        with open(path) as json_file:
            lines = json.load(json_file)
        far=list(lines['false_acceptance_rate'].values())
        frr=list(lines['false_rejection_rate'].values())

    # Creazione della curva

        fig.add_trace(go.Scatter(x=far, y=frr, mode='lines', name=model,marker={'color': 'rgb(94, 191, 174)'}))

    # Impostazioni del layout
    fig.update_layout(
        title=f'<b>DET Curve</b><br><br><sup>Dataset: <b>{dataset}</b> Model: <b>{model}</b> Metric: <b>{metric}</b> </sup>',
        xaxis=dict(title='False Positive Rate (FPR)',type='log',range=[-3.5,0],tickvals=[0.001, 0.01, 0.1,1],tickfont=dict(color=' rgb(40, 80, 70)'),title_font=dict(color=' rgb(40, 80, 70)')),
        yaxis=dict(title='Miss Rate (FNR)',type='log',tickvals=[0.001, 0.01, 0.1,1],tickfont=dict(color=' rgb(40, 80, 70)'),title_font=dict(color='rgb(40, 80, 70)')),
        title_x=0.5,
        width=700, height=500,
        plot_bgcolor='rgba(127, 255, 232,0.2)',
        title_font=dict(color=' rgb(40, 80, 70)')
        
    )


    # Visualizza il grafico
    #fig.write_image("results/"+dataset+"/"+model+"/"+metric+"/"+"det_curve.png")
    fig.show()

datasets=['KDEF_cleaned']
eer_file(datasets,models,distance_metrics,500)