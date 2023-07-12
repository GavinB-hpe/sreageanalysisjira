import copy
import logging
import jira_talker
import time

from datetime import datetime

SECS_PER_HOUR = 3600

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)
logger.warning("Warnings are visible")

result_cache_set = {}  # will hold result caches per query


class DefectInfoCache:
    """
    Hold defect info list and time info
    """
    DEFAULT_VALIDITY = 300  # data is good for 300 seconds 

    def __init__(self, validity=DEFAULT_VALIDITY):
        self.when = None
        self.data = None
        self.validity = validity

    def get(self):
        if self.when is None or self.data is None:
            return None
        if time.time() - self.when > self.validity:
            logger.warning("Data is stale")
            return None
        logger.warning("Data from cache")
        return self.data

    def put(self, data):
        self.when = time.time()
        self.data = copy.deepcopy(data)
        logger.warning("Copy took {} seconds".format(int(time.time() - self.when)))


class DefectInfo:
    """
    Just used to hold attributes
    """

    interesting_attributes = ['id']
    interesting_fields = ['created',
                          'resolutiondate',
                          'resolution',
                          'assignee',
                          'summary',
                          'status',
                          'project',
                          'reporter',
                          'updated']

    def __init__(self):
        pass


def calculate_age(di):
    """
    calculate_age works out the age of the bug from creation to either now (if not closed) or
    closed. NOTE - this implies that we ignore changes made after a bug is closed.
    :param di: object holding defect data as attributes
    :return:
    """
    ctime = datetime.strptime(di.created, jira_talker.jiratimeformat)
    if di.resolutiondate is None:
        etime = datetime.now(ctime.tzinfo)  # create with same tz as created
    else:
        etime = datetime.strptime(di.resolutiondate, jira_talker.jiratimeformat)
    age = etime - ctime
    return int(age.total_seconds() / SECS_PER_HOUR)


def get_defects(jra, query):
    global result_cache_set
    if result_cache_set.get(query) is None:
        result_cache_set[query] = DefectInfoCache()
    cached_info = result_cache_set[query].get()
    if cached_info is None:
        logger.warning("Getting data set from Jira ...")
        start = time.time()
        defects_from_jira = jra.get_issues(query)
        logger.warning("  done")
        logger.warning("  took {} seconds".format(int(time.time() - start)))
        defect_info = []
        for d in defects_from_jira:
            di = DefectInfo()
            setattr(di, 'id', d.id)
            for ia in DefectInfo.interesting_fields:
                if hasattr(d.fields, ia):
                    setattr(di, ia, getattr(d.fields, ia))
            setattr(di, 'Age', calculate_age(di))
            defect_info.append(di)
        logger.warning("Putting data in cache")
        result_cache_set[query].put(defect_info)
    else:
        logger.warning("Getting data from cache")
        defect_info = cached_info
    if defect_info is None:
        logger.fatal("No defects returned from Jira!")
        return None
    return defect_info


def get_defects_filtered(rt, query):
    unfiltered = get_defects(rt, query)
    return unfiltered
