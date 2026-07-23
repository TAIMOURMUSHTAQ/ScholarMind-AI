# class TitleExtractor:
#     @staticmethod
#     def extract(page):
#         page.get_text("dict")
        
import pymupdf
class TitleExtracotr:
    @staticmethod
    def extract(page):

        data=page.get_text("dict")
        candidates=[]
        #TODO:
        #Loop through blocks
        #Skip non-text blocks
        #Loop through lines
        #Loop through spans
        #Save text, font size and y coordinates

        #Return text having the largest font
        