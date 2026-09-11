import sys
from pathlib import Path
import numpy as np
import math
import pickle
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupKFold, cross_validate
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.metrics import f1_score, accuracy_score, roc_auc_score, precision_score, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import torch
import wandb

sys.path.insert(0, str(Path(__file__).parent.parent))

from data.data_generation import train_test_split
from features.feature_engineering import dataset_to_features

from xgboost import XGBClassifier


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
    



def to_xy(dataset):
    X = []
    y = []
    for item in dataset:
        if not isinstance(item, dict):
            continue
        feature_vector = []
        for key, value in sorted(item.items()):
            if key == "label" or key=="group":
                continue
            feature_vector.extend(_flatten_feature_value(value))
        X.append(feature_vector)
        y.append(item["label"])

    if not X:
        raise ValueError("Dataset is empty after feature extraction.")

    y = np.asarray(y, dtype=int)
    X = np.asarray(X, dtype=float)
    return X, y

def _log_search_results(grid_search, run):
    run.config.update(grid_search.best_params_)
    run.log({"best_cv_f1": grid_search.best_score_}, step=0)

    results = pd.DataFrame(grid_search.cv_results_).copy()
    parameter_columns = [
        column for column in results.columns
        if column.startswith("param_")
    ]
    for column in parameter_columns:
        results[column] = results[column].astype(str)
    results["params"] = results["params"].apply(str)
    run.log({"cv_results": wandb.Table(dataframe=results)})


def log_reg(X, y, cv, groups, run=None):

    pipeline = Pipeline([('scale', StandardScaler()), ('clf', LogisticRegression(max_iter=1000, class_weight="balanced"))])

    param_grid = [{"clf__penalty": ["l2"], "clf__C": [0.001, 0.01, 0.1, 1, 10, 100], "clf__solver": ["liblinear", "lbfgs"]}, {"clf__penalty": ["l1"], "clf__C": [0.001, 0.01, 0.1, 1, 10, 100], "clf__solver": ["liblinear"]}]
    grid_search = GridSearchCV(pipeline, param_grid=param_grid, cv=cv, scoring="f1", n_jobs=-1, refit=True, verbose=2)
    grid_search.fit(X, y, groups=groups)

    print("Best params:", grid_search.best_params_)
    print("Best f1:", grid_search.best_score_)
    if run is not None:
        _log_search_results(grid_search, run)

    return grid_search.best_estimator_


def random_forest(X, y, cv, groups, run=None):

    pipeline =  RandomForestClassifier(random_state=42)

    param_grid = {"n_estimators": [300, 500, 800],  "max_depth": [5, 10, 20, None], "min_samples_leaf": [1, 5, 10], "min_samples_split": [2, 10, 20], "max_features": ["sqrt", "log2"], "class_weight": ["balanced", "balanced_subsample"]}

    grid_search = RandomizedSearchCV(pipeline, n_iter=50,param_distributions=param_grid, cv=cv, scoring="f1", n_jobs=-1, refit=True, verbose=2)
    grid_search.fit(X, y, groups=groups)

    print("Best params:", grid_search.best_params_)
    print("Best f1:", grid_search.best_score_)
    if run is not None:
        _log_search_results(grid_search, run)

    return grid_search.best_estimator_


def xgboost_tuning(X, y, cv, groups, scale_pos, run=None):

    pipeline =  XGBClassifier(tree_method="hist",  eval_metric="logloss", random_state=42, n_jobs=1)

    param_grid = {"learning_rate": [0.01, 0.05, 0.1, 0.2, 0.3],  "max_depth": [3, 4, 6, 8, 10], "subsample":[0.7, 0.85, 1.0], "colsample_bytree": [0.3, 0.5, 0.6, 0.8], "scale_pos_weight": [scale_pos], "n_estimators": [100, 200, 400]}

    grid_search = RandomizedSearchCV(pipeline,n_iter=50, param_distributions=param_grid, cv=cv, scoring="f1", n_jobs=-1, refit=True, verbose=2)
    grid_search.fit(X, y, groups=groups)

    print("Best params:", grid_search.best_params_)
    print("Best f1:", grid_search.best_score_)
    if run is not None:
        _log_search_results(grid_search, run)

    return grid_search.best_estimator_
