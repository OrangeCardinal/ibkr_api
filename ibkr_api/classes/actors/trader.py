from ibkr_api.classes.actors.actor import Actor

class Trader(Actor):
    """
    A Trader as any actor that
    1. Make only one trade at a time
    2. Implements the methods listed below
    """

    def __init__(self, positions):
        self.positions = []


    def in_trade(self):
        """
        Check if there is an active trade currently or not
        :return: True, if there is an existing trade
        """
        raise NotImplementedError

    def back_test(self, start_date):
        """
        Provides a backtest result for the given trader
        :param start_date:
        :return:
        """
        raise NotImplementedError

    def can_close_trade(self):
        """
        Check if the
        :return: True
        """

    def can_modify_trade(self):
        """

        :return:
        """
        raise NotImplementedError

    def can_open_trade(self):
        """

        :return:
        """
        raise NotImplementedError

    def close_trade(self):
        """
        Close the trade, and do any necessary post processing (writing to db, etc)
        :return:
        """
        raise NotImplementedError

    def open_trade(self):
        """
        Opens an trade, and handle any post processing (writing to db)
        :return:
        """
        raise NotImplementedError

    def modify_trade(self):
        """
        Update
        :return:
        """
        raise NotImplementedError



    def run(self):
        if self.in_trade() and self.can_close_trade():
            self.close_trade()
        elif self.can_modify_trade():
            self.modify_trade()
        elif self.can_open_trade():
            self.open_trade()


