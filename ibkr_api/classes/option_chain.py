class OptionChain(object):
    def __init__(self, exchange, underlying_contract_id, underlying_symbol,multiplier,expirations,strikes):
        self.exchange = exchange
        self.underlying_contract_id     = underlying_contract_id
        self.underlying_symbol          = underlying_symbol
        self.multiplier                 = multiplier
        self.expirations                = expirations
        self.strikes                    = strikes


    def __str__(self):
        desc  = "\n{1} Option Chain (Contract ID #{0})\n".format(self.underlying_contract_id, self.underlying_symbol)
        desc += "-------------------\n"
        desc += "Exchange:   {0}\n".format(self.exchange)
        desc += "Multiplier: {0}\n".format(self.multiplier)

        desc += "Expirations\n"
        for i in range(len(self.expirations)):
            desc += "{:>10}".format(self.expirations[i])
            if i%3 == 2:
                desc += "\n"

        desc += "\nStrikes\n"
        for i in range(len(self.strikes)):
            desc += "{:>10}".format(self.strikes[i])
            if i%3 == 2:
                desc += "\n"

        return desc
