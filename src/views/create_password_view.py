from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from functools import partial
from views.login_view import LoginView
from utils.password_utils import (
    validate_password, save_password, password_is_correct
)


class CreatePasswordView(QWidget):
    VIEW_INDEX = 0

    def __init__(self, change_view):
        super().__init__()
        self.change_view = change_view
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        create_password_instruction_label = QLabel()
        CREATE_PASSWORD_INSTRUCTION_LABEL_TEXT = 'Choose a password with:\n• at least eight characters\n• at least one capital letter\n• at least one number'
        create_password_instruction_label.setText(
            CREATE_PASSWORD_INSTRUCTION_LABEL_TEXT)

        create_password_form = QLineEdit()
        create_password_form.setEchoMode(QLineEdit.Password)
        CREATE_PASSWORD_BUTTON_WIDTH = 115
        create_password_button = QPushButton()
        create_password_button.setFixedWidth(CREATE_PASSWORD_BUTTON_WIDTH)
        create_password_button.setText('Save password')
        create_password_button.clicked.connect(
            partial(self.handle_click_create_password_button, create_password_form, create_password_instruction_label))

        self.layout.addWidget(
            create_password_instruction_label, 0, 0, Qt.AlignCenter)
        self.layout.addWidget(create_password_form, 1, 0, Qt.AlignCenter)
        self.layout.addWidget(create_password_button, 2, 0, Qt.AlignCenter)

    def handle_click_create_password_button(self, password_form, create_password_instruction_label):
        password_validation_errors = validate_password(password_form.text())
        if len(password_validation_errors):
            create_password_instruction_label_text = "•" + '\n•'.join(
                password_validation_errors)
            create_password_instruction_label.setText(
                create_password_instruction_label_text)
        else:
            save_password(password_form.text())
            self.change_view(1)
