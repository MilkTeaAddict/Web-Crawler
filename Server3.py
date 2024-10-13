import socket
import threading
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import json


class BeautifulSoupParser:
    def __init__(self, contents):
        self.soup = BeautifulSoup(contents, 'html.parser')
        self.countries = []
        self.years = []
        self.list_of_values = []

    def find_data(self):
        countries_raw = self.soup.find_all('country')
        years_raw = self.soup.find_all('year')
        records_raw = self.soup.find_all('record')

        # Parse countries
        for i in range(len(countries_raw)):
            if i % 27 == 0 and i != 0:
                self.countries.append(countries_raw[i].get_text())

        self.countries.remove('Netherlands')  # Removing specific country

        # Parse values
        value_list = []
        for i, record in enumerate(records_raw, 1):
            value = record.find('value').get_text()
            value_list.append(value)
            if i % 28 == 0:
                self.list_of_values.append(value_list)
                value_list = []

        # Parse years
        self.years = [year.get_text() for year in years_raw[:28]][::-1]

    def make_df(self):
        data = {'years': self.years}
        for i, country in enumerate(self.countries):
            data[country] = self.list_of_values[i]
        return pd.DataFrame(data)


class Database:
    def __init__(self, name):
        self.db = sqlite3.connect(name)
        self.cursor = self.db.cursor()

    def create_table(self, table_name, pandas_df):
        with self.db:
            pandas_df.to_sql(table_name, self.db, if_exists='replace', index=False)

    def search_sql(self, table_name, column_name):
        with self.db:
            self.cursor.execute(f"SELECT {column_name} FROM {table_name}")
            return self.cursor.fetchall()


def handle_client_connection(conn, addr, db, parser):
    print(f'Got connection from {addr}')
    data = conn.recv(1024).decode()  # Receive country name

    if data:
        records = db.search_sql('data', data)

        data_values = [float(row[0]) for row in records[:28]]  # Only first 28 rows
        response = {
            'years': parser.years,
            'values': data_values
        }
        json_response = json.dumps(response)
        conn.send(json_response.encode())  # Send response as JSON
    conn.close()


def start_server(port, xml_file):
    host = socket.gethostname()
    my_socket = socket.socket()
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.bind((host, port))
    my_socket.listen(1)
    print("Server is waiting for connections...")

    # Load and parse XML
    with open(xml_file, 'r') as infile:
        contents = infile.read()
    
    parser = BeautifulSoupParser(contents)
    parser.find_data()
    dataframe = parser.make_df()

    # Initialize database and create table
    db = Database('data.db')
    db.create_table('data', dataframe)

    while True:
        conn, addr = my_socket.accept()
        handle_client_connection(conn, addr, db, parser)


def run_server_thread(port, xml_file):
    server_thread = threading.Thread(target=start_server, args=(port, xml_file))
    server_thread.daemon = True  # Allow the program to exit even if thread is running
    server_thread.start()


if __name__ == "__main__":
    run_server_thread(4000, "UNData.xml")
    input("Press Enter to exit...\n")  # Keep the main thread alive
