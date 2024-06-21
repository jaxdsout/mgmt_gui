import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QGridLayout, \
    QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, \
    QVBoxLayout, QComboBox, QToolBar, QStatusBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
import sqlite3


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(700, 700)
        self.dataset = []

        # MENU
        file_menu_item = self.menuBar().addMenu("&File")
        edit_menu_item = self.menuBar().addMenu("&Edit")
        help_menu_item = self.menuBar().addMenu("&Help")

        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        search_student_action = QAction(QIcon("icons/search.png"), "Search", self)
        search_student_action.triggered.connect(self.search)
        edit_menu_item.addAction(search_student_action)

        reset_action = QAction(QIcon("icons/reset.png"), "Reset", self)
        reset_action.triggered.connect(self.load_data)
        edit_menu_item.addAction(reset_action)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.setMenuRole(QAction.MenuRole.NoRole)
        about_action.triggered.connect(self.about)

        # TOOLBAR
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_student_action)
        toolbar.addAction(reset_action)

        # DATA TABLE
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setColumnWidth(1, 150)
        self.table.setHorizontalHeaderLabels(("ID", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.table.cellClicked.connect(self.cell_select)
        self.setCentralWidget(self.table)

        # STATUS BAR
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

    def cell_select(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)
        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def load_data(self):
        connection = sqlite3.connect("database.db")
        result = connection.execute("SELECT * FROM students;")
        self.dataset = list(result)  # Store the original data

        self.table.setRowCount(0)  # Reset row count to avoid duplication
        for row_number, row_data in enumerate(self.dataset):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()

    @staticmethod
    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    @staticmethod
    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    @staticmethod
    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    @staticmethod
    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    @staticmethod
    def about(self):
        dialog = AboutDialog()
        dialog.exec()


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Edit Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # DEFAULT VALUES
        index = mgmt_dashboard.table.currentRow()
        self.id = mgmt_dashboard.table.item(index, 0).text()
        student_name = mgmt_dashboard.table.item(index, 1).text()
        course_name = mgmt_dashboard.table.item(index, 2).text()
        mobile = mgmt_dashboard.table.item(index, 3).text()

        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        self.mobile = QLineEdit(mobile)
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = ?, course = ?, mobile = ? WHERE id = ?;",
                       (self.student_name.text(),
                        self.course_name.currentText(),
                        self.mobile.text(),
                        self.id))
        connection.commit()
        cursor.close()
        connection.close()
        self.close()
        mgmt_dashboard.load_data()

class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Delete Student")
        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)
        no.clicked.connect(self.close)

    def delete_student(self):
        index = mgmt_dashboard.table.currentRow()
        student_id = mgmt_dashboard.table.item(index, 0).text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("DELETE from students WHERE id = ?", (student_id,))
        connection.commit()
        cursor.close()
        connection.close()
        mgmt_dashboard.load_data()

        self.close()
        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was deleted successfully")
        confirmation_widget.exec()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        button = QPushButton("Submit")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)",
            (name, course, mobile)
        )
        connection.commit()
        cursor.close()
        connection.close()
        self.close()
        mgmt_dashboard.load_data()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        name = self.student_name.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM students WHERE name LIKE ?;",
                                ('%' + name + '%',))
        rows = result.fetchall()

        mgmt_dashboard.table.setRowCount(0)  # Clear the table
        for row_number, row_data in enumerate(rows):
            mgmt_dashboard.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                mgmt_dashboard.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        cursor.close()
        connection.close()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(300)
        self.setFixedHeight(300)
        self.setWindowTitle("About")
        content = """
        This app is a great resource for managing students.
        The possibilities are limitless. Expansion to come.
        """
        self.setText(content)

app = QApplication(sys.argv)
mgmt_dashboard = MainWindow()
mgmt_dashboard.show()
mgmt_dashboard.load_data()
sys.exit(app.exec())
