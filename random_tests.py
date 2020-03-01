import pandas as pd
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import numpy as np
x = [np.random.randint(1, 50) for i in range(50)]
y = [np.random.randint(1, 50) for i in range(50)]

df = pd.DataFrame({
    'x': x,
    'y': y
})

from sklearn.cluster import KMeans

kmeans = KMeans(n_clusters = 3)
hi = kmeans.fit_predict(df)
centroids = kmeans.cluster_centers_
# print(centroids)
fig = plt.figure(figsize=(5, 5))
# print(labels)
# print(hi)
# print(centroids[0][0])

plt.scatter(df['x'], df['y'], c = hi, cmap='rainbow')

plt.xlim(0, 80)
plt.ylim(0, 80)
plt.show()