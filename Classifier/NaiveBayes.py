from typing import *
import numpy as np

from LUMA.Interface.Super import _Estimator, _Supervised


class GaussianNaiveBayes(_Estimator, _Supervised):
    
    """
    Gaussian Naive Bayes is a probabilistic classification algorithm. 
    It's based on Bayes' theorem and makes an assumption 
    that the features follow a Gaussian distribution.
    """
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self.classes = np.unique(y)
        self.parameters = []
        self.priors = []
        self.X_train = X
        self.y_train = y
        
        shared_cov_matrix = np.zeros((X.shape[1], X.shape[1]))
        for c in self.classes:
            X_c = X[y == c]
            cov_matrix = np.diag(X_c.var(axis=0))
            shared_cov_matrix += cov_matrix
            self.parameters.append([X_c.mean(axis=0), cov_matrix])
        
        for params in self.parameters:
            params[1] = shared_cov_matrix / len(self.classes)
        
    def _calculate_likelihood(self, x: np.ndarray, mean: np.ndarray, cov: np.ndarray) -> float:
        dim = len(mean)
        dev = x - mean
        cov_inv = np.linalg.inv(cov)
        exponent = -0.5 * np.dot(dev, np.dot(cov_inv, dev))
        norm_term = 1 / np.sqrt((2 * np.pi) ** dim * np.linalg.det(cov))
        return norm_term * np.exp(exponent)

    def _calculate_prior(self, c: Any) -> float:
        return np.mean(self.y_train == c)

    def _classify_sample(self, x: np.ndarray) -> Any:
        posteriors = []
        for i, c in enumerate(self.classes):
            prior = self._calculate_prior(c)
            likelihood = self._calculate_likelihood(x, *self.parameters[i])
            posterior = prior * likelihood
            posteriors.append(posterior)
        return self.classes[np.argmax(posteriors)]

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.array([self._classify_sample(x) for x in X])

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        probabilities = []
        for x in X:
            posteriors = []
            for i, c in enumerate(self.classes):
                prior = self._calculate_prior(c)
                likelihood = self._calculate_likelihood(x, *self.parameters[i])
                posterior = prior * likelihood
                posteriors.append(posterior)
            posteriors = np.array(posteriors)
            probabilities.append(posteriors / np.sum(posteriors))          
        return np.array(probabilities)


class BernoulliNaiveBayes(_Estimator, _Supervised):
    
    """
    Bernoulli Naive Bayes is a classification algorithm based on 
    Bayes' theorem, which assumes that the features are binary 
    (i.e., they are either present or absent) and that they are 
    conditionally independent given the class label.
    """
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self.classes = np.unique(y)
        self.class_probs = np.zeros(len(self.classes))
        self.feature_probs = np.zeros((len(self.classes), X.shape[1]))

        for i, c in enumerate(self.classes):
            X_cls = X[y == c]
            self.class_probs[i] = len(X_cls) / len(y)
            self.feature_probs[i] = (X_cls.sum(axis=0) + 1) / (len(X_cls) + 2)

    def predict(self, X: np.ndarray) -> np.ndarray:
        predictions = []
        for x in X:
            class_scores = np.zeros(len(self.classes))
            for i, _ in enumerate(self.classes):
                class_scores[i] = np.log(self.class_probs[i])
                for j, feature in enumerate(x):
                    if feature == 1: class_scores[i] += np.log(self.feature_probs[i, j])
                    else: class_scores[i] += np.log(1 - self.feature_probs[i, j])

            predicted_class = self.classes[np.argmax(class_scores)]
            predictions.append(predicted_class)
        return np.array(predictions)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        probas = []
        for x in X:
            class_probs = np.zeros(len(self.classes))
            for i, _ in enumerate(self.classes):
                class_probs[i] = np.log(self.class_probs[i])
                for j, feature in enumerate(x):
                    if feature == 1: class_probs[i] += np.log(self.feature_probs[i, j])
                    else: class_probs[i] += np.log(1 - self.feature_probs[i, j])

            exp_class_probs = np.exp(class_probs - np.max(class_probs))
            probas.append(exp_class_probs / exp_class_probs.sum())
        return np.array(probas)

