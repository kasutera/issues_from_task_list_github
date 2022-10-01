import os
import unittest
from github.Issue import Issue
from github_client import GithubClient

class TestGithubClient(unittest.TestCase):

    token = os.environ['GITHUB_ACCESS_TOKEN']

    def setUp(self) -> None:
        return super().setUp()

    def test_issue_from_url(self):
        url = 'https://github.com/PyGithub/PyGithub/issues/11'
        github_client = GithubClient(self.token, True)
        issue: Issue = github_client._issue_from_url(url)
        self.assertEqual(
            'https://api.github.com/repos/PyGithub/PyGithub', issue.repository.url
        )
        self.assertEqual(11, issue.number)
    
    def test_generate_issue_dry(self):
        url = 'https://github.com/kasutera/issues_from_task_list_github/issues/1'
        github_client = GithubClient(self.token, True)
        title = 'test issue'
        issue: Issue = github_client._issue_from_url(url)
        actual = github_client._dry_generate_issue(
            issue.repository, title, github_client._get_myself()
        )
        expected = {
            "repository": 'https://api.github.com/repos/kasutera/issues_from_task_list_github',
            "issue_title": title,
            "assignee": 'kasutera'
        }
        self.assertEqual(actual, expected)
    
    def test_generate_issue(self):
        # dry run
        github_client = GithubClient(self.token, dry_run=True)
        url = 'https://github.com/kasutera/issues_from_task_list_github/issues/1'
        title = 'test issue'
        title_to_be_replaced = github_client.generate_issue(url, title)
        self.assertEqual(title_to_be_replaced, 'dry-run: replaced(test issue)')

    def test_get_issue_body(self):
        github_client = GithubClient(self.token, dry_run=True)
        url = 'https://github.com/kasutera/issues_from_task_list_github/issues/2'
        expected_body =  \
            '# hoge\n'   \
            '- [ ] po\n' \
            '    - fu\n' \
            '- [x] ke\n' \
            '## huga\n'  \
            '- surume'
        actual_body = github_client.get_issue_body(url)
        self.assertEqual(expected_body, actual_body)


if __name__ == "__main__":
    unittest.main()