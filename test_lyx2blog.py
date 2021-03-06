import unittest
import io
import lyx2blog
import unittest.mock


class TestLyx2Blog(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_content(self):
        content = "Hello world I am content"
        text = r"\begin{document}Hello world I am content\end{document}"
        self.assertEquals(content, lyx2blog.get_content(text))
        text = r"%% LyX 2.0.4 created this file.  For more info, see http://www.lyx.org/. %% Do not edit unless you really know what you are doing. \documentclass[english,hebrew]{article} \usepackage[T1]{fontenc} \usepackage[latin9,cp1255]{inputenc} \usepackage{babel} \begin{document}Hello world I am content\end{document}"
        self.assertEquals(content, lyx2blog.get_content(text))

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_find_problems(self, mock_stdout):
        text = r"Hello world oh no \\ensuremath is here!"
        expected_warning = r'WARNING: ensuremath found in line Hello world oh no \\ensuremath is here!' + "\n"
        lyx2blog.find_problems(text)
        self.assertEqual(expected_warning, mock_stdout.getvalue())

    def test_basic_replacements(self):
        text = r"\char34 blabla\char34{}"
        expected_result = r'"blabla"'
        text = lyx2blog.basic_replacements(text)
        self.assertEqual(expected_result, text)

        text = r"\char`\"{}blabla\char`\"{}"
        expected_result = r'"blabla"'
        text = lyx2blog.basic_replacements(text)
        self.assertEqual(expected_result, text)

    def test_parentheses_fix(self):
        text = "before )middle(. after"
        expected_result = "before (middle). after"
        text = lyx2blog.parentheses_fix(text)
        self.assertEqual(expected_result, text)

        text = r"\L{$\sum_{i=1}^{\infty}\left(6-i\right)p_{i}$}"
        expected_result = r"\L{$\sum_{i=1}^{\infty}\left(6-i\right)p_{i}$}" #no change in math mode
        text = lyx2blog.parentheses_fix(text)
        self.assertEqual(expected_result, text)

    def test_math_tag_replacement(self):
        text = r"\L{$\sum_{i=1}^{\infty}\left(6-i\right)p_{i}$}"
        expected_result = r"\(\sum_{i=1}^{\infty}\left(6-i\right)p_{i}\)"
        text = lyx2blog.math_tag_replacements(text)
        self.assertEqual(expected_result, text)

    def test_remove_comments(self):
        text = "Hello world!%this is a comment"
        expected_result = "Hello world!"
        text = lyx2blog.remove_comments(text)
        self.assertEqual(expected_result, text)

    def test_replace_tags(self):
        text = r'Hello world now in \textbf{BOLD}!'
        expected_result = r'Hello world now in <strong>BOLD</strong>!'
        text = lyx2blog.replace_tags(text)
        self.assertEqual(expected_result, text)

        text = r'Hello\inputencoding{} world! Here is \href{http://gadial.net}{my blog}'
        expected_result = r'Hello world! Here is <a href="http://gadial.net">my blog</a>'
        text = lyx2blog.replace_tags(text)
        self.assertEqual(expected_result, text)

        text = "\\begin{itemize}\n\\item ITEM 1\n\\item ITEM 2\n\\end{itemize}"
        expected_result = '<ul><li>ITEM 1</li>\n<li>ITEM 2</li>\n</ul>'
        text = lyx2blog.replace_tags(text)
        self.assertEqual(expected_result, text)

        text = "\\begin{enumerate}\n\\item ITEM 1\n\\item ITEM 2\n\\end{enumerate}"
        expected_result = '<ol><li>ITEM 1</li>\n<li>ITEM 2</li>\n</ol>'
        text = lyx2blog.replace_tags(text)
        self.assertEqual(expected_result, text)

        text = r'\textquotedblright Hello world\textquotedblleft '
        expected_result = r'"Hello world"'
        text = lyx2blog.replace_tags(text)
        self.assertEqual(expected_result, text)

        text = "\\begin{itemize}\n\\item ITEM 1\n\\end{itemize}\n\\begin{enumerate}\n\\item ITEM 2\n\\end{enumerate}"
        expected_result = "<ul><li>ITEM 1</li>\n</ul>\n<ol><li>ITEM 2</li>\n</ol>"
        text = lyx2blog.replace_tags(text)
        self.assertEqual(expected_result, text)

        text = "One approach is called \\textquotedblright\\textbf{Trapped Ions}\\textquotedblleft{} - the idea is"
        expected_result = "One approach is called \"<strong>Trapped Ions</strong>\" - the idea is"
        text = lyx2blog.replace_tags(text)
        self.assertEqual(expected_result, text)

        text = "\paragraph*{solution:}"
        expected_result = "<h4>solution:</h4>"
        text = lyx2blog.replace_tags(text)
        self.assertEqual(expected_result, text)

        text = '\paragraph*{targil {\\beginL 5\endL}:}'
        expected_result = "<h4>targil 5:</h4>"
        text = lyx2blog.replace_tags(text)
        self.assertEqual(expected_result, text)

    def test_remove_linebreaks(self):
        text = "Hello\r\nworld"
        expected_text = "Hello world"
        text = lyx2blog.remove_linebreaks(text)
        self.assertEqual(expected_text, text)

    def test_remove_L_tag(self):
        text = "\L{\[a_{1}+a_{2}+a_{3}+a_{4}=3\cdot21=87\]}"
        expected_result = "\[a_{1}+a_{2}+a_{3}+a_{4}=3\cdot21=87\]"
        text = lyx2blog.remove_L_tag(text)
        self.assertEqual(expected_result, text)


# text = '\paragraph*{targil {\\beginL 5\endL}:}'
# expected_result = "<h4>targil 5</h4>"
# print("********")
# print(expected_result)
# print("********")
# new_text = lyx2blog.replace_tags(text)
# print(new_text)
# exit()

if __name__ == '__main__':
    unittest.main()