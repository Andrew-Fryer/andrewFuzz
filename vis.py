from sklearn.decomposition import PCA
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('tmp.csv')

y = df['label']
x = df.drop(columns=['label'])

pca = PCA(n_components=2)
components = pca.fit_transform(x)

plt.scatter(components[:, 0], components[:, 1], c=y)
plt.show()

print()
