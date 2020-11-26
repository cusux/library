## Basic Regular Expressions

^ 			        beginning of a line

\* 			        preceding zero or more character

. 			        match any single character

$ 			        ending of a line

[a-b] 			    match "a" or "b" single character

[^] 			    not character whit in this bracket

\< \>			    searching for just "test" \<test\>

\			        escape

## Examples:

.at		            Matches any three-character string ending with "at", including "hat", "cat", and "bat".
[hc]at 		        Matches "hat" and "cat".
[^b]at 		        Matches all strings matched by ".at" except "bat".
[^hc]at 	        Matches all strings matched by .at other than "hat" and "cat".
^[hc]at 	        Matches "hat" and "cat", but only at the beginning of the string or line.
[hc]at$ 	        Matches "hat" and "cat", but only at the end of the string or line.
s.* 		        Matches "s" followed by zero or more characters, for example: "s" and "saw" and "seed".
s*		            Matches any character. "s" is not important. "*" preceding zero.
[hc]*at 	        Matches "hat", "cat", "hhat", "chat", "hcat", "cchchat", "at", and so on.
\<at\>		        Matches just only "at".

## Extended Regular Expressions

?			        preceding zero or one character

\+			        preceding one or more character

{N}, {N,}           N times matches before character, N and N+ times matches before character
{N,M}               Min match N max match M

|			        choice operator a|b matches "a" or "b"

()			        capture group

## Examples:

?at		            Matches "Xat" and "at". 'X' is any single character.
[hc]?at 	        Matches "hat", "cat", and "at".
+at 		        Matches "Xat". 'X' is any single character, but not "at".
[hc]+at 	        Matches "hat", "cat", "hhat", "chat", "hcat", "cchchat", and so on, but not "at".
sa{2}t		        Matches "saat" bot not "sat".
sa{2,}t		        Matches "saat", "saaat", and so on, but not "sat".
sa{3,4}t	        Matches "saaat", "saaaat".
cat|dog 	        Matches "cat" or "dog".
[Cc]at|dog|pop 	    Matches "Cat", 'cat', "dog" or "pop" .
a(bc)?d		        Matches "ad" and "abcd" 

## POSIX Character Classes

[:alnum:]	        [A-Za-z0-9]	                        Alphanumeric characters
[:alpha:]	        [A-Za-z]	                        Alphabetic characters
[:upper:]	        [A-Z]		                        Uppercase letters
[:lower:]	        [a-z]		                        Lowercase letters
[:digit:]	        [0-9]		                        Digits
[:xdigit:]	        [A-Fa-f0-9]	                        Hexadecimal digits
[:blank:]	        [ \t]		                        Space and tab
[:space:]	        [ \t\r\n\v\f]	                    Whitespace characters
[:cntrl:]	        [\x00-\x1F\x7F]	                    Control characters
[:punct:]	        [][!"#$%&'()*+,./:;<=>?@\^_`{|}~-]	Punctuation characters

## The Backslash Character and Special Expressions

‘\b’                Match the empty string at the edge of a word.
‘\B’                Match the empty string provided it’s not at the edge of a word.
‘\<’                Match the empty string at the beginning of word.
‘\>’                Match the empty string at the end of word.
‘\w’                Match word constituent, it is a synonym for ‘[_[:alnum:]]’.
‘\W’                Match non-word constituent, it is a synonym for ‘[^_[:alnum:]]’.
‘\s’                Match whitespace, it is a synonym for ‘[[:space:]]’.
‘\S’                Match non-whitespace, it is a synonym for ‘[^[:space:]]’.

For example, ‘\brat\b’ matches the separate word ‘rat’, ‘\Brat\B’ matches ‘crate’ but not ‘furry rat’.
