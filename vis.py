from sklearn.decomposition import PCA
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('tmp.csv')

pca = PCA(n_components=2)
components = pca.fit_transform(df)

plt.scatter(components[:, 0], components[:, 1])#, x=0, y=1) #, color=df['species'])
plt.show()
