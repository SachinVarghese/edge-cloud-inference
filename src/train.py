import joblib
from sklearn.linear_model import LogisticRegression
from src.data import IrisData
from xgboost import XGBClassifier

EdgeModelFolder = "edge"
CloudModelFolder = "cloud"


def train_edge_model(data: IrisData, artifacts_folder: str):
    logreg = LogisticRegression(C=1e5)
    logreg.fit(data.X, data.y)
    with open(f"{artifacts_folder}/{EdgeModelFolder}/model.joblib", "wb") as f:
        joblib.dump(logreg, f)


def train_cloud_model(data: IrisData, artifacts_folder: str):
    clf = XGBClassifier()
    clf.fit(data.X, data.y)
    clf.save_model(f"{artifacts_folder}/{CloudModelFolder}/model.bst")
