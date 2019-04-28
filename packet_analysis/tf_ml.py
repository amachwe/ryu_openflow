import numpy as np
import pandas as pd
from collections import  Counter
import sklearn.tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.utils import shuffle
data = "packet_data_reduced_20k_raw.csv"
arr = pd.read_csv(data)
arr = shuffle(arr)

train_perc = 0.5
records = arr.shape[0]
num = int(train_perc*records)

y_test = arr.iloc[0:num,3044]

y_train = arr.iloc[num:records, 3044]

x_test = arr.iloc[0:num,0:3044]
x_train = arr.iloc[num:records,0:3044]

tree = DecisionTreeClassifier(max_depth=5)
tree.fit(x_train, y_train)


import graphviz
dot_data = sklearn.tree.export_graphviz(tree, out_file=None)
graph = graphviz.Source(dot_data)
graph.render("packet_raw")

print(list(map(lambda x: print(x), filter(lambda x: x[1]>0,[(i, v) for i, v in enumerate(tree.feature_importances_)]))))
corr = 0
incorr = 0
for i in range(0, x_test.shape[0]):
    pred = tree.predict(x_test.iloc[i,:].reshape(1,-1))
    if y_test.iloc[i] == pred[0]:
        corr  +=1
    else:
        incorr +=1
        print(pred, y_test.iloc[i])


print("Result: {}".format(corr/(incorr+corr)))