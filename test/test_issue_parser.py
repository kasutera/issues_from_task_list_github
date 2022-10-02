import unittest
from markdown.issue_parser import IssueParser, TitleTuple

class TestIssueParser(unittest.TestCase):

    def test_validate_md(self):
        body =  \
            '# hoge\n'   \
            '- [ ] po\n' \
            '    - fu\n' \
            '- [x] ke\n' \
            '## huga\n'  \
            '- surume'
        
        self.assertEqual(IssueParser.is_valid_md(body), True)

    def test_get_titlepair_from_markdown(self):
        body =  \
            '# hoge\n'      \
            '- [ ] po\n'    \
            '    - fu\n'    \
            '- [x] ke\n'    \
            '## huga\n'     \
            '- [ ] `kanye` to `ye`\n' \
            '- surume'
        
        expected = [
            TitleTuple('[ ] po', 'hoge - po', '- fu'),
            TitleTuple('[ ] `kanye` to `ye`', 'hoge - huga - `kanye` to `ye`'),
        ]

        ip = IssueParser()
        self.assertEqual(ip.get_titletuple_from_markdown(body), expected)
