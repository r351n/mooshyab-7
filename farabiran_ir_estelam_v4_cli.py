import os
import csv
import ujson as json
import jsonlines
import requests
import multiprocessing
from art import text2art
from termcolor import colored


URL = "https://farabiran.ir/Estelam?handler=Search&id={}"
SESSION = requests.Session()

from tabulate import tabulate

def send_request(id_num):
    response = SESSION.get(URL.format(id_num))
    if response.status_code == 200:
        data = json.loads(response.content)
        table_data = []
        for key, value in data.items():
            table_data.append([key, value])
        table = tabulate(table_data, headers=["Field", "Value"], tablefmt="presto")
        print(table)
        return response.content
    
    else:
        print(f"ID {id_num} not found.")


def search_single_id():
    id_num = input("Enter the ID you want to search for: ")
    with multiprocessing.Pool() as pool:
        with SESSION as session, \
             jsonlines.open(f"{id_num}.jsonl", mode="w") as writer:
            # Set session object for each worker process
            pool.map_async(session.mount, [URL]*len(pool._pool))

            # Use imap_unordered to process results as soon as they become available
            for result in pool.imap_unordered(send_request, range(int(id_num), int(id_num)+1)):
                if result is not None:
                    writer.write(json.loads(result))

    save_file = input("Save to file? (y/n): ")
    if save_file.lower() == "y":
        with open(f"{id_num}.csv", "w", newline="", encoding="utf-8") as f, \
            jsonlines.open(f"{id_num}.jsonl", "r") as reader:
            data = list(reader)
            fieldnames = set()
            for obj in data:
                fieldnames.update(obj.keys())

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        os.remove(f"{id_num}.jsonl")
        print(f"File saved successfully in {id_num}.csv")
    else: 
        os.remove(f"{id_num}.jsonl")

    exit_program = input("Exit program? (y/n): ")
    if exit_program.lower() == "y":
        print("Exiting ID Searcher...")
        exit()

def search_id_range():
    start = int(input("Enter the starting ID for the range: "))
    end = int(input("Enter the ending ID for the range: "))
    with multiprocessing.Pool() as pool:
        with SESSION as session, \
             jsonlines.open(f"{start}-{end}.jsonl", mode="w") as writer:
            # Set session object for each worker process
            pool.map_async(session.mount, [URL]*len(pool._pool))

            # Use imap_unordered to process results as soon as they become available
            for result in pool.imap_unordered(send_request, range(start, end)):
                if result is not None:
                    writer.write(json.loads(result))

    save_file = input("Save to file? (y/n): ")
    if save_file.lower() == "y":
        with open(f"{start}-{end}.csv", "w", newline="", encoding="utf-8") as f, \
            jsonlines.open(f"{start}-{end}.jsonl", "r") as reader:
            data = list(reader)
            fieldnames = set()
            for obj in data:
                fieldnames.update(obj.keys())

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        os.remove(f"{start}-{end}.jsonl")
        print(f"File saved successfully in {start}-{end}.csv")
    else:
        os.remove(f"{start}-{end}.jsonl")

    exit_program = input("Exit program? (y/n): ")
    if exit_program.lower() == "y":
        print("Exiting ID Searcher...")
        exit()

def main():
    # print(text2art("Mooshyab 7", font="small"))
    title = "Mooshyab 7"
    ascii_title = text2art(title, font='small', chr_ignore=True)
    colored_title = colored(ascii_title, 'cyan', attrs=['bold', 'underline'])
    print(colored_title)
    print("Welcome to Farabiran ID Searcher CLI v1.0\n")
    while True:
        print("\n\033[1;33mWhat would you like to do?\033[0m\n")
        print("1. Search for a single ID")
        print("2. Search for a range of IDs")
        print("3. Exit")

        choice = input("\nEnter your choice: ")
        if choice == "1":
            search_single_id()
        elif choice == "2":
            search_id_range()
        elif choice == "3":
            print("Exiting ID Searcher...")
            break
        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":
    main()
