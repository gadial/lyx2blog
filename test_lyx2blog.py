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