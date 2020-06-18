import re
from .scanner import ScannerParser, Matcher, unikey
from .inline_parser import ESCAPE_CHAR, LINK_LABEL

_TRIM_4 = re.compile(r'^ {1,4}')
_EXPAND_TAB = re.compile(r'^( {0,3})\t', flags=re.M)
_INDENT_CODE_TRIM = re.compile(r'^ {1,4}', flags=re.M)
_BLOCK_QUOTE_TRIM = re.compile(r'^ {0,1}', flags=re.M)
_BLOCK_QUOTE_LEADING = re.compile(r'^ *>', flags=re.M)
_BLOCK_TAGS = {
    'address', 'article', 'aside', 'base', 'basefont', 'blockquote',
    'body', 'caption', 'center', 'col', 'colgroup', 'dd', 'details',
    'dialog', 'dir', 'div', 'dl', 'dt', 'fieldset', 'figcaption',
    'figure', 'footer', 'form', 'frame', 'frameset', 'h1', 'h2', 'h3',
    'h4', 'h5', 'h6', 'head', 'header', 'hr', 'html', 'iframe',
    'legend', 'li', 'link', 'main', 'menu', 'menuitem', 'meta', 'nav',
    'noframes', 'ol', 'optgroup', 'option', 'p', 'param', 'section',
    'source', 'summary', 'table', 'tbody', 'td', 'tfoot', 'th', 'thead',
    'title', 'tr', 'track', 'ul'
}
_BLOCK_HTML_RULE6 = (
    r'</?(?:' + '|'.join(_BLOCK_TAGS) + r')'
    r'(?: +|\n|/?>)[\s\S]*?'
    r'(?:\n{2,}|\n*$)'
)
_BLOCK_HTML_RULE7 = (
    # open tag
    r'<(?!script|pre|style)([a-z][\w-]*)(?:'
    r' +[a-zA-Z:_][\w.:-]*(?: *= *"[^"\n]*"|'
    r''' *= *'[^'\n]*'| *= *[^\s"'=<>`]+)?'''
    r')*? */?>(?=\s*\n)[\s\S]*?(?:\n{2,}|\n*$)|'
    # close tag
    r'</(?!script|pre|style)[a-z][\w-]*\s*>(?=\s*\n)[\s\S]*?(?:\n{2,}|\n*$)'
)

_PARAGRAPH_SPLIT = re.compile(r'\n{2,}')
_LIST_BULLET = re.compile(r'^ *([\*\+-]|\d+[.)])')


