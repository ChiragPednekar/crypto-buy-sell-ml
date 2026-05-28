import numpy as np

def walk_forward_validation(model_class, df, train_size=0.6, step=0.1):

    total_len = len(df)
    train_window = int(total_len * train_size)
    step_size = int(total_len * step)

    results = []

    for start in range(0, total_len - train_window, step_size):
        train = df.iloc[start:start + train_window]
        test = df.iloc[start + train_window:
                       start + train_window + step_size]

        X_train = train.drop("label", axis=1)
        y_train = train["label"]

        X_test = test.drop("label", axis=1)
        y_test = test["label"]

        model = model_class()
        model.train(X_train, y_train)

        preds = model.model.predict(X_test)
        accuracy = np.mean(preds == y_test)
        results.append(accuracy)

    return np.mean(results)