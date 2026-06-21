import json
import os
import sys
from pdf_reader import read_pdf
from toc_detector import find_toc_pages
from structure_builder import (
    extract_structure_from_content,
    extract_structure_from_toc,
    verify_structure
)
from tree_builder import assign_page_ranges, build_tree, add_node_ids

def run(pdf_path):
    print(f"\n--- Processing: {pdf_path} ---\n")
    
    # Step 1: read PDF
    pages = read_pdf(pdf_path)
    total_pages = len(pages)

    # Step 2: detect TOC
    print("Scanning for Table of Contents...")
    toc_page_indices = find_toc_pages(pages)

    # Step 3: build flat structure
    if toc_page_indices:
        toc_text = "\n".join([pages[i] for i in toc_page_indices])
        # check if TOC has page numbers (simple heuristic)
        import re
        has_page_numbers = bool(re.search(r'\d+\s*$', toc_text, re.MULTILINE))
        flat_structure = extract_structure_from_toc(toc_text, pages, has_page_numbers)
    else:
        flat_structure = extract_structure_from_content(pages)

    if not flat_structure:
        print("Could not extract structure. Exiting.")
        return

    # Step 4: verify
    accuracy, incorrect = verify_structure(flat_structure, pages)
    print(f"Found {len(incorrect)} incorrect entries out of {len(flat_structure)}")

    # Step 5: assign page ranges
    flat_structure = assign_page_ranges(flat_structure, total_pages)

    # Step 6: build tree
    tree = build_tree(flat_structure)

    # Step 7: add node IDs
    tree = add_node_ids(tree)

    # Step 8: save output
    pdf_name = os.path.basename(pdf_path)
    result = {
        "doc_name": pdf_name,
        "total_pages": total_pages,
        "structure": tree
    }

    os.makedirs("outputs", exist_ok=True)
    output_path = f"outputs/{pdf_name.replace('.pdf', '')}_groq_llama70b_2.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\nDone! Saved to {output_path}")
    print(f"Top-level sections: {len(tree)}")
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py your_file.pdf")
    else:
        run(sys.argv[1])