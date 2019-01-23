class OrderState(object):

    def __init__(self):
        self.status= ""

        self.init_margin_before= ""
        self.maintenance_margin_before= ""
        self.equity_with_loan_before= ""
        self.init_margin_change= ""
        self.maintenance_margin_change= ""
        self.equity_with_loan_change= ""
        self.init_margin_after= ""
        self.maintenance_margin_after= ""
        self.equity_with_loan_after= ""

        self.commission = 0.0
        self.min_commission = 0.0
        self.max_commission = 0.0
        self.commission_currency = ""
        self.warning_text = ""