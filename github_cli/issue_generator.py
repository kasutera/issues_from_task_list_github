from typing import Dict, Optional, Union
from .github_client import GithubClient
from github.Issue import Issue
from github.Repository import Repository
from github.AuthenticatedUser import AuthenticatedUser

class IssueGenerator():
    client: GithubClient
    dry_run: bool
    issue_no_dry_run: int = 10000

    def __init__(self, client: GithubClient, dry_run: bool) -> None:
        self.client = client
        self.dry_run = dry_run

    def _generate_issue(
        self, repo: Repository, title: str, body: Optional[str], assignee: AuthenticatedUser
    ) -> Issue:
        assert not self.dry_run
        if body is not None:
            return repo.create_issue(title=title, body=body, assignee=assignee.name)
        else:
            return repo.create_issue(title=title, assignee=assignee.name)
    
    def _dry_generate_issue(
        self, repo: Repository, title: str, body: Optional[str], assignee: AuthenticatedUser
    ) -> Dict[str, Optional[str]]:
        assert self.dry_run
        return {
            "repository": repo.url,
            "issue_title": title,
            "assignee": assignee.name,
            "body": body
        }

    def _generate_issue_union(
        self, repo: Repository, title: str, body: Optional[str], assignee: AuthenticatedUser
    ) -> Union[Dict[str, Optional[str]], Issue]:
        if self.dry_run:
            return self._dry_generate_issue(repo, title, body, assignee)
        else:
            return self._generate_issue(repo, title, body, assignee)

    def generate(self, md_issue_url: str, title: str, body: Optional[str]=None) -> str:
        """generate issue

        Args:
            md_issue_url (str): issue url (create another issue on this repository)
            title (str): title of issue

        Returns:
            str: #xxx (issue number)
        """
        issue = self.client.get_issue_from_url(md_issue_url)
        assignee = self.client.get_myself()
        dict_or_issue = self._generate_issue_union(issue.repository, title, body, assignee)

        if isinstance(dict_or_issue, dict):
            print(dict_or_issue)
            self.issue_no_dry_run += 1
            return f'#{self.issue_no_dry_run}'
        elif isinstance(dict_or_issue, Issue):
            return f'#{dict_or_issue.number}'
        else:
            raise ValueError(dict_or_issue)