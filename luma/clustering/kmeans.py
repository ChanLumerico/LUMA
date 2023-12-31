import numpy as np

from luma.interface.util import Matrix
from luma.interface.exception import NotFittedError
from luma.interface.super import Estimator, Evaluator, Unsupervised
from luma.metric.clustering import SilhouetteCoefficient


__all__ = (
    'KMeansClustering', 
    'KMeansClusteringPlus', 
    'KMediansClustering', 
    'MiniBatchKMeansClustering'
)


class KMeansClustering(Estimator, Unsupervised):
    
    """
    K-means clustering is a machine learning algorithm that  groups similar data 
    points into clusters. It works by iteratively assigning data points to the 
    nearest cluster center (centroid) and updating the centroids based on 
    the assigned data points. This process continues 
    until convergence.
    
    Parameters
    ----------
    `n_clusters` : Number of clusters
    `max_iter` : Number of iteration
    
    """
    
    def __init__(self, 
                 n_clusters: int = None, 
                 max_iter: int = 100, 
                 verbose: bool = False) -> None:
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.verbose = verbose
        self._X = None
        self._fitted = False
    
    def fit(self, X: Matrix) -> 'KMeansClustering':
        init_indices = np.random.choice(X.shape[0], self.n_clusters, replace=False)
        self.centroids = X[init_indices]
        self._X = X
        
        for i in range(self.max_iter):
            distances = np.linalg.norm(X[:, np.newaxis] - self.centroids, axis=2)
            labels = np.argmin(distances, axis=1)
            
            new_centroids = [X[labels == i].mean(axis=0) for i in range(self.n_clusters)]
            if np.all(np.array(new_centroids) == self.centroids): 
                if self.verbose: print(f'[K-Means] Ealry convergence at itertaion {i}')
                break
            
            if self.verbose and i % 10 == 0: 
                diff_norm = np.linalg.norm(np.array(new_centroids) - np.array(self.centroids))
                print(f'[K-Means] iteration: {i}/{self.max_iter}', end='')
                print(f' - delta-centroid norm: {diff_norm}')
            self.centroids = new_centroids
            
        self.centroids = np.array(self.centroids)
        self._fitted = True
        return self
    
    def predict(self, X: Matrix) -> Matrix:
        if not self._fitted: raise NotFittedError(self)
        distances = np.linalg.norm(X[:, np.newaxis] - self.centroids, axis=2)
        labels = np.argmin(distances, axis=1)
        return labels
    
    @property
    def labels(self) -> Matrix:
        return self.predict(self._X)
    
    def score(self, X: Matrix, metric: Evaluator = SilhouetteCoefficient) -> float:
        X_pred = self.predict(X)
        return metric.compute(X, X_pred)

    def set_params(self, n_clusters: int = None, max_iter: int = None) -> None:
        if n_clusters is not None: self.n_clusters = int(n_clusters)
        if max_iter is not None: self.max_iter = int(max_iter)


class KMeansClusteringPlus(Estimator, Unsupervised):
    
    """
    K-means++ is an improved version of the original K-means clustering algorithm, 
    designed to address some of its shortcomings and produce more robust and 
    efficient clustering results. K-means++ was introduced by David Arthur and 
    Sergei Vassilvitskii in a 2007 research paper titled "k-means++: 
    The Advantages of Careful Seeding."
    
    Parameters
    ----------
    `n_clusters` : Number of clusters
    `max_iter` : Number of iteration
    
    """
    
    def __init__(self, 
                 n_clusters: int = None, 
                 max_iter: int = 100,
                 verbose: bool = False) -> None:
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.verbose = verbose
        self._X = None
        self._fitted = False

    def _initialize_centroids(self, X: Matrix) -> None:
        self.centroids = [X[np.random.choice(X.shape[0])]]
        for _ in range(1, self.n_clusters):
            distances = [min([np.linalg.norm(x - c) ** 2 for c in self.centroids]) for x in X]
            distances = np.array(distances)
            
            probs = distances / distances.sum()
            next_centroid = np.random.choice(X.shape[0], p=probs)
            self.centroids.append(X[next_centroid])
        
    def fit(self, X: Matrix) -> 'KMeansClusteringPlus':
        self._X = X
        self._initialize_centroids(X)
        
        for _ in range(self.max_iter):
            distances = np.linalg.norm(X[:, np.newaxis] - self.centroids, axis=2)
            labels = np.argmin(distances, axis=1)
            
            for i in range(self.n_clusters):
                cluster_points = X[labels == i]
                if len(cluster_points) == 0: continue
                self.centroids[i] = np.mean(cluster_points, axis=0)
            
            if self.verbose and i % 10 == 0: 
                print(f'[K-Means++] iteration: {i}/{self.max_iter}', end='')
        
        self.centroids = np.array(self.centroids)
        self._fitted = True
        return self
    
    def predict(self, X: Matrix) -> Matrix:
        if not self._fitted: raise NotFittedError(self)
        distances = np.linalg.norm(X[:, np.newaxis] - self.centroids, axis=2)
        labels = np.argmin(distances, axis=1)
        return labels
    
    @property
    def labels(self) -> Matrix:
        return self.predict(self._X)
    
    def score(self, X: Matrix, metric: Evaluator = SilhouetteCoefficient) -> float:
        X_pred = self.predict(X)
        return metric.compute(X, X_pred)

    def set_params(self, n_clusters: int = None, max_iter: int = None) -> None:
        if n_clusters is not None: self.n_clusters = int(n_clusters)
        if max_iter is not None: self.max_iter = int(max_iter)


