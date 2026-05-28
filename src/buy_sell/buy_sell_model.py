import joblib
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

class BuySellModel:
    def __init__(self, config):
        self.config = config
        self.model = xgb.XGBClassifier(
            n_estimators=config["model"]["n_estimators"],
            max_depth=config["model"]["max_depth"],
            learning_rate=config["model"]["learning_rate"],
            objective="multi:softprob",
            num_class=3,
            eval_metric="mlogloss"
        )

    def train(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=self.config["training"]["test_size"],
            shuffle=False
        )

        self.model.fit(X_train, y_train)

        preds = self.model.predict(X_test)
        print(classification_report(y_test, preds))

    def predict(self, X):
        probs = self.model.predict_proba(X)
        return probs

    def save(self, path):
        joblib.dump(self.model, path)

    def load(self, path):
        self.model = joblib.load(path)