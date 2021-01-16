from sklearn.model_selection import train_test_split

from auto_learning.models import REGRESSION_MODELS
from auto_learning.hyp_param_search import HypParamSearch


def predict_y(est_name, x, y_list, y_col):
    y_test_list_list = []
    y_test_predict_list_list = []

    feature_selection = 'None'
    crossval_type = 'kfold'
    search_type = 'bayes'
    metrics = 'r2'
    problem_type = 'regression'

    est_dict = {}
    n = y_list.shape[1]
    for i in range(n):
        y = y_list[:, i]
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3)
        est_name = est_name.lower()
        func = REGRESSION_MODELS[est_name]
        est, params = func()
        hypsearch = HypParamSearch(
            x_train,
            y_train,
            x_test,
            y_test,
            est,
            problem_type=problem_type,
            feature_selection=feature_selection,
            params_dict=params,
            crossval_type=crossval_type,
            search_type=search_type,
            metrics=metrics
            )
        y_test_list, y_test_predict_list, val_score, test_score, est =\
            hypsearch.hyp_param_search()
        y_test_list_list.append(y_test_list)
        y_test_predict_list_list.append(y_test_predict_list)
        est_dict[y_col[i]] = est
    return y_test_list_list, y_test_predict_list_list, est_dict