class BlockParser(ScannerParser):
    scanner_cls = Matcher

    NEWLINE = re.compile(r'\n+')
    DEF_LINK = re.compile(
        r' {0,3}\[(' + LINK_LABEL + r')\]:(?:[ \t]*\n)?[ \t]*'
        r'<?([^\s>]+)>?(?:[ \t]*\n)?'
        r'(?: +["(]([^\n]+)[")])? *\n+'
    )

    AXT_HEADING = re.compile(
        r' {0,3}(#{1,6})(?!#+)(?: *\n+|'
        r'\s+([^\n]*?)(?:\n+|\s+?#+\s*\n+))'
    )
    SETEX_HEADING = re.compile(r'([^\n]+)\n *(=|-){2,}[ \t]*\n+')
    THEMATIC_BREAK = re.compile(
        r' {0,3}((?:-[ \t]*){3,}|'
        r'(?:_[ \t]*){3,}|(?:\*[ \t]*){3,})\n+'
    )

    INDENT_CODE = re.compile(r'(?:\n*)(?:(?: {4}| *\t)[^\n]+\n*)+')

    FENCED_CODE = re.compile(
        r'( {0,3})(`{3,}|~{3,})([^`\n]*)\n'
        r'(?:|([\s\S]*?)\n)'
        r'(?: {0,3}\2[~`]* *\n+|$)'
    )
    BLOCK_QUOTE = re.compile(
        r'(?: {0,3}>[^\n]*\n)+'
    )
    LIST_START = re.compile(
        r'( {0,3})([\*\+-]|\d{1,9}[.)])(?:[ \t]*|[ \t][^\n]+)\n+'
    )

    BLOCK_HTML = re.compile((
        r' {0,3}(?:'
        r'<(script|pre|style)[\s>][\s\S]*?(?:</\1>[^\n]*\n+|$)|'
        r'<!--(?!-?>)[\s\S]*?-->[^\n]*\n+|'
        r'<\?[\s\S]*?\?>[^\n]*\n+|'
        r'<![A-Z][\s\S]*?>[^\n]*\n+|'
        r'<!\[CDATA\[[\s\S]*?\]\]>[^\n]*\n+'
        r'|' + _BLOCK_HTML_RULE6 + '|' + _BLOCK_HTML_RULE7 + ')'
    ), re.I)

    LIST_MAX_DEPTH = 6
    BLOCK_QUOTE_MAX_DEPTH = 6
    RULE_NAMES = (
        'newline', 'thematic_break',
        'fenced_code', 'indent_code',
        'block_quote', 'block_html',
        'list_start',
        'axt_heading', 'setex_heading',
        'def_link',
    )

    def __init__(self):
        super(BlockParser, self).__init__()
        self.block_quote_rules = list(self.RULE_NAMES)
        self.list_rules = list(self.RULE_NAMES)

    def parse_newline(self, m, state):
        return {'type': 'newline', 'blank': True}

    def parse_thematic_break(self, m, state):
        return {'type': 'thematic_break', 'blank': True}

    def parse_indent_code(self, m, state):
        text = expand_leading_tab(m.group(0))
        code = _INDENT_CODE_TRIM.sub('', text)
        code = code.lstrip('\n')
        spanarg = {}
        spanarg["from"] = m.span()[0]
        spanarg["to"] = m.span()[1]
        return self.tokenize_block_code(code, None, state, spanarg)

    def parse_fenced_code(self, m, state):
        info = ESCAPE_CHAR.sub(r'\1', m.group(3))
        spaces = m.group(1)
        code = m.group(4) or ''
        if spaces and code:
            _trim_pattern = re.compile('^' + spaces, re.M)
            code = _trim_pattern.sub('', code)

        spanarg = {}
        spanarg["from"] = m.span()[0]
        spanarg["to"] = m.span()[1]
        return self.tokenize_block_code(code + '\n', info, state, spanarg)

    def tokenize_block_code(self, code, info, state, span):
        token = {'type': 'block_code', 'raw': code, "span":span}
        if info:
            token['params'] = (info, )
        return token

    def parse_axt_heading(self, m, state):
        level = len(m.group(1))
        text = m.group(2) or ''
        text = text.strip()
        if set(text) == {'#'}:
            text = ''
        spanarg = {}
        spanarg["from"] = m.span()[0]
        spanarg["to"] = m.span()[1]
        return self.tokenize_heading(text, level, state, spanarg)

    def parse_setex_heading(self, m, state):
        level = 1 if m.group(2) == '=' else 2
        text = m.group(1)
        text = text.strip()
        spanarg = {}
        spanarg["from"] = m.span()[0]
        spanarg["to"] = m.span()[1]
        return self.tokenize_heading(text, level, state,spanarg)

    def tokenize_heading(self, text, level, state, span):
        return {'type': 'heading', 'text': text, "span": span, 'params': (level,)}

    def get_block_quote_rules(self, depth):
        if depth > self.BLOCK_QUOTE_MAX_DEPTH - 1:
            rules = list(self.block_quote_rules)
            rules.remove('block_quote')
            return rules
        return self.block_quote_rules

    def parse_block_quote(self, m, state):
        depth = state.get('block_quote_depth', 0) + 1
        state['block_quote_depth'] = depth
        print("BLOCK",m)
        spanarg = {}
        spanarg["from"] = m.span()[0]
        spanarg["to"] = m.span()[1]
        # normalize block quote text
        text = _BLOCK_QUOTE_LEADING.sub('', m.group(0))
        text = expand_leading_tab(text)
        text = _BLOCK_QUOTE_TRIM.sub('', text)

        rules = self.get_block_quote_rules(depth)
        children = self.parse(text, state, rules, span=spanarg)
        state['block_quote_depth'] = depth - 1
        
        return {'type': 'block_quote', 'children': children, "span": spanarg}

    def get_list_rules(self, depth):
        if depth > self.LIST_MAX_DEPTH - 1:
            rules = list(self.list_rules)
            rules.remove('list_start')
            return rules
        return self.list_rules

    def parse_list_start(self, m, state, string):
        items = []
        spaces = m.group(1)
        marker = m.group(2)
        items, pos = _find_list_items(string, m.start(), spaces, marker)
        print("start:",m)
        print("start",items,pos)
        spanarg = {}
        spanarg["from"] = m.span()[0]
        spanarg["to"] = pos
        tight = '\n\n' not in ''.join(items).strip()

        ordered = len(marker) != 1
        if ordered:
            start = int(marker[:-1])
            if start == 1:
                start = None
        else:
            start = None

        list_tights = state.get('list_tights', [])
        list_tights.append(tight)
        state['list_tights'] = list_tights

        depth = len(list_tights)
        rules = self.get_list_rules(depth)
        children = [
            self.parse_list_item(item, depth, state, rules, spanarg)
            for item in items
        ]
        list_tights.pop()
        params = (ordered, depth, start)
        token = {'type': 'list', 'children': children, 'params': params, "span":{"from":m.span()[0],"to":pos}}
        return token, pos

    def parse_list_item(self, text, depth, state, rules, span):
        len_text = len(text)
        print("SSSS",text)
        print(len_text)
        text = self.normalize_list_item_text(text)
        old_from = span["from"]
        span["from"] = span["from"] + len_text
        if not text:
            children = [{'type': 'block_text', 'text': '', "span":{"from":old_from,"to":span["from"]}}]
        else:
            children = self.parse(text, state, rules, {"from":old_from,"to":span["from"]})
        return {
            'type': 'list_item',
            'params': (depth,),
            'children': children,
            "span": {"from":old_from,"to":span["from"]}
        }

    @staticmethod
    def normalize_list_item_text(text):
        text_length = len(text)
        text = _LIST_BULLET.sub('', text)

        if not text.strip():
            return ''

        space = text_length - len(text)
        text = expand_leading_tab(text)
        if text.startswith('     '):
            text = text[1:]
            space += 1
        else:
            text_length = len(text)
            text = _TRIM_4.sub('', text)
            space += max(text_length - len(text), 1)

        # outdent
        if '\n ' in text:
            pattern = re.compile(r'\n {1,' + str(space) + r'}')
            text = pattern.sub(r'\n', text)
        return text

    def parse_block_html(self, m, state):
        html = m.group(0).rstrip()
        spanarg = {}
        spanarg["from"] = m.span()[0]
        spanarg["to"] = m.span()[1]
        return {'type': 'block_html', 'raw': html, "span":spanarg}

    def parse_def_link(self, m, state):
        key = unikey(m.group(1))
        link = m.group(2)
        title = m.group(3)
        spanarg = {}
        spanarg["from"] = m.span()[0]
        spanarg["to"] = m.span()[1]
        if key not in state['def_links']:
            state['def_links'][key] = (link, title, spanarg)

    def parse_text(self, text, state, spanmapping, startindex, span = None):
        list_tights = state.get('list_tights')
        if list_tights and list_tights[-1]:
            return {'type': 'block_text', 'text': text.strip(), "span":span}
        tokens = []
        spanarg = {}
        print("STARTINDEX", startindex)
        splits = _PARAGRAPH_SPLIT.split(text)
        for s in splits:
            #s = s.strip()
            if s:
                print("SUBSTRINGPARSETEXT",s)
                if len(spanmapping) > 0:
                    print("spanmapping", spanmapping)
                    print("startindex",startindex["startindex"])
                    spanarg = spanmapping[startindex["startindex"]]
                    if startindex["startindex"]+1 < len(spanmapping):
                        startindex["startindex"] += 1
                    #table hack: there are still items in spanmapping although this is the last iteration, happends because matcher picks paragraphs
                    #differently than parse_text, so we have to span from current startindex to last in spanmapping
                    # check if current iteration is last
                    if splits[-1] == s: 
                        last_spanmap = spanmapping[-1]
                        spanarg["to"] = last_spanmap["to"]
                #tokens.append({'type': 'paragraph', 'text': s, "span":{"from":span["from"],"to":span["to"]}})
                print("appending",spanarg, s)
                tokens.append({'type': 'paragraph', 'text': s, "span":spanarg})
                spanarg = {}
        return tokens

    def parse(self, s, state, rules=None, span=None):
        if rules is None:
            rules = self.rules

        l = list(self._scan(s, state, rules, span=span, d=1))
        print("P A R S E")
        print(l)
        print("P A R S E")
        return l

    def render(self, tokens, inline, state):
        data = self._iter_render(tokens, inline, state)

        if inline.renderer.IS_TREE:
            return list(data)
        return ''.join(data)

    def _iter_render(self, tokens, inline, state):
        for tok in tokens:
            print("T O K E N")
            print(tok)
            method = inline.renderer._get_method(tok['type'])
            if 'blank' in tok:
                yield method()
                continue

            if 'children' in tok:
                children = self.render(tok['children'], inline, state)
            elif 'raw' in tok:
                print("RAW")
                children = tok['raw']
            else:
                print("before children tok", tok)
                print("method before children",inline)
                children = inline(tok['text'], state, tok["span"])
            params = tok.get('params')
            if params:
                print("PARAMSMETHOD",method)
                print("PARAMSTOKEN",tok)
                p = method(children, *params, span=tok["span"])
                print("PARAMS>",p)
                yield p
            else:
                print("NOPARAMAS METHOD",method)
                print("TOK BEFORE METHOD",tok)
                m =  method(children, span=tok["span"])
                print("CHILDREN>",m)
                yield m

            print("************************")


