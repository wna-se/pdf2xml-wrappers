#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from subprocess import run, PIPE;
from sys import argv;
from re import sub, UNICODE;
from pathlib import Path;
from argparse import ArgumentParser;
from xml.etree import ElementTree;

class PdfText:
    def __init__(self, pdftoxml_file):
        self.pdftoxml_file = pdftoxml_file
    
    def pdf_to_page_texts(self, pdf_file): 
        xml_pages = self.pdf_to_xml_pages(pdf_file)
        page_texts = self.xml_pages_to_page_texts(xml_pages)
        for idx, page_text in enumerate(page_texts):
            page_texts[idx] = self.soft_hyphen_cleanup(
                self.angle_bracket_cleanup(page_text)
            )
        return page_texts

    def pdf_to_txt_files(self, pdf_file, txt_file_pattern):
        print("Running pdftoxml on {}".format(pdf_file))
        
        page_texts = self.pdf_to_page_texts(pdf_file)
        for idx, page_text in enumerate(page_texts):
            page_num = idx + 1
            txt_file = Path(str(txt_file_pattern)%(page_num))
            print("Writing page {} to {}".format(page_num, txt_file))
            txt_file.write_text(page_text)
    
    def xml_pages_to_page_texts(self, xml):
        etree = ElementTree.fromstring(xml)
        pages = []
        for page in etree.findall("PAGE"):
            lines = []
            for line in page.findall("BLOCK/TEXT"):
                words = []
                for word in line.findall("TOKEN"):
                    words.append(word.text)
                lines.append(" ".join(words))
            pages.append("\n".join(lines))
        return pages

    def soft_hyphen_cleanup(self, page_text):
        page_text = sub(u"[¬\-]\n+(\S+)\s*", u"$1\n", page_text) # end of li-\nne => end of line\n
        return page_text

    def angle_bracket_cleanup(self, page_text):
        page_text = sub(u"<", u'\u2039', page_text, flags=UNICODE) # < => ‹
        page_text = sub(u">", u'\u203a', page_text, flags=UNICODE) # > => ›
        return page_text

    def pdf_to_xml_pages(self, pdf_file):
        process_result = run(
            [
                str(self.pdftoxml_file),
                "-noImage",
                "-noImageInline",
                "-blocks",
                "-q",
                str(pdf_file), 
                "-"
            ],
            #encoding = "utf-8",
            stdout = PIPE
        )
        return process_result.stdout.decode()

class CLI(ArgumentParser):
    def __init__(self, default_pdftoxml_file):
        super().__init__()
        self.add_argument(
            "-f", "--input-file", 
            dest = "pdf_file", required = True,
            help = "read PDF from PDF_FILE", metavar = "PDF_FILE"
        )
        self.add_argument(
            "-o", "--output-pattern", 
            dest = "txt_file_pattern", required = True,
            help = "write text to TXT_PATTERN", metavar = "TXT_PATTERN"
        )
        self.add_argument(
            "-p", "--pdftoxml-path", 
            dest = "pdftoxml_file", required = False, default = default_pdftoxml_file,
            help = "Absolute path to PDFTOXML", metavar = "PDFTOXML"
        )

    def run(self):
        args = self.parse_args()
        pdftoxml_file = Path(args.pdftoxml_file).resolve()
        pdf_file = Path(args.pdf_file).resolve()

        if Path(args.txt_file_pattern).is_absolute():
            txt_file_pattern = Path(args.txt_file_pattern) 
        else:
            txt_file_pattern = Path.cwd().joinpath(args.txt_file_pattern)

        pdf_processor = PdfText(pdftoxml_file)
        pdf_processor.pdf_to_txt_files(pdf_file, txt_file_pattern)

if argv[0]==__file__:
    current_script_dir = Path(argv[0]).parent.resolve()
    pdftoxml_file = current_script_dir.joinpath("pdftoxml")
    CLI(pdftoxml_file).run()