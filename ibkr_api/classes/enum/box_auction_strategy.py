from enum import IntEnum


class BoxAuctionStrategy(IntEnum):
    """
    Order.auction_strategy values (used only for BOX orders)
    """
    MATCH           = 1
    IMPROVEMENT     = 2
    TRANSPARENT     = 3