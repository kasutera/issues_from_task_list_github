import unittest
from issue_parser import IssueParser, TitlePair

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
            '- [ ] kanye\n' \
            '- surume'
        
        expected = [
            TitlePair('[ ] po', 'hoge - po'),
            TitlePair('[ ] kanye', 'hoge - huga - kanye'),
        ]
    

if __name__ == "__main__":
    unittest.main()