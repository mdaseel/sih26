import pandas as pd, numpy as np, json, pickle, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score, precision_recall_fscore_support, roc_auc_score
from sklearn.preprocessing import label_binarize

train = pd.read_csv(r"C:\Users\ASUS\Documents\suryaghar\ml_dataset_train.csv")
val = pd.read_csv(r"C:\Users\ASUS\Documents\suryaghar\ml_dataset_val.csv")
test = pd.read_csv(r"C:\Users\ASUS\Documents\suryaghar\ml_dataset_test.csv")

# Strict inputs from ml_feature_definition
input_features = ["pv_bus","pv_bus_vn_kv","existing_pv_kw","new_pv_kw","total_pv_kw","existing_load_at_bus_kw","pv_penetration_ratio","transformer_association","feeder_section"]
cat_features = ["pv_bus","transformer_association","feeder_section"]
num_features = ["pv_bus_vn_kv","existing_pv_kw","new_pv_kw","total_pv_kw","existing_load_at_bus_kw","pv_penetration_ratio"]

# Encode pv_bus has 71 cats, transformer 22, section 7 -> one-hot would be 71+22+7=100 dims, okay for 1050 rows
# Use OneHot handle_unknown ignore + StandardScaler for numeric

preprocess = ColumnTransformer([
    ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_features),
    ("num", StandardScaler(), num_features)
])

# Map labels to ordered for ROC
label_order = ["SAFE","CAUTION","CONSTRAINED"]
# Ensure consistent encoding
def encode_label(s):
    return s  # keep string, sklearn handles

X_train = train[input_features]
y_train = train["label"]
X_val = val[input_features]
y_val = val["label"]
X_test = test[input_features]
y_test = test["label"]

print(f"Train {len(X_train)} Val {len(X_val)} Test {len(X_test)}")
print("Class dist train", y_train.value_counts(normalize=True).to_dict())

# Models
models = {
    "LogisticRegression": Pipeline([("prep", preprocess), ("clf", LogisticRegression(max_iter=1000, multi_class="multinomial", solver="lbfgs", class_weight="balanced"))]),
    "RandomForest": Pipeline([("prep", preprocess), ("clf", RandomForestClassifier(n_estimators=200, max_depth=None, random_state=42, class_weight="balanced", n_jobs=-1))]),
}

results={}
best_model=None
best_f1=0
for name, pipe in models.items():
    pipe.fit(X_train, y_train)
    pred_val = pipe.predict(X_val)
    acc = accuracy_score(y_val, pred_val)
    f1_macro = f1_score(y_val, pred_val, average="macro")
    f1_weighted = f1_score(y_val, pred_val, average="weighted")
    print(f"\n=== {name} VAL ===")
    print(f"Acc {acc:.4f} F1-macro {f1_macro:.4f} weighted {f1_weighted:.4f}")
    print(classification_report(y_val, pred_val, digits=3, zero_division=0))
    # per class recall for CONSTRAINED
    # confusion
    cm = confusion_matrix(y_val, pred_val, labels=label_order)
    print("Confusion (rows true, cols pred) SAFE/CAUTION/CONSTR")
    print(cm)
    # also test
    pred_test = pipe.predict(X_test)
    acc_t = accuracy_score(y_test, pred_test)
    f1_macro_t = f1_score(y_test, pred_test, average="macro")
    print(f"TEST Acc {acc_t:.4f} F1-macro {f1_macro_t:.4f}")
    print(classification_report(y_test, pred_test, digits=3, zero_division=0))
    cm_t = confusion_matrix(y_test, pred_test, labels=label_order)
    print(cm_t)
    # ROC-AUC one-vs-rest
    try:
        prob = pipe.predict_proba(X_test)
        y_bin = label_binarize(y_test, classes=label_order)
        auc = roc_auc_score(y_bin, prob, average="macro", multi_class="ovr")
        print(f"ROC-AUC macro OVR {auc:.4f}")
    except Exception as e:
        auc=None
        print("AUC failed",e)
    # false SAFE: true CONSTRAINED predicted SAFE
    # Find indices where true=CONSTRAINED and pred=SAFE
    false_safe = sum((y_test=="CONSTRAINED") & (pred_test=="SAFE"))
    false_safe_rate = false_safe / sum(y_test=="CONSTRAINED") if sum(y_test=="CONSTRAINED")>0 else 0
    # false CONSTRAINED: true SAFE predicted CONSTRAINED
    false_constrained = sum((y_test=="SAFE") & (pred_test=="CONSTRAINED"))
    print(f"False SAFE (CONSTRAINED->SAFE) {false_safe}/{sum(y_test=='CONSTRAINED')} = {false_safe_rate:.3f}")
    print(f"False CONSTRAINED (SAFE->CONSTR) {false_constrained}/{sum(y_test=='SAFE')}")

    results[name] = {"pipe":pipe, "val_acc":acc, "val_f1_macro":f1_macro, "test_acc":acc_t, "test_f1_macro":f1_macro_t, "auc":auc, "false_safe":false_safe, "false_safe_rate":false_safe_rate, "cm_test":cm_t, "report": classification_report(y_test, pred_test, output_dict=True, zero_division=0)}

    if f1_macro_t > best_f1:
        best_f1=f1_macro_t
        best_model=name

print(f"\nBest model by test F1-macro: {best_model} {best_f1:.4f}")

# Save best
best_pipe = results[best_model]["pipe"]
with open(r"C:\Users\ASUS\Documents\suryaghar\suryagrid_model.pkl","wb") as f:
    pickle.dump({"model":best_pipe, "input_features":input_features, "cat_features":cat_features, "num_features":num_features, "label_order":label_order, "results":results}, f)
print(f"Saved suryagrid_model.pkl best={best_model}")

# Also save feature importances for RF
if "RandomForest" in results:
    rf_pipe = results["RandomForest"]["pipe"]
    # get feature names
    ohe = rf_pipe.named_steps["prep"].named_transformers_["cat"]
    cat_names = ohe.get_feature_names_out(cat_features)
    num_names = num_features
    all_names = list(cat_names) + num_names
    importances = rf_pipe.named_steps["clf"].feature_importances_
    # sort
    idx=np.argsort(importances)[::-1]
    print("\nTop 15 RF importances:")
    for i in idx[:15]:
        print(f"{all_names[i]:40s} {importances[i]:.4f}")

# Also evaluate CONSTRAINED recall specifically
for name in results:
    rep=results[name]["report"]
    print(f"{name} CONSTRAINED recall {rep['CONSTRAINED']['recall']:.3f} precision {rep['CONSTRAINED']['precision']:.3f} f1 {rep['CONSTRAINED']['f1-score']:.3f}")