if __name__ == "__main__":
    print("one")
    training, train_groups, test, total = train_test_split()
    print("two")

    FEATURE_CACHE = Path(__file__).parent / "cached_features_content.pkl"

    if FEATURE_CACHE.exists():
        training = pickle.loads(FEATURE_CACHE.read_bytes())
    else:
        training =  dataset_to_features(training, content=True)
        FEATURE_CACHE.write_bytes(pickle.dumps(training))
    test = dataset_to_features(test, content=True)
    print("three")

    X_train, y_train = to_xy(training)
    neg, pos = (y_train == 0).sum(), (y_train == 1).sum()
    scale_pos = math.sqrt(neg/pos)

    print("got data")

    num_groups = len(set(train_groups))
    num_splits = min(5, num_groups)
    gkf = GroupKFold(n_splits=num_splits)

    model_map = {"Logistic Regression": log_reg, "Random Forest": random_forest, "XGBoost":xgboost_tuning}
    X_test, y_test = to_xy(test)
    for key, value in model_map.items():
        wandb_run = wandb.init(
            project="ipi_detection_content",
            name=key,
            config={"model": key, "feature_cache": str(FEATURE_CACHE)},
        )
        if key == "XGBoost":
            best_model = value(X=X_train, y=y_train, cv=gkf, groups=train_groups, scale_pos=scale_pos, run=wandb_run)
        else:
            best_model = value(X=X_train, y=y_train, cv=gkf, groups=train_groups, run=wandb_run)
        preds = best_model.predict(X_test)
        probs = best_model.predict_proba(X_test)[:, 1] 
        print(f"======={key}=======")
        print("Accuracy:", accuracy_score(y_test, preds))
        print("F1:", f1_score(y_test, preds))
        print("Precision:", precision_score(y_test, preds))
        print("Recall:", recall_score(y_test, preds))
        print("ROC AUC:", roc_auc_score(y_test, probs))
        wandb.log({
            "test_accuracy": accuracy_score(y_test, preds),
            "test_f1": f1_score(y_test, preds),
            "test_precision": precision_score(y_test, preds),
            "test_recall": recall_score(y_test, preds),
            "test_roc_auc": roc_auc_score(y_test, probs),
        })
        wandb_run.finish()

        
    # df = pd.DataFrame(training)  # from dataset_to_features, before to_xy
        # print(df.groupby("label")["group"].describe())
    
        # for xgboost
        
    # models = {
        #     "Logistic Regression": Pipeline([("scale", StandardScaler()), ("clf", LogisticRegression(max_iter=1000, class_weight="balanced"))]),
        #     "Random Forest": RandomForestClassifier(n_estimators=300, class_weight="balanced", random_state=42),
        #     #TODO:udnerstand this + how it differest from ranodm forets
        #     "XGBoost":XGBClassifier(n_estimators=200, tree_method="hist", scale_pos_weight=scale_pos, eval_metric="logloss", random_state=42, n_jobs=1)
        # }

    # print("got models")    
    # for key, value in models.items():
    #     print(f"THIS IS MODEL: {key}")

    #     wandb_run = wandb.init(project="ipi_detection", name=key, config={"model":key}, reinit=True)


    #     scores = cross_validate(value, X_train, y_train, groups=train_groups, cv = gkf, scoring=["accuracy", "f1", "roc_auc", "precision", "recall"], n_jobs=1)
    #     print(f"\n{key}")
    #     for metric in ["accuracy", "f1", "roc_auc", "precision", "recall"]:
    #         values = scores[f"test_{metric}"]
    #         mean_val, std_val= values.mean(), values.std()
    #         wandb.log({f"{metric}_mean":mean_val, f"{metric}_std": std_val})
    #         print(f"{metric}: {values.mean()} +- {values.std()}")

    #     wandb_run.finish()






