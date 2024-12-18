-- Создание таблицы мест обучения
create table training_place (
	id serial primary key,
	full_name varchar(255) not null,
	short_name varchar(255) not null
);

-- Создание таблицы квалификаций
create table qualification (
	id serial primary key,
	name_qualification varchar(255) not null,
	description text
);

-- Создание таблицы специальностей
create table specialty (
	id serial primary key,
	full_name_specialty varchar(255) not null,
	short_name_specialty varchar(255) not null,
	qualification_id int not null,
	constraint fk_qualification foreign key (qualification_id) references qualification(id)
);

-- Создание таблицы документов
create table document_employee (
	id serial primary key,
	series int not null,
	number_document int not null,
	issue_date date not null,
	issued_by text not null
);

-- Создание таблицы образования
create table education (
	id serial primary key,
	level_education varchar(255) not null,
	series int not null,
	number_education int not null,
	registration_number varchar(255),
	issue_date date not null,
	specialty_id int not null,
	constraint fk_specialty foreign key (specialty_id) references specialty(id)
);

-- Создание таблицы должностей
create table position (
	id serial primary key,
	name_position varchar(255) not null,
	responsibilities text
);

-- Создание таблицы сотрудников
create table employee (
	id serial primary key,
	last_name varchar(255) not null,
	first_name varchar(255) not null,
	surname varchar(255),
	phone_number varchar(255),
	birth_date date not null,
	snils varchar(255) not null,
	inn varchar(255) not null,
	passport varchar(255) not null,
	work_experience int,
	material_status boolean,
	hire_date date not null,
	dismissal_date date,
	is_deleted boolean default false 
);

-- Создание таблицы должностей сотрудников (связующая таблица)
create table employee_position (
	id serial primary key,
	position_id int not null,
	employee_id int not null,
	department varchar(255) check (department in ('IT', 'HR', 'Finance', 'Marketing', 'QA', 'Development', 'Sales', 'Support', 'Research', 'Logistics', 'Operations', 'Designer', 'Graphics Designer', 'Moution Designer', '3D designer', 'Web Designer', 'UX designer', 'UI designer', 'Java Programmer', 'CSS Programer')),
	constraint fk_position foreign key (position_id) references position(id),
	constraint fk_employee foreign key (employee_id) references employee(id)
);

-- Создание таблицы обучения
create table training (
	id serial primary key,
	name_training varchar(255) not null,
	type_training varchar(255) check (type_training in ('Python Programming', 'Project Management Workshop', 'Advanced Data Science', 'Team Leadership', 'Business Analysis', 'Machine Learning', 'Web Development', 'Agile Methodologies', 'Database Optimization', 'Cybersecurity Basics', 'Network Administration', 'Digital Marketing', 'IT Infrastructure', 'Cloud Computing', 'Data Visualization', 'Strategic Planning', 'Big Data Processing', 'Artificial Intelligence', 'Customer Relations', 'Product Management')) not null,
	start_date date not null,
	end_date date not null,
	format_training boolean not null,
	training_place_id int not null,
	constraint fk_training_place foreign key (training_place_id) references training_place(id)
);

-- Создание таблицы обучения сотрудников (связующая таблица)
create table employee_training (
	id serial primary key,
	training_id int not null,
	employee_id int not null,
	completed boolean not null,
	document_path varchar(255),
	constraint fk_training foreign key (training_id) references training(id),
	constraint fk_employee_training foreign key (employee_id) references employee(id)
);

-- Создание таблицы образования сотрудников (связующая таблица)
create table employee_education (
	id serial primary key,
	employee_id int not null,
	education_id int not null,
	constraint fk_employee_id foreign key (employee_id) references employee(id),
	constraint fk_education_id foreign key (education_id) references education(id)
);
