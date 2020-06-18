import re
try:
    from urllib.parse import quote
    import html
except ImportError:
    from urllib import quote
    html = None


class Scanner(re.Scanner):
    def iter(self, string, state, parse_text, span = None):
        sc = self.scanner.scanner(string)
        a = re.Scanner([])
        pos = 0
        for match in iter(sc.search, None):
            name, method = self.lexicon[match.lastindex - 1][1]
            hole = string[pos:match.start()]
            if hole:
                text = parse_text(hole, state)
                yield text

            #corresponding inline parser method
            print("METHOD",method,span)
            mm = method(match, state, span)
            yield mm
            pos = match.end()

        hole = string[pos:]
        if hole:
            yield parse_text(hole, state)


class ScannerParser(object):
    scanner_cls = Scanner
    RULE_NAMES = tuple()

    def __init__(self):
        self.rules = list(self.RULE_NAMES)
        self.rule_methods = {}
        self._cached_sc = {}

    def register_rule(self, name, pattern, method):
        self.rule_methods[name] = (pattern, lambda m, state: method(self, m, state))

    def get_rule_pattern(self, name):
        if name not in self.RULE_NAMES:
            return self.rule_methods[name][0]
        return getattr(self, name.upper())

    def get_rule_method(self, name):
        if name not in self.RULE_NAMES:
            return self.rule_methods[name][1]
        return getattr(self, 'parse_' + name)

    def parse_text(self, text, state):
        raise NotImplementedError

    def _scan(self, s, state, rules, span = None, d = None):
        sc = self._create_scanner(rules)
        if d:
            print("DEBUG")
            if type(sc) is not Matcher:
                print("DEBUG2")
        if type(sc) == Matcher or 1:
            for tok in sc.iter(s, state, self.parse_text, span=span if span else {}):
                if isinstance(tok, list):
                    for t in tok:
                        print("list",tok)
                        yield t
                elif tok:
                    print("nolist",tok)
                    yield tok

    def _create_scanner(self, rules):
        sc_key = '|'.join(rules)
        sc = self._cached_sc.get(sc_key)
        if sc:
            return sc

        lexicon = [
            (self.get_rule_pattern(n), (n, self.get_rule_method(n)))
            for n in rules
        ]
        sc = self.scanner_cls(lexicon)
        self._cached_sc[sc_key] = sc
        return sc


class Matcher(object):
    PARAGRAPH_END = re.compile(
        r'(?:\n{2,})|'
        r'(?:\n {0,3}#{1,6})|'  # axt heading
        r'(?:\n {0,3}(?:`{3,}|~{3,}))|'  # fenced code
        r'(?:\n {0,3}>)|'  # blockquote
        r'(?:\n {0,3}(?:[\*\+-]|1[.)]))|'  # list
        r'(?:\n {0,3}<)'  # block html
    )

    def __init__(self, lexicon):
        self.lexicon = lexicon

    def search_pos(self, string, pos):
        m = self.PARAGRAPH_END.search(string, pos)
        if not m:
            return None
        if set(m.group(0)) == {'\n'}:
            print("match is",m)
            print("mgroup(0)",m.group(0))
            return m.end()
        print("paragraph found:",m.start()+1)
        return m.start() + 1

    def iter(self, string, state, parse_text, span = None):
        pos = 0
        endpos = len(string)
        secondIterCall = False
        if span:
            print("second call",span)
            pos = span["from"]
            endpos = span["to"]
            secondIterCall = True
            savespan = {"from":pos,"to":endpos}
        else:
            print("first call")
        last_end = 0
        span = {"from":0,"to":0}
        spanmapping = []
        startindex = {"startindex":0}
        while 1:
            print("searching:",pos)
            if pos >= endpos:
                break
            for rule, (name, method) in self.lexicon:
                match = rule.match(string, pos)
                if match is not None:
                    print("match found",match)
                    start, end = match.span()
                    if start > last_end:
                        
                        if not secondIterCall:
                            span["from"] = last_end
                            span["to"] = start
                        else:
                            span["from"] = pos
                            span["to"] = endpos
                        print("before parse text")
                        print("span",span)
                        yield parse_text(string[last_end:start], state, spanmapping, startindex, span=span)
                        print("startindex after", startindex)

                    if name.endswith('_start'):
                        print("_start", method)
                        token = method(match, state, string)
                        yield token[0]
                        end = token[1]
                    else:
                        print("MMMMM",method)
                        yield method(match, state)
                    last_end = pos = end
                    span["from"] = pos
                    break
            else:
                span["from"] = pos
                found = self.search_pos(string, pos)
                if found is None:
                    break
                pos = found
                span["to"] = found
                spanmapping.append({"from":span["from"],"to":span["to"]})
                print("appending new",{"from":span["from"],"to":span["to"]})
                print("spanmapping now",spanmapping)

        if last_end < endpos:
            if not secondIterCall:
                span["to"] = len(string)
            else:
                span["to"] = savespan["to"]
            spanmapping.append({"from":span["from"],"to":span["to"]})
            print("appended,spanmapping no:",spanmapping)
            yield parse_text(string[last_end:], state, spanmapping, startindex, span=span)
            print("startindex2 after", startindex)

        print("MATCHER",spanmapping)


def escape(s, quote=True):
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    if quote:
        s = s.replace('"', "&quot;")
    return s


def escape_url(link):
    safe = '/#:()*?=%@+,&'
    if html is None:
        return quote(link.encode('utf-8'), safe=safe)
    return html.escape(quote(html.unescape(link), safe=safe))


def escape_html(s):
    if html is not None:
        return html.escape(html.unescape(s)).replace('&#x27;', "'")
    return escape(s)


def unikey(s):
    return ' '.join(s.split()).lower()
