import pandas as pd, pickle, numpy as np
from sklearn.metrics import confusion_matrix, accuracy_score

test=pd.read_csv(r"C:\Users\ASUS\Documents\suryaghar\ml_dataset_test_enriched_v2.csv")
model_data=pickle.load(open(r"C:\Users\ASUS\Documents\suryaghar\suryagrid_model_v2.pkl","rb"))
model=model_data['model']
X_test=test[model_data['input_features']]
y_test=test['label']
proba=model.predict_proba(X_test)
classes=list(model.classes_)
# map class index
idx_safe=classes.index('SAFE')
idx_caution=classes.index('CAUTION')
idx_constr=classes.index('CONSTRAINED')
print(f"Classes {classes}")

# Evaluate thresholds for CONSTRAINED: predict CONSTR if prob_constr > thr, else argmax among remaining
thresholds=[0.2,0.25,0.3,0.35,0.4,0.45,0.5,0.6]
for thr in thresholds:
    preds=[]
    for p in proba:
        if p[idx_constr] > thr:
            preds.append('CONSTRAINED')
        else:
            # choose max among SAFE and CAUTION
            if p[idx_safe] > p[idx_caution]:
                preds.append('SAFE')
            else:
                preds.append('CAUTION')
    # compute metrics
    from sklearn.metrics import accuracy_score, recall_score, precision_score
    acc=accuracy_score(y_test, preds)
    # false SAFE: true CONSTR pred SAFE
    false_safe=sum((y_test=='CONSTRAINED') & (pd.Series(preds)=='SAFE'))
    false_constr=sum((y_test=='SAFE') & (pd.Series(preds)=='CONSTRAINED'))
    # recall CONSTR
    # confusion
    # also compute
    total_constr=sum(y_test=='CONSTRAINED')
    total_safe=sum(y_test=='SAFE')
    print(f"thr {thr:.2f} acc {acc:.3f} falseSAFE {false_safe}/{total_constr}={false_safe/total_constr:.3f} falseCONSTR {false_constr}/{total_safe}={false_constr/total_safe:.3f} ")

# Default argmax already has implicit thr ~0.33, but we show trade-off
# Also check current model false safe at default is 0
print("\nDefault argmax false SAFE", sum((y_test=='CONSTRAINED') & (pd.Series(model.predict(X_test))=='SAFE')))

# Also evaluate on old model for comparison
old_data=pickle.load(open(r"C:\Users\ASUS\Documents\suryaghar\suryagrid_model.pkl","rb"))
old_model=old_data['model']
# Old test is different split (225) but we can evaluate on same enriched test's old features subset
# For old model, need old features
old_test=pd.read_csv(r"C:\Users\ASUS\Documents\suryaghar\ml_dataset_test.csv")
X_old=old_test[old_data['input_features']]
y_old=old_test['label']
proba_old=old_model.predict_proba(X_old)
for thr in thresholds:
    preds=[]
    for p in proba_old:
        if p[list(old_model.classes_).index('CONSTRAINED')] > thr:
            preds.append('CONSTRAINED')
        else:
            # choose max among other two
            idx_s=list(old_model.classes_).index('SAFE')
            idx_c=list(old_model.classes_).index('CAUTION')
            preds.append('SAFE' if p[idx_s]>p[idx_c] else 'CAUTION')
    false_safe=sum((y_old=='CONSTRAINED') & (pd.Series(preds)=='SAFE'))
    print(f"OLD thr {thr:.2f} falseSAFE {false_safe}/{sum(y_old=='CONSTRAINED')}")

print("Done")
