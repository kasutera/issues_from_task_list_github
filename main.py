import argparse
import os

from markdown.issue_parser import IssueParser
from github_cli.github_client import GithubClient
from github_cli.issue_generator import IssueGenerator

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue_url", help="Specify where issue markdown is")
    parser.add_argument("--execute", help="Actually execute creation",
                    action="store_true")
    parser.add_argument("--prefix", help="Prefix to add to issue title")
    args = parser.parse_args()
    is_dry_run = not args.execute
    url = args.issue_url
    title_prefix = args.prefix

    access_token = os.environ.get('GITHUB_ACCESS_TOKEN')
    assert access_token is not None, "Please export GITHUB_ACCESS_TOKEN"

    client = GithubClient(access_token)
    generator = IssueGenerator(client, is_dry_run)
    parser = IssueParser()

    issue_markdown = client.get_issue_body(url)
    if not parser.is_valid_md(issue_markdown):
        raise ValueError('Specified URL seems not to have valid markdown for this app')
    
    title_tuples = parser.get_titletuple_from_markdown(issue_markdown)
    for title_tuple in title_tuples:
        if title_prefix:
            title_tuple.add_prefix_issue_title(title_prefix)

        number_xxx = generator.generate(url, title_tuple.issue_title, title_tuple.issue_body)
        issue_markdown = issue_markdown.replace(title_tuple.src_str, number_xxx)
    
    print(issue_markdown)
