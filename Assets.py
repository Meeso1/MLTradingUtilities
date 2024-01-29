from typing import Iterable


class Assets:
    def __init__(self, tokens: list[str], initial: float = 100):
        if initial <= 0:
            raise ValueError("Initial value must be positive")

        self._initial: float = initial
        self.money: float = initial
        self.stocks: dict[str, float] = {token: 0 for token in tokens}

    def buy(self, token: str, stock_amount: float, price: float) -> None:
        if token not in self.stocks:
            raise ValueError(f"Unknown token: '{token}'")

        if stock_amount <= 0:
            raise ValueError("Stock amount must be positive")

        if price <= 0:
            raise ValueError("Price must be positive")

        if self.money < stock_amount * price:
            raise ValueError(f"Not enough money: {self.money} available, {stock_amount * price} required")

        self.money -= stock_amount * price
        self.stocks[token] += stock_amount

    def sell(self, token: str, stock_amount: float, price: float) -> None:
        if token not in self.stocks:
            raise ValueError(f"Unknown token: '{token}'")

        if stock_amount <= 0:
            raise ValueError("Stock amount must be positive")

        if price <= 0:
            raise ValueError("Price must be positive")

        if self.stocks[token] < stock_amount:
            raise ValueError(f"Not enough stocks: {self.stocks[token]} available, {stock_amount} required")

        self.money += stock_amount * price
        self.stocks[token] -= stock_amount

    def current_return(self, prices_dict: dict[str, float]) -> float:
        value = sum((amount * prices_dict[token]) for token, amount in self.stocks.items())
        return (value + self.money) / self._initial - 1

    def held(self) -> Iterable[str]:
        for token, value in self.stocks.items():
            if value > 0:
                yield token
