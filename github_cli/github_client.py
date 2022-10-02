import re
from github import Github
from github.Issue import Issue
from github.Repository import Repository
from github.AuthenticatedUser import AuthenticatedUser

class GithubClient():

    BASE_URL='https://github.com/'
    py_github: Github

    def __init__(self, access_token: str) -> None:
        self.py_github = Github(access_token)
    
    
    def get_myself(self) -> AuthenticatedUser:
        return self.py_github.get_user()
    
    def get_issue_from_url(self, url: str) -> Issue:
        assert re.match('^' + self.BASE_URL + r'[^/]+/[^/]+/issues/\d+$', url), url

        url_edit = url.replace(self.BASE_URL, '')

        repo_str, issue_number_str = url_edit.split('/issues/')
        issue_number: int = int(issue_number_str)
        repo = self.py_github.get_repo(repo_str)
        return repo.get_issue(issue_number)
    
    def get_repo_from_issue_url(self, url: str) -> Repository:
        return self.get_issue_from_url(url).repository

    def get_repo_from_url(self, url: str) -> Repository:
        assert re.match('^' + self.BASE_URL + r'[^/]+/[^/]+/*$', url), url

        url_edit = url.replace(self.BASE_URL, '')
        url_edit = re.sub(r'/*$', '', url_edit)
        return self.py_github.get_repo(url_edit)
    
    def get_issue_body(self, md_issue_url: str) -> str:
        return self.get_issue_from_url(md_issue_url).body.replace('\r\n', '\n')
