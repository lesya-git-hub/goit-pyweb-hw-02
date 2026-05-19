import pickle
from collections import UserDict
from colorama import Fore, Style, init
init(autoreset=True)
from datetime import datetime, timedelta

# Decorator for handling input errors in command handler functions
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Please provide all required arguments."
    return inner

# OOP AddressBook inherits from UserDict to manage records like a dictionary
class AddressBook(UserDict):
    # functions to add, find, delete, edit records within the book
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        self.data.pop(name, None)

# Returns contacts with birthdays in the next 7 days and moves weekend congratulations to Monday
    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        now = datetime.now().date()
        for record in self.data.values():
            if record.birthday is None:
                continue
            birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
            birthday_date_current_year = birthday_date.replace(year=now.year)
            difference = birthday_date_current_year - now
            if difference.days < 0:
                difference = birthday_date_current_year.replace(year=now.year+1) - now
            if 0 <= difference.days <= 7:
                upcoming_birthday = now + difference
                if upcoming_birthday.weekday() == 5:
                    upcoming_birthday = upcoming_birthday + timedelta(days=2)
                if upcoming_birthday.weekday() == 6:
                    upcoming_birthday = upcoming_birthday + timedelta(days=1)
                congrat_date = {
                    "name": record.name.value,
                    "birthday": upcoming_birthday.strftime("%d.%m.%Y")
                    }
                upcoming_birthdays.append(congrat_date)
        return upcoming_birthdays

# funtion to display result user-friendly
    def __str__(self):
        if not self.data:
            return "Address book is empty."
        return '\n'.join(str(record) for record in self.data.values())

# classes to build AddressBook with
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        super().__init__(value)

class Phone(Field):
    # Phone validation is done in constructor to ensure data integrity
    def __init__(self, value):
        if not (value.isdigit() and len(value) == 10):
            raise ValueError("Phone number must contain exactly 10 digits")
        super().__init__(value)

# Birthday field with validation for DD.MM.YYYY format
class Birthday(Field):
    # validation is done in constructor to ensure data integrity
    def __init__(self, value):
        try:
            datetime.strptime(value,"%d.%m.%Y")
        except ValueError:
            raise ValueError("Incorrect format, please use DD.MM.YYYY")
        super().__init__(value)


# class Record is used to manage single record of name and phone
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
# Optional field for storing a contact's birthday
    
    def add_phone(self, phone):
        phone_number = Phone(phone)
        self.phones.append(phone_number)

    
    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def remove_phone(self, phone):
        phone_remove = self.find_phone(phone)
        if phone_remove:
            self.phones.remove(phone_remove)
    
    def edit_phone(self, old_phone, new_phone):
        phone_number = self.find_phone(old_phone)
        if not phone_number:
            raise ValueError("Phone number not found")
        new_phone_number = Phone(new_phone)
        phone_number.value = new_phone_number.value

# Adds a validated birthday to a contact record
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

# Returns the saved birthday or a message if it is not set
    def show_birthday(self):
        if self.birthday is not None:
            return self.birthday.value
        return "Birthday not set"

# Returns contact data in a readable format including phone numbers and birthday  
    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones)
        birthday_str = "Not set"
        if self.birthday is not None:
            birthday_str = self.birthday.value
        return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {birthday_str}"
   

# function to read user requests
def parse_input(user_input):
    parts = user_input.strip().split()
    command = parts[0].lower() if parts else ""
    args = parts[1:]
    return command, args

# Adds a new contact or updates an existing one, with optional birthday support
@input_error
def add_contact(args, contacts):
    if len(args) < 2:
        return "Please enter name and phone number."

    name, phone = args[0], args[1]
    birthday = args[2] if len(args) > 2 else None

    try:
        record = contacts.find(name)

        if record is None:
            record = Record(name)
            record.add_phone(phone)
            if birthday is not None:
                record.add_birthday(birthday)
            contacts.add_record(record)
            return "Contact added."
        else:
            record.add_phone(phone)
            if birthday is not None:
                record.add_birthday(birthday)
            return "The existing contact updated."
        
    except ValueError as e:
        return str(e)
    
