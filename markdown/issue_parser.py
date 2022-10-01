from multiprocessing.sharedctypes import Value
import re
from typing import List, Optional
from mistletoe import Document
from mistletoe.ast_renderer import ASTRenderer
import mistletoe.block_token as token
import mistletoe.span_token

import sys
sys.path.append('contrib')
from contrib.markdown_renderer import MarkdownRenderer

class TitleTuple():
    src_str: str
    issue_title: str
    issue_body: Optional[str]

    def __init__(self, src_str: str, title: str, issue_body: Optional[str]=None) -> None:
        self.src_str = src_str
        self.issue_title = title
        self.issue_body = issue_body
    
    def __str__(self) -> str:
        return str({
            'src_str': self.src_str,
            'issue_title': self.issue_title,
            'issue_body': self.issue_body
        })
    
    def __repr__(self) -> str:
        return f'TitleTuple({self.src_str}, {self.issue_title}, {self.issue_body})'
    
    def __eq__(self, other) -> bool:
        if isinstance(other, TitleTuple):
            return self.src_str == other.src_str \
                and self.issue_title == other.issue_title \
                and self.issue_body == other.issue_body
        else:
            return False

    
    def set_issue_body(self, body: str) -> None:
        self.issue_body = body
    
    def add_prefix_issue_title(self, prefix: str) -> 'TitleTuple':
        self.issue_title = prefix + self.issue_title
        return self


class IssueParser():
    renderer: MarkdownRenderer

    def __init__(self):
        self.renderer = MarkdownRenderer().__enter__()

    def __del__(self) -> None:
        self.renderer.__exit__(None, None, None)

    @classmethod
    def is_valid_md(cls, input: str) -> bool:
        for line in input.split('\n'):
            stripped = line.strip()
            is_bullet = re.match(r'^[-+*] ', stripped)
            is_title = re.match(r'^#+ ', stripped)
            is_empty_line = not stripped
            if not (is_bullet or is_title or is_empty_line):
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

    
    def _parse_base_children_ast(self, base_children) -> List[TitleTuple]:
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
    
    def _parse_list_ast(self, elem_list: token.List) -> List[TitleTuple]:
        assert isinstance(elem_list, token.List), elem_list
        list = []
        for child in elem_list.children:
            assert isinstance(child, token.ListItem), child
            list.extend(
                self._parse_listitem_ast(child)
            )
        return list
    
    def _parse_listitem_ast(self, elem_listitem: token.ListItem) -> List[TitleTuple]:
        assert isinstance(elem_listitem, token.ListItem), elem_listitem
        list = []
        children = elem_listitem.children
        assert len(children) <= 2, children

        assert isinstance(children[0], token.Paragraph), children[0]
        title_tuple = self._parse_paragraph_ast(children[0])

        if len(children) == 2:
            child = children[1]
            assert isinstance(child, token.List), child

            if title_tuple:
                body = "\n".join(self.renderer.render_list(child))
                title_tuple.set_issue_body(body)
                list.append(title_tuple)

            list.extend(
                self._parse_list_ast(child)
            )
        elif title_tuple:
            list.append(title_tuple)
            
        return list
    
    def _parse_paragraph_ast(self, elem_paragraph: token.Paragraph) -> Optional[TitleTuple]:
        assert isinstance(elem_paragraph, token.Paragraph), elem_paragraph
        paragraph_text = '\n'.join(self.renderer.render_paragraph(elem_paragraph))

        # overwrite ast
        child = mistletoe.span_token.RawText(paragraph_text)
        elem_paragraph.children = [child]

        # for loop (len = 1)
        for child in elem_paragraph.children:
            if isinstance(child, mistletoe.span_token.RawText):
                return self._parse_rawtext_ast(child)
            else:
                raise ValueError(child)
    
    def _parse_rawtext_ast(self, elem_rawtext: mistletoe.span_token.RawText) -> Optional[TitleTuple]:
        assert isinstance(elem_rawtext, mistletoe.span_token.RawText), elem_rawtext
        if elem_rawtext.content.startswith('[ ] '): 
            title_with_bracket = elem_rawtext.content
            title = title_with_bracket.replace('[ ] ', '', 1)
            formatted_title = self._get_formatted_text_from_headings(title)
            return TitleTuple(src_str=title_with_bracket, title=formatted_title)
        else:
            return None

    
    def get_titletuple_from_markdown(self, md_str: str) -> List[TitleTuple]:
        if not self.is_valid_md(md_str):
            raise ValueError(md_str)
        
        doc = Document(md_str)
        return self._parse_base_children_ast(doc.children)


if __name__ == "__main__":
    body =  \
        '# hoge\n'   \
        '- [ ] po\n' \
        '    - fu\n' \
        '- [x] ke\n' \
        '## huga\n'  \
        '- [ ] `kanye` to `ye`\n' \
        '- surume'
    
    ip = IssueParser()
    title_pairs = ip.get_titletuple_from_markdown(body)

    print(",".join([str(p) for p in title_pairs]))
