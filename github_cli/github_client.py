import re
from typing import Dict, Union
from github import Github
from github.Issue import Issue
from github.Repository import Repository
from github.AuthenticatedUser import AuthenticatedUser

# - 指定されたissue内容を読み込める
# - issueを生成できる
#   - ↑と同一のディレクトリ
#   - assigneeを指定できる
#       - usernameが取れる
# - dry runをできるようにしとく

class GithubClient():

    BASE_URL='https://github.com/'
    dry_run: bool
    py_github: Github

    def __init__(self, access_token: str, dry_run: bool) -> None:
        self.dry_run = dry_run
        self.py_github = Github(access_token)
    
    def _get_myself(self) -> AuthenticatedUser:
        return self.py_github.get_user()
    
    def _generate_issue(self, repo: Repository, title: str, assignee: AuthenticatedUser) -> Issue:
        assert not self.dry_run
        return repo.create_issue(title=title, assignee=assignee.name)
    
    def _dry_generate_issue(self, repo: Repository, title: str, assignee: AuthenticatedUser) -> Dict[str, str]:
        assert self.dry_run
        return {
            "repository": repo.url,
            "issue_title": title,
            "assignee": assignee.name
        }

    def _generate_issue_union(self, repo: Repository, title: str, assignee: AuthenticatedUser) -> Union[Dict[str, str], Issue]:
        if self.dry_run:
            return self._dry_generate_issue(repo, title, assignee)
        else:
            return self._generate_issue(repo, title, assignee)
    
    def _issue_from_url(self, url: str) -> Issue:
        assert re.match('^' + self.BASE_URL + r'[^/]+/[^/]+/issues/\d+$', url), url

        url_edit = url.replace(self.BASE_URL, '')

        repo_str, issue_number_str = url_edit.split('/issues/')
        issue_number: int = int(issue_number_str)
        repo = self.py_github.get_repo(repo_str)
        return repo.get_issue(issue_number)

    def generate_issue(self, md_issue_url: str, title: str) -> str:
        """generate issue

        Args:
            md_issue_url (str): issue url (create another issue on this repository)
            title (str): title of issue

        Returns:
            str: #xxx (issue number), or replaced title if dry-run
        """
        issue = self._issue_from_url(md_issue_url)
        assignee = self._get_myself()
        dict_or_issue = self._generate_issue_union(issue.repository, title, assignee)

        if isinstance(dict_or_issue, dict):
            print(dict_or_issue)
            return 'dry-run: replaced({})'.format(dict_or_issue['issue_title'])
        else:
            return f'#{dict_or_issue.number}'
    
    def get_issue_body(self, md_issue_url: str) -> str:
        return self._issue_from_url(md_issue_url).body.replace('\r\n', '\n')