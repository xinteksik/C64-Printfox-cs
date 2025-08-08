#!/usr/bin/env python3
import argparse
from pypdf import PdfReader, PdfWriter, PageObject, Transformation


def parse_range(pages_str, total_pages):
    """Parse 'start-end', 'start-', or '-end' into 1-based start/end."""
    if not pages_str:
        return 1, total_pages
    parts = pages_str.split("-")
    if len(parts) != 2:
        raise ValueError("Invalid page range format. Use start-end, start-, or -end.")
    start_str, end_str = parts
    start = int(start_str) if start_str.strip() else 1
    end = int(end_str) if end_str.strip() else total_pages
    if start < 1 or end > total_pages or start > end:
        raise ValueError(f"Invalid range {start}-{end} for document with {total_pages} pages.")
    return start, end


def compute_booklet_pairs(total_pages):
    """Return booklet page order pairs."""
    m = ((total_pages + 3) // 4) * 4
    pairs = []
    for i in range(m // 4):
        front_left = m - 2 * i
        front_right = 1 + 2 * i
        back_left = 2 + 2 * i
        back_right = m - 1 - 2 * i
        pairs.append((front_left, front_right))
        pairs.append((back_left, back_right))
    return m, pairs


def get_page(pages, index_1based, w, h):
    """Return page object or blank page."""
    if 1 <= index_1based <= len(pages):
        return pages[index_1based - 1]
    else:
        return PageObject.create_blank_page(width=w, height=h)


def impose_booklet(input_path, output_path, reorder_only=False, page_range=None):
    reader_full = PdfReader(input_path)
    total_original = len(reader_full.pages)

    start, end = parse_range(page_range, total_original) if page_range else (1, total_original)

    # Vyber jen zadané stránky (kopie seznamu, ne nový PDF objekt)
    selected_pages = [reader_full.pages[i] for i in range(start - 1, end)]

    if not selected_pages:
        raise ValueError("No pages selected.")

    w = float(selected_pages[0].mediabox.width)
    h = float(selected_pages[0].mediabox.height)

    n = len(selected_pages)
    padded_count, pairs = compute_booklet_pairs(n)

    writer = PdfWriter()
    if reorder_only:
        flat_order = [idx for pair in pairs for idx in pair]
        for idx in flat_order:
            page = get_page(selected_pages, idx, w, h)
            writer.add_page(page)
    else:
        for left_idx, right_idx in pairs:
            left_page = get_page(selected_pages, left_idx, w, h)
            right_page = get_page(selected_pages, right_idx, w, h)
            sheet = PageObject.create_blank_page(width=2 * w, height=h)
            t_left = Transformation().translate(0, 0)
            t_right = Transformation().translate(w, 0)
            sheet.merge_transformed_page(left_page, t_left, expand=False)
            sheet.merge_transformed_page(right_page, t_right, expand=False)
            writer.add_page(sheet)

    with open(output_path, "wb") as f:
        writer.write(f)


def main():
    parser = argparse.ArgumentParser(description="Impose a portrait PDF into booklet order.")
    parser.add_argument("input", help="Path to input PDF")
    parser.add_argument("output", help="Path to output PDF")
    parser.add_argument("--pages", help="Page range in format start-end, start-, or -end", default=None)
    parser.add_argument("--reorder-only", action="store_true", help="Only reorder pages (no 2-up imposition)")
    args = parser.parse_args()

    impose_booklet(args.input, args.output, reorder_only=args.reorder_only, page_range=args.pages)


if __name__ == "__main__":
    main()