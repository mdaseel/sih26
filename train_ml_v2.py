import pandas as pd, numpy as np, pickle, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score, roc_auc_score
from sklearn.preprocessing import label_binarize

train=pd.read_csv(r"C:\Users\ASUS\Documents\suryaghar\ml_dataset_train_enriched_v2.csv")
val=pd.read_csv(r"C:\Users\ASUS\Documents\suryaghar\ml_dataset_val_enriched_v2.csv")
test=pd.read_csv(r"C:\Users\ASUS\Documents\suryaghar\ml_dataset_test_enriched_v2.csv")

# enriched features
input_features = ["pv_bus","pv_bus_vn_kv","existing_pv_kw","new_pv_kw","total_pv_kw","existing_load_at_bus_kw","pv_penetration_ratio",
                  "transformer_association","feeder_section",
                  "transformer_sn_kva","pv_to_transformer_ratio","new_pv_to_transformer_ratio","load_to_transformer_ratio",
                  "base_voltage_pu","feeder_distance_km","upstream_r_ohm","upstream_x_ohm","upstream_z_ohm"]
cat_features = ["pv_bus","transformer_association","feeder_section"]
num_features = [c for c in input_features if c not in cat_features]

print(f"Train {len(train)} Val {len(val)} Test {len(test)}")
print(f"Features {len(input_features)} cat {len(cat_features)} num {len(num_features)}")

preprocess = ColumnTransformer([
    ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_features),
    ("num", StandardScaler(), num_features)
])

label_order=["SAFE","CAUTION","CONSTRAINED"]

X_train=train[input_features]; y_train=train["label"]
X_val=val[input_features]; y_val=val["label"]
X_test=test[input_features]; y_test=test["label"]

models={
    "LogisticRegression": Pipeline([("prep", preprocess), ("clf", LogisticRegression(max_iter=1000, multi_class="multinomial", solver="lbfgs", class_weight="balanced"))]),
    "RandomForest": Pipeline([("prep", preprocess), ("clf", RandomForestClassifier(n_estimators=300, max_depth=None, random_state=42, class_weight="balanced", n_jobs=-1))]),
    "RandomForest_Balanced": Pipeline([("prep", preprocess), ("clf", RandomForestClassifier(n_estimators=300, max_depth=12, min_samples_leaf=5, random_state=42, class_weight="balanced", n_jobs=-1))]),
}

results={}
best=None; best_f1=0
for name, pipe in models.items():
    pipe.fit(X_train, y_train)
    pred_val=pipe.predict(X_val)
    acc=accuracy_score(y_val, pred_val)
    f1_macro=f1_score(y_val, pred_val, average="macro")
    print(f"\n=== {name} VAL Acc {acc:.4f} F1 {f1_macro:.4f}")
    print(classification_report(y_val, pred_val, digits=3, zero_division=0))
    pred_test=pipe.predict(X_test)
    acc_t=accuracy_score(y_test, pred_test)
    f1_t=f1_score(y_test, pred_test, average="macro")
    print(f"TEST Acc {acc_t:.4f} F1 {f1_t:.4f}")
    print(classification_report(y_test, pred_test, digits=3, zero_division=0))
    cm=confusion_matrix(y_test, pred_test, labels=label_order)
    print(cm)
    # false SAFE
    false_safe = sum((y_test=="CONSTRAINED") & (pred_test=="SAFE"))
    false_safe_rate = false_safe / sum(y_test=="CONSTRAINED") if sum(y_test=="CONSTRAINED")>0 else 0
    print(f"False SAFE {false_safe}/{sum(y_test=='CONSTRAINED')} = {false_safe_rate:.3f}")
    # ROC AUC
    try:
        prob=pipe.predict_proba(X_test)
        # align classes
        # model classes may be alphabetical, need to map to label_order for binarize
        # Use label_binarize on y_test with classes=pipe.classes_
        y_bin=label_binarize(y_test, classes=pipe.classes_)
        auc=roc_auc_score(y_bin, prob, average="macro", multi_class="ovr")
        print(f"AUC {auc:.4f}")
    except Exception as e:
        auc=None; print("AUC fail",e)
    results[name]={"pipe":pipe, "val_acc":acc, "val_f1":f1_macro, "test_acc":acc_t, "test_f1":f1_t, "false_safe":false_safe, "cm":cm, "auc":auc, "report":classification_report(y_test, pred_test, output_dict=True, zero_division=0)}
    if f1_t>best_f1:
        best_f1=f1_t; best=name

print(f"\nBest {best} F1 {best_f1:.4f}")
best_pipe=results[best]["pipe"]
with open(r"C:\Users\ASUS\Documents\suryaghar\suryagrid_model_v2.pkl","wb") as f:
    pickle.dump({"model":best_pipe, "input_features":input_features, "cat_features":cat_features, "num_features":num_features, "label_order":label_order, "results":results}, f)
print(f"Saved v2 best {best}")

# Feature importances for RF
if "RandomForest" in results:
    rf=results["RandomForest"]["pipe"]
    ohe=rf.named_steps["prep"].named_transformers_["cat"]
    cat_names=list(ohe.get_feature_names_out(cat_features))
    all_names=cat_names + num_features
    imps=rf.named_steps["clf"].feature_importances_
    idx=np.argsort(imps)[::-1]
    print("\nTop 15 importances RF:")
    for i in idx[:15]:
        print(f"{all_names[i]:40s} {imps[i]:.4f}")
# Also for best if balanced
if best in results and "RandomForest" in best:
    pass

# Test two known cases explicitly
print("\n=== Test 734 and 6231 ===")
for bus,new in [("734",66),("6231",53)]:
    # Find in test set
    hit=test[(test['pv_bus']==bus) & (test['new_pv_kw']==new)]
    if len(hit)==0:
        # try pv_dataset_augmented
        import pandas as pd
        df=pd.read_csv(r"C:\Users\ASUS\Documents\suryaghar\pv_dataset_enriched_augmented.csv", dtype={'pv_bus':str})
        hit=df[(df['pv_bus']==bus) & (df['new_pv_kw']==new)]
        print(f"Found in pv_dataset_augmented {bus} {new}: {len(hit)}")
        if len(hit)==0:
            continue
        # use first
        row=hit.iloc[0]
        # need to prepare input row for model
        # Need to ensure same columns
        # Create df with input_features
        # Map transformer etc from valid
        # Simpler: use test hit if available, else skip
        continue
    row=hit.iloc[0]
    proba=results[best]["pipe"].predict_proba(hit[input_features])
    pred=results[best]["pipe"].predict(hit[input_features])[0]
    print(f"Bus {bus} {new}kW true {row['label']} pred {pred} proba {dict(zip(results[best]['pipe'].classes_, proba[0]))}")
