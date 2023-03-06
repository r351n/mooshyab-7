import os
import csv
import ujson as json
import jsonlines
import requests
import multiprocessing
from art import text2art
from termcolor import colored
from tabulate import tabulate

URL = "https://farabiran.ir/Estelam?handler=Search&id={}"
SESSION = requests.Session()

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
        return None

def search_ids(search_type):
    try:
        if search_type == 1:
            id_num = input("Enter the ID you want to search for: ")
            start_id = int(id_num)
            end_id = int(id_num) + 1
            file_name = f"{id_num}"
        elif search_type == 2:
            start_id = int(input("Enter the starting ID for the range: "))
            end_id = int(input("Enter the ending ID for the range: "))
            file_name = f"{start_id}-{end_id}"
        else:
            print("Invalid input")
            return

        with multiprocessing.Pool() as pool, \
             SESSION as session, \
             jsonlines.open(f"{file_name}.jsonl", mode="w") as writer:
            # Set session object for each worker process
            pool.map_async(session.mount, [URL]*len(pool._pool))

            # Use imap_unordered to process results as soon as they become available
            for result in pool.imap_unordered(send_request, range(start_id, end_id)):
                if result is not None:
                    writer.write(json.loads(result))

        save_file = input("Save to file? (y/n): ")
        if save_file.lower() == "y":
            with open(f"{file_name}.csv", "w", newline="", encoding="utf-8") as f, \
                jsonlines.open(f"{file_name}.jsonl", "r") as reader:
                data = list(reader)
                fieldnames = set()
                for obj in data:
                    fieldnames.update(obj.keys())

                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)

            os.remove(f"{file_name}.jsonl")
            print(f"File saved successfully in {file_name}.csv")
        else:
            os.remove(f"{file_name}.jsonl")

        exit_program = input("Exit program? (y/n): ")
        if exit_program.lower() == "y":
            print("Exiting ID Searcher...")
            exit()
    except ValueError as e:
        print("Invalid input")
    except json.JSONDecodeError as e:
        print("Invalid response from server")
    except requests.exceptions.RequestException as e:
        print("Failed to connect to server")

def main():
    title = "Mooshyab 7"
    ascii_title = text2art(title, font='small', chr_ignore=True)
    colored_title = colored(ascii_title, 'cyan', attrs=['bold', 'underline'])
    print(colored_title)
    print("Welcome to Farabiran ID Searcher CLI v1.0\n")
    while True:
        try:
            print("\n\033[1;33mWhat would you like to do?\033[0m\n")
            print("1. Search for a single ID")
            print("2. Search for a range of IDs")
            print("3. Exit")

            choice = input("\nEnter your choice: ")
            if choice == "1":
                search_ids(1)
            elif choice == "2":
                search_ids(2)
            elif choice == "3":
                print("Exiting ID Searcher...")
                break
            else:
                print("Invalid choice, please try again.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()