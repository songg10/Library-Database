import sqlite3
from sqlite3 import Error

def option_menu():
	print("What would you like to do?")
	print("1. Find an item in the library.\n2. Borrow an item from the library\n3. Return a borrowed item\n4. Donate an item to the library\n5. Find all event in the library\n6. Register for an event in the library\n7. Volunteer for the library\n8. Ask for help from a librarian")

def create_connection(db_file):
	conn = None
	try:
		conn = sqlite3.connect(db_file)
	except Error as e:
		print("Could not connect to the database.")
		print(e)

	return conn

def search_item(conn, borrow = False):
	print("\nHow would you like to find your item by?:\n1. ISBN.\n2. Name of the item.\n3. Author of the item.\n4. Everything in the library")
	if not borrow:
		user_input = int(input("Please choose a number of which you would like to find the item by: "))
	else:
		user_input = 4
	cur = conn.cursor()

	if user_input == 1:
		ID = input("Please enter the item's ISBN: ")
		cur.execute("SELECT * FROM Item WHERE ID=?", (ID,))
	elif user_input == 2:
		name =  input("Please enter the item's name: ")
		cur.execute("SELECT * FROM Item WHERE name LIKE ?", (name,))
	elif user_input == 3:
		author = input("Please enter the name of the item's author: ")
		cur.execute("SELECT * FROM Item WHERE author LIKE ?", (author,))
	else:
		cur.execute("SELECT * FROM Item")

	rows = cur.fetchall()
	print("Here are the items:")
	if len(rows) > 0:
		for row in rows:
			print(row)
	else:
		print("There is no such item in the library")

	return len(rows)

def getEvent(conn):
	cur = conn.cursor()
	cur.execute("SELECT * FROM Event")
	rows = cur.fetchall()
	print("Here are all the events: ")
	for row in rows:
		print(row)

def register(cur, SIN):
	print("It seems like you are not a member of the library. Please enter the following information to become a member: ")
	firstName = input("Please enter your first name: ")
	lastName = input("Please enter your last name: ")
	email = input("Please enter your email: ")
	try:
		cur.execute("INSERT INTO Person(SIN, firstName, lastName, email) VALUES (?,?,?,?)", (SIN, firstName, lastName, email))
	except Error as e:
		print(e)

