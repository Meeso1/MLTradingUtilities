import random
from Assets import Assets


class Action:
    def __init__(self, action_kind: str, token: str, amount: float, price: float | None = None):
        if action_kind not in {"limit buy", "limit sell", "market buy", "market sell"}:
            raise ValueError(f"Unknown action kind: {action_kind}")

        if action_kind not in {"limit buy", "limit sell"} and price is None:
            raise ValueError("Price is required for limit orders")

        if price is not None and price <= 0:
            raise ValueError("Price must be positive")

        self.action_kind: str = action_kind
        self.token: str = token
        self.amount: float = amount
        self.price: float | None = price
        self.executed: bool = False

    def apply(self, assets: Assets, high: float, low: float) -> None:
        match self.action_kind:
            case "limit buy":
                if low >= self.price:
                    return
                assets.buy(self.token, self.amount, self.price)
            case "market buy":
                assets.buy(self.token, self.amount, random.uniform(low, high))
            case "limit sell":
                if high <= self.price:
                    return
                assets.sell(self.token, self.amount, self.price)
            case "market sell":
                assets.sell(self.token, self.amount, random.uniform(low, high))
            case _:
                raise ValueError(f"Unknown action kind: {self.action_kind}")

        self.executed = True

    def __str__(self):
        return f"{self.action_kind} {self.amount} {self.token}" + \
                f"{('' if self.price is None else f' @ {self.price}')}{'' if self.executed else '(not executed)'}"
