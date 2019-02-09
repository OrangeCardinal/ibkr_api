from logging                    import getLogger
from threading                  import Thread
from ibkr_api.base.api_calls    import ApiCalls

logger = getLogger(__name__)
class Actor(Thread):
    """

    """
    def __init__(self, name, code):
        super().__init__()
        self.name   = name  # Human Readable Name for the Actor
        self.code   = code  # Short descriptor for the Actor
        self.api    = ApiCalls()

    def run(self):
        """
        Main method for each Actor to implement
        :return:
        """
        raise NotImplementedError