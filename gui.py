import os
import datetime
from selenium.common import ElementClickInterceptedException
import customtkinter as ctk
import functions


class Gui(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.users_list = []
        self.users_files = os.listdir('!users/')  # load files from !users/
        self.progress_reset()  # check if user has saved progress info from another day, if yes set it to 0
        self.title('Ligmos')

        # create app window
        ctk.set_appearance_mode("dark")
        self.geometry('1000x600')
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # create scrollable frame for user data
        self.scr_users = ctk.CTkScrollableFrame(self)
        self.scr_users.grid_columnconfigure(0, weight=1)
        self.scr_users.grid(row=0, column=0, padx=5, pady=5, sticky='wnse', columnspan=1)
        self.load_user_list()

        # create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, padx=5, pady=5, sticky='wnse')
        self.main_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # create login input field
        self.login_input = ctk.CTkEntry(self.main_frame, placeholder_text="Your login here")
        self.login_input.grid(row=1, column=1, padx=10, pady=10, sticky='w')
        self.login_text = ctk.CTkLabel(self.main_frame, text='Login: ', fg_color='transparent')
        self.login_text.grid(row=1, column=0, sticky="e")

        # create passwd input field
        self.passwd_var = ctk.StringVar(value='')
        self.passwd_input = ctk.CTkEntry(self.main_frame, placeholder_text="Your password here")
        self.passwd_input.configure(show='*')
        self.passwd_input.grid(row=2, column=1, padx=10, pady=10, sticky='w')
        self.passwd_text = ctk.CTkLabel(self.main_frame, text='Password: ', fg_color='transparent')
        self.passwd_text.grid(row=2, column=0, sticky="e")

        # create lesson number segmented button
        self.lesson_number = ctk.CTkSegmentedButton(self.main_frame, values=[1, 2, 3, 4, 5],
                                                    variable=ctk.IntVar(value=1))
        self.lesson_number.grid(row=3, column=1, padx=10, pady=10, sticky='w')
        self.number_text = ctk.CTkLabel(self.main_frame, text='Number of lessons: ', fg_color='transparent')
        self.number_text.grid(row=3, column=0, sticky="e")

        # create save user data button
        self.save_user_btn = ctk.CTkButton(self.main_frame, text="Save user data", command=self.save_user_data)
        self.save_user_btn.grid(row=4, column=0, padx=10, pady=10, sticky="e")

        # create start doing lessons button
        self.start_btn = ctk.CTkButton(self.main_frame, text="Start doing lessons", command=self.start_lesson)
        self.start_btn.grid(row=4, column=1, padx=10, pady=10, sticky="w")

    def progress_reset(self):
        today_date = datetime.date.today()  # get today's date
        for file in self.users_files:
            data = functions.load_dict('!users/' + file)
            modification_date = datetime.date.fromtimestamp(os.path.getmtime('!users/' + file))  # get timestamp date from user file and convert it into datetime format
            if today_date != modification_date:  # check if user has saved progress info from another day, if yes set it to 0
                data['lessons_today'] = 0
            functions.export(data, '!users/' + file)

    def user_box(self, user_file, i):  # create box in scrollable user frame for user_file data
        data = functions.load_dict('!users/' + user_file)
        box = ctk.CTkFrame(self.scr_users, fg_color='#434952')
        self.users_list.append(box)
        box.grid_columnconfigure(0, weight=4)
        box.grid_columnconfigure(1, weight=1)
        box.grid_rowconfigure((0, 1, 2), weight=1)
        box.grid(row=i * 2, column=0, padx=10, pady=(10, 0), sticky="nswe", rowspan=2)

        # create button with user login that loads user data into main frame
        user_btn = ctk.CTkButton(box, text=(data['login']), width=20, command=lambda: self.load_user_data(user_file))
        user_btn.grid(row=0, column=0, padx=5, pady=5, sticky='we')

        # create button that deletes user profile
        del_btn = ctk.CTkButton(box, text='Delete', width=5, command=lambda: self.delete_user(user_file))
        del_btn.grid(row=0, column=1, padx=5, pady=5, sticky='we')

        # create progress bar for daily lessons, max daily lessons is 5
        progress_text = ctk.CTkLabel(box, text='Progress today ', fg_color='transparent')
        progress_text.grid(row=1, column=0, sticky="ew", columnspan=2, pady=(5, 0))
        progressbar = ctk.CTkProgressBar(box, orientation="horizontal")
        progressbar.grid(row=2, column=0, padx=5, pady=(0, 5), sticky='we', columnspan=2)
        progressbar.set(data['lessons_today'] / 5)

    def load_user_data(self, user_file):  # load user data into main frame when executed
        data = functions.load_dict('!users/' + user_file)

        # clear login and passwd fields
        self.login_input.delete(0, len(self.login_input.get()))
        self.passwd_input.delete(0, len(self.passwd_input.get()))

        # insert user login and passwd into correct fields
        self.login_input.insert(0, data['login'])
        self.passwd_input.insert(0, data['passwd'])
        self.lesson_number.set(data['lessons_to_do'])

    def save_user_data(self):  # save user data into json file in !users/ directory
        login = self.login_input.get()  # reads current login

        # load current lessons_today for specific user
        data = functions.load_dict('!users/' + login + '.json')
        if 'lessons_today' in data:
            lessons_today = data['lessons_today']
        else:
            lessons_today = 0

        # overwrite user data and save it
        data['lessons_today'] = lessons_today
        data['login'] = login
        data['passwd'] = self.passwd_input.get()
        data['lessons_to_do'] = int(self.lesson_number.get())
        functions.export(data, '!users/' + login + '.json')

        # refresh scrollable frame for user profiles
        self.users_files = os.listdir('!users/')
        self.load_user_list()

    def load_user_list(self):  # clear scrollable frame for user profiles and load them again
        for box in self.users_list:
            box.destroy()
        self.users_list = []
        for i, file in enumerate(self.users_files):
            self.user_box(file, i)

    def delete_user(self, user_file):  # delete specific user data and refresh list
        os.remove('!users/' + user_file)
        if os.path.exists('!databases/' + user_file):
            os.remove('!databases/' + user_file)
        self.users_files = os.listdir('!users/')
        self.load_user_list()

    def start_lesson(self):  # start n number of lessons for current user
        login = self.login_input.get()
        controller = functions.Controller(login)
        controller.logon(login, self.passwd_input.get())

        # do n numbers of lessons, if it can't do more than stop and set daily_lessons to 5 in user file
        try:
            controller.do_lesson(int(self.lesson_number.get()))
        except ElementClickInterceptedException:
            data = functions.load_dict('!users/' + login + '.json')
            print('You exceeded your daily lessons limit! ')
            data['lessons_today'] = 5
            functions.export(data, '!users/' + login + '.json')
        functions.export(controller.dictionary, '!databases/' + login + '.json')  # save user database of words from lingos
        self.load_user_list()
