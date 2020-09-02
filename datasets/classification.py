import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

dados = pd.read_csv('./datasets/data.csv',
                    sep=',',
                    names=['temp_min','temp_max','humi_min','humi_max','uv_min','uv_max']
)

target = pd.read_csv('./datasets/target.csv', names=['condicao'])

X_train, X_test, y_train, y_test = train_test_split(dados, target, random_state=0)

def prever(data):
    knn = KNeighborsClassifier(n_neighbors=3)
    knn.fit(X_train, y_train.values.ravel())
    return str(knn.predict(data))
