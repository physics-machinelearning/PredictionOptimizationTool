import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score
from sklearn.model_selection import KFold
import itertools


class HypParamSearch:
    def __init__(self, x, y, est, params_list):
        self.x = x.astype('float')
        self.y = y
        self.est = est
        self.params_list = params_list
    
    def kf_crossval(self, est):
        kf = KFold(n_splits=10)
        y_test_list = []
        y_test_predict_list = []
        for train, test in kf.split(self.x):
            x_train, x_test = self.x[train], self.x[test]
            y_train, y_test = self.y[train], self.y[test]
            
            sc = StandardScaler()
            x_train_sc = sc.fit_transform(x_train)
            x_test_sc = sc.transform(x_test)
            
            est.fit(x_train_sc, y_train)
            y_test = y_test.flatten()
            y_test_predict = est.predict(x_test_sc).flatten()
            
            y_test_list.extend(y_test.tolist())
            y_test_predict_list.extend(y_test_predict.tolist())
            
        r2 = r2_score(y_test_list, y_test_predict_list)
        return r2, y_test_list, y_test_predict_list
    
    def hyp_param_search(self):
        keys = list(self.params_list.keys())
        
        params_list = list(self.params_list.values())
        if len(params_list) == 1:
            params_list = [[params_list[0][i]] for i in range(len(params_list[0]))]
        else:
            params_list = params_list[0]
            for i in range(1, len(self.params_list.keys())):
                params_list = list(itertools.product(params_list, list(self.params_list.values())[i]))
                params_list = [list(temp) for temp in params_list]
                
                if i>=2:
                    params_list = [temp[0]+[temp[1]] for temp in params_list]
                
        r2_list = []
        for params in params_list:
            param_dict = {}
            for i, key in enumerate(keys):
                param_dict[key] = params[i]
            est = self.est(**param_dict)
            r2, _, _ = self.kf_crossval(est)
            r2_list.append(r2)
            
        index = r2_list.index(max(r2_list))
        
        param_dict = {}
        params = params_list[index]
        for key, param in zip(keys, params):
            param_dict[key] = param
        
        est = self.est(**param_dict)

        r2, y_test_list, y_test_predict_list = self.kf_crossval(est)
        
        return est, y_test_list, y_test_predict_list