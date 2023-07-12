from jira import JIRA
from config import JIRA_API_TOKEN, JIRAURL
from . import PAGESIZE

class JIRA_TALKER:
    
    def __init__(self) -> None:
        self.jra = JIRA(JIRAURL, token_auth=JIRA_API_TOKEN)

    def get_issues(self, query):
        all = []
        startat = 0
        issues = self.jra.search_issues(query, maxResults=PAGESIZE, startAt=startat)
        all = all + issues
        while (len(issues) >= PAGESIZE):
            startat += PAGESIZE
            issues = self.jra.search_issues(query, maxResults=PAGESIZE, startAt=startat)
            all = all + issues
        return all
