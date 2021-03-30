from random import randint
import sqlite3


def generate_id():
    ans = "400000" + "".join([str(randint(0, 9)) for i in range(9)])
    start = list(map(int, list(ans)))
    for i in range(len(start)):
        if i % 2 == 0:
            start[i] *= 2
        if start[i] > 9:
            start[i] -= 9
    last_digit = (10 - sum(start) % 10) % 10
    return ans + str(last_digit)


def checkLuhn(cardNo):
    nDigits = len(cardNo)
    nSum = 0
    isSecond = False

    for i in range(nDigits - 1, -1, -1):
        d = ord(cardNo[i]) - ord('0')

        if (isSecond == True):
            d = d * 2

        # We add two digits to handle
        # cases that make two digits after
        # doubling
        nSum += d // 10
        nSum += d % 10

        isSecond = not isSecond

    if (nSum % 10 == 0):
        return True
    else:
        return False


class Bank:
    def __init__(self):
        self.status = False
        self.conn = sqlite3.connect('card.s3db')
        self.cur = self.conn.cursor()
        self.cur.execute("DROP TABLE IF EXISTS card")
        self.conn.commit()
        self.cur.execute("CREATE TABLE IF NOT EXISTS card("
                         "'id' INTEGER ,"
                         "'number' TEXT,"
                         "'pin' TEXT,"
                         "'balance' INTEGER DEFAULT 0);")
        self.conn.commit()
    def create_account(self):
        id = generate_id()
        card = [id[6:], id, randint(1000, 9999), 0]
        self.cur.execute("INSERT INTO card VALUES ({}, {}, {}, {})".format(*card))
        self.conn.commit()
        return Card(*card)
    def get_balance(self, id):
        self.cur.execute("SELECT balance FROM card WHERE id = {}".format(id))
        return self.cur.fetchone()[0]

    def add_income(self, id):
        income = input("Enter income:\n>")
        self.cur.execute("UPDATE card "
                         "SET balance = balance + {}"
                         " WHERE id = {}".format(income, id))
        self.conn.commit()
        print("Income was added!")
        print()

    def transfer(self, first_id):
        print("Transfer")
        second_id = input("Enter card number:\n>")
        if first_id == second_id:
            print("You can't transfer money to the same account!")
            print()
            return
        try:
            self.cur.execute("SELECT * FROM card WHERE number = {}".format(second_id))
            if not checkLuhn(second_id):
                print("Probably you made a mistake in the card number. Please try again!")
                raise ValueError
            if self.cur.fetchone() == None:
                print("Such a card does not exist.")
                raise ValueError
        except ValueError:
            print()
            return
        value = int(input("Enter how much money you want to transfer:\n>"))
        self.cur.execute("SELECT balance FROM card WHERE number = {}".format(first_id))
        if self.cur.fetchone()[0] < value:
            print("Not enough money!")
            print()
            return
        self.cur.execute("UPDATE card SET balance = balance - {} WHERE number = {}".format(value, first_id))
        self.cur.execute("UPDATE card SET balance = balance + {} WHERE number = {}".format(value, second_id))
        print("Success!")
        print()
        self.conn.commit()
    def close(self, card_number):
        self.cur.execute("DELETE FROM card WHERE number = {}".format(card_number))
        self.conn.commit()
        print("The account has been closed!")
        print()
        self.status = 0
    def log_out(self):
        self.status = False


class Card:
    def __init__(self, id, number, pin, balance):
        global conn, cur, used_cards
        self.id = id
        self.pin = pin
        self.balance = balance
        self.number = number

bank = Bank()

while True:
    if not bank.status:
        print("""1. Create an account
2. Log into account
0. Exit""")
        choice = input(">")
        print()
        if choice == "1":
            card = bank.create_account()
            print("Your card has been created"
                  "\nYour card number:"
                  "\n{}"
                  "\nYour card PIN:"
                  "\n{}".format(card.number, card.pin))
            print()
        elif choice == "2":
            print("Enter your card number:")
            id = input(">")
            print("Enter your PIN:")
            pin = input(">")
            print()
            try:
                bank.cur.execute("SELECT *  FROM card WHERE number = {} AND pin = {} ".format(id, pin))
                card = Card(*bank.cur.fetchone())
            except:
                print("Wrong card number or PIN!\n")
            else:
                print("You have successfully logged in!\n")
                bank.status = 1
        elif choice == "0":
            print("Bye!")
            exit()
    else:
        print("1. Balance\n"
              "2. Add income\n"
              "3. Do transfer\n"
              "4. Close account\n"
              "5. Log out\n"
              "0. Exit")
        choice = input(">")
        print()
        if choice == "1":
            print("Balance: {}".format(bank.get_balance(card.id)))
            print()
        elif choice == "2":
            bank.add_income(card.id)
        elif choice == "3":
            bank.transfer(card.number)
        elif choice == "4":
            bank.close(card.number)
        elif choice == "5":
            bank.log_out()
            print("You have successfully logged out!")
            print()
        elif choice == "0":
            print("Bye")
            bank.conn.commit()
            exit()