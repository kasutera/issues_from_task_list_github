from multiprocessing.sharedctypes import Value
import re
from typing import List, Optional
from mistletoe import Document
from mistletoe.ast_renderer import ASTRenderer
import mistletoe.block_token as token
import mistletoe.span_token

class TitlePair():
    src_str: str
    issue_title: str

    def __init__(self, src_str, title) -> None:
        self.src_str = src_str
        self.issue_title = title
    
    def __str__(self) -> str:
        return str({
            'src_str': self.src_str,
            'title': self.issue_title,
        })
    
    def add_prefix_issue_title(self, prefix: str) -> 'TitlePair':
        self.issue_title = prefix + self.issue_title
        return self


class IssueParser():
    @classmethod
    def is_valid_md(cls, input: str) -> bool:
        for line in input.split('\n'):
            stripped = line.strip()
            is_bullet = re.match(r'^[-+*] ', stripped)
            is_title = re.match(r'^#+ ', stripped)
            is_empty_line = not stripped
            if not (is_bullet or is_title or is_empty_line):
                print(line)
                return False
        return True

    HEADINGS_MAX = 6
    headings: List[Optional[str]] = [None] * (HEADINGS_MAX + 1)

    @classmethod
    def _get_formatted_text_from_headings(cls, title: str, headings=headings) -> str:
        assert headings[0] is None, headings

        header = ""
        for heading in headings[1:]:
            if not heading:
                break
            header += heading + " - "
        
        return header + title

    
    def _parse_base_children_ast(self, base_children) -> List[TitlePair]:
        # heading[0] is always none

        def reset_headings_geq(number: int): 
            # number is 1-origin
            assert 1 <= number <= self.HEADINGS_MAX
            for i in range(number, self.HEADINGS_MAX + 1):
                self.headings[i] = None
        
        list = []
        for base_child in base_children:
            if isinstance(base_child, token.Heading):
                reset_headings_geq(base_child.level)
                assert len(base_child.children) == 1, base_child.children
                self.headings[base_child.level] = base_child.children[0].content
            elif isinstance(base_child, token.List):
                list.extend(
                    self._parse_list_ast(base_child)
                )
            else:
                raise ValueError(base_child)
        return list
    
    def _parse_list_ast(self, elem_list: token.List) -> List[TitlePair]:
        assert isinstance(elem_list, token.List), elem_list
        list = []
        for child in elem_list.children:
            assert isinstance(child, token.ListItem), child
            list.extend(
                self._parse_listitem_ast(child)
            )
        return list
    
    def _parse_listitem_ast(self, elem_listitem: token.ListItem) -> List[TitlePair]:
        assert isinstance(elem_listitem, token.ListItem), elem_listitem
        list = []
        for child in elem_listitem.children:
            if isinstance(child, token.Paragraph):
                list.extend(
                    self._parse_paragraph_ast(child)
                )
            elif isinstance(child, token.List):
                list.extend(
                    self._parse_list_ast(child)
                )
            else:
                raise ValueError(child)
        return list
    
    def _parse_paragraph_ast(self, elem_paragraph: token.Paragraph) -> List[TitlePair]:
        assert isinstance(elem_paragraph, token.Paragraph), elem_paragraph
        assert len(elem_paragraph.children) == 1, elem_paragraph.children
        list = []
        for child in elem_paragraph.children:
            if isinstance(child, mistletoe.span_token.RawText):
                toadd = self._parse_rawtext_ast(child)
                if toadd is not None:
                    list.append(toadd)
            else:
                raise ValueError(child)
        return list
    
    def _parse_rawtext_ast(self, elem_rawtext: mistletoe.span_token.RawText) -> Optional[TitlePair]:
        assert isinstance(elem_rawtext, mistletoe.span_token.RawText), elem_rawtext
        if elem_rawtext.content.startswith('[ ] '): 
            title_with_bracket = elem_rawtext.content
            title = title_with_bracket.replace('[ ] ', '', 1)
            formatted_title = self._get_formatted_text_from_headings(title)
            return TitlePair(src_str=title_with_bracket, title=formatted_title)
        else:
            return None

    
    def get_titlepair_from_markdown(self, md_str: str) -> List[TitlePair]:
        if not self.is_valid_md(md_str):
            raise ValueError(md_str)
        
        with ASTRenderer() as renderer:
            doc = Document(md_str)
            return self._parse_base_children_ast(doc.children)


if __name__ == "__main__":
    body =  \
        '# hoge\n'   \
        '- [ ] po\n' \
        '    - fu\n' \
        '- [x] ke\n' \
        '## huga\n'  \
        '- [ ] kanye\n' \
        '- surume'
    
    ip = IssueParser()
    title_pairs = ip.get_titlepair_from_markdown(body)

    print(",".join([str(p) for p in title_pairs]))
