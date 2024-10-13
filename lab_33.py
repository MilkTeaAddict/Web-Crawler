import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import *
import json
import socket


class PullDownMenu:
    def __init__(self, country):
        self.root = tk.Tk()
        self.root.title('Countries')
        self.root.geometry("300x200")
        self.options = country
        self.clicked = StringVar()
        self.clicked.set("Select a Country")
        
        # Dropdown Menu
        self.drop = OptionMenu(self.root, self.clicked, *self.options)
        self.drop.pack(pady=20)

        # Send to Server Button
        self.button = Button(self.root, text="Send to Server", command=self.show)
        self.button.pack()

        # Label to display status
        self.label = Label(self.root, text=" ")
        self.label.pack(pady=10)

    def run(self):
        self.root.mainloop()
        return self.clicked.get()

    def show(self):
        selected_country = self.clicked.get()
        if selected_country == "Select a Country":
            self.label.config(text="Please select a country")
        else:
            self.label.config(text=f'{selected_country} sent to server')
            Client(4000, selected_country)


def Client(portnumber, data):
    port = portnumber
    host = socket.gethostname()
    client_socket = socket.socket()

    try:
        client_socket.connect((host, port))
        client_socket.send(data.encode())
        print("Receiving data...")
        
        # Increase buffer size to 4096 for larger data
        response = client_socket.recv(4096).decode()
        adict = json.loads(response)
        
        list_of_years = adict['years']
        list_of_values = adict['values'][::-1]
        print(list_of_years)
        print(list_of_values)
        plot(list_of_values, list_of_years)

    except ConnectionRefusedError:
        print(f"Connection to {host}:{port} refused. Ensure the server is running.")
    finally:
        client_socket.close()


def plot(values, years):
    x = years
    y = values
    plt.figure(figsize=(10, 5))
    plt.plot(x, y, marker='o')

    # Labeling the axes and the title
    plt.xlabel('Years')
    plt.ylabel('Country Data')
    plt.title('Country Data over Time')

    # Display the plot
    plt.show()


# List of countries for the dropdown
country_list = [
    'Australia', 'Austria', 'Belarus', 'Belgium', 'Bulgaria', 'Canada', 'Croatia', 'Cyprus', 'Czechia', 'Denmark',
    'Estonia', 'European Union', 'Finland', 'France', 'Germany', 'Greece', 'Hungary', 'Iceland', 'Ireland', 'Italy',
    'Japan', 'Latvia', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Malta', 'Monaco', 'Netherlands', 'New Zealand',
    'Norway', 'Poland', 'Portugal', 'Romania', 'Russian Federation', 'Slovakia', 'Slovenia', 'Spain', 'Sweden',
    'Switzerland', 'Turkey', 'Ukraine', 'United Kingdom', 'United States of America'
]

# Run the client UI
pull = PullDownMenu(country_list)
pull.run()
