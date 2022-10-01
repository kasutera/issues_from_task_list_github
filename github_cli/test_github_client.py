import os
import unittest
from github.Issue import Issue
from github_client import GithubClient

class TestGithubClient(unittest.TestCase):

    token = os.environ['GITHUB_ACCESS_TOKEN']

    def setUp(self) -> None:
        return super().setUp()

    def test_get_issue_from_url(self):
        url = 'https://github.com/PyGithub/PyGithub/issues/11'
        github_client = GithubClient(self.token)
        issue: Issue = github_client.get_issue_from_url(url)
        self.assertEqual(
            'https://api.github.com/repos/PyGithub/PyGithub', issue.repository.url
        )
        self.assertEqual(11, issue.number)
    
    def test_get_issue_body(self):
        github_client = GithubClient(self.token)
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