from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_regression


def select_best_features(X, y, k=10):

    selector = SelectKBest(
        score_func=f_regression,
        k=k
    )

    selector.fit(X, y)

    selected_features = X.columns[
        selector.get_support()
    ].tolist()

    return selected_features
