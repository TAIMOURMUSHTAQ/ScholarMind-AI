from src.models.layout_block import LayoutBlock


class ReadingOrderAnalyzer:
    """
    Arrange layout blocks into the natural reading order.

    Strategy
    --------
    1. Detect whether the page is likely single-column or two-column.
    2. If single-column:
           Sort blocks by Y coordinate.
    3. If two-column:
           Read the left column first,
           then the right column.
    """

    @staticmethod
    def sort(layout_blocks):
        """
        Sort layout blocks into reading order.

        Parameters
        ----------
        layout_blocks : list[LayoutBlock]

        Returns
        -------
        list[LayoutBlock]
        """

        if not layout_blocks:
            return []

        # -----------------------------------
        # Calculate page boundaries
        # -----------------------------------

        min_x = min(block.x0 for block in layout_blocks)
        max_x = max(block.x1 for block in layout_blocks)

        page_width = max_x - min_x
        page_center = min_x + (page_width / 2)

        # -----------------------------------
        # Split into columns
        # -----------------------------------

        left_column = []
        right_column = []

        for block in layout_blocks:

            block_center = (block.x0 + block.x1) / 2

            if block_center < page_center:
                left_column.append(block)
            else:
                right_column.append(block)

        # -----------------------------------
        # Detect if page is actually
        # single-column
        # -----------------------------------

        if len(left_column) == 0 or len(right_column) == 0:

            layout_blocks.sort(
                key=lambda b: (b.y0, b.x0)
            )

            return layout_blocks

        # -----------------------------------
        # Sort each column separately
        # -----------------------------------

        left_column.sort(
            key=lambda b: (b.y0, b.x0)
        )

        right_column.sort(
            key=lambda b: (b.y0, b.x0)
        )

        # -----------------------------------
        # Reading order
        #
        # Entire left column
        # then
        # Entire right column
        # -----------------------------------

        ordered_blocks = []

        ordered_blocks.extend(left_column)
        ordered_blocks.extend(right_column)

        return ordered_blocks