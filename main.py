import argparse
from dataclasses import dataclass
import os
from pathlib import Path
from sys import prefix

from github.Repository import Repository

from markdown.issue_parser import IssueParser
from github_cli.github_client import GithubClient
from github_cli.issue_generator import IssueGenerator

@dataclass(frozen=True)
class Args():
    repo: Repository
    issue_markdown_txt: str
    is_dry_run: bool
    prefix_issue_title: str

def handle_args(client: GithubClient) -> Args:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--issue_url",
        help="Specify where issue markdown is (repository set to that issue)",
    )
    parser.add_argument(
        "--issue_path",
        help="Specify where issue markdown is (please specify --repository)",
    )
    parser.add_argument(
        "--repository",
        help="Repository URL"
    )
    parser.add_argument(
        "--execute",
        help="Actually execute creation",
        action="store_true"
    )
    parser.add_argument(
        "--prefix",
        help="Prefix to add to issue title"
    )
    args = parser.parse_args()
    is_dry_run = not args.execute
    url = args.issue_url
    issue_path = args.issue_path
    repository = args.repository
    title_prefix = args.prefix

    if url is not None and issue_path is None and repository is None:
        issue_markdown = client.get_issue_body(url)
        repo = client.get_repo_from_issue_url(url)
        return Args(repo, issue_markdown, is_dry_run, prefix)

    elif url is None and issue_path is not None and repository is not None:
        path = Path(issue_path)
        assert path.exists, path
        issue_markdown = path.read_text()
        repo = client.get_repo_from_url(url)

        return Args(repo, issue_markdown, is_dry_run, prefix)
    
    else:
        parser.print_help()
        raise 


def main():
    access_token = os.environ.get('GITHUB_ACCESS_TOKEN')
    assert access_token is not None, "Please export GITHUB_ACCESS_TOKEN"

    client = GithubClient(access_token)

    args = handle_args(client)
    generator = IssueGenerator(client, args.is_dry_run)
    parser = IssueParser()

    issue_markdown_txt = args.issue_markdown_txt

    if not parser.is_valid_md(issue_markdown_txt):
        raise ValueError('Specified element seems not to have valid markdown for this app')
    
    title_tuples = parser.get_titletuple_from_markdown(issue_markdown_txt)
    for title_tuple in title_tuples:
        if args.prefix_issue_title:
            title_tuple.add_prefix_issue_title(args.prefix_issue_title)

        number_xxx = generator.generate(args.repo, title_tuple.issue_title, title_tuple.issue_body)
        issue_markdown_txt = issue_markdown_txt.replace(title_tuple.src_str, number_xxx)
    
    print(issue_markdown_txt)

main()
