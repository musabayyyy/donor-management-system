

class DonorNotFound(Exception):
    pass

class ReceiverNotFound(Exception):
    pass

class DonationNotFound(Exception):
    pass


class Person:
    def __init__(self, cnic, name, address, phone):
        self.cnic = cnic
        self.name = name
        self.address = address
        self.phone = phone

    def show_info(self):
        print("CNIC:", self.cnic)
        print("Name:", self.name)
        print("Address:", self.address)
        print("Phone:", self.phone)


class Donor(Person):
    def __init__(self, cnic, name, address, phone, donor_id):
        super().__init__(cnic, name, address, phone)
        self.donor_id = donor_id

    def show_info(self):
        print("\n--- Donor Info ---")
        print("Donor ID:", self.donor_id)
        super().show_info()


class Receiver(Person):
    def __init__(self, cnic, name, address, phone, receiver_id, reason):
        super().__init__(cnic, name, address, phone)
        self.receiver_id = receiver_id
        self.reason = reason

    def show_info(self):
        print("\n--- Receiver Info ---")
        print("Receiver ID:", self.receiver_id)
        super().show_info()
        print("Reason:", self.reason)


class Donation:
    def __init__(self, donation_id, donor_id, receiver_id, amount):
        self.donation_id = donation_id
        self.donor_id = donor_id
        self.receiver_id = receiver_id
        self.amount = amount

    def show_info(self):
        print("\n--- Donation Info ---")
        print("Donation ID:", self.donation_id)
        print("Donor ID:", self.donor_id)
        print("Receiver ID:", self.receiver_id)
        print("Amount: Rs.", self.amount)


