from ibkr_api.base.constants import UNSET_INTEGER, UNSET_DOUBLE

NO_ROW_NUMBER_SPECIFIED = -1

class ScannerSubscription(object):

    def __init__(self):
        self.numberOfRows = NO_ROW_NUMBER_SPECIFIED
        self.instrument = ""
        self.locationCode = ""
        self.scanCode = ""
        self.above_price = UNSET_DOUBLE
        self.below_price = UNSET_DOUBLE
        self.above_volume = UNSET_INTEGER
        self.market_cap_above = UNSET_DOUBLE
        self.market_cap_below = UNSET_DOUBLE
        self.moodyRatingAbove = ""
        self.moodyRatingBelow = ""
        self.spRatingAbove = ""
        self.spRatingBelow = ""
        self.maturityDateAbove = ""
        self.maturityDateBelow = ""
        self.couponRateAbove = UNSET_DOUBLE
        self.couponRateBelow = UNSET_DOUBLE
        self.excludeConvertible = False
        self.averageOptionVolumeAbove = UNSET_INTEGER
        self.scannerSettingPairs = ""
        self.stockTypeFilter = ""

    def __str__(self):
        s = "Instrument: %s, LocationCode: %s, ScanCode: %s" % (self.instrument, self.locationCode, self.scanCode)

        return s

