from sqlalchemy import Column, String, Integer, Date, Boolean, ForeignKey, Text, Enum, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker


# Настройка базы данных
DATABASE_URL = 'postgresql://postgres:1234@localhost:5432/employee_managment'
engine = create_engine(DATABASE_URL)

Base = declarative_base()

# Создание сессии
Session = sessionmaker(bind=engine)
session = Session()


# Таблица "Место обучения"
class TrainingPlace(Base):
    __tablename__ = "training_place"
    id = Column(Integer, primary_key = True, autoincrement = True)
    full_name = Column(String(255), nullable = False)
    short_name = Column(String(255), nullable = False)

# Таблица "Квалификация"
class Qualification(Base):
    __tablename__ = "qualification"
    id = Column(Integer, primary_key = True, autoincrement = True)
    name_qualification = Column(String(255), nullable = False)
    description = Column(Text)

# Таблица "Специальность"
class Specialty(Base):
    __tablename__ = "specialty"
    id = Column(Integer, primary_key = True, autoincrement = True)
    full_name_specialty = Column(String(255), nullable = False)
    short_name_specialty = Column(String(255), nullable = False)
    qualification_id = Column(Integer, ForeignKey("qualification.id"), nullable = False)
    r_qualification = relationship("Qualification")

# Таблица "Документ"
class DocumentEmployee(Base):
    __tablename__ = "document_employee"
    id = Column(Integer, primary_key = True, autoincrement = True)
    series = Column(Integer, nullable = False)
    number_document = Column(Integer, nullable = False)
    issue_date = Column(Integer, nullable = False)
    issue_by = Column(Text, nullable = False)

# Таблица "Образование"
class Education(Base):
    __tablename__ = "education"
    id = Column(Integer, primary_key = True, autoincrement = True)
    level_education = Column(String(255), nullable = False)
    series = Column(Integer, nullable = False)
    number_education = Column(Integer, nullable = False)
    registration_number = Column(String(255))
    issue_date = Column(Date, nullable = False)
    specialty_id = Column(Integer, ForeignKey("specialty.id"), nullable = False)
    r_specialty = relationship("Specialty")

# Таблица "Должность"
class Position(Base):
    __tablename__ = "position"
    id = Column(Integer, primary_key = True, autoincrement = True)
    name_position = Column(String(255), nullable = False)
    responsibilities = Column(Text)

# Таблица "Сотрудник"
class Employee(Base):
    __tablename__ = "employee"
    id = Column(Integer, primary_key = True, autoincrement = True)
    last_name = Column(String(255), nullable = False)
    first_name = Column(String(255), nullable = False)
    surname = Column(String(255))
    phone_number = Column(String(255))
    birth_date = Column(Date, nullable = False)
    snils = Column(String(255), nullable = False)
    inn = Column(String(255), nullable = False)
    passport = Column(String(255), nullable = False)
    work_experience = Column(Integer)
    material_status = Column(Boolean)
    hire_date = Column(Date, nullable = False)
    dismissal_date = Column(Date)
    is_deleted = Column(Boolean, default=False)
    
# Таблица "Должность сотрудника"
class EmployeePosition(Base):
    __tablename__ = "employee_position"
    id = Column(Integer, primary_key = True, autoincrement = True)
    position_id = Column(Integer, ForeignKey("position.id"), nullable = False)
    employee_id = Column(Integer, ForeignKey("employee.id"), nullable = False)
    department = Column(Enum('IT', 'HR', 'Finance', 'Marketing', 'QA', 'Development', 'Sales', 'Support', 'Research', 'Logistics', 'Operations', 'Designer', 'Graphics Designer', 'Moution Designer', '3D designer', 'Web Designer', 'UX designer', 'UI designer', 'Java Programmer', 'CSS Programer', name = 'department'))
    r_position = relationship("Position")
    r_employee = relationship("Employee")
    
# Таблица "Обучение"
class Training(Base):
    __tablename__ = "training"
    id = Column(Integer, primary_key = True, autoincrement = True)
    name_training = Column(String(255), nullable = False)
    type_training = Column(String(Enum('Python Programming', 'Project Management Workshop', 'Advanced Data Science', 'Team Leadership', 'Business Analysis', 'Machine Learning', 'Web Development', 'Agile Methodologies', 'Database Optimization', 'Cybersecurity Basics', 'Network Administration', 'Digital Marketing', 'IT Infrastructure', 'Cloud Computing', 'Data Visualization', 'Strategic Planning', 'Big Data Processing', 'Artificial Intelligence', 'Customer Relations', 'Product Management', name = 'training_type_enum')), nullable = False)
    start_date = Column(Date, nullable = False)
    end_date = Column(Date, nullable = False)
    format_training = Column(Boolean, nullable = False)
    training_place_id = Column(Integer, ForeignKey("training_place.id"), nullable = False)
    r_training_place = relationship("TrainingPlace")

# Таблица "Обучение сотрудника"
class EmployeeTraining(Base):
    __tablename__ = "employee_training"
    id = Column(Integer, primary_key = True, autoincrement = True)
    training_id = Column(Integer, ForeignKey("training.id"), nullable = False)
    employee_id = Column(Integer, ForeignKey("employee.id"), nullable = False)
    completed = Column(Boolean, nullable = False)
    document_path = Column(String(255))
    r_training = relationship("Training")
    r_employee = relationship("Employee")

# Таблица "Образование сотрудника"   
class EmployeeEducation (Base):
    __tablename__ = "employee_education"
    id = Column(Integer, primary_key = True, autoincrement = True)
    employee_id = Column(Integer, ForeignKey("employee.id"), nullable = False)
    education_id = Column(Integer, ForeignKey("education.id"), nullable = False)
    r_employee = relationship("Employee")
    r_education = relationship("Education")
    
def get_session():
   """Возвращаем сессию для работы с базой данных"""
   return session
