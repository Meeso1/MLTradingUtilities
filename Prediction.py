from numpy import ndarray


class Prediction:
    def __init__(self, decoded_results_dict: dict[str, ndarray[float]]):
        self.results: dict[str, TokenPrediction] = \
            {token: TokenPrediction(result) for token, result in decoded_results_dict.items()}


class TokenPrediction:
    def __init__(self, result: ndarray[float]):
        self.close_changes: ndarray[float] = result[:, 0]
        self.high_changes: ndarray[float] = result[:, 1]
        self.low_changes: ndarray[float] = result[:, 2]