# FileHandler class
class FileHandler:
    def __init__(self, filename):
        self.filename = filename

    def write(self, data):
        try:
            with open(self.filename, 'a', encoding='utf-8') as f:
                f.write(data + '\n')
        except OSError:
            print("Cannot save data")

    def write_all(self, lines):
        # Replace the whole file in one go (safer than clear + many appends)
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                for line in lines:
                    f.write(line + '\n')
        except OSError:
            print("Cannot save data")

    def read(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return f.readlines()
        except FileNotFoundError:
            return []   # first run: file does not exist yet

    def clear(self):
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                f.write("")
        except OSError:
            print("Cannot clear file")


# Main System
class System:
    def __init__(self):
        self.donor_file = FileHandler("donors.txt")
        self.receiver_file = FileHandler("receivers.txt")
        self.donation_file = FileHandler("donations.txt")

        self.donors = []
        self.receivers = []
        self.donations = []

        self.load_data()

    def load_data(self):
        # Lines that are blank or damaged are skipped instead of crashing the program
        for line in self.donor_file.read():
            parts = line.strip().split('|')
            if len(parts) == 5:
                self.donors.append(Donor(parts[0], parts[1], parts[2], parts[3], parts[4]))

        for line in self.receiver_file.read():
            parts = line.strip().split('|')
            if len(parts) == 6:
                self.receivers.append(Receiver(parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]))

        for line in self.donation_file.read():
            parts = line.strip().split('|')
            if len(parts) == 4:
                self.donations.append(Donation(parts[0], parts[1], parts[2], parts[3]))

    def save_data(self):
        donor_lines = []
        for d in self.donors:
            donor_lines.append('|'.join([d.cnic, d.name, d.address, d.phone, d.donor_id]))
        self.donor_file.write_all(donor_lines)

        receiver_lines = []
        for r in self.receivers:
            receiver_lines.append('|'.join([r.cnic, r.name, r.address, r.phone, r.receiver_id, r.reason]))
        self.receiver_file.write_all(receiver_lines)

        donation_lines = []
        for don in self.donations:
            donation_lines.append('|'.join([don.donation_id, don.donor_id, don.receiver_id, don.amount]))
        self.donation_file.write_all(donation_lines)

    # ---------- validation helpers ----------
    @staticmethod
    def clean(value, label):
        value = " ".join(str(value).split())      # removes extra spaces and new lines
        if value == "":
            raise ValueError(label + " is required")
        if '|' in value:
            raise ValueError(label + " cannot contain the | character")
        return value

    @staticmethod
    def check_cnic(cnic):
        digits = cnic.replace('-', '')
        if not (digits.isdigit() and len(digits) == 13):
            raise ValueError("CNIC must be 13 digits (e.g. 35202-1234567-1)")
        return cnic

    @staticmethod
    def check_phone(phone):
        digits = ''.join(ch for ch in phone if ch.isdigit())
        bad = [ch for ch in phone if ch not in '0123456789+- ()']
        if bad or not (10 <= len(digits) <= 13):
            raise ValueError("Enter a valid phone number (e.g. 0300-1234567)")
        return phone

    @staticmethod
    def check_amount(amount):
        try:
            value = float(str(amount).replace(',', ''))
        except ValueError:
            raise ValueError("Amount must be a number")
        if not (0 < value < 1e12):
            raise ValueError("Amount must be greater than 0")
        if value == int(value):
            return str(int(value))
        return str(round(value, 2))

    # ---------- find / lookup ----------
    def find_donor(self, donor_id):
        for d in self.donors:
            if d.donor_id == donor_id:
                return d
        raise DonorNotFound("Donor '" + str(donor_id) + "' not found")

    def find_receiver(self, receiver_id):
        for r in self.receivers:
            if r.receiver_id == receiver_id:
                return r
        raise ReceiverNotFound("Receiver '" + str(receiver_id) + "' not found")

    def find_donation(self, donation_id):
        for don in self.donations:
            if don.donation_id == donation_id:
                return don
        raise DonationNotFound("Donation '" + str(donation_id) + "' not found")

    def donor_name(self, donor_id):
        try:
            return self.find_donor(donor_id).name
        except DonorNotFound:
            return "Unknown donor"

    def receiver_name(self, receiver_id):
        try:
            return self.find_receiver(receiver_id).name
        except ReceiverNotFound:
            return "Unknown receiver"

    def total_amount(self):
        total = 0.0
        for don in self.donations:
            try:
                total += float(don.amount)
            except ValueError:
                pass
        return total

    # ---------- donor records (used by console AND app) ----------
    def add_donor_record(self, cnic, name, address, phone, donor_id):
        cnic = self.check_cnic(self.clean(cnic, "CNIC"))
        name = self.clean(name, "Name")
        address = self.clean(address, "Address")
        phone = self.check_phone(self.clean(phone, "Phone"))
        donor_id = self.clean(donor_id, "Donor ID")

        for d in self.donors:
            if d.donor_id == donor_id:
                raise ValueError("Donor ID '" + donor_id + "' already exists")
            if d.cnic.replace('-', '') == cnic.replace('-', ''):
                raise ValueError("A donor with this CNIC already exists")

        donor = Donor(cnic, name, address, phone, donor_id)
        self.donors.append(donor)
        self.save_data()
        return donor

    def update_donor_record(self, donor_id, name=None, address=None, phone=None):
        donor = self.find_donor(donor_id)
        new_name = donor.name if name is None else self.clean(name, "Name")
        new_address = donor.address if address is None else self.clean(address, "Address")
        new_phone = donor.phone if phone is None else self.check_phone(self.clean(phone, "Phone"))
        donor.name, donor.address, donor.phone = new_name, new_address, new_phone
        self.save_data()

    def delete_donor_record(self, donor_id):
        donor = self.find_donor(donor_id)
        count = sum(1 for don in self.donations if don.donor_id == donor_id)
        if count > 0:
            raise ValueError("This donor has " + str(count) + " donation(s) on record. Delete those donations first.")
        self.donors.remove(donor)
        self.save_data()

    # ---------- receiver records ----------
    def add_receiver_record(self, cnic, name, address, phone, receiver_id, reason):
        cnic = self.check_cnic(self.clean(cnic, "CNIC"))
        name = self.clean(name, "Name")
        address = self.clean(address, "Address")
        phone = self.check_phone(self.clean(phone, "Phone"))
        receiver_id = self.clean(receiver_id, "Receiver ID")
        reason = self.clean(reason, "Reason")

        for r in self.receivers:
            if r.receiver_id == receiver_id:
                raise ValueError("Receiver ID '" + receiver_id + "' already exists")
            if r.cnic.replace('-', '') == cnic.replace('-', ''):
                raise ValueError("A receiver with this CNIC already exists")

        receiver = Receiver(cnic, name, address, phone, receiver_id, reason)
        self.receivers.append(receiver)
        self.save_data()
        return receiver

    def update_receiver_record(self, receiver_id, name=None, address=None, phone=None, reason=None):
        r = self.find_receiver(receiver_id)
        new_name = r.name if name is None else self.clean(name, "Name")
        new_address = r.address if address is None else self.clean(address, "Address")
        new_phone = r.phone if phone is None else self.check_phone(self.clean(phone, "Phone"))
        new_reason = r.reason if reason is None else self.clean(reason, "Reason")
        r.name, r.address, r.phone, r.reason = new_name, new_address, new_phone, new_reason
        self.save_data()

    def delete_receiver_record(self, receiver_id):
        receiver = self.find_receiver(receiver_id)
        count = sum(1 for don in self.donations if don.receiver_id == receiver_id)
        if count > 0:
            raise ValueError("This receiver has " + str(count) + " donation(s) on record. Delete those donations first.")
        self.receivers.remove(receiver)
        self.save_data()

    # ---------- donation records ----------
    def add_donation_record(self, donation_id, donor_id, receiver_id, amount):
        donation_id = self.clean(donation_id, "Donation ID")
        donor_id = self.clean(donor_id, "Donor ID")
        receiver_id = self.clean(receiver_id, "Receiver ID")
        amount = self.check_amount(amount)

        for don in self.donations:
            if don.donation_id == donation_id:
                raise ValueError("Donation ID '" + donation_id + "' already exists")
        self.find_donor(donor_id)          # raises DonorNotFound
        self.find_receiver(receiver_id)    # raises ReceiverNotFound

        donation = Donation(donation_id, donor_id, receiver_id, amount)
        self.donations.append(donation)
        self.save_data()
        return donation

    def update_donation_record(self, donation_id, donor_id=None, receiver_id=None, amount=None):
        don = self.find_donation(donation_id)
        new_donor = don.donor_id if donor_id is None else self.clean(donor_id, "Donor ID")
        new_receiver = don.receiver_id if receiver_id is None else self.clean(receiver_id, "Receiver ID")
        new_amount = don.amount if amount is None else self.check_amount(amount)
        self.find_donor(new_donor)
        self.find_receiver(new_receiver)
        don.donor_id, don.receiver_id, don.amount = new_donor, new_receiver, new_amount
        self.save_data()

    def delete_donation_record(self, donation_id):
        don = self.find_donation(donation_id)
        self.donations.remove(don)
        self.save_data()

    # ================= Console versions (same as before) =================
    # Donor functions
    def add_donor(self):
        print("\n--- Add Donor ---")
        cnic = input("CNIC: ").strip()
        name = input("Name: ").strip()
        address = input("Address: ").strip()
        phone = input("Phone: ").strip()
        donor_id = input("Donor ID: ").strip()

        try:
            self.add_donor_record(cnic, name, address, phone, donor_id)
            print("Donor added!")
        except ValueError as e:
            print("Error:", e)

    def view_donors(self):
        if len(self.donors) == 0:
            print("\nNo donors found")
            return

        print("\n--- All Donors ---")
        for donor in self.donors:
            donor.show_info()
            print("---")

    def update_donor(self):
        did = input("\nDonor ID: ").strip()
        try:
            self.find_donor(did)
        except DonorNotFound:
            print("Donor not found")
            return

        print("\n1. Name")
        print("2. Address")
        print("3. Phone")
        ch = input("Choice: ").strip()

        try:
            if ch == '1':
                self.update_donor_record(did, name=input("New Name: ").strip())
            elif ch == '2':
                self.update_donor_record(did, address=input("New Address: ").strip())
            elif ch == '3':
                self.update_donor_record(did, phone=input("New Phone: ").strip())
            else:
                print("Invalid choice")
                return
            print("Updated!")
        except ValueError as e:
            print("Error:", e)

    def delete_donor(self):
        did = input("\nDonor ID: ").strip()
        try:
            self.delete_donor_record(did)
            print("Deleted!")
        except DonorNotFound:
            print("Donor not found")
        except ValueError as e:
            print("Error:", e)

    # Receiver functions
    def add_receiver(self):
        print("\n--- Add Receiver ---")
        cnic = input("CNIC: ").strip()
        name = input("Name: ").strip()
        address = input("Address: ").strip()
        phone = input("Phone: ").strip()
        receiver_id = input("Receiver ID: ").strip()
        reason = input("Reason: ").strip()

        try:
            self.add_receiver_record(cnic, name, address, phone, receiver_id, reason)
            print("Receiver added!")
        except ValueError as e:
            print("Error:", e)

    def view_receivers(self):
        if len(self.receivers) == 0:
            print("\nNo receivers found")
            return

        print("\n--- All Receivers ---")
        for receiver in self.receivers:
            receiver.show_info()
            print("---")

    def update_receiver(self):
        rid = input("\nReceiver ID: ").strip()
        try:
            self.find_receiver(rid)
        except ReceiverNotFound:
            print("Receiver not found")
            return

        print("\n1. Name")
        print("2. Address")
        print("3. Phone")
        print("4. Reason")
        ch = input("Choice: ").strip()

        try:
            if ch == '1':
                self.update_receiver_record(rid, name=input("New Name: ").strip())
            elif ch == '2':
                self.update_receiver_record(rid, address=input("New Address: ").strip())
            elif ch == '3':
                self.update_receiver_record(rid, phone=input("New Phone: ").strip())
            elif ch == '4':
                self.update_receiver_record(rid, reason=input("New Reason: ").strip())
            else:
                print("Invalid choice")
                return
            print("Updated!")
        except ValueError as e:
            print("Error:", e)

    def delete_receiver(self):
        rid = input("\nReceiver ID: ").strip()
        try:
            self.delete_receiver_record(rid)
            print("Deleted!")
        except ReceiverNotFound:
            print("Receiver not found")
        except ValueError as e:
            print("Error:", e)

    # Donation functions
    def add_donation(self):
        print("\n--- Add Donation ---")
        donation_id = input("Donation ID: ").strip()
        donor_id = input("Donor ID: ").strip()
        receiver_id = input("Receiver ID: ").strip()
        amount = input("Amount: ").strip()

        try:
            self.add_donation_record(donation_id, donor_id, receiver_id, amount)
            print("Donation added!")
        except (ValueError, DonorNotFound, ReceiverNotFound) as e:
            print("Error:", e)

    def view_donations(self):
        if len(self.donations) == 0:
            print("\nNo donations found")
            return

        print("\n--- All Donations ---")
        for donation in self.donations:
            donation.show_info()
            print("---")

    def update_donation(self):
        don_id = input("\nDonation ID: ").strip()
        try:
            self.find_donation(don_id)
        except DonationNotFound:
            print("Donation not found")
            return

        print("\n1. Donor ID")
        print("2. Receiver ID")
        print("3. Amount")
        ch = input("Choice: ").strip()

        try:
            if ch == '1':
                self.update_donation_record(don_id, donor_id=input("New Donor ID: ").strip())
            elif ch == '2':
                self.update_donation_record(don_id, receiver_id=input("New Receiver ID: ").strip())
            elif ch == '3':
                self.update_donation_record(don_id, amount=input("New Amount: ").strip())
            else:
                print("Invalid choice")
                return
            print("Updated!")
        except (ValueError, DonorNotFound, ReceiverNotFound) as e:
            print("Error:", e)

    def delete_donation(self):
        don_id = input("\nDonation ID: ").strip()
        try:
            self.delete_donation_record(don_id)
            print("Deleted!")
        except DonationNotFound:
            print("Donation not found")


