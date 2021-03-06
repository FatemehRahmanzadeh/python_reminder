import file_manager
from work import Work
from hashlib import md5
from tabulate import tabulate
from colorama import Fore


class User:
    def __init__(self, user_email, name, last_name, username,
                 password, status, lock_time):
        """

        :param user_email: an unique email address for each user
        :param name: first name of user
        :param last_name: last name of user
        :param username: a freewill name chosen by user
        :param password: a safe password chosen by user
        :param status: if account is locked this attribute is false else, its true
        :param lock_time: last time user's account locked
        """
        self.user_email = user_email
        self.name = name
        self.last_name = last_name
        self.username = username
        self.__password = password
        self.fullname = name + last_name
        self.works = []
        self.categories = {}
        self.events = {}
        self.status = status
        self.locked_time = lock_time

    def categorize_works(self):
        """
        this method takes works from self.works attribute and categorise them
         based on self.category attribute of work
        :return: a massage about categorise succeed or failed
        """
        for task in self.works:
            if task.category not in self.categories.keys():
                self.categories[task.category] = [task]
            else:
                self.categories[task.category].append(task)

        return self.categories

    def delete_work(self, work_name):
        """
        this method remove a work from work list of user and from akk_users_works.json
        :param work_name: name of work which user is going to delete
        :return: a massage about successful delete of fail.
        """

        for w in self.works:
            if w.work_name == work_name:
                w.status = 'done'
                self.works.remove(w)
        return self.works

    def accept_a_work(self, received_work):
        """
        this method accepts a work from a user and adds it to user's work list
        :param received_work: shared work from sender user
        :return: an accept or reject massage
        """
        work_names = [work.work_name for work in self.works]
        if received_work.work_name not in work_names:
            received_work.work_refresh()
            self.works.append(received_work)
            return f'{Fore.LIGHTGREEN_EX}{received_work.work_name} has been accepted{Fore.RESET}'
        else:
            return f'{Fore.YELLOW}{received_work.work_name} already exist in your work list{Fore.RESET}'

    def show_works(self):
        """
        this method prints json file of works pretty
        :return:
        """
        if not self.works:
            return f'{Fore.LIGHTCYAN_EX}there is no work in your work list{Fore.RESET}'

        my_works_table = {f'{Fore.BLUE}attributes{Fore.RESET}':
            [
                f'{Fore.BLUE}date_time{Fore.RESET}',
                f'{Fore.BLUE}category{Fore.RESET}',
                f'{Fore.BLUE}importance{Fore.RESET}',
                f'{Fore.BLUE}urgency{Fore.RESET}',
                f'{Fore.BLUE}status{Fore.RESET}',
                f'{Fore.BLUE}location{Fore.RESET}',
                f'{Fore.BLUE}link{Fore.RESET}',
                f'{Fore.BLUE}description{Fore.RESET}'
            ]
        }
        for _ in self.works:
            my_works_table[f'{Fore.BLUE}{_.work_name}{Fore.RESET}'] = \
                [f'{Fore.LIGHTGREEN_EX}{_.work_datetime}{Fore.RESET}',
                 f'{Fore.LIGHTGREEN_EX}{_.category}{Fore.RESET}',
                 f'{Fore.LIGHTGREEN_EX}{_.importance}{Fore.RESET}',
                 f'{Fore.LIGHTGREEN_EX}{_.urgency}{Fore.RESET}',
                 f'{Fore.LIGHTGREEN_EX}{_.status}{Fore.RESET}',
                 f'{Fore.LIGHTGREEN_EX}{_.location}{Fore.RESET}',
                 f'{Fore.LIGHTGREEN_EX}{_.link}{Fore.RESET}',
                 f'{Fore.LIGHTGREEN_EX}{_.description}{Fore.RESET}']
        return tabulate(my_works_table, my_works_table.keys(), tablefmt="presto")

    def log_out(self):
        for w in self.works:
            w.status = "done"
        return "you are logging out.."

    def __str__(self):
        return f'name: {self.name}\n last name: {self.last_name}\nusername: {self.username}\n' \
               f'Email: {self.user_email}'

    @classmethod
    def register(cls, user_data):
        """
        this method takes information of a User class and makes an instance from it
        :return: an instance of User class or an error about wrong inputs
        """
        new_user_data = {'email': user_data[0],
                         'name': user_data[1],
                         'last_name': user_data[2],
                         'username': user_data[3],
                         'password': user_data[4],
                         'status': True,
                         'lock_time': '0000-00-00 00:00:00'}
        password = str(new_user_data['password']).encode()
        hashed_password = md5(password).hexdigest()
        new_user_data['password'] = hashed_password
        new_user = cls(*(new_user_data.values()))

        all_users_data = file_manager.read_from_file('users_data.json')

        if user_data[3] in all_users_data.keys():
            print(f'{user_data[3]} already exists')
        else:
            file_manager.write_to_file('users_data.json', new_user_data, new_user.username)
            return new_user

    @classmethod
    def login(cls, username, password):
        """
        this method takes two argument and checks if there is a match user with this information
        :param username: unchecked username
        :param password: unchecked password
        :return: True if username and password are match, or False otherwise
        """

        data = file_manager.read_from_file('users_data.json')
        works = file_manager.read_from_file('all_users_works.json')

        user_has_work = True if username in works.keys() else False
        my_works = works[username] if user_has_work else {}

        password = str(password).encode()
        hash_password = md5(password).hexdigest()

        if username in data.keys():
            if hash_password == data[username]['password']:
                current_user = cls(*(data[username].values()))
                if user_has_work:
                    for _ in my_works.values():
                        current_user.works.append(Work(*(_.values())))
                return current_user
            else:
                return False
        else:
            print(f'No user named {username}...')
            return False
