import numpy as np

from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.neighbors import KNeighborsRegressor
from xgboost import XGBRegressor


def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)

    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    metrics = {
        "rmse": rmse,
        "mae": mae,
        "r2": r2
    }

    return metrics, y_pred


def train_knn(X_train, y_train):
    params = {
        "n_neighbors": [3, 5, 7, 9],
        "weights": ["uniform", "distance"]
    }

    grid = GridSearchCV(
        KNeighborsRegressor(),
        params,
        cv=5,
        scoring="r2",
        n_jobs=-1
    )

    grid.fit(X_train, y_train)

    return grid.best_estimator_, grid.best_params_


def train_xgboost(X_train, y_train):
    params = {
        "n_estimators": [100, 200],
        "max_depth": [3, 5, 7],
        "learning_rate": [0.01, 0.05, 0.1]
    }

    grid = GridSearchCV(
        XGBRegressor(
            objective="reg:squarederror",
            random_state=42
        ),
        params,
        cv=5,
        scoring="r2",
        n_jobs=-1
    )

    grid.fit(X_train, y_train)

    return grid.best_estimator_, grid.best_params_
