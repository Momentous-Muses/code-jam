# import all the required modules
import socket
import threading
# from tkinter import Tk, Toplevel, Label, LabelFrame, CENTER
import tkinter as tk 
from tkinter import font
from tkinter import ttk

PORT = 5050
SERVER = "192.168.0.103"
ADDRESS = (SERVER, PORT)
FORMAT = "utf-8"


# GUI class for the chat
class GUI:
	# constructor method
	def __init__(self):

		# chat window which is currently hidden
		self.window = tk.Tk()
		self.window.withdraw()

		# login window
		self.login = tk.Toplevel()
		# set the title
		self.login.title("Login")
		self.login.resizable(width=False,
							height=False)
		self.login.configure(width=400,
							height=300)
		# create a Label
		self.pls = tk.Label(self.login,
						text="Please login to continue",
						justify=tk.CENTER,
						font="Helvetica 14 bold")

		self.pls.place(relheight=0.15,
					relx=0.2,
					rely=0.07)
		# create a Label
		self.label_name = tk.Label(self.login,
							text="Name: ",
							font="Helvetica 12")

		self.label_name.place(relheight=0.2,
							relx=0.1,
							rely=0.2)

		# create a entry box for
		# tyoing the message
		self.entry_name = tk.Entry(self.login,
							font="Helvetica 14")

		self.entry_name.place(relwidth=0.4,
							relheight=0.12,
							relx=0.35,
							rely=0.2)

		# set the focus of the cursor
		self.entry_name.focus()

		# create a Continue Button
		# along with action
		self.go = tk.Button(self.login,
						text="CONTINUE",
						font="Helvetica 14 bold",
						command=lambda: self.go_ahead(self.entry_name.get()))

		self.go.place(relx=0.4,
					rely=0.55)
		self.window.mainloop()

	def go_ahead(self, name):
		self.login.destroy()
		self.layout(name)

		# the thread to receive messages
		rcv = threading.Thread(target=self.receive)
		rcv.start()

	# The main layout of the chat
	def layout(self, name):

		self.name = name
		# to show chat window
		self.window.deiconify()
		self.window.title("CHATROOM")
		self.window.resizable(width=False,
							height=False)
		self.window.configure(width=470,
							height=550,
							bg="#17202A")
		self.label_head = tk.Label(self.window,
							bg="#17202A",
							fg="#EAECEE",
							text=self.name,
							font="Helvetica 13 bold",
							pady=5)

		self.label_head.place(relwidth=1)
		self.line = tk.Label(self.Window,
						width=450,
						bg="#ABB2B9")

		self.line.place(relwidth=1,
						rely=0.07,
						relheight=0.012)

		self.text_cons = tk.Text(self.Window,
							width=20,
							height=2,
							bg="#17202A",
							fg="#EAECEE",
							font="Helvetica 14",
							padx=5,
							pady=5)

		self.text_cons.place(relheight=0.745,
							relwidth=1,
							rely=0.08)

		self.label_bottom = tk.Label(self.Window,
								bg="#ABB2B9",
								height=80)

		self.label_bottom.place(relwidth=1,
							rely=0.825)

		self.entry_msg = tk.Entry(self.labelBottom,
							bg="#2C3E50",
							fg="#EAECEE",
							font="Helvetica 13")

		# place the given widget
		# into the gui window
		self.entry_msg.place(relwidth=0.74,
							relheight=0.06,
							rely=0.008,
							relx=0.011)

		self.entry_msg.focus()

		# create a Send Button
		self.button_msg = tk.Button(self.labelBottom,
								text="Send",
								font="Helvetica 10 bold",
								width=20,
								bg="#ABB2B9",
								command=lambda: self.sendButton(self.entry_msg.get()))

		self.button_msg.place(relx=0.77,
							rely=0.008,
							relheight=0.06,
							relwidth=0.22)

		self.text_cons.config(cursor="arrow")

		# create a scroll bar
		scrollbar = tk.Scrollbar(self.text_cons)

		# place the scroll bar
		# into the gui window
		scrollbar.place(relheight=1,
						relx=0.974)

		scrollbar.config(command=self.text_cons.yview)

		self.text_cons.config(state=tk.DISABLED)

	# function to basically start the thread for sending messages
	def sendButton(self, msg):
		self.textCons.config(state=tk.DISABLED)
		self.msg = msg
		self.entry_msg.delete(0, tk.END)
		snd = threading.Thread(target=self.sendMessage)
		snd.start()

	# function to receive messages
	def receive(self):
		while True:
			try:
				message = "Hello, simple message"

				# if the messages from the server is NAME send the client's name
				if message == 'NAME':
					client.send(self.name.encode(FORMAT))
				else:
					# insert messages to text box
					self.textCons.config(state=NORMAL)
					self.textCons.insert(END,
										message+"\n\n")

					self.textCons.config(state=DISABLED)
					self.textCons.see(END)
			except:
				# an error will be printed on the command line or console if there's an error
				print("An error occurred!")
				client.close()
				break

	# function to send messages
	def sendMessage(self):
		self.textCons.config(state=DISABLED)
		while True:
			message = (f"{self.name}: {self.msg}")
			client.send(message.encode(FORMAT))
			break


# create a GUI class object
g = GUI()
