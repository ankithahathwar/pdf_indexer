def assign_page_ranges(flat_list, total_pages):
    """
    Give each section a start_index and end_index
    based on where the next section begins.
    """
    for i, item in enumerate(flat_list):
        item["start_index"] = item.get("physical_index")
        if i < len(flat_list) - 1:
            item["end_index"] = flat_list[i+1]["physical_index"]
        else:
            item["end_index"] = total_pages
    return flat_list

def get_parent_code(structure_code):
    """
    "1.2.3" → "1.2"
    "1.1"   → "1"
    "1"     → None
    """
    parts = str(structure_code).split(".")
    if len(parts) <= 1:
        return None
    return ".".join(parts[:-1])

def build_tree(flat_list):
    """
    Convert flat list into nested tree using structure codes.
    """
    node_map = {}
    root_nodes = []

    for item in flat_list:
        code = item.get("structure")
        node = {
            "title": item.get("title"),
            "start_index": item.get("start_index"),
            "end_index": item.get("end_index"),
            "nodes": []
        }
        node_map[code] = node

        parent_code = get_parent_code(code)
        if parent_code and parent_code in node_map:
            node_map[parent_code]["nodes"].append(node)
        else:
            root_nodes.append(node)

    # clean up empty nodes arrays
    def clean(node):
        if not node["nodes"]:
            del node["nodes"]
        else:
            for child in node["nodes"]:
                clean(child)
        return node

    return [clean(node) for node in root_nodes]

def add_node_ids(tree, counter=[0]):
    """Stamp each node with a unique zero-padded ID."""
    for node in tree:
        node["node_id"] = str(counter[0]).zfill(4)
        counter[0] += 1
        if node.get("nodes"):
            add_node_ids(node["nodes"], counter)
    return tree