def expand_leading_tab(text):
    return _EXPAND_TAB.sub(_expand_tab_repl, text)


def _expand_tab_repl(m):
    s = m.group(1)
    return s + ' ' * (4 - len(s))


def _create_list_item_pattern(spaces, marker):
    prefix = r'( {0,' + str(len(spaces) + len(marker)) + r'})'

    if len(marker) > 1:
        if marker[-1] == '.':
            prefix = prefix + r'\d{0,9}\.'
        else:
            prefix = prefix + r'\d{0,9}\)'
    else:
        if marker == '*':
            prefix = prefix + r'\*'
        elif marker == '+':
            prefix = prefix + r'\+'
        else:
            prefix = prefix + r'-'

    s1 = ' {' + str(len(marker) + 1) + ',}'
    if len(marker) > 4:
        s2 = ' {' + str(len(marker) - 4) + r',}\t'
    else:
        s2 = r' *\t'
    return re.compile(
        prefix + r'(?:[ \t]*|[ \t]+[^\n]+)\n+'
        r'(?:\1(?:' + s1 + '|' + s2 + ')'
        r'[^\n]+\n+)*'
    )


def _find_list_items(string, pos, spaces, marker):
    items = []

    if marker in {'*', '-'}:
        is_hr = re.compile(
            r' *((?:-[ \t]*){3,}|(?:\*[ \t]*){3,})\n+'
        )
    else:
        is_hr = None

    pattern = _create_list_item_pattern(spaces, marker)
    while 1:
        m = pattern.match(string, pos)
        if not m:
            break

        text = m.group(0)
        if is_hr and is_hr.match(text):
            break

        new_spaces = m.group(1)
        if new_spaces != spaces:
            spaces = new_spaces
            pattern = _create_list_item_pattern(spaces, marker)

        items.append(text)
        pos = m.end()
    return items, pos
