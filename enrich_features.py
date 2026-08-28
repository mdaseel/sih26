import pandas as pd, numpy as np, json
# Load datasets
df=pd.read_csv(r"C:\Users\ASUS\Documents\suryaghar\pv_dataset.csv", dtype={'pv_bus':str})
elec=pd.read_csv(r"C:\Users\ASUS\Documents\suryaghar\electrical_features.csv", dtype={'bus_id':str})
valid=pd.read_csv(r"C:\Users\ASUS\Documents\suryaghar\valid_pv_buses.csv", dtype={'bus_id':str})

# Merge electrical features
df=df.merge(elec, left_on='pv_bus', right_on='bus_id', how='left')
# For safety, fill missing sn with 5000
df['transformer_sn_kva']=df['transformer_sn_kva'].fillna(5000)
df['base_voltage_pu']=df['base_voltage_pu'].fillna(0.97)

# Compute ratios (avoid div by zero)
df['pv_to_transformer_ratio']=df['total_pv_kw'] / df['transformer_sn_kva']
df['new_pv_to_transformer_ratio']=df['new_pv_kw'] / df['transformer_sn_kva']
df['load_to_transformer_ratio']=df['existing_load_at_bus_kw'] / df['transformer_sn_kva'].replace(0,1)
df['pv_penetration_ratio']=df['total_pv_kw'] / df['existing_load_at_bus_kw'].replace(0,1)
df.loc[df['existing_load_at_bus_kw']==0,'pv_penetration_ratio']=df['total_pv_kw']/1.0
# Also keep original penetration but add corrected version with trafo
# feeder_distance etc already from elec: feeder_distance_km, upstream_r_ohm, upstream_x_ohm, upstream_z_ohm

# Check leakage: ensure no post columns used
print(df[['pv_bus','transformer_sn_kva','base_voltage_pu','feeder_distance_km','upstream_z_ohm','pv_to_transformer_ratio']].head().to_string())
print(df.describe()[['transformer_sn_kva','pv_to_transformer_ratio','feeder_distance_km','upstream_z_ohm','base_voltage_pu']].to_string())

# Save enriched
df.to_csv(r"C:\Users\ASUS\Documents\suryaghar\pv_dataset_enriched.csv", index=False)
print(f"Saved enriched {len(df)} rows to pv_dataset_enriched.csv")

# Also create enriched ml splits: need to recreate train/val/test with same seed but enriched features
from sklearn.model_selection import train_test_split
# Define enriched input features
input_features_enriched = ["pv_bus","pv_bus_vn_kv","existing_pv_kw","new_pv_kw","total_pv_kw","existing_load_at_bus_kw","pv_penetration_ratio",
                           "transformer_association","feeder_section",
                           "transformer_sn_kva","pv_to_transformer_ratio","new_pv_to_transformer_ratio","load_to_transformer_ratio",
                           "base_voltage_pu","feeder_distance_km","upstream_r_ohm","upstream_x_ohm","upstream_z_ohm"]

# Ensure transformer_association and feeder_section still present (from valid join? df has them? pv_dataset has not, need to add from valid)
# df currently has bus_id from elec, but not transformer_association from valid - add
valid_map_trafo=dict(zip(valid['bus_id'].astype(str), valid['transformer_association']))
valid_map_section=dict(zip(valid['bus_id'].astype(str), valid['feeder_section']))
df['transformer_association']=df['pv_bus'].map(valid_map_trafo)
df['feeder_section']=df['pv_bus'].map(valid_map_section)
# Recheck
print(df[['transformer_association','feeder_section']].head().to_string())

# Save again with those
df.to_csv(r"C:\Users\ASUS\Documents\suryaghar\pv_dataset_enriched.csv", index=False)

# Now split stratified same as before seed 42
label_col="label"
train, temp = train_test_split(df, test_size=0.30, stratify=df[label_col], random_state=42)
val, test = train_test_split(temp, test_size=0.50, stratify=temp[label_col], random_state=42)
print(f"Split train {len(train)} val {len(val)} test {len(test)}")

# Save enriched ml datasets (strict + new features)
cols_to_keep = input_features_enriched + [label_col, "constraint_type","delta_pv_bus_voltage_pu","pv_max_voltage_pu","pv_max_transformer_loading_pct","reverse_power_flow"]
for name, d in [("train",train),("val",val),("test",test)]:
    d[cols_to_keep].to_csv(f"C:\\Users\\ASUS\\Documents\\suryaghar\\ml_dataset_{name}_enriched.csv", index=False)
    print(f"Saved ml_dataset_{name}_enriched.csv {len(d)}")

# Also save input list for training script
with open(r"C:\Users\ASUS\Documents\suryaghar\enriched_features.json","w") as f:
    json.dump({"input_features_enriched": input_features_enriched}, f, indent=2)
