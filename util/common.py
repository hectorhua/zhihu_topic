# -*- coding: utf-8 -*-

import re
import urllib
import requests

try:
    import urlparse as url_parse
except ImportError:
    import urllib.parse as url_parse
    
# tags that do not contain content
EMPTY_TAGS = 'br', 'hr', 'meta', 'link', 'base', 'img', 'embed', 'param', 'area', 'col', 'input'

def unescape(text, encoding='utf-8', keep_unicode=False):
    """Interpret escape characters

    >>> unescape('&lt;hello&nbsp;&amp;%20world&gt;')
    '<hello & world>'
    """
    if not text:
        return ''
    try:
        text = to_unicode(text, encoding)
    except UnicodeError:
        pass

    def fixup(m):
        text = m.group(0)
        if text[:2] == '&#':
            # character reference
            try:
                if text[:3] == '&#x':
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    #text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = re.sub('&#?\w+;', fixup, text)
    text = urllib.unquote(text)
    if keep_unicode:
        return text
    try:
        text = text.encode(encoding, 'ignore')
    except UnicodeError:
        pass
    
    if encoding != 'utf-8':
        return text

    # remove annoying characters
    chars = {
        '\xc2\x82' : ',',        # High code comma
        '\xc2\x84' : ',,',       # High code double comma
        '\xc2\x85' : '...',      # Tripple dot
        '\xc2\x88' : '^',        # High carat
        '\xc2\x91' : '\x27',     # Forward single quote
        '\xc2\x92' : '\x27',     # Reverse single quote
        '\xc2\x93' : '\x22',     # Forward double quote
        '\xc2\x94' : '\x22',     # Reverse double quote
        '\xc2\x95' : ' ',  
        '\xc2\x96' : '-',        # High hyphen
        '\xc2\x97' : '--',       # Double hyphen
        '\xc2\x99' : ' ',
        '\xc2\xa0' : ' ',
        '\xc2\xa6' : '|',        # Split vertical bar
        '\xc2\xab' : '<<',       # Double less than
        '\xc2\xae' : '®',
        '\xc2\xbb' : '>>',       # Double greater than
        '\xc2\xbc' : '1/4',      # one quarter
        '\xc2\xbd' : '1/2',      # one half
        '\xc2\xbe' : '3/4',      # three quarters
        '\xca\xbf' : '\x27',     # c-single quote
        '\xcc\xa8' : '',         # modifier - under curve
        '\xcc\xb1' : ''          # modifier - under line
    }
    def replace_chars(match):
        char = match.group(0)
        return chars[char]
    return re.sub('(' + '|'.join(chars.keys()) + ')', replace_chars, text)


def to_unicode(obj, encoding='utf-8'):
    """Convert obj to unicode
    """
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = obj.decode(encoding, 'ignore')
    return obj


def remove_tags(html, keep_children=True):
    """Remove HTML tags leaving just text
    If keep children is True then keep text within child tags

    >>> remove_tags('hello <b>world</b>!')
    'hello world!'
    >>> remove_tags('hello <b>world</b>!', False)
    'hello !'
    >>> remove_tags('hello <br>world<br />!', False)
    'hello world!'
    >>> remove_tags('<span><b></b></span>test</span>', False)
    'test'
    """
    html = re.sub('<(%s)[^>]*>' % '|'.join(EMPTY_TAGS), '', html)
    if not keep_children:
        for tag in set(re.findall('<(\w+?)\W', html)):
            if tag not in EMPTY_TAGS:
                html = re.compile('<\s*%s.*?>.*?</\s*%s\s*>' % (tag, tag), re.DOTALL).sub('', html)
    return re.compile('<[^<]*?>').sub('', html)


def normalize(s, encoding='utf-8'):
    """Normalize the string by removing tags, unescaping, and removing surrounding whitespace
    
    >>> normalize('''<span>Tel.:   029&nbsp;-&nbsp;12345678   </span>''')
    'Tel.: 029 - 12345678'
    """
    if isinstance(s, basestring):
        return re.sub('\s+', ' ', unescape(remove_tags(s), encoding=encoding, keep_unicode=isinstance(s, unicode))).strip()
    else:
        return s


def get_elem_text(self, elem):
    """抽取lxml.etree库中elem对象中文字

    Args:
        elem: lxml.etree库中elem对象

    Returns:
        elem中文字
    """
    rc = []
    for node in elem.itertext():
        rc.append(node.strip())
    return ''.join(rc)


def get_encoding_from_reponse(self, r):
    """获取requests库get或post返回的对象编码

    Args:
        r: requests库get或post返回的对象

    Returns:
        对象编码
    """
    encoding = requests.utils.get_encodings_from_content(r.text)
    return encoding[0] if encoding else requests.utils.get_encoding_from_headers(r.headers)


def replace_html(s):
    """替换html‘&quot;’等转义内容为正常内容

    Args:
        s: 文字内容

    Returns:
        s: 处理反转义后的文字
    """
    s = s.replace('&#39;', '\'')
    s = s.replace('&quot;', '"')
    s = s.replace('&amp;', '&')
    s = s.replace('&gt;', '>')
    s = s.replace('&lt;', '<')
    s = s.replace('&yen;', '¥')
    s = s.replace('amp;', '')
    s = s.replace('&lt;', '<')
    s = s.replace('&gt;', '>')
    s = s.replace('&nbsp;', ' ')
    s = s.replace('\\', '')
    return s


def replace_dict(dicts):
    retu_dict = dict()
    for k, v in dicts.items():
        retu_dict[replace_all(k)] = replace_all(v)
    return retu_dict


def replace_list(lists):
    retu_list = list()
    for l in lists:
        retu_list.append(replace_all(l))
    return retu_list


def replace_all(data):
    if isinstance(data, dict):
        return replace_dict(data)
    elif isinstance(data, list):
        return replace_list(data)
    elif isinstance(data, str):
        return replace_html(data)
    else:
        return data


def str_to_dict(json_str):
    json_dict = eval(json_str)
    return replace_all(json_dict)


def replace_space(s):
    s = s.replace(' ', '')
    s = s.replace('\r\n', '')
    s = s.replace('\r', '')
    s = s.replace('\n', '')
    return s


def get_url_param(url):
    result = url_parse.urlparse(url)
    return url_parse.parse_qs(result.query, True)