# User System
class UserSystem:
    def __init__(self, system):
        self.system = system
        self.user_file = FileHandler("users.txt")
        self.users = {}
        self.load_users()

    def load_users(self):
        for line in self.user_file.read():
            line = line.strip()
            if line:
                parts = line.split('|')
                if len(parts) == 3:
                    self.users[parts[0]] = {'password': parts[1], 'role': parts[2]}

        # Default users
        if len(self.users) == 0:
            self.users['donor1'] = {'password': '123', 'role': 'donor'}
            self.users['receiver1'] = {'password': '123', 'role': 'receiver'}
            self.save_users()

    def save_users(self):
        lines = []
        for username in self.users:
            lines.append(username + '|' + self.users[username]['password'] + '|' + self.users[username]['role'])
        self.user_file.write_all(lines)

    def check_login(self, username, password):
        # Returns the role ('donor' / 'receiver') or None if login is wrong
        user = self.users.get(username)
        if user is not None and user['password'] == password:
            return user['role']
        return None

    def login(self):
        print("\n--- User Login ---")
        username = input("Username: ").strip()
        password = input("Password: ").strip()

        role = self.check_login(username, password)
        if role:
            print("\nWelcome", username)
            return username, role

        print("\nWrong username or password")
        return None, None

    def donor_menu(self):
        while True:
            print("\n--- Donor Menu ---")
            print("1. View Donations")
            print("2. View Receivers")
            print("3. Back")

            choice = input("Choice: ").strip()

            if choice == '1':
                self.system.view_donations()
            elif choice == '2':
                self.system.view_receivers()
            elif choice == '3':
                break
            else:
                print("Invalid choice")

    def receiver_menu(self):
        while True:
            print("\n--- Receiver Menu ---")
            print("1. View Donations")
            print("2. View Donors")
            print("3. Back")

            choice = input("Choice: ").strip()

            if choice == '1':
                self.system.view_donations()
            elif choice == '2':
                self.system.view_donors()
            elif choice == '3':
                break
            else:
                print("Invalid choice")