# function to change contacts
@input_error
def change_contact(args, contacts):
    if len(args) < 3:
        return "Please enter name, old phone, and new phone."

    name, old_phone, new_phone = args[0], args[1], args[2]

    record = contacts.find(name)
    if record is None:
        return "Contact not found."

    try:
        record.edit_phone(old_phone, new_phone)
        return "Phone changed successfully."
    except ValueError as e:
        return str(e)

@input_error
def show_phone(args, contacts):
    if len(args) < 1:
        return "Please enter a contact name."

    name = args[0]
    record = contacts.find(name)

    if record is None:
        return "Contact not found."

    if not record.phones:
        return "No phones found for this contact."

    return '; '.join(phone.value for phone in record.phones)

def show_all(contacts):
    return str(contacts)

@input_error
def show_birthday(args, contacts):
    name = args[0]
    record = contacts.find(name)
    if record is None:
        return "Contact not found."
    else:
        return record.show_birthday()
    
# get name + birthday from args, if found → call record.add_birthday() and return success message
@input_error
def add_birthday(args, contacts):
    name = args[0]
    birthday = args[1]
    try:
        record = contacts.find(name)
        if record is None:
            return f"Contact {name} not found."
        record.add_birthday(birthday)
        return f"Birthday added to contact {name}."
    except ValueError as e:
        return str(e)
@input_error
def birthdays(args, contacts):
    upcoming_birthdays = contacts.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No birthdays coming in the next 7 days."
    formatted_list = [f"🎂 {entry['name']}: {entry['birthday']}" for entry in upcoming_birthdays]
    result = "\n".join(formatted_list)
    return f"These birthdays are coming up in the next seven days:\n{result}"

@input_error
def delete_contact(args, contacts):
    if len(args) < 1:
        return "Please enter a contact name."

    name = args[0]

    if contacts.find(name) is None:
        return "Contact not found."

    contacts.delete(name)
    return "Contact deleted."
 
# The program saves the AddressBook object to a file when the application closes 
# and restores it when the application starts.
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as file:
        pickle.dump(book, file)

# Loads the saved AddressBook object from a pickle file
def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as file:
            return pickle.load(file)
    except (FileNotFoundError, EOFError):
        return AddressBook()

# main function which operates with classes, methods and functions to communicate with user, 
# process user input and manage contacts in the contact book

def main():
    contacts = load_data()
    print("🤖 Welcome to the assistant bot!")

    while True:
        user_input = input(
            "Enter a command: "
            + Fore.CYAN + Style.BRIGHT
            + "add, change, phone, all, delete, add-birthday, show-birthday, birthdays or exit: "
            + Style.RESET_ALL
            +"Example 1: add Stephen 1234567890\n"
            +"Example 2: add-birthday Stephen 11.04.1995\n"
        ).strip()

        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(contacts)
            print("🤖 Good bye!")
            break
        elif command == "hello":
            print("🤖 How can I help you?")
        elif command == "add":
            result = add_contact(args, contacts)
            save_data(contacts)
            print(result)
        elif command == "change":
            result = change_contact(args, contacts)
            save_data(contacts)
            print(result)
        elif command == "add-birthday":
            result = add_birthday(args, contacts)
            save_data(contacts)
            print(result)
        elif command == "show-birthday":
            result = show_birthday(args, contacts)
            print(result)
        elif command == "birthdays":
            print(birthdays(args, contacts))
        elif command == "all":
            print(show_all(contacts))
        elif command == "phone":
            print(show_phone(args, contacts))
        elif command == "delete":
            result = delete_contact(args, contacts)
            save_data(contacts)
            print(result)
        else:
            print("🤨 Invalid command.")
if __name__ == "__main__":
    main()


