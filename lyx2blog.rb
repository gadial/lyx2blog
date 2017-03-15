#!/usr/bin/env ruby
BASIC_REPLACEMENTS = {
    '\char`\"{}' => '"',
    /\\char34\s?({})?/ => '"'
}
TAGS = {
    "title{}" => "",
    "maketitle"  => "",
    "selectlanguage{}"  => "",
    "inputencoding{}"  => "",
    "textbf{}" => '<strong>\1</strong>',
    "href{}{}" => '<a href="\1">\2</a>',
    "section{}" => '<h2>\1</h2>',
    ['\{\\\\beginL', '\\\\endL\}'] => '\1',
    ['\\\\item', "(?=\n\\\\item)"] => '<li>\1</li>',
    ['\\\\item', "(?=\n\\\\end\{)"] => '<li>\1</li>',
    ['\\\\begin\{itemize\}', '\\\\end\{itemize\}'] => '<ul>\1</ul>',
    ['\\\\begin\{enumerate\}', '\\\\end\{enumerate\}'] => '<ol>\1</ol>',
    "L{}" => '\1'
}

class String
    def basic_replacements
        result = dup
        for s in BASIC_REPLACEMENTS.keys
            result.gsub!(s, BASIC_REPLACEMENTS[s])
        end
        result
    end
    
    def replace_tag(tag_data)
        tag, replacement = tag_data
        tag_regexp = /\\#{tag.gsub('{}', '\{(.*?)\}')}/m if String === tag
        tag_regexp = /#{tag.first}\s(.*?)#{tag.last}/m if Array === tag
        gsub tag_regexp, replacement
    end
    
    def replace_tags
        TAGS.inject(self, :replace_tag)
    end
    def remove_comments
        gsub(/%.*/, "")
    end
    def remove_linebreaks
        #tex has linebreaks in the middle of paragraphs for no reason
        gsub(/(?<!\n)\n(?!\n)/, " ")
    end
    def math_tag_replacements #relies on the fact that LyX converts math to \L{$...$} in my heb posts        
        gsub(/\\L\{\$([^\$]*)\$\}/,'\(\1\)')
    end
    def parentheses_fix #relies on the fact that parentheses in mathmode are of the form \left( and \right)
        gsub(/(?<!\\left)\(|(?<!\\right)\)/,{'(' => ')', ')' => '('})
    end
    def find_problems
        scan(/^.*\\ensuremath.*$/){|s| puts "WARNING: ensuremath found in line '#{s}'"}
        self
    end
    def get_content
        self[/(?<=\\begin\{document\})(.*)(?=\\end\{document\})/m] ||  self
    end
    def all_changes
        get_content.
        find_problems.
        basic_replacements.
        parentheses_fix.
        math_tag_replacements.
        remove_comments.
        replace_tags.
        remove_linebreaks.
        force_encoding("utf-8")
    end
end

# text = '\begin{enumerate}
# \item This is the
# first item
# \item and this is the second
# item for this
# \item third now bye bye
# \end{enumerate}
# '
# 
# puts text.all_changes    

if __FILE__ == $0
    filename = File.basename(ARGV[0], ".lyx")
    `lyx --export latex #{filename}.lyx`
    text = File.read("#{filename}.tex", :encoding => 'ISO-8859-8')
    File.open("#{filename}.blog", "w"){|f| f.write text.all_changes}
end