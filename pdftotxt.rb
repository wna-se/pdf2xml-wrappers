#!/usr/bin/env ruby
# -*- coding: utf-8 -*-
# https://github.com/kermitt2/grobid/raw/master/grobid-home/pdf2xml/lin-64/pdftoxml

require 'nokogiri'
require 'optparse'
require 'pathname'
require 'open3'

class PdfText
    def initialize(pdftoxml_file)
        @pdftoxml_file = pdftoxml_file
    end
    
    def pdf_to_page_texts(pdf_file)
        xml_pages = self.pdf_to_xml_pages pdf_file
        page_texts = self.xml_pages_to_page_texts xml_pages
        page_texts.map do |text| 
            self.soft_hyphen_cleanup self.angle_bracket_cleanup text 
        end
    end

    def pdf_to_txt_files(pdf_file, txt_file_pattern)
        puts "Running pdftoxml on #{pdf_file}"
        
        page_texts = self.pdf_to_page_texts pdf_file
        page_texts.each_with_index do |page_text, idx|
            page_num = idx + 1
            txt_file = Pathname.new txt_file_pattern.to_s % page_num
            puts "Writing page #{page_num} to #{txt_file}"
            txt_file.write(page_text)
        end
    end

    def xml_pages_to_page_texts(xml)
        nokogiri =  Nokogiri::XML(xml)
        pages = nokogiri.xpath("//PAGE").map do |page| 
            lines = page.xpath("BLOCK/TEXT").map do |line|
                words = line.xpath("TOKEN").map do |word| 
                    word.text
                end
                words.join(" ")
            end
            lines.join("\n")
        end
        pages
    end

    def soft_hyphen_cleanup(page_text)
        page_text = page_text.gsub("[¬\-]\n+(\S+)\s*", "$1\n") # end of li-\nne => end of line\n
    end

    def angle_bracket_cleanup(page_text)
        page_text = page_text.gsub("<","\u2039") # < => ‹
        page_text = page_text.gsub(">","\u203a") # > => ›
        page_text
    end

    def pdf_to_xml_pages(pdf_file)
        stdout, stderr, status = Open3.capture3(
            @pdftoxml_file.to_s,
            "-noImage",
            "-noImageInline",
            "-blocks",
            "-q",
            pdf_file.to_s, 
            "-"
        )
        stdout
    end
end

class CLI < OptionParser
    def initialize(argv, default_pdftoxml_file)
        super()
        @ARGV = argv
        @pdftoxml_file = default_pdftoxml_file
        self.on("-f", "--input-file PDF_FILE") do |pdf_file|
            @pdf_file = pdf_file
        end
        self.on("-o", "--output-pattern TXT_FILE_PATTERN") do |txt_file_pattern|
            @txt_file_pattern = txt_file_pattern
        end
        self.on("-p", "--pdftoxml-file [PDFTOXML_FILE]") do |pdftoxml_file|
            @pdftoxml_file = pdftoxml_file || default_pdftoxml_file
        end
        self.parse! @ARGV
    end 

    def run
        puts @txt_file_pattern
        pdftoxml_file = Pathname.new(@pdftoxml_file).realpath
        pdf_file = Pathname.new(@pdf_file).realpath
        if Pathname.new(@txt_file_pattern).absolute? 
            txt_file_pattern = Pathname.new(@txt_file_pattern) 
        else 
            txt_file_pattern = Pathname.getwd().join(@txt_file_pattern)
        end

        pdf_processor = PdfText.new(pdftoxml_file)
        pdf_processor.pdf_to_txt_files(pdf_file, txt_file_pattern)
    end
end

if __FILE__ == $0
    current_script_dir = Pathname.new(__FILE__).parent.realpath
    pdftoxml_file = current_script_dir.join("pdftoxml")
    CLI.new(Array.new(ARGV), pdftoxml_file).run()
end