import json
from collections import deque
import itertools
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from urllib.parse import quote

pages_file = "wikipages_mini.json"
driver = webdriver.Chrome()

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

def run_wiki_bot(path, website="wikipedia.org", wiki_speedruns_lobby_info={}):
    start_url = ""
    search_url = ""
    sleep_time = 0.1
    if website == "wikipedia.org":
        start_url = "https://en." + website + "/wiki/" + path[0]
        search_url = "https://en." + website + "/wiki/"
        driver.get(start_url)
    elif website == "wikispeedruns.com" and wiki_speedruns_lobby_info == {}:
        # Set up wikipedia speedruns for correct pages (XPATH is pretty rigid so it might need to be updated often
        # but the inputs and start button don't have an id so not really a better way to select them.)
        start_url = "https://" + website
        search_url = "/wiki/"
        driver.get(start_url)
        start_input = driver.find_element(By.XPATH, '//*[@id="quick-play"]/div[2]/div/div[1]/div[2]/div/div[1]/div/div/input')
        start_input.clear()
        start_input.send_keys(path[0].replace("-", " ").replace("_", " ").title())
        time.sleep(2)
        start_input.send_keys(Keys.RETURN)
        end_input = driver.find_element(By.XPATH, '//*[@id="quick-play"]/div[2]/div/div[1]/div[2]/div/div[3]/div/div/input')
        end_input.clear()
        end_input.send_keys(path[-1].replace("-", " ").replace("_", " ").title())
        time.sleep(2)
        end_input.send_keys(Keys.RETURN)
        start_button = driver.find_element(By.XPATH, '//*[@id="quick-play"]/div[2]/div/div[4]/button[1]')
        start_button.click()
        time.sleep(1)
        skip_button = driver.find_element(By.ID, "start-btn")
        skip_button.click()
    elif website == "wikispeedruns.com" and "lobby_number" in wiki_speedruns_lobby_info:
        start_url = "https://" + website + "/lobby/" + wiki_speedruns_lobby_info['lobby_number']
        search_url = "/wiki/"
        driver.get(start_url)
        name_input = driver.find_element(By.ID, "name")
        name_input.clear()
        name_input.send_keys(wiki_speedruns_lobby_info['username'])
        pass_input = driver.find_element(By.ID, "desc")
        pass_input.clear()
        pass_input.send_keys(wiki_speedruns_lobby_info['lobby_password'])
        submit_button = driver.find_element(By.XPATH, '//*[@id="joinForm"]/button')
        submit_button.click()
        time.sleep(1)
        start_link = None
        try:
            print(f"{start_url}/play/{wiki_speedruns_lobby_info['prompt_number']}")
            start_link = driver.find_element(By.CSS_SELECTOR, f'a[href="/lobby/{wiki_speedruns_lobby_info['lobby_number']}/play/{wiki_speedruns_lobby_info['prompt_number']}"]')
        except:
            print("Prompts table wasn't found. Code is outdated or login information was incorrect.")
            return None, "Something went wrong loading your data"
        input("All set! Press enter to start.")
        start_link.click()
        time.sleep(1)
        skip_button = driver.find_element(By.ID, "start-btn")
        skip_button.click()
    elif website == "wikispeedrun.org":
        start_url = "https://" + website + "/settings"
        search_url = "/wiki/"
        driver.get(start_url)
        time.sleep(1)
        start_input = driver.find_element(By.ID, 'startArticle')
        start_input.clear()
        start_input.send_keys(path[0].replace("-", " ").replace("_", " ").title())
        time.sleep(2)
        start_input.send_keys(Keys.RETURN)
        end_input = driver.find_element(By.ID, 'endArticle')
        end_input.clear()
        end_input.send_keys(path[-1].replace("-", " ").replace("_", " ").title())
        time.sleep(2)
        end_input.send_keys(Keys.RETURN)
        start_button = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div[2]/div/form/div[5]/button[2]')
        start_button.click()
    else:
        return None, "Invalid Website or Login Info"

    start_time_millis = int(time.time() * 1000)
    time_waiting = 0
    prev_page = path[0]
    page_load = True
    for page in path[1:]:
        next_page_url_encoded = f"{search_url}{quote(page)}"
        next_page_url_unencoded = f"{search_url}{page}"
        page_link = None
        while page_link == None:
            if website == "wikispeedruns.com" and page_load:
                time.sleep(1)
                time_waiting += 1
                page_load = False
            try:
                page_link = driver.find_element(By.CSS_SELECTOR, f'a[href="{next_page_url_unencoded}"]')
            except:
                try:
                    page_link = driver.find_element(By.CSS_SELECTOR, f'a[href="{next_page_url_encoded}"]')
                except:
                    if prev_page.replace("-", " ").replace("_", " ").lower == page.replace("-", " ").replace("_", " ").lower():
                        print("Skipping page, duplicate redirect found")
                        continue
                    page_link = None
                    time.sleep(sleep_time)
                    time_waiting += sleep_time

        if page_link != None: 
            prev_page = page
            driver.execute_script("arguments[0].click();", page_link)
            page_load = True
    end_time_millis = int(time.time() * 1000)
    total_time = end_time_millis - start_time_millis
    return total_time, time_waiting


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

    if starting_title != "":
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

    if starting_title != "" and ending_title != "":
        path = bidirectional_bfs(starting_title, ending_title)
        print(path)
        run_bot = input("Do you want to run the automatic bot for this path? (Y/N): ")
        if run_bot.upper() == "Y" or run_bot.upper() == "YES":
            print("Do you want to run this bot on wikispeedruns.com, wikispeedrun.org or wikipedia.com?")
            website = input("If you don't want to type out the whole link you can type 1 for wikispeedruns.com, 2 for wikispeedrun.org anything else will default to wikipedia.com: ")
            if website == "1" or website == "wikispeedruns.com":
                in_lobby = input("Are you in a lobby for wikispeedruns.com? (Y/N): ")
                if in_lobby.upper() == "N" or in_lobby.upper() == "NO":
                    total_time, wait_time = run_wiki_bot(path, "wikispeedruns.com")
                else:
                    login_info = {}
                    login_info['lobby_number'] = input("Input lobby number here (the numbers after the last / in the url): ")
                    login_info['lobby_password'] = input("Input lobby password here: ")
                    login_info['username'] = input("Put the name you will go as here: ")
                    login_info['prompt_number'] = input("In the lobby there should be a prompt # column for different challenges. Input the prompt #: ")
                    total_time, wait_time = run_wiki_bot(path, "wikispeedruns.com", login_info)
            elif website == "2" or website == "wikispeedrun.org":
                total_time, wait_time = run_wiki_bot(path, "wikispeedrun.org")
            else:
                total_time, wait_time = run_wiki_bot(path)

        if total_time != None:
            print(f"Total time to completion: {total_time / 1000} seconds")
            print(f"Total wait/load time: {wait_time} seconds")
            print(f"Time excluding wait/load time: {(total_time / 1000) - wait_time} seconds")
            total_time = None
            wait_time = None

    command = input("Type quit to exit the program or anything else to find a path between two wikipedia pages: ")