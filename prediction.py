import numpy as np
from sklearn.linear_model import Ridge, Lasso
from sklearn.svm import SVR

from crossval import HypParamSearch


def predict_y(est, x, y_list):
    ridge_params_list = {'alpha':[10**i for i in range(-4,4)]}
    svr_params_list = {'gamma':[10**i for i in range(-5,11)],'C':[10**i for i in range(-10,1)], 'epsilon':[10**i for i in range(-20, 11)]}

    y_test_list_list = []
    y_test_predict_list_list = []

    n = y_list.shape[1]
    for i in range(n):
        y = y_list[:,i]
        print(x.shape, y.shape)
        if est is 'Ridge':
            hypsearch = HypParamSearch(x, y, Ridge, ridge_params_list)
            est, y_test_list, y_test_predict_list = hypsearch.hyp_param_search()
        elif est is 'Lasso':
            hypsearch = HypParamSearch(x, y, Ridge, ridge_params_list)
            est, y_test_list, y_test_predict_list = hypsearch.hyp_param_search()
        elif est is 'SVR':
            hypsearch = HypParamSearch(x, y, Ridge, ridge_params_list)
            est, y_test_list, y_test_predict_list = hypsearch.hyp_param_search()

        y_test_list_list.append(y_test_list)
        y_test_predict_list_list.append(y_test_predict_list)

    return y_test_list_list, y_test_predict_list_list
