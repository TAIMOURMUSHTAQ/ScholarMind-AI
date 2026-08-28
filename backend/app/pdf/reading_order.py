class ReadingOrderAnalyzer:
    """Arranges layout blocks into natural reading order.

    Heuristic: detect single vs. two-column layout by splitting blocks at
    the horizontal page center; two-column pages are read left-column-then-
    right-column. This is tuned for common single/IEEE-style two-column
    academic layouts and can misorder more complex/mixed layouts.
    """

    @staticmethod
    def sort(layout_blocks):
        if not layout_blocks:
            return []

        min_x = min(b.x0 for b in layout_blocks)
        max_x = max(b.x1 for b in layout_blocks)
        page_center = min_x + (max_x - min_x) / 2

        left_column, right_column = [], []
        for block in layout_blocks:
            center = (block.x0 + block.x1) / 2
            (left_column if center < page_center else right_column).append(block)

        if not left_column or not right_column:
            layout_blocks.sort(key=lambda b: (b.y0, b.x0))
            return layout_blocks

        left_column.sort(key=lambda b: (b.y0, b.x0))
        right_column.sort(key=lambda b: (b.y0, b.x0))
        return left_column + right_column
