class AuthorExtractor:
    @staticmethod
    def extract(page,title):
        data=page.get_text("dict")
        found_title=False
        for block in data["blocks"]:
            #Skip non-text blocks
            if block["type"]!=0:
                continue
            block_text=""
            for line in block["lines"]:
                for span in line["span"]:
                    block_text+=span["text"]+" "
            block_text=block_text.strip()

            if not block_text:
                continue
            #Have we reached the title block?
            if title in block_text:
                found_title=True

            #The first meaningful block after title
            if found_title:
                authors=[]
                #Split by commas
                for author in block_text.split(","):
                    author=author.strip()
                    #Remove common academic titles
                    author=(
                        author.replace("Fellow","")
                        .replace("IEEE","")
                        .strip()    
                    )
                    if author:
                        author.append(author)
                return authors
            return []
        