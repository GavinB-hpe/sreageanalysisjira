
CLOSED = 0
FIXED = 1
# DEFECT select drop-down
ALL_DEFECTS = 0
TR1_DEFECTS = 1
FTC_DEFECTS = 2
TR2_DEFECTS = 2
MR1_DEFECTS = 2

TR1_QUERY = 'labels in (sentry-tr1)'
TR1_CLOSED_QUERY = '(labels in (sentry-tr1)) and (status != Done)'
TR1_FIXED_QUERY = '(labels in (sentry-tr1)) and (resolution = Unresolved)'
FTC_QUERY = 'labels in (sentry-gse)'
FTC_CLOSED_QUERY = '(labels in (sentry-gse)) and (status != Done)'
FTC_FIXED_QUERY = '(labels in (sentry-gse)) and (resolution = Unresolved)'
TR2_QUERY = 'labels in (sentry-tr2)'
TR2_CLOSED_QUERY = '(labels in (sentry-tr2)) and (status != Done)'
TR2_FIXED_QUERY = '(labels in (sentry-tr2)) and (resolution = Unresolved)'
MR1_QUERY = 'labels in (sentry-mr1)'
MR1_CLOSED_QUERY = '(labels in (sentry-mr1)) and (status != Done)'
MR1_FIXED_QUERY = '(labels in (sentry-mr1)) and (resolution = Unresolved)'
ALL_QUERY = 'labels in (sentry-gse, sentry-tr1, sentry-tr2, sentry-mr1)'
ALL_CLOSED_QUERY = '(labels in (sentry-gse, sentry-tr1, sentry-tr2, sentry-mr1)) and (status != Done)'
ALL_FIXED_QUERY = '(labels in (sentry-gse, sentry-tr1, sentry-tr2, sentry-mr1)) and (resolution = Unresolved)'

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
    if choice == TR2_DEFECTS:
        if which == CLOSED:
            return TR2_CLOSED_QUERY
        if which == FIXED:
            return TR2_FIXED_QUERY
    if choice == MR1_DEFECTS:
        if which == CLOSED:
            return MR1_CLOSED_QUERY
        if which == FIXED:
            return MR1_FIXED_QUERY
    assert False, "Bad selection"
    return None