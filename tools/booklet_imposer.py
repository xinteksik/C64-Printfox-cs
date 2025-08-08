#!/usr/bin/env python3
"""
booklet_imposer.py

Take a portrait PDF (single pages) and rearrange + impose it into a booklet-ready PDF:
- Pages are re-ordered into booklet (signature) order.
- Two input pages are placed side-by-side on one landscape sheet (left/right),
  producing a PDF ready for duplex printing (flip on short edge), then fold in half.

Usage:
  python booklet_imposer.py input.pdf output.pdf

Options:
  --reorder-only    Only reorder pages (no 2-up imposition). Output keeps original page size.

Notes:
- If the number of pages is not divisible by 4, blank pages are added automatically.
- For duplex print, select "Flip on SHORT edge" (sometimes called "short-edge binding").
"""

import argparse
from pypdf import PdfReader, PdfWriter, PageObject, Transformation


def compute_booklet_pairs(total_pages: int):
    """
    Return a list of tuples representing each sheet side:
    [(left_idx, right_idx), (left_idx, right_idx), ...]
    where indices are 1-based into the padded document (blanks beyond original pages).
    The order alternates: first pair = front of sheet 1, second pair = back of sheet 1, etc.
    """
    m = ((total_pages + 3) // 4) * 4  # pad to multiple of 4
    pairs = []
    for i in range(m // 4):
        # 1-based indices for booklet order
        front_left = m - 2 * i
        front_right = 1 + 2 * i
        back_left = 2 + 2 * i
        back_right = m - 1 - 2 * i
        pairs.append((front_left, front_right))  # front side
        pairs.append((back_left, back_right))    # back side
    return m, pairs


def get_page(reader: PdfReader, index_1based: int, w: float, h: float, total_original: int):
    """
    Return a page object for the given 1-based index. If it exceeds the original
    page count, return a blank page of size (w x h).
    """
    if 1 <= index_1based <= total_original:
        page = reader.pages[index_1based - 1]
        return page
    else:
        # blank filler page
        return PageObject.create_blank_page(width=w, height=h)


def impose_booklet(input_path: str, output_path: str, reorder_only: bool = False):
    reader = PdfReader(input_path)
    writer = PdfWriter()

    if len(reader.pages) == 0:
        raise ValueError("Input PDF has no pages.")

    # Use the first page as size reference
    ref_page = reader.pages[0]
    w = float(ref_page.mediabox.width)
    h = float(ref_page.mediabox.height)

    n = len(reader.pages)
    padded_count, pairs = compute_booklet_pairs(n)

    if reorder_only:
        # Just output the pages in booklet reading order (not imposed 2-up)
        # Convert pair list into a flat order: left, right, left, right, ...
        flat_order = [idx for pair in pairs for idx in pair]
        for idx in flat_order:
            page = get_page(reader, idx, w, h, n)
            # Clone the page to avoid mutating original objects
            writer.add_page(page)
    else:
        # Create landscape sheets sized 2*w by h, and place left/right pages
        for left_idx, right_idx in pairs:
            left_page = get_page(reader, left_idx, w, h, n)
            right_page = get_page(reader, right_idx, w, h, n)

            sheet = PageObject.create_blank_page(width=2 * w, height=h)

            # Normalize rotations if any (merge_transformed_page applies transformation matrix)
            t_left = Transformation().translate(0, 0)
            t_right = Transformation().translate(w, 0)

            sheet.merge_transformed_page(left_page, t_left, expand=False)
            sheet.merge_transformed_page(right_page, t_right, expand=False)

            writer.add_page(sheet)

    with open(output_path, "wb") as f:
        writer.write(f)


def main():
    parser = argparse.ArgumentParser(description="Impose a portrait PDF into booklet order (ready for duplex print).")
    parser.add_argument("input", help="Path to input PDF")
    parser.add_argument("output", help="Path to output PDF")
    parser.add_argument("--reorder-only", action="store_true",
                        help="Only reorder pages into booklet reading order (no 2-up imposition)")

    args = parser.parse_args()
    impose_booklet(args.input, args.output, reorder_only=args.reorder_only)


if __name__ == "__main__":
    main()