def main():
	continuing = True
	while continuing:
		skip = False
		option_menu()
		user_input = int(input("Please choose a number: "))

		while user_input > 8 or user_input < 1:
			user_input = int(input("Please choose an appropriate number from 1 to 8 (inclusive): "))

		print()
		if user_input == 1:
			conn = create_connection('library.db')
			with conn:
				search_item(conn)

			if conn:
				conn.close()

		if user_input == 2:
			conn = create_connection('library.db')
			with conn:
				success = True
				if search_item(conn, True) > 0:
					bookID = int(input("Please enter the ISBN of the book you would like to borrow: "))
					cur = conn.cursor()
					rows = cur.execute("SELECT status FROM Item WHERE ID=?", (bookID,)).fetchall()
					if len(rows) > 0:
						row = rows[0][0]
						if row == "On Loan" or row == "Unavailable" or row == "Coming Soon":
							print("Sorry this book is ", row, " you cannot borrow this book at the moment.")
							skip = True
						if not skip:
							borrowerID = int(input("According to the library policy, every borrower needs to enter their SIN in\norder to successfully borrow a book. Please enter your SIN: "))
							try:
								cur.execute("INSERT INTO Borrowed(SIN, ID, borrowDate, dueDate) VALUES (?, ?, datetime('now','localtime'), datetime('now', '+14 day','localtime'))", (borrowerID, bookID))
								conn.commit()
							except Error as e:
								success = False
								print(e)
					else:
						print("The book you are trying to borrow doesn't exist, please try again")
						skip = True

					if not skip:
						if success:
							if cur.rowcount > 0:
								print("Congratulation you have successfully borrow the item\nAccording to the library policy, the due date will be exactly 14 days after the day the book was borrowed, which is: ", end='')
								conn.commit()
								cur.execute("SELECT dueDate FROM Borrowed WHERE ID=? AND SIN=?", (bookID, borrowerID))
								rows = cur.fetchall()
								print(rows[0][0])
								print("If you return the item late, you will be fined $5.")
							else:
								print("Operation failed")
						else:
							print("Sorry our library doesn't have anything at the moment. Please try again later.")
				
			if conn:
				conn.close()

		if user_input == 3:
			conn = create_connection('library.db')
			with conn:
				borrowerID = int(input('''Please enter your SIN: '''))
				bookID = int(input("Please enter the ISBN of the book that you are returning: "))
				cur = conn.cursor()
				cur.execute("UPDATE Borrowed SET returnDate=datetime('now','localtime') WHERE SIN=? AND ID=?", (borrowerID, bookID))
				if cur.rowcount > 0:
					conn.commit()
					rows = cur.execute("SELECT returnDate, dueDate FROM Borrowed WHERE SIN=? AND ID=?", (borrowerID, bookID)).fetchone()
					if rows[0][0] > rows[0][1]:
						cur.execute("UPDATE Borrowed SET finesAmount=5.0 WHERE SIN=? AND ID=?", (borrowerID, bookID))
					cur.execute("SELECT finesAmount FROM Borrowed WHERE SIN=? AND ID=?", (borrowerID, bookID))
					rows = cur.fetchall()
					print("Balance owning: ", rows[0][0])
					cur.execute("UPDATE Item SET status='Available' WHERE ID=?", (bookID,))
				else:
					print("You have either entered the wrong SIN or ISBN or both.\nTHe system record does not contain any information about the loan that you are trying to return")

			if conn:
				conn.close()

		if user_input == 4:
			conn = create_connection('library.db')
			with conn:
				print("Please enter the details of the item you are donating:")
				ISBN = int(input("ISBN: "))
				name = input("Name of the item: ")
				itemType = input("Type of the item: ")
				author = input("Author: ")
				cur = conn.cursor()
				try:
					cur.execute("INSERT INTO Item(ID, name, type, author) VALUES(?,?,?,?)", (ISBN, name, itemType, author))
					conn.commit()
					print("Thank you for your donation.")
				except Error as e:
					print("Operation Failed: Your item cannot be donated at the moment. We apologize for the inconvinience")
					#print(e)

			if conn:
				conn.close()

		if user_input == 5:
			conn = create_connection('library.db')
			with conn: 
				getEvent(conn)

			if conn:
				conn.close()

		if user_input == 6:
			conn = create_connection('library.db')
			with conn:
				getEvent(conn)
				event = int(input("Please enter the event ID that you would like to register for: "))
				cur = conn.cursor()
				cur.execute("SELECT * FROM Event WHERE eventID=?", (event,))
				rows = cur.fetchall()
				while len(rows) <= 0:
					event = int(input("The event ID that you entered is incorrect, please enter the correct event ID you would like to register for: "))
					cur = conn.cursor()
					cur.execute("SELECT * FROM Event WHERE eventID=?", (event,))
					rows = cur.fetchall()

				SIN = int(input('''Please enter your SIN: '''))
				rows = cur.execute("SELECT * FROM Person WHERE SIN=?", (SIN,)).fetchall()
				if len(rows) <= 0:
					register(cur,SIN)

				try:
					cur.execute("INSERT INTO Attend(eventID,SIN) VALUES(?,?)", (event,SIN))
					conn.commit()
				except Error as e:
					print(e)

			if conn:
				conn.close()

		if user_input == 7:
			conn = create_connection('library.db')
			with conn:
				SIN = int(input('''Please enter your SIN: '''))
				cur = conn.cursor()
				cur.execute("SELECT position FROM Person WHERE SIN=?", (SIN,))
				rows = cur.fetchall()
				if len(rows) <= 0:
					register(cur, SIN)
				else:
					if rows[0][0] != None:
						print("It seems like you have already been working for us, in that case, you won't have to register the second time.")
						skip = True
				if not skip:
					cur.execute("UPDATE Person SET position='Volunteer' WHERE SIN=?", (SIN,))
					if cur.rowcount > 0:
						print("Congratulation! You have successfully been registered as an volunteer. Please check your email for further announcements")
					else:
						print("Operation Error: There has been a problem during the registration. Please try again later. We apologize for the inconvinience")

			if conn:
				conn.close()

		if user_input == 8:
			conn = create_connection('library.db')
			with conn:
				cur = conn.cursor()
				cur.execute("SELECT firstName,lastName,email FROM Person where position LIKE 'librarian'")
				rows = cur.fetchall()
				print("Here are the list of all available librarian: ")
				for row in rows:
					for col in row:
						print(col, end=" ")
				print()
				print("\nFor now the only option is contacting the libraian through email, expected waiting time would be between 1-2 business day.")

			if conn:
				conn.close()

		user_input = input("\nWould you like to do anything else [y/n].\nEnter \'y\' to start again; enter anything else (or n) to exit: ")
		print("")
		if user_input != "y":
			continuing = False

if __name__ == '__main__':
    main()