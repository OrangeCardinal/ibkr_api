class Scanner(object):
    NO_ROW_NUMBER_SPECIFIED = -1

    def __init__(self, **kwargs):
        self.numberOfRows                   = Scanner.NO_ROW_NUMBER_SPECIFIED
        self.instrument                     = ""
        self.location_code                  = ""
        self.scan_code                      = ""
        self.above_price                    = ""
        self.below_price                    = ""
        self.above_volume                   = ""
        self.market_cap_above               = ""
        self.market_cap_below               = ""
        self.moody_rating_above             = ""
        self.moody_rating_below             = ""
        self.sp_rating_above                = ""
        self.sp_rating_below                = ""
        self.maturity_date_above            = ""
        self.maturity_date_below            = ""
        self.coupon_rate_above              = ""
        self.coupon_rate_below              = ""
        self.exclude_convertible            = False
        self.average_option_volume_above    = ""
        self.scanner_setting_pairs          = ""
        self.stock_type_filter              = ""

        # Assign any attributes from keyword arguments as needed
        for arg, val in kwargs.items():
            if hasattr(self,arg):
                setattr(self,arg,val)


    def __str__(self):
        s  = "Market Scanner\n"
        s += "Instrument: {0}\n".format(self.instrument)
        s += "Location Code: {0}\n".format(self.location_code)
        s += "Scan Code: {0}\n".format(self.scan_code)

        return s

