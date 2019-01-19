from enum import Enum
#Legal ones are: 3 hours, 4 hours, 8 hours, 1 day

class BarSize(Enum):
    ####################
    # Access By Number #
    ####################
    ONE_HOUR        = '1 hour'
    ONE_DAY         = '1 day'
    ONE_MINUTE      = '1 min'
    ONE_MONTH       = '1M'
    ONE_WEEK        = '1W'
    ONE_SECOND      = '1 sec'
    TWO_HOUR        = '2 hours'
    TWO_MINUTES     = '2 mins'
    THREE_MINUTES   = '3 mins'
    FOUR_HOURS      = '4 hours'
    FIVE_MINUTES    = '5 mins'
    FIVE_SECONDS    = '5 secs'
    EIGHT_HOURS     = '8 hours'
    TEN_MINUTES     = '10 mins'
    TEN_SECONDS     = '10 secs'
    FIFTEEN_MINUTES = '15 mins'
    FIFTEEN_SECONDS = '15 secs'
    TWENTY_MINUTES  = '20 mins'
    THIRTY_MINUTES  = '30 mins'
    THIRTY_SECONDS  = '30 secs'

    ######################
    # Access by Duration #
    ######################
    SECONDS_1   = '1 sec'
    SECONDS_5   = '5 secs'
    SECONDS_10  = '10 secs'
    SECONDS_15  = '15 secs'
    SECONDS_30  = '30 secs'
    MINUTES_1   = '1 min'
    MINUTES_2   = '2 mins'
    MINUTES_3   = '3 mins'
    MINUTES_5   = '5 mins'
    MINUTES_10  = '10 mins'
    MINUTES_15  = '15 mins'
    MINUTES_20  = '20 mins'
    MINUTES_30  = '30 mins'
    MONTH_1     = '1M'
    HOUR_1      = '1 hour'
    HOUR_2      = '2 hours'
    HOUR_3      = '3 hours'
    HOUR_4      = '4 hours'
    HOUR_8      = '8 hours'
    DAY_1       = '1 day'
    WEEK_1      = '1W'