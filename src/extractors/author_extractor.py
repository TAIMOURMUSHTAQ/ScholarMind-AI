class AuthorExtractor:

    @staticmethod
    def extract(page, title):

        data = page.get_text("dict")

        found_title = False

        # Loop through all blocks
        for block in data["blocks"]:

            # Skip non-text blocks (images, drawings, etc.)
            if block["type"] != 0:
                continue

            block_text = ""

            # Loop through all lines
            for line in block["lines"]:

                # Loop through all spans
                for span in line["spans"]:

                    block_text += span["text"] + " "

            block_text = block_text.strip()

            # Ignore empty blocks
            if not block_text:
                continue

            # Check if this block contains the title
            if title in block_text:
                found_title = True
                continue

            # First meaningful block after the title
            if found_title:

                # Clean common academic titles
                block_text = (
                    block_text
                    .replace("Fellow, IEEE", "")
                    .replace("Senior Member, IEEE", "")
                    .replace("Member, IEEE", "")
                    .replace(" and ", ",")
                )

                authors = []

                # Split authors
                for author in block_text.split(","):

                    author = author.strip()

                    if author:
                        authors.append(author)

                return authors

        # No authors found
        return []