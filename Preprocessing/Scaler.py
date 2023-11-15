from typing import *
import numpy as np

from LUMA.Interface.Super import _Transformer
from LUMA.Interface.Exception import NotFittedError


class StandardScaler(_Transformer):
    
    """
    Standard scaling is a data preprocessing technique to transform 
    the data so that it has a mean of 0 and a standard deviation of 1.
    """
    
    def __init__(self) -> None:
        self.mean = None
        self.std = None
        self._fitted = False

    def fit(self, X: np.ndarray) -> None:
        self.mean = np.mean(X, axis=0)
        self.std = np.std(X, axis=0)
        self._fitted = True

    def transform(self, X: np.ndarray) -> np.ndarray:
        if not self._fitted: raise NotFittedError(self)
        return (X - self.mean) / self.std

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        self.fit(X)
        return self.transform(X)

    def inverse_transform(self, X: np.ndarray) -> np.ndarray:
        if not self._fitted: raise NotFittedError(self)
        return (X * self.std) + self.mean


class MinMaxScaler(_Transformer):
    
    """
    MinMax scaling (also known as Min-Max normalization)
    to rescale features to a specific range, typically between 0 and 1. 
    The purpose of MinMax scaling is to transform the features in a way 
    that they fall within a specific interval.
    """
    
    def __init__(self, feature_range: tuple=(0, 1)) -> None:
        self.feature_range = feature_range
        self.min = None
        self.max = None
        self._fitted = False

    def fit(self, X: np.ndarray) -> None:
        self.min = np.min(X, axis=0)
        self.max = np.max(X, axis=0)
        self._fitted = True

    def transform(self, X: np.ndarray) -> np.ndarray:
        if not self._fitted: raise NotFittedError(self)
        min_val, max_val = self.feature_range
        scaled = (X - self.min) / (self.max - self.min) * (max_val - min_val)
        return scaled + min_val

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        self.fit(X)
        return self.transform(X)

    def inverse_transform(self, X: np.ndarray) -> np.ndarray:
        if not self._fitted: raise NotFittedError(self)
        min_val, max_val = self.feature_range
        original = (X - min_val) / (max_val - min_val) * (self.max - self.min)
        return original + self.min

