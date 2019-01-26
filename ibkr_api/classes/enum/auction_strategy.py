from enum import IntEnum

class AuctionStrategy(IntEnum):
    """
    auction_strategy values for a given Order
    """
    AUCTION_UNSET       =   0
    AUCTION_MATCH       =   1
    AUCTION_IMPROVEMENT =   2
    AUCTION_TRANSPARENT =   3