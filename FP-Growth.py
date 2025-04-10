import argparse
import math
from array import array


parser = argparse.ArgumentParser(description="FP-Growth Frequent Pattern Mining")
parser.add_argument("min_support", type=float, help="Minimum support")
parser.add_argument("input_file", type=str, help="Input file")
parser.add_argument("output_file", type=str, help="Output file")

args = parser.parse_args()
given_support = args.min_support
input_file = args.input_file
output_file = args.output_file

output_lines = []

class FPNode:
    def __init__(self, item, count, parent):
        self.item = item        #root.item = None
        self.count = count       
        self.parent = parent    
        self.children = {}       
        self.link = None        


def update_tree(items, node, header_table):
    if len(items) == 0:
        return
    first_item = items[0]
    if first_item in node.children:
        node.children[first_item].count += 1
    else:
        new_node = FPNode(first_item, 1, node)
        node.children[first_item] = new_node
        if header_table[first_item]["node"] is None:
            header_table[first_item]["node"] = new_node
        else:
            current = header_table[first_item]["node"]
            while current.link is not None:
                current = current.link
            current.link = new_node
    update_tree(items[1:], node.children[first_item], header_table)



def build_tree(freq, transactions):
    if not freq:
        return None

    header_table = {item: {"support": count, "node": None} for item, count in freq.items()}
    root = FPNode(None, 1, None)

    for trans in transactions.values():
        temp = {item for item in trans if item in freq}
        if temp:
            sorted_items = sorted(temp, key=lambda x: freq[x], reverse=True)
            update_tree(sorted_items, root, header_table)
    
    return header_table



def find_paths(base_item, header_table):
    conditional_transactions = {}
    freq = {} 
    node = header_table[base_item]["node"]
    trans_id = 0
    while node is not None:   
        path = []
        current_node = node
        counts = node.count
        while current_node.parent is not None and current_node.parent.item is not None:
            current_node = current_node.parent
            item = current_node.item
            path.append(item)
            freq[item] = freq.get(item, 0) + counts
        
        if path:
            transaction = array('i', reversed(path))
            for _ in range(counts):
                conditional_transactions[trans_id] = transaction
                trans_id += 1
        node = node.link
    
    return conditional_transactions, freq



def mine_tree(header_table, min_support, prefix, freq_itemsets):
    sorted_items = sorted(header_table.items(), key=lambda x: x[1]["support"])

    for item, value in sorted_items:
        support = value["support"]
        new_prefix = prefix.copy()
        new_prefix.add(item)
        
        freq_itemsets[frozenset(new_prefix)] = support
        pattern_str = ",".join(map(str, sorted(new_prefix)))
        support_str = f"{support/total_transactions:.4f}"
        output_lines.append(f"{pattern_str}:{support_str}")

        conditional_transactions, freq = find_paths(item, header_table)
        
        if conditional_transactions:
            freq = {item: count for item, count in freq.items() if count >= min_support_count}
            conditional_header = build_tree(freq, conditional_transactions)
            if conditional_header:
                mine_tree(conditional_header, min_support, new_prefix, freq_itemsets)


with open(input_file, "r") as infile:
    data = infile.read()

lines = data.strip().split("\n")
transactions = {}
freq = {}
for i, line in enumerate(lines):
    temp = set()
    for x in line.strip().split(","):
        item = int(x)
        temp.add(item)
        freq[item] = freq.get(item, 0) + 1
    transactions[i] = temp

total_transactions = i+1
min_support_count = given_support * total_transactions
freq = {item: count for item, count in freq.items() if count >= min_support_count}
header_table = build_tree(freq, transactions)

freq_itemsets = {}
mine_tree(header_table, min_support_count, set(), freq_itemsets)


output_str = "\n".join(output_lines)
with open(f"output/{output_file}", "w") as outfile:
    outfile.write(output_str)
