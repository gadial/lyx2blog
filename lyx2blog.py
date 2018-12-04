import os
import sys
import subprocess
import re

LYX_EXE = r'c:\Program Files (x86)\LyX 2.3\bin\LyX2.3.exe'
BASIC_REPLACEMENTS = {
    r'\\char`\\"{}': r'"',
    r'\\char34\s?({})?' : r'"'
}
TAGS = {
    "title{}": "",
    "maketitle" : "",
    "selectlanguage{}" : "",
    "inputencoding{}" : "",
    "textbf{}": '<strong>\1</strong>',
    "href{}{}": '<a href="\1">\2</a>',
    ("section{}", "section*{}"): '<h2>\1</h2>',
    ('\{\\\\beginL', '\\\\endL\}'): '\1',
    ('\\\\item', "(?=\n\\\\item)"): '<li>\1</li>',
    ('\\\\item', "(?=\n\\\\end\{)"): '<li>\1</li>',
    ('\\\\begin\{itemize\}', '\\\\end\{itemize\}'): '<ul>\1</ul>',
    ('\\\\begin\{enumerate\}', '\\\\end\{enumerate\}'): '<ol>\1</ol>',
    ('\\\\begin\{quote\}', '\\\\end\{quote\}'): '<blockquote>\1</blockquote>',
    "L{}": '\1',
    'textquotedblright': '"',
    'textquotedblleft ': '"',
    'textquotedblleft{}': '"',
    'textquotedbl ' : '"',
    'textquotedbl{}': '"'
}

def re_search(regex, s, *params):
    """Assumes re has one capture group; returns it or None"""
    result = re.search(regex, s, *params)
    if result and len(result.groups()) > 0:
        return result.group(1)
    return None

def convert_lyx_to_tex(lyx_file):
    commandLine = [LYX_EXE, "--export", "latex", "{}.lyx".format(filename)]
    subprocess.Popen(commandLine)

def get_content(text):
    """The content is everything between and not including the \document tags"""
    return re_search(r'(?<=begin\{document\})(.*)(?=\\end\{document\})', text, re.DOTALL) or text

def find_problems(text):
    for bad_line in re.findall(r'^.*\\ensuremath.*$', text):
        print("WARNING: ensuremath found in line {}".format(bad_line))
    return text

def basic_replacements(text):
    for (target, result) in BASIC_REPLACEMENTS.items():
        text = re.sub(target, result, text)
    return text

def parentheses_fix(text):  # relies on the fact that parentheses in mathmode are of the form \left( and \right)
    replacement = {'(': ')', ')': '('}
    return re.sub(r'(?<!\\left)\(|(?<!\\right)\)', lambda s: replacement.get(s.group(0), s.group(0)), text)

def math_tag_replacements(text):  # relies on the fact that LyX converts math to \L{$...$} in my heb posts
    return re.sub(r'\\L\{\$([^\$]*)\$\}', lambda s: "\({}\)".format(s.group(1)), text)

def peform_all_changes(text):
    text = get_content(text)
    text = find_problems(text)
    text = parentheses_fix(text)
    text = math_tag_replacements(text)
    # remove_comments.
    # replace_tags.
    # remove_linebreaks.
    # force_encoding("utf-8")
    return text

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("Usage: {} FILENAME".format(sys.argv[0]))
        exit(0)
    filename = os.path.splitext(os.path.basename(sys.argv[1]))[0]
    convert_lyx_to_tex(filename)
    with open(filename + ".tex") as texfile:
        text = texfile.read()
    text = peform_all_changes(text)
    with open(filename + ".blog", "w") as blogfile:
        blogfile.write(text)
#     text = File.read("#{filename}.tex", :encoding => 'ISO-8859-8')
#     File.open("#{filename}.blog", "w"){|f| f.write text.all_changes}
# end