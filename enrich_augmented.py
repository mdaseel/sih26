import pandas as pd, json
df=pd.read_csv(r"C:\Users\ASUS\Documents\suryaghar\pv_dataset_augmented.csv", dtype={'pv_bus':str})
elec=pd.read_csv(r"C:\Users\ASUS\Documents\suryaghar\electrical_features.csv", dtype={'bus_id':str})
valid=pd.read_csv(r"C:\Users\ASUS\Documents\suryaghar\valid_pv_buses.csv", dtype={'bus_id':str})
# merge
df=df.merge(elec, left_on='pv_bus', right_on='bus_id', how='left')
df['transformer_sn_kva']=df['transformer_sn_kva'].fillna(5000)
df['base_voltage_pu']=df['base_voltage_pu'].fillna(0.97)
df['pv_to_transformer_ratio']=df['total_pv_kw']/df['transformer_sn_kva']
df['new_pv_to_transformer_ratio']=df['new_pv_kw']/df['transformer_sn_kva']
df['load_to_transformer_ratio']=df['existing_load_at_bus_kw']/df['transformer_sn_kva'].replace(0,1)
df['pv_penetration_ratio']=df['total_pv_kw']/df['existing_load_at_bus_kw'].replace(0,1)
df.loc[df['existing_load_at_bus_kw']==0,'pv_penetration_ratio']=df['total_pv_kw']/1.0
# add transformer/section maps (already in valid, but ensure)
map_trafo=dict(zip(valid['bus_id'].astype(str), valid['transformer_association']))
map_section=dict(zip(valid['bus_id'].astype(str), valid['feeder_section']))
df['transformer_association']=df['pv_bus'].map(map_trafo)
df['feeder_section']=df['pv_bus'].map(map_section)
# Save enriched augmented
df.to_csv(r"C:\Users\ASUS\Documents\suryaghar\pv_dataset_enriched_augmented.csv", index=False)
print(f"Saved enriched augmented {len(df)} rows")
print(df['label'].value_counts().to_dict())
# Now split stratified
from sklearn.model_selection import train_test_split
label_col="label"
train, temp = train_test_split(df, test_size=0.30, stratify=df[label_col], random_state=42)
val, test = train_test_split(temp, test_size=0.50, stratify=temp[label_col], random_state=42)
print(f"Train {len(train)} Val {len(val)} Test {len(test)}")
print(train[label_col].value_counts(normalize=True).to_dict())
# Save enriched splits
input_features_enriched = ["pv_bus","pv_bus_vn_kv","existing_pv_kw","new_pv_kw","total_pv_kw","existing_load_at_bus_kw","pv_penetration_ratio",
                           "transformer_association","feeder_section",
                           "transformer_sn_kva","pv_to_transformer_ratio","new_pv_to_transformer_ratio","load_to_transformer_ratio",
                           "base_voltage_pu","feeder_distance_km","upstream_r_ohm","upstream_x_ohm","upstream_z_ohm"]
cols_to_keep = input_features_enriched + [label_col, "constraint_type","delta_pv_bus_voltage_pu","pv_max_voltage_pu","pv_max_transformer_loading_pct","reverse_power_flow"]
for name,d in [("train",train),("val",val),("test",test)]:
    d[cols_to_keep].to_csv(f"C:\\Users\\ASUS\\Documents\\suryaghar\\ml_dataset_{name}_enriched_v2.csv", index=False)
    print(f"Saved ml_dataset_{name}_enriched_v2.csv")
# Save pv_dataset_enriched_augmented for reference
print(df[["pv_bus","new_pv_kw","delta_pv_bus_voltage_pu","label"]].head().to_string())
# Check class dist augmented vs original
orig=pd.read_csv(r"C:\Users\ASUS\Documents\suryaghar\pv_dataset.csv")
print("Original 1500 dist", orig['label'].value_counts().to_dict())
print("Augmented 1692 dist", df['label'].value_counts().to_dict())