class KMediansClustering(Estimator, Unsupervised):
    
    """
    K-median clustering is a data clustering method that divides a dataset into 
    K clusters with each cluster having a median point as its representative. 
    It uses distance metrics like Manhattan or Euclidean distance to minimize 
    the sum of distances between data points and their cluster medians, 
    making it less sensitive to outliers and adaptable to non-Euclidean data.
    
    Parameters
    ----------
    `n_clusters` : Number of clusters
    `max_iter` : Number of iteration
    
    """
    
    def __init__(self, 
                 n_clusters: int = None, 
                 max_iter: int = 100,
                 verbose: bool = False) -> None:
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.verbose = verbose
        self._X = None
        self._fitted = False
        
    def fit(self, X: Matrix) -> 'KMediansClustering':
        self._X = X
        self.medians = X[np.random.choice(X.shape[0], self.n_clusters, replace=False)]
        
        for i in range(self.max_iter):
            distances = np.abs(X[:, np.newaxis] - self.medians)
            labels = np.argmin(distances.sum(axis=2), axis=1)

            new_medians = [np.median(X[labels == i], axis=0) for i in range(self.n_clusters)]
            new_medians = np.array(new_medians)
            
            if np.all(np.array(new_medians) == self.medians): 
                if self.verbose: print(f'[K-Medians] Ealry convergence at itertaion {i}')
                break
            
            if self.verbose and i % 10 == 0: 
                diff_norm = np.linalg.norm(np.array(new_medians) - np.array(self.medians))
                print(f'[K-Medians] iteration: {i}/{self.max_iter}', end='')
                print(f' - delta-centroid norm: {diff_norm}')
            
            self.medians = new_medians
        
        self._fitted = True
        return self
    
    def predict(self, X: Matrix) -> Matrix:
        if not self._fitted: raise NotFittedError(self)
        distances = np.abs(X[:, np.newaxis] - self.medians)
        labels = np.argmin(distances.sum(axis=2), axis=1)
        return labels
    
    @property
    def labels(self) -> Matrix:
        return self.predict(self._X)
    
    def score(self, X: Matrix, metric: Evaluator = SilhouetteCoefficient) -> float:
        X_pred = self.predict(X)
        return metric.compute(X, X_pred)
    
    def set_params(self, n_clusters: int = None, max_iter: int = None) -> None:
        if n_clusters is not None: self.n_clusters = int(n_clusters)
        if max_iter is not None: self.max_iter = int(max_iter)


class MiniBatchKMeansClustering(Estimator, Unsupervised):
    
    """
    Mini-Batch K-Means is an efficient variation of the traditional K-Means 
    clustering algorithm, designed to handle large datasets more effectively. 
    It operates by randomly selecting small subsets of the dataset (mini-batches) 
    and using these subsets, rather than the entire dataset, to update the 
    cluster centroids in each iteration. This approach significantly reduces 
    the computational cost and memory requirements, making it well-suited 
    for big data applications.
    
    Parameters
    ----------
    `n_clusters` : Number of clusters to estimate
    `batch_size` : Size of a single mini-batch
    `max_iter` : Maximum amount of iteration
    
    """
    
    def __init__(self, 
                 n_clusters: int = None, 
                 batch_size: int = 100, 
                 max_iter: int = 100):
        self.n_clusters = n_clusters
        self.batch_size = batch_size
        self.max_iter = max_iter
        self.centroids = None
        self._X = None
        self._fitted = False

    def fit(self, X: Matrix) -> 'MiniBatchKMeansClustering':
        m, _ = X.shape
        self._X = X
        
        rand_idx = np.random.choice(m, self.n_clusters, replace=False)
        self.centroids = X[rand_idx]

        for _ in range(self.max_iter):
            batch_idx = np.random.choice(m, self.batch_size, replace=False)
            batch = X[batch_idx]
            
            distances = np.linalg.norm(batch[:, np.newaxis] - self.centroids, axis=2)
            closest_cluster_idx = np.argmin(distances, axis=1)
            
            for i in range(self.n_clusters):
                cluster_points = batch[closest_cluster_idx == i]
                if len(cluster_points) > 0:
                    self.centroids[i] = np.mean(cluster_points, axis=0)
        
        self._fitted = True
        return self

    def predict(self, X: Matrix) -> Matrix:
        if not self._fitted: raise NotFittedError(self)
        distances = np.linalg.norm(X[:, np.newaxis] - self.centroids, axis=2)
        return np.argmin(distances, axis=1)
    
    @property
    def labels(self) -> Matrix:
        return self.predict(self._X)

    def score(self, X: Matrix, metric: Evaluator = SilhouetteCoefficient) -> float:
        X_pred = self.predict(X)
        return metric.compute(X, X_pred)
    
    def set_params(self, 
                   n_clusters: int = None,
                   batch_size: int = None,
                   max_iter: int = None) -> None:
        if n_clusters is not None: self.n_clusters = int(n_clusters)
        if batch_size is not None: self.batch_size = int(batch_size)
        if max_iter is not None: self.max_iter = int(max_iter)

