from __future__ import annotations
from itertools import accumulate
from MLTradingUtilities.Action import Action
from MLTradingUtilities.Assets import Assets
from MLTradingUtilities.Prediction import Prediction, TokenPrediction


class HoldStrategy:
    class Evaluation:
        def __init__(self, token_name: str, token: TokenPrediction):
            self.name: str = token_name
            self.token: TokenPrediction = token

            acc_close_changes = [i for i in accumulate(token.close_changes, lambda v, n: v * (1 + n), initial=1)][1:]
            self.growth_rate: float = max(change / (days + 1) for days, change in enumerate(acc_close_changes))

        def __str__(self):
            return f"'{self.name}': {self.growth_rate}"

    class HistoryEntry:
        def __init__(self, prediction: Prediction, evaluations: list[HoldStrategy.Evaluation], desired: list[str],
                     held: list[str], actions: list[Action]):
            self.predictions: Prediction = prediction
            self.evaluations: list[HoldStrategy.Evaluation] = evaluations
            self.desired: list[str] = desired
            self.held: list[str] = held
            self.actions: list[Action] = actions

    def __init__(self):
        self.history: list[HoldStrategy.HistoryEntry] = []

    def apply(self, prediction: Prediction, assets: Assets) -> list[Action]:
        evaluations = [self.Evaluation(name, token) for name, token in prediction.results.items()]
        evaluations.sort(key=lambda e: e.growth_rate, reverse=True)

        held = list(assets.held())
        desired = [evaluation.name for evaluation, _ in zip(evaluations, range(3))]
        actions = []

        # Sell unwanted tokens
        for token in held:
            if token in desired:
                continue
            actions.append(Action("market sell", token, assets.stocks[token]))

        # Buy desired tokens
        if assets.money > 1e-2:
            to_buy = desired
            for token in held:
                to_buy.remove(token)
            for token in to_buy:
                actions.append(Action("market buy", token, assets.money / len(to_buy)))

        self.history.append(HoldStrategy.HistoryEntry(prediction, evaluations, desired, held, actions))

        return actions
