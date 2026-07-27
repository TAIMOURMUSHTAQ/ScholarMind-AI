class ReadingOrderAnalyzer:
    @staticmethod
    def sort(blocks):
        """
        Temporary implementation
        Next sprint we will detect columns automatically"""
        return sorted(
            blocks,
            key=lambda b:(b.y0,b.x0)
        )