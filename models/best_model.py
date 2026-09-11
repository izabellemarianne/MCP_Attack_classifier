from xgboost import XGBClassifier
import pickle
from pathlib import Path
from train import to_xy
FEATURE_CACHE = Path(__file__).parent / "cached_features_content.pkl"
training = pickle.loads(FEATURE_CACHE.read_bytes())

X_train, y_train = to_xy(training)


best_model = XGBClassifier(
    subsample=1.0,
    scale_pos_weight=0.41731242476584085,
    n_estimators=200,
    max_depth=6,
    learning_rate=0.3,
    colsample_bytree=0.8,
    tree_method="hist",
    eval_metric="logloss",
    random_state=42,
    n_jobs=1
)
best_model.fit(X_train, y_train)

BEST_MODEL_PATH = Path(__file__).parent.parent / "serving/best_model.json"
best_model.save_model(BEST_MODEL_PATH)