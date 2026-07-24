class TitleExtractor:
    @staticmethod
    def extract(page):
        data = page.get_text("dict")
        candidates = []
        # Loop through all blocks
        for block in data["blocks"]:
            # Skip non-text blocks (images, drawings, etc.)
            if block["type"] != 0:
                continue
            # Loop through lines
            for line in block["lines"]:
                # Loop through spans
                for span in line["spans"]:
                    text = span["text"].strip()
                    # Ignore empty spans
                    if not text:
                        continue
                    candidates.append(
                        {
                            "text": text,
                            "size": span["size"],
                            "y": span["bbox"][1]
                        }
                    )
        # No text found
        if not candidates:
            return ""
        # Sort by largest font first
        candidates.sort(
            key=lambda item: item["size"],
            reverse=True
        )
        # Return the text with the largest font
        return candidates[0]["text"]

