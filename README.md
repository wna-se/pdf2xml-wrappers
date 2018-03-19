# pdf2xml-wrappers

A simple Ruby/Python wrapper for the command line utility pdftoxml to parse the output XML as either plain text. The required pdftotext binary for Linux, Windows or macOS is available in the [kermitt2/grobid GitHub respository](https://github.com/kermitt2/grobid/tree/master/grobid-home/pdf2xml).

`pdf2otxt.[py|rb] [-h] -f PDF_FILE -o TXT_PATTERN [-p PDFTOXML]`


| optional arguments                            | description                     |
|-----------------------------------------------|---------------------------------|
|  -h, --help                                   | show this help message and exit |
|  -f PDF_FILE, --input-file PDF_FILE           | read PDF from PDF_FILE          |
|  -o TXT_PATTERN, --output-pattern TXT_PATTERN | write text to TXT_PATTERN       |
|  -p PDFTOXML, --pdftoxml-path PDFTOXML        | Absolute path to PDFTOXML       |

