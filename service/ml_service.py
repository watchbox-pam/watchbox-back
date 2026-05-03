import numpy as np
import pickle
from typing import Dict, List
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds


class MLService:
    def __init__(self):
        self.user_index: Dict[str, int] = {}
        self.movie_index: Dict[int, int] = {}
        self.movie_ids: List[int] = []
        self.user_factors_svd: np.ndarray = None
        self.item_factors_svd: np.ndarray = None
        self.user_factors_als: np.ndarray = None
        self.item_factors_als: np.ndarray = None
        self.is_trained = False

    def train(self, ratings: List[dict], implicit_feedback: List[dict]):
        if not ratings and not implicit_feedback:
            return
        self._build_indexes(ratings, implicit_feedback)
        if ratings:
            self._train_svd(ratings)
        if implicit_feedback:
            self._train_als(implicit_feedback)
        self.is_trained = True

    def _build_indexes(self, ratings: List[dict], implicit_feedback: List[dict]):
        for r in ratings + implicit_feedback:
            if r["user_id"] not in self.user_index:
                self.user_index[r["user_id"]] = len(self.user_index)
            movie_id = r.get("movie_id")
            if movie_id and movie_id not in self.movie_index:
                self.movie_index[movie_id] = len(self.movie_index)
                self.movie_ids.append(movie_id)

    def _train_svd(self, ratings: List[dict]):
        n_users = len(self.user_index)
        n_movies = len(self.movie_index)
        if n_users < 2 or n_movies < 2:
            return

        matrix = np.zeros((n_users, n_movies))
        for r in ratings:
            uid = self.user_index.get(r["user_id"])
            mid = self.movie_index.get(r["movie_id"])
            if uid is not None and mid is not None:
                matrix[uid][mid] = r["rating"]

        k = min(50, n_users - 1, n_movies - 1)
        sparse_matrix = csr_matrix(matrix)
        U, sigma, Vt = svds(sparse_matrix, k=k)

        self.user_factors_svd = U * sigma
        self.item_factors_svd = Vt.T

    def _train_als(self, implicit_feedback: List[dict], factors: int = 50, iterations: int = 20, regularization: float = 0.01):
        n_users = len(self.user_index)
        n_movies = len(self.movie_index)
        if n_users < 2 or n_movies < 2:
            return

        rows, cols, data = [], [], []
        for fb in implicit_feedback:
            uid = self.user_index.get(fb["user_id"])
            mid = self.movie_index.get(fb["movie_id"])
            if uid is not None and mid is not None:
                rows.append(uid)
                cols.append(mid)
                data.append(fb["weight"])

        if not data:
            return

        R = csr_matrix((data, (rows, cols)), shape=(n_users, n_movies)).toarray()
        k = min(factors, n_users - 1, n_movies - 1)
        np.random.seed(42)
        X = np.random.normal(0, 0.1, (n_users, k))
        Y = np.random.normal(0, 0.1, (n_movies, k))

        for _ in range(iterations):
            for u in range(n_users):
                YtY = Y.T @ Y
                reg = regularization * np.eye(k)
                X[u] = np.linalg.solve(YtY + reg, Y.T @ R[u])
            for i in range(n_movies):
                XtX = X.T @ X
                reg = regularization * np.eye(k)
                Y[i] = np.linalg.solve(XtX + reg, X.T @ R[:, i])

        self.user_factors_als = X
        self.item_factors_als = Y

    def predict_svd(self, user_id: str, movie_id: int) -> float:
        return self.predict_svd_batch(user_id, [movie_id]).get(movie_id, 0.0)

    def predict_svd_batch(self, user_id: str, movie_ids: List[int]) -> Dict[int, float]:
        result = {mid: 0.0 for mid in movie_ids}
        if self.user_factors_svd is None or self.item_factors_svd is None:
            return result
        uid = self.user_index.get(user_id)
        if uid is None:
            return result
        ids_arr = np.array(movie_ids)
        indices = np.array([self.movie_index.get(mid, -1) for mid in movie_ids])
        valid = indices >= 0
        if valid.any():
            scores = self.item_factors_svd[indices[valid]] @ self.user_factors_svd[uid]
            scores = np.clip(scores / 10.0, 0.0, 1.0)
            for mid, score in zip(ids_arr[valid].tolist(), scores.tolist()):
                result[mid] = score
        return result

    def predict_als(self, user_id: str, movie_ids: List[int]) -> Dict[int, float]:
        result = {mid: 0.0 for mid in movie_ids}
        if self.user_factors_als is None or self.item_factors_als is None:
            return result
        uid = self.user_index.get(user_id)
        if uid is None:
            return result
        ids_arr = np.array(movie_ids)
        indices = np.array([self.movie_index.get(mid, -1) for mid in movie_ids])
        valid = indices >= 0
        if valid.any():
            scores = self.item_factors_als[indices[valid]] @ self.user_factors_als[uid]
            scores = np.clip(scores, 0.0, 1.0)
            for mid, score in zip(ids_arr[valid].tolist(), scores.tolist()):
                result[mid] = score
        return result

    def save(self, path: str = "ml_model.pkl"):
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path: str = "ml_model.pkl") -> "MLService":
        with open(path, "rb") as f:
            return pickle.load(f)