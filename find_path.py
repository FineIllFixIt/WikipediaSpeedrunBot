import json
from collections import deque
import itertools

pages_file = "wikipages_mini.json"

pages = None
print("Loading File...")
with open(pages_file, "r", encoding="utf-8") as file:
    pages = json.load(file)
print("Done Loading File")

def bidirectional_bfs(start, end):
    outgoing_visited = {start: None}
    incoming_visited  = {end: None}

    outgoing_queue = deque([start])
    incoming_queue = deque([end])

    while outgoing_queue and incoming_queue:
        current_out = outgoing_queue.popleft()
        for page in pages[current_out]['outgoing']:
            if page in incoming_visited:
                return get_path(outgoing_visited, incoming_visited, current_out, page)
            if page not in outgoing_visited:
                outgoing_visited[page] = current_out
                outgoing_queue.append(page)

        current_in = incoming_queue.popleft()
        for page in pages[current_in]['incoming']:
            if page in outgoing_visited:
                return get_path(outgoing_visited, incoming_visited, page, current_in)
            if page not in incoming_visited:
                incoming_visited[page] = current_in
                incoming_queue.append(page)

    return None

def get_path(outgoing_visited, incoming_visited, intersect_out, intersect_in):
    path_out = []
    curr = intersect_out
    while curr is not None:
        path_out.append(curr)
        curr = outgoing_visited[curr]
    path_out.reverse()

    path_in = []
    curr = intersect_in
    while curr is not None:
        path_in.append(curr)
        curr = incoming_visited[curr]

    return path_out + path_in

def get_title_option(title):
    title_case = title.title()
    upper_case = title.capitalize()

    fragments = title.split(' ')
    num_spaces = len(fragments) - 1
    char_options = ["_", "-"]

    results = []
    for combos in itertools.product(char_options, repeat=num_spaces):
        zipped = zip(fragments, list(combos) + [''])
        new_sentence = "".join(f + c for f, c in zipped)
        results.append(new_sentence)

    fragments = title_case.split(' ')
    for combos in itertools.product(char_options, repeat=num_spaces):
        zipped = zip(fragments, list(combos) + [''])
        new_sentence = "".join(f + c for f, c in zipped)
        results.append(new_sentence)

    fragments = upper_case.split(' ')
    for combos in itertools.product(char_options, repeat=num_spaces):
        zipped = zip(fragments, list(combos) + [''])
        new_sentence = "".join(f + c for f, c in zipped)
        results.append(new_sentence)
        
    return results


command = ""
while command != "q" and command != "quit":
    starting_page = input("Input the title of the starting wikipedia page: ")
    starting_pages = get_title_option(starting_page)

    starting_title = ""
    for page in starting_pages:
        if page in pages:
            starting_title = page
            break
    if starting_title == "":
        starting_title = input("Page not found. Either try again or input the url: ").split("/")[-1]
        if starting_title not in pages:
            starting_title = ""
            print("That url didn't work. The wikipages file might be out of date or the url was input wrong. Please try a different page.")

    ending_page = input("Input the title of the ending wikipedia page: ")
    ending_pages = get_title_option(ending_page)

    ending_title = ""
    for page in ending_pages:
        if page in pages:
            ending_title = page
            break
    if ending_title == "":
        ending_title = input("Page not found. Either try again or input the url: ").split("/")[-1]
        if ending_title not in pages:
            ending_title = ""
            print("That url didn't work. The wikipages file might be out of date or the url was input wrong. Please try a different page.")


    print(starting_title)
    print(ending_title)
    path = bidirectional_bfs(starting_title, ending_title)
    print(path)
    command = input("Type quit to exit the program or anything else to find a path between two wikipedia pages: ")