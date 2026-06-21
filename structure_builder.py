import litellm
import json
from config import MODEL

def ask_llm(prompt):
    response = litellm.completion(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content

def tag_pages(pages, start_index=0):
    """
    Wrap each page text with physical index tags.
    The LLM uses these tags to identify page numbers.
    """
    tagged = ""
    for i, page_text in enumerate(pages):
        page_num = i + start_index + 1
        tagged += f"<physical_index_{page_num}>\n{page_text}\n<physical_index_{page_num}>\n\n"
    return tagged

def parse_llm_json(response):
    """Safely parse JSON from LLM response."""
    try:
        # remove markdown code fences if present
        text = response.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except:
        return []

def extract_structure_from_content(pages):
    """
    Path C — No TOC.
    LLM reads tagged pages and infers structure from headings.
    Returns flat list of sections.
    """
    print("No TOC found. Inferring structure from content...")
    tagged = tag_pages(pages)

    prompt = f"""
    You are given a document with pages marked by <physical_index_N> tags.
    Your job is to extract the hierarchical structure of this document.
    
    Use "structure" codes like "1", "1.1", "1.2", "2", "2.1" to show hierarchy.
    Use the physical_index tag number to record which page a section starts on.
    
    Reply ONLY with a JSON array like:
    [
        {{"structure": "1", "title": "Introduction", "physical_index": 3}},
        {{"structure": "1.1", "title": "Background", "physical_index": 4}},
        {{"structure": "2", "title": "Methods", "physical_index": 10}}
    ]
    Do not say anything else.
    
    Document:
    {tagged[:15000]}
    """
    response = ask_llm(prompt)
    return parse_llm_json(response)

def extract_structure_from_toc(toc_text, pages, has_page_numbers):
    """
    Path A or B — TOC exists.
    Converts TOC text into structured JSON.
    """
    print("TOC found. Extracting structure from TOC...")

    if has_page_numbers:
        # Path A — TOC has page numbers, extract directly
        prompt = f"""
        You are given a table of contents from a document.
        Convert it into a JSON array with structure codes, titles, and page numbers.
        
        Use "structure" codes like "1", "1.1", "2" etc to represent hierarchy.
        
        Reply ONLY with a JSON array like:
        [
            {{"structure": "1", "title": "Introduction", "physical_index": 3}},
            {{"structure": "1.1", "title": "Background", "physical_index": 4}}
        ]
        Do not say anything else.
        
        Table of contents:
        {toc_text}
        """
    else:
        # Path B — TOC exists but no page numbers, scan document to find pages
        tagged = tag_pages(pages)
        prompt = f"""
        You are given a table of contents and a full document with page tags.
        Find which physical page each section starts on using the <physical_index_N> tags.
        
        Reply ONLY with a JSON array like:
        [
            {{"structure": "1", "title": "Introduction", "physical_index": 3}},
            {{"structure": "1.1", "title": "Background", "physical_index": 4}}
        ]
        Do not say anything else.
        
        Table of contents:
        {toc_text}
        
        Document:
        {tagged[:15000]}
        """

    response = ask_llm(prompt)
    return parse_llm_json(response)

def verify_structure(structure, pages):
    """
    Spot check: ask LLM if each section title actually appears on its assigned page.
    Returns accuracy score and list of wrong entries.
    """
    print("Verifying structure accuracy...")
    correct = 0
    incorrect = []

    for i, item in enumerate(structure):
        page_num = item.get("physical_index")
        if page_num is None:
            continue
        page_idx = page_num - 1
        if page_idx < 0 or page_idx >= len(pages):
            incorrect.append({**item, "list_index": i})
            continue

        page_text = pages[page_idx]
        title = item.get("title", "")

        prompt = f"""
        Does the section titled "{title}" start on or appear in the following page text?
        Reply ONLY with {{"answer": "yes"}} or {{"answer": "no"}}.
        
        Page text:
        {page_text[:2000]}
        """
        response = ask_llm(prompt)
        try:
            data = json.loads(response.strip())
            if data.get("answer") == "yes":
                correct += 1
            else:
                incorrect.append({**item, "list_index": i})
        except:
            incorrect.append({**item, "list_index": i})

    total = len(structure)
    accuracy = correct / total if total > 0 else 0
    print(f"Accuracy: {accuracy*100:.1f}%")
    return accuracy, incorrect