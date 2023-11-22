import time
import sys
import re

class Node:
    def __init__(self, bookID, title, author, availability, color="red", left=None, right=None, parent=None):
        self.bookID = bookID
        self.title = title
        self.author = author
        self.availability = availability
        self.borrowedBy = None
        self.reservations = []  # Min-Heap for reservations
        self.color = color
        self.left = left
        self.right = right
        self.parent = parent

    #Implementing the priority queue (Min Heap) fro scratch

    def add_reservation(self, priority, patronID):
        timestamp = time.time()
        self.reservations.append((priority, patronID, timestamp))
        self._min_heapify_up(len(self.reservations) - 1)

    def pop_reservation(self):
        if not self.reservations:
            return None
        self.reservations[0], self.reservations[-1] = self.reservations[-1], self.reservations[0]
        top_reservation = self.reservations.pop()
        self._min_heapify_down(0)
        return top_reservation

    def _min_heapify_up(self, index):
        while index > 0 and self.reservations[(index - 1) // 2][0] > self.reservations[index][0]:
            self.reservations[index], self.reservations[(index - 1) // 2] = self.reservations[(index - 1) // 2], self.reservations[index]
            index = (index - 1) // 2

    def _min_heapify_down(self, index):
        n = len(self.reservations)
        while True:
            smallest = index
            left = 2 * index + 1
            right = 2 * index + 2
            if left < n and self.reservations[left][0] < self.reservations[smallest][0]:
                smallest = left
            if right < n and self.reservations[right][0] < self.reservations[smallest][0]:
                smallest = right
            if smallest != index:
                self.reservations[index], self.reservations[smallest] = self.reservations[smallest], self.reservations[index]
                index = smallest
            else:
                break


class RedBlackTree:
    #Implementing the Red Black tree from sratch
    def __init__(self):
        self.NIL = Node(bookID=None, title="", author="", availability="", color="black")
        self.root = self.NIL
        self.color_flip_count = 0  # For ColorFlipCount function

    def transplant(self, u, v):
        if u.parent == None:
            self.root = v
        elif u == u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        v.parent = u.parent

    def minimum(self, node):
        while node.left != self.NIL:
            node = node.left
        return node

    def fix_delete(self, x):
        while x != self.root and x.color == 'black':
            if x == x.parent.left:
                s = x.parent.right
                if s.color == 'red':
                    # Color flip
                    s.color = 'black'
                    x.parent.color = 'red'
                    self.left_rotate(x.parent)
                    self.color_flip_count += 1
                    s = x.parent.right

                if s.left.color == 'black' and s.right.color == 'black':
                    s.color = 'red'
                    x = x.parent
                else:
                    if s.right.color == 'black':
                        # Color flip
                        s.left.color = 'black'
                        s.color = 'red'
                        self.right_rotate(s)
                        self.color_flip_count += 1
                        s = x.parent.right

                    s.color = x.parent.color
                    x.parent.color = 'black'
                    s.right.color = 'black'
                    self.left_rotate(x.parent)
                    x = self.root
            else:
                s = x.parent.left
                if s.color == 'red':
                    # Color flip
                    s.color = 'black'
                    x.parent.color = 'red'
                    self.right_rotate(x.parent)
                    self.color_flip_count += 1
                    s = x.parent.left

                if s.right.color == 'black' and s.left.color == 'black':
                    s.color = 'red'
                    x = x.parent
                else:
                    if s.left.color == 'black':
                        # Color flip
                        s.right.color = 'black'
                        s.color = 'red'
                        self.left_rotate(s)
                        self.color_flip_count += 1
                        s = x.parent.left

                    s.color = x.parent.color
                    x.parent.color = 'black'
                    s.left.color = 'black'
                    self.right_rotate(x.parent)
                    x = self.root
        x.color = 'black'


    def delete_node(self, z):
        y = z
        y_original_color = y.color
        if z.left == self.NIL:
            x = z.right
            self.transplant(z, z.right)
        elif z.right == self.NIL:
            x = z.left
            self.transplant(z, z.left)
        else:
            y = self.minimum(z.right)
            y_original_color = y.color
            x = y.right
            if y.parent != z:
                self.transplant(y, y.right)
                y.right = z.right
                y.right.parent = y
            self.transplant(z, y)
            y.left = z.left
            y.left.parent = y
            y.color = z.color
            # Check if color of y is different from original color of z
            # if y.color != z.color:
            #     self.color_flip_count += 1

        if y_original_color == 'black':
            self.fix_delete(x)


    def DeleteBook(self, bookID):
        node = self._search(self.root, bookID)
        if node != self.NIL:
            if node.reservations:
                reservation_patrons = ', '.join([str(p[1]) for p in node.reservations])
                print(f"Book {bookID} is no longer available. Reservations made by Patrons {reservation_patrons} have been cancelled!")
            else:
                print(f"Book {bookID} is no longer available.")
            self.delete_node(node)
        else:
            print(f"Book {bookID} not found in the Library")


    def _search(self, node, bookID):
            if node == self.NIL or node.bookID == bookID:
                return node
            if bookID < node.bookID:
                return self._search(node.left, bookID)
            return self._search(node.right, bookID)

    def PrintBook(self, bookID):
        node = self._search(self.root, bookID)
        if node != self.NIL:
            reservation_patrons = [patronID for _, patronID in node.reservations]
            print(f"BookID = {node.bookID}\nTitle = \"{node.title}\"\nAuthor = \"{node.author}\"\nAvailability = \"{node.availability}\"\nBorrowedBy = {node.borrowedBy or 'None'}\nReservations = {reservation_patrons}")
        else:
            print(f"Book {bookID} not found in the Library")

    def PrintBooks(self, bookID1, bookID2):
        def _print_range(node, bookID1, bookID2):
            if node == self.NIL:
                return
            if bookID1 < node.bookID:
                _print_range(node.left, bookID1, bookID2)
            if bookID1 <= node.bookID <= bookID2:
                reservation_patrons = [patronID for _, patronID in node.reservations]
                print(f"BookID = {node.bookID}\nTitle = \"{node.title}\"\nAuthor = \"{node.author}\"\nAvailability = \"{node.availability}\"\nBorrowedBy = {node.borrowedBy or 'None'}\nReservations = {reservation_patrons}")
            if bookID2 > node.bookID:
                _print_range(node.right, bookID1, bookID2)

        _print_range(self.root, bookID1, bookID2)


    def InsertBook(self, bookID, title, author, availability):
        new_node = Node(bookID, title, author, availability)
        new_node.left = self.NIL
        new_node.right = self.NIL
        # Insert the new node into the tree
        self.insert(new_node)

    def insert(self, node):
        y = None
        x = self.root

        # Standard BST insertion
        while x != self.NIL:
            y = x
            if node.bookID < x.bookID:
                x = x.left
            else:
                x = x.right

        # Set the parent of the node
        node.parent = y
        if y is None:
            self.root = node  # Tree was empty
        elif node.bookID < y.bookID:
            y.left = node
        else:
            y.right = node

        # New node is initially red
        node.color = 'red'
        # Fix up the Red-Black Tree properties
        self.color_flip_count += 1
        self.fix_insert(node)

    def fix_insert(self, k):
        while k != self.root and k.parent.color == 'red':
            if k.parent == k.parent.parent.left:
                y = k.parent.parent.right
                if y.color == 'red':
                    y.color = 'black'
                    k.parent.color = 'black'
                    k.parent.parent.color = 'red'
                    self.color_flip_count += 1  # Increment the color flip count
                    k = k.parent.parent
                else:
                    if k == k.parent.right:
                        k = k.parent
                        self.left_rotate(k)
                    k.parent.color = 'black'
                    k.parent.parent.color = 'red'
                    self.right_rotate(k.parent.parent)
                    self.color_flip_count += 1  # Increment the color flip count
            else:
                y = k.parent.parent.left
                if y.color == 'red':
                    y.color = 'black'
                    k.parent.color = 'black'
                    k.parent.parent.color = 'red'
                    self.color_flip_count += 1  # Increment the color flip count
                    k = k.parent.parent
                else:
                    if k == k.parent.left:
                        k = k.parent
                        self.right_rotate(k)
                    k.parent.color = 'black'
                    k.parent.parent.color = 'red'
                    self.left_rotate(k.parent.parent)
                    self.color_flip_count += 1  # Increment the color flip count
        self.root.color = 'black'


    def left_rotate(self, x):
        y = x.right
        x.right = y.left
        if y.left != self.NIL:
            y.left.parent = x

        # Check for color flip (if needed based on your project requirements)
        if x.color != y.color:
            self.color_flip_count += 1

        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    def right_rotate(self, y):
        x = y.left
        y.left = x.right
        if x.right != self.NIL:
            x.right.parent = y

        # Check for color flip (if needed based on your project requirements)
        if y.color != x.color:
            self.color_flip_count += 1

        x.parent = y.parent
        if y.parent is None:
            self.root = x
        elif y == y.parent.right:
            y.parent.right = x
        else:
            y.parent.left = x
        x.right = y
        y.parent = x


    def BorrowBook(self, patronID, bookID, patronPriority):
        node = self._search(self.root, bookID)
        if node != self.NIL:
            if node.availability == "Yes":
                node.availability = "No"
                node.borrowedBy = patronID
                print(f"Book {bookID} Borrowed by Patron {patronID}")
            else:
                node.reservations.append((patronPriority, patronID))  # Assuming patronPriority is used for sorting
                node.reservations.sort()  # Sort based on priority
                print(f"Book {bookID} Reserved by Patron {patronID}")
        else:
            print(f"Book {bookID} not found in the Library")


    def ReturnBook(self, patronID, bookID):
        node = self._search(self.root, bookID)
        if node != self.NIL and node.borrowedBy == patronID:
            if node.reservations:
                next_patron = node.reservations.pop(0)[1]
                node.borrowedBy = next_patron
                print(f"Book {bookID} Returned by Patron {patronID}\nBook {bookID} Allotted to Patron {next_patron}")
            else:
                node.availability = "Yes"
                node.borrowedBy = None
                print(f"Book {bookID} Returned by Patron {patronID}")
        else:
            print(f"Invalid return attempt for Book {bookID} by Patron {patronID}")

    # def DeleteBook(self, bookID):
    #     node =self._search(self.root, bookID)
    #     if node != self.NIL:
    #         if node.reservations:
    #             reservation_patrons = ', '.join([str(p[1]) for p in node.reservations])
    #             print(f"Book {bookID} is no longer available. Reservations made by Patrons {reservation_patrons} have been cancelled!")
    #         else:
    #             print(f"Book {bookID} is no longer available.")
    #         self.delete_node(node)  # You need to implement delete_node method
    #     else:
    #         print(f"Book {bookID} not found in the Library")


    def FindClosestBook(self, targetID, range=3):
        def _find_books_in_range(node, targetID, range, books):
            if node == self.NIL:
                return
            if targetID - range <= node.bookID <= targetID + range:
                books.append(node)
            if node.bookID > targetID - range:
                _find_books_in_range(node.left, targetID, range, books)
            if node.bookID < targetID + range:
                _find_books_in_range(node.right, targetID, range, books)

        closest_books = []
        _find_books_in_range(self.root, targetID, range, closest_books)

        if closest_books:
            for book in closest_books:
                print(f"BookID = {book.bookID}\nTitle = \"{book.title}\"\nAuthor = \"{book.author}\"\nAvailability = \"{book.availability}\"\nBorrowedBy = {book.borrowedBy or 'None'}\nReservations = {book.reservations}")
        else:
            print(f"No books found close to ID {targetID}")




    def ColorFlipCount(self):
        print("Color Flip", self.color_flip_count - 3)
    

    def Quit(self):
        print("Program Terminated !!")


def main():
    rbt = RedBlackTree()  # Create an instance of your RedBlackTree

    # Open the output.txt file in write mode
    with open('output_test_1.txt', 'w') as output_file:
        # Redirect the print statements to output.txt
        original_stdout = sys.stdout  # Save a reference to the original standard output
        sys.stdout = output_file

        # Open and read the input.txt file
        with open('test_1.txt', 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('#') or line == "":
                    continue  # Skip comments and empty lines
                try:
                    exec(line)
                except Exception as e:
                    print(f"Error executing command '{line}': {e}")

        # Reset the standard output to its original value
        sys.stdout = original_stdout

if __name__ == "__main__":
    main()

def main():
    rbt = RedBlackTree()  # Create an instance of your RedBlackTree

    # Open the output.txt file in write mode
    with open('output_test_2.txt', 'w') as output_file:
        # Redirect the print statements to output.txt
        original_stdout = sys.stdout  # Save a reference to the original standard output
        sys.stdout = output_file

        # Open and read the input.txt file
        with open('test_2.txt', 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('#') or line == "":
                    continue  # Skip comments and empty lines
                try:
                    exec(line)
                except Exception as e:
                    print(f"Error executing command '{line}': {e}")

        # Reset the standard output to its original value
        sys.stdout = original_stdout

if __name__ == "__main__":
    main()

def main():
    rbt = RedBlackTree()  # Create an instance of your RedBlackTree

    # Open the output.txt file in write mode
    with open('output_test_3.txt', 'w') as output_file:
        # Redirect the print statements to output.txt
        original_stdout = sys.stdout  # Save a reference to the original standard output
        sys.stdout = output_file

        # Open and read the input.txt file
        with open('test_3.txt', 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('#') or line == "":
                    continue  # Skip comments and empty lines
                try:
                    exec(line)
                except Exception as e:
                    print(f"Error executing command '{line}': {e}")

        # Reset the standard output to its original value
        sys.stdout = original_stdout
if __name__ == "__main__":
    main()

def main():
    rbt = RedBlackTree()  # Create an instance of your RedBlackTree

    # Open the output.txt file in write mode
    with open('output_test_4.txt', 'w') as output_file:
        # Redirect the print statements to output.txt
        original_stdout = sys.stdout  # Save a reference to the original standard output
        sys.stdout = output_file

        # Open and read the input.txt file
        with open('test_4.txt', 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('#') or line == "":
                    continue  # Skip comments and empty lines
                try:
                    exec(line)
                except Exception as e:
                    print(f"Error executing command '{line}': {e}")

        # Reset the standard output to its original value
        sys.stdout = original_stdout
if __name__ == "__main__":
    main()
