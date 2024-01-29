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

            self.accumulated_close_changes = \
                [i for i in accumulate(token.close_changes, lambda v, n: v * (1 + n), initial=1)][1:]
            self.growth_rate: float = \
                max((change - 1) / (days + 1) for days, change in enumerate(self.accumulated_close_changes))

        def __str__(self):
            return f"'{self.name}': {self.growth_rate}"

        def is_decreasing(self) -> bool:
            return self.accumulated_close_changes[0] < 1

        def is_increasing(self) -> bool:
            return all(change > 0.01 for change in self.token.close_changes[:3])

        def get_buy_price(self, last_low: float, last_high: float) -> float:
            new_high = last_high * (1 + self.token.high_changes[0])
            new_low = last_low * (1 + self.token.low_changes[0])
            spread = new_high - new_low
            return new_high - 0.25 * spread

    class HistoryEntry:
        def __init__(self, prediction: Prediction, evaluations: dict[str, HoldStrategy.Evaluation], desired: list[str],
                     held: list[str], actions: list[Action]):
            self.predictions: Prediction = prediction
            self.evaluations: dict[str, HoldStrategy.Evaluation] = evaluations
            self.desired: list[str] = desired
            self.held: list[str] = held
            self.actions: list[Action] = actions

    def __init__(self):
        self.history: list[HoldStrategy.HistoryEntry] = []

    def apply(self, prediction: Prediction, assets: Assets, last_prices: dict[str, tuple[float, float]]) -> list[Action]:
        evaluations = [self.Evaluation(name, token) for name, token in prediction.results.items()]
        evaluations.sort(key=lambda e: e.growth_rate, reverse=True)

        desired = [token for token, _ in zip((e.name for e in evaluations if e.is_increasing()), range(3))]
        evaluations_per_token: dict[str, HoldStrategy.Evaluation] = \
            {evaluation.name: evaluation for evaluation in evaluations}
        held = list(assets.held())
        actions = []

        # Sell held tokens that are expected to decrease
        for token in held:
            if evaluations_per_token[token].is_decreasing():
                actions.append(Action("market sell", token, assets.stocks[token]))

        # Buy desired tokens
        if assets.money > 1e-2:
            available_money = assets.money
            for token in desired:
                entry_amount = available_money * 0.4
                available_money -= entry_amount

                buy_price = evaluations_per_token[token].get_buy_price(*last_prices[token])
                actions.append(Action("limit buy", token, entry_amount / buy_price, buy_price))

        self.history.append(HoldStrategy.HistoryEntry(prediction, evaluations_per_token, desired, held, actions))

        return actions
