from mwsql import Dump
import json
import time

# This file parses through wikipedia dump files and converts it into a giant json file
# The giant json file lists every link to and from every wikipedia page included in these dumps

page_file = "../WikipediaFiles/enwiki-20260801-page.sql.gz"
page_links_file = "../WikipediaFiles/enwiki-20260801-pagelinks.sql.gz"
link_target_file = "../WikipediaFiles/enwiki-20260801-linktarget.sql.gz"

page_dump = Dump.from_file(page_file)
page_link_dump = Dump.from_file(page_links_file)
link_target_dump = Dump.from_file(link_target_file)

pages_outgoing_dict = {}
pages_incoming_dict = {}
link_target_dict = {}

link_target_id_idx = link_target_dump.col_names.index("lt_id")
link_target_namespace_idx = link_target_dump.col_names.index("lt_namespace")
link_target_title_id = link_target_dump.col_names.index("lt_title")
start_time = time.perf_counter()
print("Started Processing Links")
for row in link_target_dump:
    if row[link_target_namespace_idx] == "0":
        link_target_dict[row[link_target_id_idx]] = row[link_target_title_id]
print("Finished Building Link Target Dictionary")
end_link_target_time = time.perf_counter()
time_diff_1 = (end_link_target_time - start_time)
print(f"Processing Link Target Dictionary took: {(time_diff_1 / (60 * 60)):.4f} hours")

id_idx = page_dump.col_names.index("page_id")
namespace_idx = page_dump.col_names.index("page_namespace")
title_idx = page_dump.col_names.index("page_title")
for row in page_dump:
    if row[namespace_idx] == "0":
        new_outgoing_page = {'title': row[title_idx], 'outgoing': []}
        pages_outgoing_dict[row[id_idx]] = new_outgoing_page
        new_incoming_page = {'id': row[id_idx], 'incoming': []}
        pages_incoming_dict[row[title_idx]] = new_incoming_page
print("Done Building Pages Dictionary")
end_page_time = time.perf_counter()
time_diff_2 = (end_page_time - end_link_target_time)
print(f"Processing Pages Dictionary took: {(time_diff_2 / (60 * 60)):.4f} hours")

from_id_idx = page_link_dump.col_names.index("pl_from")
target_id_idx = page_link_dump.col_names.index("pl_target_id")
for row in page_link_dump:
    from_page_id  = row[from_id_idx]
    link_target_id = row[target_id_idx]
    target_page_title = None
    if link_target_id in link_target_dict:
        target_page_title = link_target_dict[link_target_id]

    if from_page_id in pages_outgoing_dict and target_page_title in pages_incoming_dict:
        pages_outgoing_dict[from_page_id]['outgoing'].append(target_page_title)
        pages_incoming_dict[target_page_title]['incoming'].append(pages_outgoing_dict[from_page_id]['title'])
print("Done Mapping Connections")
end_page_link_time = time.perf_counter()
time_diff_3 = (end_page_link_time - end_page_time)
print(f"Processing Page Links Dictionary took: {(time_diff_3 / (60 * 60)):.4f} hours")

pages_fused_dict = {}
for page in pages_outgoing_dict.values():
    page_title = page['title']
    page_incoming = pages_incoming_dict[page_title]
    pages_fused_dict[page_title] = {'incoming': page_incoming['incoming'], 'outgoing': page['outgoing']}
print("Finished Fusing Dictionaries")
end_fuse_time = time.perf_counter()
time_diff_4 = (end_fuse_time - end_page_link_time)
print(f"Fusing Page Links Dictionaries took: {(time_diff_4 / (60 * 60)):.4f} hours")

with open("wikipages.json", "w") as json_file:
    json.dump(pages_fused_dict, json_file)
print("Generated Json File")
end_time = time.perf_counter()
time_diff_5 = (end_time - start_time)
print(f"Finished processing in {(time_diff_5 / (60 * 60)):.4f} hours")