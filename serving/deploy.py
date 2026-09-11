from fastapi import FastAPI
import pickle
from xgboost import XGBClassifier
import numpy as np
from pydantic import BaseModel
import torch
from features.feature_engineering import dataset_to_features

class SessionPayload(BaseModel):
    response: list

model = XGBClassifier()
model.load_model("serving/best_model.json")
app = FastAPI()
def _flatten_feature_value(value):
    if type(value) == bool:
        return [float(value)]
    elif isinstance(value, torch.Tensor):
        return value.detach().cpu().reshape(-1).tolist()
    elif isinstance(value, np.ndarray):
        return value.reshape(-1).astype(float).tolist()
    elif isinstance(value, (list, tuple)):
        return [float(v) for v in value]
    elif isinstance(value, (int, float)):
        return [float(value)]
    else:
        return [float(value)]
    
def to_x(dataset):
    X = []
    for item in dataset:
        if not isinstance(item, dict):
            continue
        feature_vector = []
        for key, value in sorted(item.items()):
            if key == "label" or key=="group":
                continue
            feature_vector.extend(_flatten_feature_value(value))
        X.append(feature_vector)
    
    if not X:
        raise ValueError("Dataset is empty after feature extraction.")

    X = np.asarray(X, dtype=float)
    return X


@app.post("/predict")
def predict(session: SessionPayload):
    log_line = session.dict
    feature_vec = dataset_to_features(log_line)
    x = to_x(feature_vec)

    pred = model.predict(x)
    prob = model.predict_proba(x)[:, 1]

    return f"Prediction: {pred[0]} \n Probability: {prob[0]}"



    
