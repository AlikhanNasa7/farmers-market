from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
import datetime
from sqlalchemy import not_
from sqlalchemy import func
from models import *

DATABASE_URI = 'mysql+pymysql://root:123beTomas!@localhost:3306/assignment3'

engine = create_engine(DATABASE_URI, echo=True)

Session = sessionmaker(bind=engine)

session = Session()

bacterial_diseases = session.query(Disease).join(Discover).filter(
    and_(
        Disease.pathogen == 'bacteria',
        Discover.first_enc_date < datetime.date(2020, 1, 1)
    )
).all()

print("Diseases caused by 'bacteria' discovered before 2020:")
for disease in bacterial_diseases:
    print(f"Disease Code: {disease.disease_code}, Description: {disease.description}, Pathogen: {disease.pathogen}")

doctors_not_infectious = session.query(Doctor.name, Doctor.surname, Doctor.degree).filter(
    ~Doctor.DiseaseType.any(DiseaseType.description == 'infectious diseases')
).all()

print("\nDoctors not specialized in 'infectious diseases':")
for name, surname,  degree in doctors_not_infectious:
    print(f"Name: {name} {surname}, Degree: {degree}")


doctors_multiple_specializations = session.query(
    Doctor.name,
    Doctor.surname,
    Doctor.degree
).join(Doctor.DiseaseType).group_by(Doctor.id).having(func.count(DiseaseType.id) > 2).all()

print("\nDoctors specialized in more than 2 disease types:")
for name, surname, degree in doctors_multiple_specializations:
    print(f"Name: {name}, Surname: {surname}, Degree: {degree}")


average_salary_virology = session.query(
    Country.cname,
    func.avg(User.salary).label('average_salary')
).join(Doctor, Doctor.cname == Country.cname)\
 .join(t_Specialize, Doctor.email == t_Specialize.c.email)\
 .join(DiseaseType, t_Specialize.c.id == DiseaseType.id)\
 .filter(DiseaseType.description == 'virology')\
 .group_by(Country.cname)\
 .all()

print("\nCountries and the average salary of doctors specialized in 'virology':")
for cname, avg_salary in average_salary_virology:
    print(f"Country: {cname}, Average Salary: {avg_salary:.2f}")

departments_multiple_countries = session.query(
    PublicServant.department,
    func.count(PublicServant.email).label('employee_count')
).join(t_Record, PublicServant.email == t_Record.c.email)\
 .join(Disease, t_Record.c.disease_code == Disease.disease_code)\
 .filter(Disease.description == 'covid-19')\
 .group_by(PublicServant.department)\
 .having(func.count(func.distinct(PublicServant.cname)) > 1)\
 .all()

print("\nDepartments with public servants reporting 'covid-19' across multiple countries:")
for department, emp_count in departments_multiple_countries:
    print(f"Department: {department}, Employees Reporting COVID-19: {emp_count}")

from sqlalchemy import update

covid_disease = session.query(Disease).filter(Disease.description == 'covid-19').first()

if covid_disease:
    stmt = update(PublicServant).where(
        PublicServant.email.in_(
            session.query(t_Record.c.email).filter(
                t_Record.c.disease_code == covid_disease.disease_code,
                t_Record.c.total_patients > 3
            )
        )
    ).values(
        salary=PublicServant.salary * 2
    )

    session.execute(stmt)
    session.commit()

    print("\nSalaries of eligible public servants have been doubled.")
else:
    print("\nNo 'covid-19' disease found in the database.")


users_to_delete = session.query(User).filter(
    or_(
        User.name.like('%bek%'),
        User.name.like('%gul%')
    )
).all()

# Delete each user
for user in users_to_delete:
    session.delete(user)

# Commit the changes
session.commit()

print(f"\nDeleted {len(users_to_delete)} users whose names contain 'bek' or 'gul'.")


from sqlalchemy import Index

# Define a non-unique index on 'disease_code'
Index('idx_disease_code', Disease.disease_code)

# Apply the index creation
Base.metadata.create_all(engine)

print("\nSecondary index on 'disease_code' has been created.")


top_countries = session.query(
    Country.cname,
    func.sum(t_Record.c.total_patients).label('total_patients')
).join(t_Record, Country.cname == t_Record.c.cname)\
 .group_by(Country.cname)\
 .order_by(func.sum(t_Record.c.total_patients).desc())\
 .limit(2)\
 .all()

print("\nTop 2 countries with the highest number of total patients recorded:")
for cname, total in top_countries:
    print(f"Country: {cname}, Total Patients: {total}")

covid_disease = session.query(Disease).filter(Disease.description == 'covid-19').first()

if covid_disease:
    total_covid19_patients = session.query(func.count(t_PatientDisease.c.email)).filter(
        t_PatientDisease.c.disease_code == covid_disease.disease_code
    ).scalar()

    print(f"\nTotal number of patients who have 'covid-19' disease: {total_covid19_patients}")
else:
    print("\nNo 'covid-19' disease found in the database.")

from sqlalchemy import text

# Define the SQL for creating the view
create_view_sql = """
CREATE OR REPLACE VIEW patient_disease_view AS
SELECT 
    Users.name AS patient_name,
    Users.surname AS patient_surname,
    Disease.description AS disease_description
FROM 
    Users
JOIN 
    Patients ON Users.email = Patients.email
JOIN 
    PatientDisease ON Users.email = PatientDisease.email
JOIN 
    Disease ON PatientDisease.disease_code = Disease.disease_code;
"""

engine.execute(text(create_view_sql))

print("\nView 'patient_disease_view' has been created successfully.")

patient_disease_records = session.execute(text("SELECT patient_name, patient_surname, disease_description FROM patient_disease_view")).fetchall()

print("\nList of all patients’ full names along with their diagnosed diseases:")
for record in patient_disease_records:
    full_name = f"{record.patient_name} {record.patient_surname}"
    disease = record.disease_description
    print(f"Patient: {full_name}, Disease: {disease}")
