from ibkr_api.classes.contracts.contract import Contract

class Option(Contract):
    def __init__(self, symbol, right, strike, exchange="SMART"):
        super().__init__()
        