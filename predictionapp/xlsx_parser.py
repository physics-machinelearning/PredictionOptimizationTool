import pandas as pd


class ReadExcel:
    def __init__(self, path):
        self.path = path

    def read_excel(self):
        self.xy_df = pd.read_csv(self.path, header=0)
        return self.xy_df

    def read_col(self, cols):
        return self.xy_df.iloc[:, cols]
