# PredictionOptimizationTool
Tool which is capable of reading .csv, predicting target property and optimizing x for improving target property

## Overview
This tool is capable of predicting objective variables and optimizing explanatory variables for minimizing or maximizing objective variables
(Optimization capability has not made yet)

## How to use
- Run ```python main.py```
- Read .csv file and select explanatory variables and objective variables
![スクリーンショット 2020-02-09 16 53 41](https://user-images.githubusercontent.com/45067993/74098625-ba6d7a00-4b5d-11ea-9343-ca8ba78e40e7.png)
- Select prediction model

- Download models: Pickle file will be downloaded in your current folder. Pickle file is dictionary whose key is objective variable name and value is model. For example, ```{objective_varable_name1: est1, objective_variable_name2: est2}```
