from enum import Enum

class ReportType(Enum):
        FINANCIAL_SUMMARY    = "ReportsFinSummary"      ,
        OWNERSHIP            = "ReportsOwnership"       ,
        SNAPSHOT             = "ReportSnapshot"         ,
        FINANCIAL_STATEMENTS = "ReportsFinStatements"   ,
        RESC                 = "RESC"                   ,
        CALENDAR             = "CalendarReport"