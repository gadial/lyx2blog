#!/usr/bin/env ruby
BASIC_REPLACEMENTS = {'\char`\"{}' => '"'}
TAGS = {
    "title{}" => "",
    "maketitle"  => "",
    "selectlanguage{}"  => "",
    "inputencoding{}"  => "",
    "textbf{}" => '<strong>\1</strong>',
    "href{}{}" => '<a href="\1">\2</a>',
    ["beginL", "endL"] => '\1',
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
        tag_regexp = /\\#{tag.gsub('{}', '\{(.*?)\}')}/ if String === tag
        tag_regexp = /\{\\#{tag.first} (.*?)\\#{tag.last}\}/ if Array === tag
        gsub tag_regexp, replacement
    end
    
    def replace_tags
        TAGS.inject(self, :replace_tag)
    end
    def remove_comments
        gsub(/%.*/, "")
    end
    def math_tag_replacements #relies on the fact that LyX converts math to \L{$...$} in my heb posts        
        gsub(/\\L\{\$([^\$]*)\$\}/,'\(\1\)')
    end
    def parentheses_fix #relies on the fact that parentheses in mathmode are of the form \left( and \right)
        gsub(/(?<!\\left)\(|(?<!\\right)\)/,{'(' => ')', ')' => '('})
    end
end

filename = File.basename(ARGV[0], ".lyx")
`lyx --export latex #{filename}.lyx`
text = File.read("#{filename}.tex", :encoding => 'ISO-8859-8').match(/(?<=\\begin\{document\})(.*)(?=\\end\{document\})/m)[0]
File.open("#{filename}.blog", "w") do |f|
    f.write text.
    basic_replacements.
    parentheses_fix.
    math_tag_replacements.
    remove_comments.
    replace_tags.
    force_encoding("utf-8")
end                                  