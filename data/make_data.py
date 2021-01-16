from sklearn import datasets
import pandas as pd


def create_boston_data():
    boston = datasets.load_boston()

    boston_df = pd.DataFrame(boston.data)
    boston_df.columns = boston.feature_names

    boston_df['PRICE'] = pd.DataFrame(boston.target)
    boston_df.to_csv('boston.csv', sep=',', index=False, encoding='utf-8', header=True)


if __name__ == "__main__":
    create_boston_data()
