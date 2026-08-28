import pandas as pd
from sklearn.model_selection import train_test_split
import csv

df=pd.read_csv(r"C:\Users\ASUS\Documents\suryaghar\pv_dataset.csv")
# Join feeder static attributes from valid_pv_buses.csv for transformer/section
valid=pd.read_csv(r"C:\Users\ASUS\Documents\suryaghar\valid_pv_buses.csv", dtype={'bus_id':str})
# map bus_id -> transformer, feeder_section
map_trafo=dict(zip(valid['bus_id'].astype(str), valid['transformer_association']))
map_section=dict(zip(valid['bus_id'].astype(str), valid['feeder_section']))
# ensure pv_bus as string
df['pv_bus']=df['pv_bus'].astype(str)
df['transformer_association']=df['pv_bus'].map(map_trafo)
df['feeder_section']=df['pv_bus'].map(map_section)
# penetration
df['pv_penetration_ratio']=df['total_pv_kw'] / df['existing_load_at_bus_kw'].replace(0,1)
# fill nans for buses with zero load -> ratio = total
df.loc[df['existing_load_at_bus_kw']==0,'pv_penetration_ratio']=df['total_pv_kw']/1.0

# Define strict feature columns
input_features=["pv_bus","pv_bus_vn_kv","existing_pv_kw","new_pv_kw","total_pv_kw","existing_load_at_bus_kw","pv_penetration_ratio","transformer_association","feeder_section"]
# label
label_col="label"

# Check leakage: ensure no post-sim cols in inputs
post_cols=[c for c in df.columns if c.startswith('base_') or c.startswith('pv_') or c.startswith('delta_') or c in ['reverse_power_flow','constraint_type','constraint_reason','worst_line','worst_transformer','max_voltage_rise_pu']]
print(f"Input features: {input_features}")
print(f"Post cols excluded: {post_cols[:10]}... total {len(post_cols)}")

# Stratified split 70/15/15 seed 42 on label
train, temp = train_test_split(df, test_size=0.30, stratify=df[label_col], random_state=42)
val, test = train_test_split(temp, test_size=0.50, stratify=temp[label_col], random_state=42)
print(f"Train {len(train)} Val {len(val)} Test {len(test)}")
print("Train label",train[label_col].value_counts(normalize=True).to_dict())
print("Val label",val[label_col].value_counts(normalize=True).to_dict())
print("Test label",test[label_col].value_counts(normalize=True).to_dict())
# Bus leakage check: overlap
train_buses=set(train['pv_bus'].unique())
val_buses=set(val['pv_bus'].unique())
test_buses=set(test['pv_bus'].unique())
print(f"Buses train {len(train_buses)} val {len(val_buses)} test {len(test_buses)}")
print(f"Overlap train-val {len(train_buses & val_buses)} train-test {len(train_buses & test_buses)} val-test {len(val_buses & test_buses)}")
print(f"All buses covered train? {len(train_buses)==71} val {len(val_buses)} test {len(test_buses)}")
# Duplicate check across splits
train_keys=set(zip(train['pv_bus'],train['existing_pv_kw'],train['new_pv_kw']))
val_keys=set(zip(val['pv_bus'],val['existing_pv_kw'],val['new_pv_kw']))
test_keys=set(zip(test['pv_bus'],test['existing_pv_kw'],test['new_pv_kw']))
print(f"Key overlap train-val {len(train_keys & val_keys)} train-test {len(train_keys & test_keys)} val-test {len(val_keys & test_keys)}")

# Save strict ML datasets (inputs + label only for training, full for eval optional)
cols_to_save = input_features + [label_col, "constraint_type", " pv_pv_bus_voltage_pu".strip() ] # keep label only
# Actually keep label + constraint_type for eval, but model trains on label
cols_train = input_features + [label_col]
df_train_inputs = train[input_features + [label_col] + ["constraint_type","delta_pv_bus_voltage_pu","pv_max_voltage_pu","pv_max_transformer_loading_pct","reverse_power_flow"]]
df_val_inputs = val[input_features + [label_col] + ["constraint_type","delta_pv_bus_voltage_pu","pv_max_voltage_pu","pv_max_transformer_loading_pct","reverse_power_flow"]]
df_test_inputs = test[input_features + [label_col] + ["constraint_type","delta_pv_bus_voltage_pu","pv_max_voltage_pu","pv_max_transformer_loading_pct","reverse_power_flow"]]

df_train_inputs.to_csv(r"C:\Users\ASUS\Documents\suryaghar\ml_dataset_train.csv", index=False)
df_val_inputs.to_csv(r"C:\Users\ASUS\Documents\suryaghar\ml_dataset_val.csv", index=False)
df_test_inputs.to_csv(r"C:\Users\ASUS\Documents\suryaghar\ml_dataset_test.csv", index=False)
# Also save strict inputs only
train[input_features + [label_col]].to_csv(r"C:\Users\ASUS\Documents\suryaghar\ml_train_strict.csv", index=False)

print("Saved ml_dataset_train/val/test.csv with inputs+label+aux targets")
print(train[input_features].dtypes.to_string())
# Check distributions
print(train[input_features].describe(include='all').to_string())
