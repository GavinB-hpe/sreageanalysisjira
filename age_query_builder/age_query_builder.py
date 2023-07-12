
CLOSED = 0
FIXED = 1
# DEFECT select drop-down
ALL_DEFECTS = 0
TR1_DEFECTS = 1
FTC_DEFECTS = 2

TR1_QUERY = 'labels in (sentry-tr1)'
TR1_CLOSED_QUERY = TR1_QUERY
TR1_FIXED_QUERY = TR1_QUERY
FTC_QUERY = 'labels in (sentry-gse)'
FTC_CLOSED_QUERY = FTC_QUERY
FTC_FIXED_QUERY = FTC_QUERY
ALL_QUERY = 'labels in (sentry-gse, sentry-tr1)'
ALL_CLOSED_QUERY = ALL_QUERY
ALL_FIXED_QUERY = ALL_QUERY

def get_query(which=CLOSED, choice=ALL_DEFECTS):
    if choice == ALL_DEFECTS:
        if which == CLOSED:
           return ALL_CLOSED_QUERY
        if which == FIXED:
            return ALL_FIXED_QUERY
    if choice == TR1_DEFECTS:
        if which == CLOSED:
            return TR1_CLOSED_QUERY
        if which == FIXED:
            return TR1_FIXED_QUERY
    if choice == FTC_DEFECTS:
        if which == CLOSED:
            return FTC_CLOSED_QUERY
        if which == FIXED:
            return FTC_FIXED_QUERY
    assert False, "Bad selection"
    return None