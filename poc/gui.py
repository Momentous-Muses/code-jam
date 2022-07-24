import tkinter as tk

import asgiref.sync


class ChatClientGUI:
    """
    GUI class for the chat client

        - Adapted from: https://www.geeksforgeeks.org/gui-chat-application-using-tkinter-in-python/
    """

    def __init__(self, *args, **kwargs):
        """Create a new instance of GUI"""
        self.__create_state_vars()

        # chat window which is currently hidden
        self.window = tk.Tk()
        self.window.withdraw()

        self.__draw_login_window()

    def __draw_login_window(self):
        # login window
        self.login = tk.Toplevel()

        # set the title
        self.login.title("Login")
        self.login.resizable(width=False, height=False)
        self.login.configure(width=400, height=300)
        # create a Label
        self.login_label = tk.Label(
            self.login,
            text="Please login to continue",
            justify=tk.CENTER,
            font="Helvetica 14 bold",
        )

        self.login_label.place(relheight=0.15, relx=0.2, rely=0.07)

        # create a Label
        self.label_name = tk.Label(self.login, text="Name: ", font="Helvetica 12")

        self.label_name.place(relheight=0.2, relx=0.1, rely=0.2)

        # create a entry box for
        # typing the message
        self.entry_name = tk.Entry(self.login, font="Helvetica 14")

        self.entry_name.place(relwidth=0.4, relheight=0.12, relx=0.35, rely=0.2)

        # set the focus of the cursor
        self.entry_name.focus()

        # Continue Button
        self.go = tk.Button(
            self.login,
            text="CONTINUE",
            font="Helvetica 14 bold",
            command=lambda: self.complete_login(self.entry_name.get()),
        )

        self.go.place(relx=0.4, rely=0.55)

    def __create_state_vars(self):
        self.msgs_to_send = []
        self.is_chatting = False

    def start_mainloop(self):
        """
        Draw the GUI Canvas

            - Start the Tkinter GUI eventloop
        """
        self.window.mainloop()

    def complete_login(self, name):
        """
        Complete login

        Args:
            name (str): Username of the client
        """
        self.login.destroy()
        self.draw_chat_layout(name)
        self.is_chatting = True

    def draw_chat_layout(self, name):
        """The main layout of the chat page"""
        self.name = name

        # to show chat window
        self.window.deiconify()
        self.window.title("CHATROOM")
        self.window.resizable(width=False, height=False)
        self.window.configure(width=470, height=550, bg="#17202A")

        self.label_head = tk.Label(
            self.window,
            bg="#17202A",
            fg="#EAECEE",
            text=self.name,
            font="Helvetica 13 bold",
            pady=5,
        )

        self.label_head.place(relwidth=1)
        self.line = tk.Label(self.window, width=450, bg="#ABB2B9")

        self.line.place(relwidth=1, rely=0.07, relheight=0.012)

        self.text_cons = tk.Text(
            self.window,
            width=20,
            height=2,
            bg="#17202A",
            fg="#EAECEE",
            font="Helvetica 14",
            padx=5,
            pady=5,
        )
        self.text_cons.place(relheight=0.745, relwidth=1, rely=0.08)

        self.label_bottom = tk.Label(self.window, bg="#ABB2B9", height=80)
        self.label_bottom.place(relwidth=1, rely=0.825)

        self.entry_msg = tk.Entry(
            self.label_bottom, bg="#2C3E50", fg="#EAECEE", font="Helvetica 13"
        )
        self.entry_msg.place(relwidth=0.74, relheight=0.06, rely=0.008, relx=0.011)

        self.entry_msg.focus()

        # create a Send Button
        self.button_msg = tk.Button(
            self.label_bottom,
            text="Send",
            font="Helvetica 10 bold",
            width=20,
            bg="#ABB2B9",
            command=lambda: self.send_button(self.entry_msg.get()),
        )
        self.button_msg.place(relx=0.77, rely=0.008, relheight=0.06, relwidth=0.22)

        self.text_cons.config(cursor="arrow")

        # create a scroll bar
        scrollbar = tk.Scrollbar(self.text_cons)

        # place the scroll bar
        # into the gui window
        scrollbar.place(relheight=1, relx=0.974)

        scrollbar.config(command=self.text_cons.yview)

        self.text_cons.config(state=tk.DISABLED)

    def send_button(self, msg):
        """
        Receive Button events

            - starts the thread for sending messages

        Args:
            msg (str): Message to send
        """
        self.text_cons.config(state=tk.DISABLED)
        self.msgs_to_send.append(msg)
        self.entry_msg.delete(0, tk.END)

    @asgiref.sync.sync_to_async
    def receive_message(self, message: str):
        """Receive messages"""
        if self.is_chatting:
            self.text_cons.config(state=tk.NORMAL)
            self.text_cons.insert(tk.END, message + "\n\n")

            self.text_cons.config(state=tk.DISABLED)
            self.text_cons.see(tk.END)

    @asgiref.sync.sync_to_async
    def send_message(self):
        """Send new message"""
        if self.msgs_to_send:
            self.text_cons.config(state=tk.DISABLED)
            for msg in self.msgs_to_send:
                yield msg
            self.msgs_to_send = list()
