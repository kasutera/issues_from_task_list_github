import os
import unittest
from github.Issue import Issue
from github_cli.github_client import GithubClient
from github_cli.issue_generator import IssueGenerator

class TestIssueGenerator(unittest.TestCase):

    token = os.environ['GITHUB_ACCESS_TOKEN']

    def setUp(self) -> None:
        return super().setUp()

    def test_generate_issue_dry(self):
        url = 'https://github.com/kasutera/issues_from_task_list_github/issues/1'
        client = GithubClient(self.token)
        issue_generator = IssueGenerator(client, True)
        title = 'test issue'
        body = '- this is body\n' \
            '- with bullet'
        issue: Issue = client.get_issue_from_url(url)
        actual = issue_generator._dry_generate_issue(
            issue.repository, title, body, client.get_myself()
        )
        expected = {
            "repository": 'https://api.github.com/repos/kasutera/issues_from_task_list_github',
            "issue_title": title,
            "body": body,
            "assignee": 'kasutera'
        }
        self.assertEqual(actual, expected)
    
    def test_generate_issue(self):
        # dry run
        client = GithubClient(self.token)
        issue_generator = IssueGenerator(client, True)
        url = 'https://github.com/kasutera/issues_from_task_list_github/issues/1'
        title = 'test issue'
        title_to_be_replaced = issue_generator.generate(url, title)
        self.assertEqual(title_to_be_replaced, '#10001')
