import litellm
import json
from config import MODEL, TOC_CHECK_PAGES

def ask_llm(prompt):
    """Send a prompt to the LLM and return the text response."""
    response = litellm.completion(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content

def is_toc_page(page_text):
    """Ask LLM if this page is a table of contents. Returns True or False."""
    prompt = f"""
    Does the following page contain a table of contents?
    Reply with only a JSON object like: {{"is_toc": "yes"}} or {{"is_toc": "no"}}
    Do not say anything else.
    
    Page text:
    {page_text[:2000]}
    """
    response = ask_llm(prompt)
    try:
        data = json.loads(response.strip())
        return data.get("is_toc") == "yes"
    except:
        return False

def find_toc_pages(pages):
    """
    Scan first N pages to find which ones are TOC pages.
    Returns a list of page indices that contain TOC content.
    """
    toc_pages = []
    found_toc = False

    for i, page_text in enumerate(pages[:TOC_CHECK_PAGES]):
        result = is_toc_page(page_text)
        if result:
            toc_pages.append(i)
            found_toc = True
            print(f"  TOC found on page {i+1}")
        elif found_toc:
            # once we've seen TOC pages and hit a non-TOC page, stop
            break

    return toc_pages