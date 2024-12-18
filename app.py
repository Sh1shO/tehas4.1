import datetime
from PySide6.QtWidgets import QApplication, QMessageBox, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QDialog, QFormLayout, QLineEdit, QComboBox, QDateEdit, QDialogButtonBox, QLabel
from PySide6.QtCore import Qt, QDate
from db import get_session, Employee, TrainingPlace, Position, Specialty, Education, EmployeeEducation, EmployeePosition, Training, EmployeeTraining
from PySide6.QtCore import QDate
from fpdf import FPDF
from sqlalchemy import and_
from sqlalchemy.sql import func
import os
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

class EmployeeListWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Список сотрудников")
        self.setGeometry(100, 100, 1300, 600)

        self.layout = QVBoxLayout()

        # Таблица сотрудников
        self.table = QTableWidget(self)
        self.layout.addWidget(self.table)

        # Кнопки действий
        self.buttons_panel = QHBoxLayout()
        self.add_button = QPushButton("Добавить сотрудника", self)
        self.add_button.clicked.connect(self.add_employee)
        self.buttons_panel.addWidget(self.add_button)

        self.update_button = QPushButton("Редактировать", self)
        self.update_button.clicked.connect(self.update_employee)
        self.buttons_panel.addWidget(self.update_button)

        self.delete_button = QPushButton("Удалить", self)
        self.delete_button.clicked.connect(self.delete_employee)
        self.buttons_panel.addWidget(self.delete_button)

        self.report_button1 = QPushButton("Генерировать отчет 1", self)
        self.report_button1.clicked.connect(self.generate_training_report)
        self.buttons_panel.addWidget(self.report_button1)
        
        self.report_button2 = QPushButton("Генерировать отчет 2", self)
        self.report_button2.clicked.connect(self.generate_employee_card_report)
        self.buttons_panel.addWidget(self.report_button2)

        self.stats_button = QPushButton("Статистика", self)
        self.stats_button.clicked.connect(self.show_statistics)
        self.buttons_panel.addWidget(self.stats_button)

        self.layout.addLayout(self.buttons_panel)

        self.setLayout(self.layout)

        # Загружаем данные сотрудников
        self.load_employees()
        
    def load_employees(self):
        """Загружаем список сотрудников из базы данных"""
        session = get_session()
        employees = session.query(Employee).filter(Employee.is_deleted == False).all()  # Фильтруем по удаленным
        self.table.setRowCount(len(employees))
        self.table.setColumnCount(13)  # Добавим столбец для id

        # Устанавливаем заголовки столбцов
        self.table.setHorizontalHeaderLabels([
            "", "Фамилия", "Имя", "Отчество", "Телефон", "Дата рождения", 
            "СНИЛС", "ИНН", "Паспорт", "Стаж работы", "Семейное положение", 
            "Дата приема", "Дата увольнения"
        ])

        for row, employee in enumerate(employees):
            # Устанавливаем видимые данные
            self.table.setItem(row, 0, QTableWidgetItem(str(employee.id)))  # Добавляем id в скрытый столбец
            self.table.setItem(row, 1, QTableWidgetItem(employee.last_name))  # Фамилия
            self.table.setItem(row, 2, QTableWidgetItem(employee.first_name))  # Имя
            self.table.setItem(row, 3, QTableWidgetItem(employee.surname))  # Отчество
            self.table.setItem(row, 4, QTableWidgetItem(employee.phone_number))  # Телефон
            self.table.setItem(row, 5, QTableWidgetItem(str(employee.birth_date)))  # Дата рождения
            self.table.setItem(row, 6, QTableWidgetItem(employee.snils))  # СНИЛС
            self.table.setItem(row, 7, QTableWidgetItem(employee.inn))  # ИНН
            self.table.setItem(row, 8, QTableWidgetItem(employee.passport))  # Паспорт
            self.table.setItem(row, 9, QTableWidgetItem(str(employee.work_experience)))  # Стаж работы
            self.table.setItem(row, 10, QTableWidgetItem("Да" if employee.material_status else "Нет"))  # Материальный статус
            self.table.setItem(row, 11, QTableWidgetItem(str(employee.hire_date)))  # Дата приема
            self.table.setItem(row, 12, QTableWidgetItem(str(employee.dismissal_date) if employee.dismissal_date else 'Нет'))  # Дата увольнения

        # Автоматическая настройка ширины столбцов
        self.table.resizeColumnsToContents()

        # Скрываем первый столбец (с id)
        self.table.setColumnHidden(0, True)

        # Настроим горизонтальную прокрутку для длинных строк
        self.table.horizontalHeader().setStretchLastSection(True)

        session.close()

    def delete_employee(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            employee_id = int(self.table.item(selected_row, 0).text())  # Приводим к int
            session = get_session()
            employee = session.query(Employee).filter(Employee.id == employee_id).first()
            if employee:
                employee.is_deleted = True
                session.commit()
            session.close()
            self.load_employees()

    def restore_employee(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            employee_id = int(self.table.item(selected_row, 0).text())  # Приводим к int
            session = get_session()
            employee = session.query(Employee).filter(Employee.id == employee_id).first()
            if employee:
                employee.is_deleted = False
                session.commit()
            session.close()
            self.load_employees()

    def update_employee(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            # Получаем ID сотрудника из скрытого столбца (столбец 0)
            employee_id = self.table.item(selected_row, 0).text()
            if employee_id.isdigit():  # Проверяем, что это число
                employee_id = int(employee_id)
                dialog = EditEmployeeDialog(employee_id, self)
                if dialog.exec() == QDialog.Accepted:
                    self.load_employees()
            else:
                self.show_message("Ошибка", "Некорректный ID сотрудника.", QMessageBox.Critical)

    def save_employee(self):
        session = get_session()

        # Сохраняем сотрудника
        new_employee = Employee(
            first_name=self.first_name_input.text(),
            last_name=self.last_name_input.text(),
            surname=self.surname_input.text(),
            phone_number=self.phone_number_input.text(),
            birth_date=self.birth_date_input.date().toPython(),
            snils=self.snils_input.text(),
            inn=self.inn_input.text(),
            passport=self.passport_input.text(),
            work_experience=int(self.work_experience_input.text()),
            hire_date=self.hire_date_input.date().toPython()
        )

        session.add(new_employee)
        session.commit()

        # Сохраняем должность и отдел
        position_id = self.position_combo.currentData()
        department = self.department_combo.currentText()
        employee_position = EmployeePosition(position_id=position_id, employee_id=new_employee.id, department=department)
        session.add(employee_position)

        # Сохраняем образование
        education_id = self.education_combo.currentData()
        employee_education = EmployeeEducation(employee_id=new_employee.id, education_id=education_id)
        session.add(employee_education)

        session.commit()
        session.close()
        self.accept()

    def add_employee(self):
        dialog = AddEmployeeDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.load_employees()  # Обновляем таблицу после добавления сотрудника
    
    def show_message(self, title, message, icon=QMessageBox.Information):
        """Отображает всплывающее сообщение."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()

    def generate_training_report(self):
        try:
            session = get_session()

            # Извлечение данных о сотрудниках и их обучении
            data = (
                session.query(
                    Employee.last_name,
                    Employee.first_name,
                    Employee.surname,
                    Training.start_date,
                    Training.end_date,
                    Training.name_training,
                    Training.format_training
                )
                .join(EmployeeTraining, Employee.id == EmployeeTraining.employee_id)
                .join(Training, EmployeeTraining.training_id == Training.id)
                
                .filter(Employee.is_deleted == False)
                .all()
            )

            # Создание PDF
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            # Устанавливаем шрифт FreeSans
            pdf.add_font('FreeSans', '', 'FreeSans.ttf', uni=True)
            pdf.set_font('FreeSans', '', 16)
            # Заголовок отчёта
            pdf.set_font('FreeSans', '', 16)
            pdf.cell(200, 10, "Отчет об обучении сотрудников", ln=True, align='C')
            pdf.ln(10)

            total_amount = 0  # Итоговая стоимость обучения

            # Заполнение данных
            pdf.set_font('FreeSans', '', 12)
            for row in data:
                last_name, first_name, surname, start, end, name_training, format_training = row
                training_cost = 0
                total_amount += training_cost

                pdf.cell(200, 10, f"{last_name} {first_name} {surname}", ln=True)
                pdf.cell(200, 10, f"Период обучения: {start} - {end}", ln=True)
                pdf.cell(200, 10, f"Курс: {name_training}", ln=True)
                pdf.cell(200, 10, f"Стоимость: {training_cost:.2f} руб.", ln=True)
                pdf.ln(5)

            # Итоговая сумма
            pdf.ln(10)
            pdf.set_font('FreeSans', '', 14)
            pdf.cell(0, 10, f"Итоговая сумма за обучение всех сотрудников: {total_amount:.2f} р.", ln=True, align='R')

            # Сохранение PDF
            pdf_output_path = f"./training_report.pdf"
            pdf.output(pdf_output_path)

            print(f"Отчет был успешно экспортирован в {pdf_output_path}")
            session.close()
            
            QMessageBox.information(self, "Успех", f"Отчет был успешно экспортирован в:\n{pdf_output_path}")
        
        except Exception as e:
            print(f"Произошла ошибка при создании отчета: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при создании отчета: {str(e)}")

    def generate_employee_card_report(self):
        try:
            session = get_session()

            # Загружаем сотрудников
            employees = session.query(Employee).filter(Employee.is_deleted == False).all()

            # Создаём общий PDF
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_font('FreeSans', '', 'FreeSans.ttf', uni=True)

            for employee in employees:
                # Добавляем новую страницу для каждого сотрудника
                pdf.add_page()

                # Заголовок карточки сотрудника
                pdf.set_font('FreeSans', '', 16)
                pdf.cell(200, 10, f"Карточка сотрудника: {employee.last_name} {employee.first_name} {employee.surname}", ln=True, align='C')
                pdf.ln(10)

                # Базовая информация о сотруднике
                pdf.set_font('FreeSans', '', 12)
                pdf.cell(200, 10, f"ФИО: {employee.last_name} {employee.first_name} {employee.surname or ''}", ln=True)
                pdf.cell(200, 10, f"Телефон: {employee.phone_number or 'Не указан'}", ln=True)
                pdf.cell(200, 10, f"Дата рождения: {employee.birth_date}", ln=True)
                pdf.cell(200, 10, f"СНИЛС: {employee.snils}", ln=True)
                pdf.cell(200, 10, f"ИНН: {employee.inn}", ln=True)
                pdf.cell(200, 10, f"Паспорт: {employee.passport}", ln=True)
                pdf.cell(200, 10, f"Стаж работы: {employee.work_experience}", ln=True)
                pdf.cell(200, 10, f"Семейное положение: {employee.material_status}", ln=True)
                pdf.cell(200, 10, f"Дата приёма на работу: {employee.hire_date}", ln=True)
                pdf.cell(200, 10, f"Дата увольнения: {employee.dismissal_date or 'Не уволен'}", ln=True)
                pdf.ln(5)

                # Должность сотрудника
                position = session.query(EmployeePosition).filter(EmployeePosition.employee_id == employee.id).first()
                if position:
                    pdf.cell(200, 10, f"Должность: {position.r_position.name_position}", ln=True)
                    pdf.cell(200, 10, f"Отдел: {position.department or 'Не указан'}", ln=True)
                else:
                    pdf.cell(200, 10, "Должность: Не указана", ln=True)

                pdf.ln(5)

                # Образование
                education = session.query(EmployeeEducation).filter(EmployeeEducation.employee_id == employee.id).all()
                pdf.cell(200, 10, "Образование:", ln=True)
                if education:
                    for edu in education:
                        pdf.cell(200, 10, f"- {edu.r_education.level_education} ({edu.r_education.issue_date})", ln=True)
                else:
                    pdf.cell(200, 10, "Нет данных об образовании", ln=True)

                pdf.ln(5)

                # Курсы обучения
                pdf.cell(200, 10, "Пройденные курсы:", ln=True)
                training_list = session.query(EmployeeTraining).filter(EmployeeTraining.employee_id == employee.id).all()
                if training_list:
                    for t in training_list:
                        training_name = t.r_training.name_training or "Неизвестный курс"
                        start_date = t.r_training.start_date or "Не указана"
                        end_date = t.r_training.end_date or "Не указана"
                        pdf.cell(200, 10, f"- {training_name}: {start_date} - {end_date}", ln=True)
                else:
                    pdf.cell(200, 10, "Нет пройденных курсов", ln=True)

            # Сохранение единого PDF
            pdf_output_path = "./all_employee_cards.pdf"
            pdf.output(pdf_output_path)

            print(f"Карточки сотрудников были успешно экспортированы в {pdf_output_path}.")
            session.close()

            QMessageBox.information(self, "Успех", f"Отчет был успешно экспортирован в:\n{pdf_output_path}")

        except Exception as e:
            print(f"Произошла ошибка при создании карточки сотрудника: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при создании карточки сотрудника: {str(e)}")
        
    def show_statistics(self):
        self.stats_window = StatisticsWindow()
        self.stats_window.show()

class AddTrainingDialog(QDialog):
    def __init__(self, employee_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить обучение")
        self.setGeometry(100, 100, 400, 300)

        self.layout = QFormLayout()

        # Выбор тренинга
        self.training_combo = QComboBox(self)
        session = get_session()
        trainings = session.query(Training).all()
        for training in trainings:
            self.training_combo.addItem(training.name_training, training.id)

        self.layout.addRow("Тренинг", self.training_combo)

        # Кнопки для добавления
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.save_training)
        self.buttons.rejected.connect(self.reject)

        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

    def save_training(self):
        session = get_session()
        training_id = self.training_combo.currentData()
        employee_training = EmployeeTraining(employee_id=self.employee_id, training_id=training_id, completed=False)
        session.add(employee_training)
        session.commit()
        session.close()
        self.accept()

class AddEmployeeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить сотрудника")
        self.setGeometry(100, 100, 400, 400)

        self.layout = QFormLayout()

        # Поля для сотрудника
        self.first_name_input = QLineEdit(self)
        self.last_name_input = QLineEdit(self)
        self.surname_input = QLineEdit(self)
        self.phone_number_input = QLineEdit(self)
        self.birth_date_input = QDateEdit(self)
        self.birth_date_input.setDate(QDate.currentDate())
        self.snils_input = QLineEdit(self)
        self.inn_input = QLineEdit(self)
        self.passport_input = QLineEdit(self)
        self.work_experience_input = QLineEdit(self)
        self.hire_date_input = QDateEdit(self)
        self.hire_date_input.setDate(QDate.currentDate())

        # Добавляем поля в форму
        self.layout.addRow("Имя", self.first_name_input)
        self.layout.addRow("Фамилия", self.last_name_input)
        self.layout.addRow("Отчество", self.surname_input)
        self.layout.addRow("Телефон", self.phone_number_input)
        self.layout.addRow("Дата рождения", self.birth_date_input)
        self.layout.addRow("СНИЛС", self.snils_input)
        self.layout.addRow("ИНН", self.inn_input)
        self.layout.addRow("Паспорт", self.passport_input)
        self.layout.addRow("Стаж работы", self.work_experience_input)
        self.layout.addRow("Дата приема", self.hire_date_input)

        # Должность и отдел
        self.position_combo = QComboBox(self)
        self.department_combo = QComboBox(self)

        # Заполняем комбобоксы должностей и отделов
        session = get_session()
        positions = session.query(Position).all()
        for position in positions:
            self.position_combo.addItem(position.name_position, position.id)  # Получаем должность

        self.department_combo.addItem('HR')
        self.department_combo.addItem('IT')
        self.department_combo.addItem('Finance')
        # Добавьте другие отделы, если необходимо

        self.layout.addRow("Должность", self.position_combo)
        self.layout.addRow("Отдел", self.department_combo)

        # Образование
        self.education_combo = QComboBox(self)
        education_list = session.query(Education).all()
        for education in education_list:
            self.education_combo.addItem(education.level_education, education.id)
        
        self.layout.addRow("Образование", self.education_combo)

        # Кнопки для добавления
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.save_employee)
        self.buttons.rejected.connect(self.reject)

        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

    def save_employee(self):
        session = get_session()

        # Сохраняем сотрудника
        new_employee = Employee(
            first_name=self.first_name_input.text(),
            last_name=self.last_name_input.text(),
            surname=self.surname_input.text(),
            phone_number=self.phone_number_input.text(),
            birth_date=self.birth_date_input.date().toPython(),
            snils=self.snils_input.text(),
            inn=self.inn_input.text(),
            passport=self.passport_input.text(),
            work_experience=int(self.work_experience_input.text()),
            hire_date=self.hire_date_input.date().toPython()
        )

        session.add(new_employee)
        session.commit()

        # Сохраняем должность и отдел
        position_id = self.position_combo.currentData()
        department = self.department_combo.currentText()
        employee_position = EmployeePosition(position_id=position_id, employee_id=new_employee.id, department=department)
        session.add(employee_position)

        # Сохраняем образование
        education_id = self.education_combo.currentData()
        employee_education = EmployeeEducation(employee_id=new_employee.id, education_id=education_id)
        session.add(employee_education)

        session.commit()
        session.close()
        self.accept()

class EditEmployeeDialog(QDialog):
    def __init__(self, employee_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактировать сотрудника")
        self.setGeometry(100, 100, 400, 350)

        self.employee_id = employee_id
        self.layout = QFormLayout()

        # Поля ввода
        self.first_name_input = QLineEdit(self)
        self.last_name_input = QLineEdit(self)
        self.surname_input = QLineEdit(self)
        self.phone_number_input = QLineEdit(self)
        self.birth_date_input = QDateEdit(self)
        self.snils_input = QLineEdit(self)
        self.inn_input = QLineEdit(self)
        self.passport_input = QLineEdit(self)
        self.work_experience_input = QLineEdit(self)
        self.hire_date_input = QDateEdit(self)
        
        self.material_status_input = QComboBox(self)
        self.material_status_input.addItem("Да")
        self.material_status_input.addItem("Нет")

        self.dismissal_date_input = QDateEdit(self)

        # Загружаем данные сотрудника из базы данных
        session = get_session()
        employee = session.query(Employee).filter(Employee.id == self.employee_id).first()

        self.last_name_input.setText(employee.last_name)
        self.first_name_input.setText(employee.first_name)
        self.surname_input.setText(employee.surname)
        self.phone_number_input.setText(employee.phone_number)
        self.birth_date_input.setDate(QDate(employee.birth_date.year, employee.birth_date.month, employee.birth_date.day))
        self.snils_input.setText(employee.snils)
        self.inn_input.setText(employee.inn)
        self.passport_input.setText(employee.passport)
        self.work_experience_input.setText(str(employee.work_experience))
        self.hire_date_input.setDate(QDate(employee.hire_date.year, employee.hire_date.month, employee.hire_date.day))

        self.material_status_input.setCurrentIndex(0 if employee.material_status else 1)
        if employee.dismissal_date:
            self.dismissal_date_input.setDate(QDate(employee.dismissal_date.year, employee.dismissal_date.month, employee.dismissal_date.day))
        else:
            self.dismissal_date_input.setDate(QDate.currentDate())

        # Добавление элементов
        self.layout.addRow("Фамилия", self.last_name_input)
        self.layout.addRow("Имя", self.first_name_input)
        self.layout.addRow("Отчество", self.surname_input)
        self.layout.addRow("Телефон", self.phone_number_input)
        self.layout.addRow("Дата рождения", self.birth_date_input)
        self.layout.addRow("СНИЛС", self.snils_input)
        self.layout.addRow("ИНН", self.inn_input)
        self.layout.addRow("Паспорт", self.passport_input)
        self.layout.addRow("Стаж работы", self.work_experience_input)
        self.layout.addRow("Дата приема", self.hire_date_input)
        self.layout.addRow("Материальный статус", self.material_status_input)
        self.layout.addRow("Дата увольнения", self.dismissal_date_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.save_changes)
        self.buttons.rejected.connect(self.reject)

        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

    def save_changes(self):
        session = get_session()
        employee = session.query(Employee).filter(Employee.id == self.employee_id).first()

        # Обновляем данные
        employee.first_name = self.first_name_input.text()
        employee.last_name = self.last_name_input.text()
        employee.surname = self.surname_input.text()
        employee.phone_number = self.phone_number_input.text()
        employee.birth_date = self.birth_date_input.date().toPython()  # Используем toPython()
        employee.snils = self.snils_input.text()
        employee.inn = self.inn_input.text()
        employee.passport = self.passport_input.text()
        employee.work_experience = int(self.work_experience_input.text())
        employee.hire_date = self.hire_date_input.date().toPython()  # Используем toPython()

        session.commit()
        session.close()
        self.accept()

class StatisticsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Статистика обучения")
        self.setGeometry(100, 100, 800, 600)
        
        # Основной layout
        layout = QVBoxLayout()
        
        # Панель с элементами управления
        control_panel = QHBoxLayout()
        
        # Выбор дат
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addMonths(-6))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        
        control_panel.addWidget(QLabel("С:"))
        control_panel.addWidget(self.start_date)
        control_panel.addWidget(QLabel("По:"))
        control_panel.addWidget(self.end_date)
        
        # Выбор типа графика
        self.chart_type = QComboBox()
        self.chart_type.addItems([
            "Обучение по должностям (гистограмма)", 
            "Обучение по должностям (линейный)", 
            "Виды обучения (круговая)",
            "Количество обучений по месяцам"
        ])
        control_panel.addWidget(self.chart_type)
        
        # Кнопка обновления
        update_btn = QPushButton("Обновить")
        update_btn.clicked.connect(self.update_chart)
        control_panel.addWidget(update_btn)
        
        layout.addLayout(control_panel)
        
        # Область для графика
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        self.setLayout(layout)
        
        # Показываем первый график при запуске
        self.update_chart()

    def update_chart(self):
        self.figure.clear()
        session = get_session()
        start_date = self.start_date.date().toPython()
        end_date = self.end_date.date().toPython()
        
        chart_type = self.chart_type.currentText()
        
        # Добавим отладочную информацию
        print(f"Выбранный период: с {start_date} по {end_date}")
        
        if "количество обучений по месяцам" in chart_type.lower():
            # График по месяцам
            data = (
                session.query(
                    func.date_trunc('month', Training.start_date).label('month'),
                    func.count(EmployeeTraining.id).label('count')
                )
                .join(EmployeeTraining)
                .filter(
                    Training.start_date.between(start_date, end_date),
                    EmployeeTraining.completed == True  # Учитываем только завершенные обучения
                )
                .group_by('month')
                .order_by('month')
                .all()
            )
            
            print("Данные по месяцам:", data)  # Отладочная информация
            
            if data:
                months = [d[0].strftime('%Y-%m') for d in data]
                counts = [d[1] for d in data]
                
                ax = self.figure.add_subplot(111)
                bars = ax.bar(months, counts)
                
                # Добавляем подписи значений над столбцами
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{int(height)}',
                           ha='center', va='bottom')
                
                ax.set_xlabel('Месяц')
                ax.set_ylabel('Количество обучений')
                ax.set_title(f'Количество обучений по месяцам\n{start_date} - {end_date}')
                plt.xticks(rotation=45, ha='right')
                
            else:
                ax = self.figure.add_subplot(111)
                ax.text(0.5, 0.5, 'Нет данных за выбранный период', 
                       ha='center', va='center', transform=ax.transAxes)
        
        elif "гистограмма" in chart_type or "линейный" in chart_type:
            # Получаем данные о количестве обучений по должностям
            data = (
                session.query(
                    Position.name_position,
                    func.count(EmployeeTraining.id).label('count')
                )
                .join(EmployeePosition, Position.id == EmployeePosition.position_id)
                .join(Employee, EmployeePosition.employee_id == Employee.id)
                .join(EmployeeTraining, Employee.id == EmployeeTraining.employee_id)
                .join(Training, EmployeeTraining.training_id == Training.id)
                .filter(
                    Training.start_date >= start_date,
                    Training.end_date <= end_date,
                    EmployeeTraining.completed == True,  # Только завершенные обучения
                    Employee.is_deleted == False  # Только активные сотрудники
                )
                .group_by(Position.name_position)
                .having(func.count(EmployeeTraining.id) > 0)
                .order_by(func.count(EmployeeTraining.id).desc())
                .all()
            )
            
            # Добавим отладочную информацию
            print(f"Период: с {start_date} по {end_date}")
            print("Полученные данные:", data)
            
            if data:
                positions = [d[0] for d in data]
                counts = [d[1] for d in data]
                
                ax = self.figure.add_subplot(111)
                
                if "гистограмма" in chart_type:
                    bars = ax.bar(positions, counts)
                    for bar in bars:
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width()/2., height,
                               f'{int(height)}',
                               ha='center', va='bottom')
                else:
                    ax.plot(positions, counts, marker='o', linestyle='-', linewidth=2, markersize=8)
                    for x, y in zip(positions, counts):
                        ax.text(x, y, f'{int(y)}', ha='center', va='bottom')
                
                ax.set_xlabel('Должности')
                ax.set_ylabel('Количество завершенных обучений')
                ax.set_title(f'Статистика обучений по должностям\n{start_date} - {end_date}')
                plt.xticks(rotation=45, ha='right')
                
            else:
                ax = self.figure.add_subplot(111)
                ax.text(0.5, 0.5, 'Нет данных за выбранный период', 
                       ha='center', va='center', transform=ax.transAxes)
            
        elif "круговая" in chart_type:
            # Получаем данные о видах обучения
            data = (
                session.query(
                    Training.type_training,
                    func.count(EmployeeTraining.id).label('count')
                )
                .join(EmployeeTraining)
                .filter(
                    Training.start_date.between(start_date, end_date),
                    EmployeeTraining.completed == True  # Учитываем только завершенные обучения
                )
                .group_by(Training.type_training)
                .all()
            )
            
            print("Данные по типам обучения:", data)  # Отладочная информация
            
            if data:
                types = [d[0] for d in data]
                counts = [d[1] for d in data]
                
                ax = self.figure.add_subplot(111)
                wedges, texts, autotexts = ax.pie(counts, labels=types, autopct='%1.1f%%')
                ax.set_title(f'Распределение видов обучения\n{start_date} - {end_date}')
                
                # Улучшаем читаемость меток
                plt.setp(autotexts, size=8, weight="bold")
                plt.setp(texts, size=8)
                
            else:
                ax = self.figure.add_subplot(111)
                ax.text(0.5, 0.5, 'Нет данных за выбранный период', 
                       ha='center', va='center', transform=ax.transAxes)
        
        self.figure.tight_layout()
        self.canvas.draw()
        
        session.close()

if __name__ == "__main__":
    app = QApplication([])
    window = EmployeeListWindow()
    window.show()
    app.exec()
