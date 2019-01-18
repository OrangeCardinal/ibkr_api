from enum import IntEnum

class AuctionStrategy(IntEnum):
    """
    Order.auction_strategy values (used only for BOX orders)
    """
    MATCH           = 1
    IMPROVEMENT     = 2
    TRANSPARENT     = 3