# Admin login
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def check_admin(username, password):
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

def admin_login():
    print("\n--- Admin Login ---")
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    if check_admin(username, password):
        print("\nWelcome Admin")
        return True
    else:
        print("\nWrong username or password")
        return False


# Admin menu
def admin_menu(system):
    while True:
        print("\n====== ADMIN MENU ======")
        print("1. Donor Management")
        print("2. Receiver Management")
        print("3. Donation Management")
        print("4. Logout")

        choice = input("Choice: ").strip()

        if choice == '1':
            donor_menu(system)
        elif choice == '2':
            receiver_menu(system)
        elif choice == '3':
            donation_menu(system)
        elif choice == '4':
            break
        else:
            print("Invalid choice")


def donor_menu(system):
    while True:
        print("\n--- Donor Menu ---")
        print("1. Add")
        print("2. View")
        print("3. Update")
        print("4. Delete")
        print("5. Back")

        choice = input("Choice: ").strip()

        if choice == '1':
            system.add_donor()
        elif choice == '2':
            system.view_donors()
        elif choice == '3':
            system.update_donor()
        elif choice == '4':
            system.delete_donor()
        elif choice == '5':
            break
        else:
            print("Invalid choice")


def receiver_menu(system):
    while True:
        print("\n--- Receiver Menu ---")
        print("1. Add")
        print("2. View")
        print("3. Update")
        print("4. Delete")
        print("5. Back")

        choice = input("Choice: ").strip()

        if choice == '1':
            system.add_receiver()
        elif choice == '2':
            system.view_receivers()
        elif choice == '3':
            system.update_receiver()
        elif choice == '4':
            system.delete_receiver()
        elif choice == '5':
            break
        else:
            print("Invalid choice")


def donation_menu(system):
    while True:
        print("\n--- Donation Menu ---")
        print("1. Add")
        print("2. View")
        print("3. Update")
        print("4. Delete")
        print("5. Back")

        choice = input("Choice: ").strip()

        if choice == '1':
            system.add_donation()
        elif choice == '2':
            system.view_donations()
        elif choice == '3':
            system.update_donation()
        elif choice == '4':
            system.delete_donation()
        elif choice == '5':
            break
        else:
            print("Invalid choice")


# Main program (console version)
def main():
    system = System()
    user_system = UserSystem(system)

    while True:
        print("\n" + "="*40)
        print("  DONATION MANAGEMENT SYSTEM")
        print("="*40)
        print("1. Admin Login")
        print("2. User Login")
        print("3. Exit")

        choice = input("\nChoice: ").strip()

        if choice == '1':
            if admin_login():
                admin_menu(system)

        elif choice == '2':
            username, role = user_system.login()
            if username:
                if role == 'donor':
                    user_system.donor_menu()
                elif role == 'receiver':
                    user_system.receiver_menu()

        elif choice == '3':
            print("\nThank you!")
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()