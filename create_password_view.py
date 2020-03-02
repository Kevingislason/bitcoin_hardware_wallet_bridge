from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from functools import partial
import bcrypt
from login_view import Login_View


class Create_Password_View(QGridLayout):

    def __init__(self, set_layout):
        super().__init__()
        self.set_layout = set_layout

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

        self.addWidget(
            create_password_instruction_label, 0, 0, Qt.AlignCenter)
        self.addWidget(create_password_form, 1, 0, Qt.AlignCenter)
        self.addWidget(create_password_button, 2, 0, Qt.AlignCenter)

    def handle_click_create_password_button(self, password_form, create_password_instruction_label):
        password_validation_errors = self.validate_password(
            password_form.text())
        if len(password_validation_errors):
            create_password_instruction_label_text = "•" + '\n•'.join(
                password_validation_errors)
            create_password_instruction_label.setText(
                create_password_instruction_label_text)
        else:
            self.save_password(password_form.text())
            self.set_layout(Login_View(self.set_layout))

    def validate_password(self, password):
        validation_errors = []
        if len(password) < 8:
            validation_errors.append(
                "password must have at least eight characters")
        if not any(c.isupper() for c in password):
            validation_errors.append(
                "password must have at least one uppercase letter")
        if not any(c.isdigit() for c in password):
            validation_errors.append(
                "password must have at least one number")
        return validation_errors

    def save_password(self, password):
        password = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password, salt)
        with open('password.bfe', 'w+') as secrets:
            secrets.write(hashed_password.decode('utf-8'))
        secrets.close()
