import pandas as pd
import random, math

from app import app, db
from flask import render_template, request, redirect, url_for
from .models import Student, Staff, Project
from .stakeholderFunctions import staffForCode, normaliseCode
from .harryAllocation import allocation

@app.route('/home')
def home():
    return render_template('home.html')

@app.route("/students")
def students():
    students = Student.query.all()
    return render_template('studentTable.html', students=students)

@app.route('/students/update', methods=['POST'])
def update_students():
    data = request.get_json()
    for row in data:
        student = Student.query.filter_by(id=row['id']).first()
        student.name = row['name']
        student.username = row['username']
        student.degree = row['degree']
        student.code1 = row['code1']
        student.title1 = row['title1']
        student.reason1 = row['reason1']
        student.code2 = row['code2']
        student.title2 = row['title2']
        student.reason2 = row['reason2']
        student.code3 = row['code3']
        student.title3 = row['title3']
        student.reason3 = row['reason3']
        student.code4 = row['code4']
        student.title4 = row['title4']
        student.reason4 = row['reason4']
        db.session.commit()
    return 'Data updated successfully!'

@app.route('/students/refresh')
def refresh_students():
    df = pd.read_csv('datafiles/anonymisedForms.csv')
    Student.query.delete()
    for i, row in df.iterrows():
        student = Student(
            name=row[4],
            username=row[3].split('@')[0],
            degree=row[7],
            code1=normaliseCode(row[9]),
            title1=row[10],
            reason1=row[11],
            code2=normaliseCode(row[12]),
            title2=row[13],
            reason2=row[14],
            code3=normaliseCode(row[15]),
            title3=row[16],
            reason3=row[17],
            code4=normaliseCode(row[18]),
            title4=row[19],
            reason4=row[20],
            allocated_code='0',
            allocated_staff='blank',
            # student.pinned=False
        )
        db.session.add(student)
    db.session.commit()
    students = Student.query.all()
    return redirect(url_for('students'))

@app.route("/staff")
def staff():
    staff = Staff.query.all()
    return render_template('staffTable.html', staff=staff)

@app.route('/staff/update', methods=['POST'])
def update_staff():
    data = request.get_json()
    for row in data:
        staff = Staff.query.filter_by(id=row['id']).first()
        staff.name = row['name']
        staff.max_load = row['max_load']
        staff.current_load = row['current_load']
        db.session.commit()
    return 'Data updated successfully!'

@app.route("/staff/refresh")
def refresh_staff():
    Staff.query.delete()

    all_codes = set()
    for student in Student.query.all():
        all_codes.add(staffForCode(student.code1))
        all_codes.add(staffForCode(student.code2))
        all_codes.add(staffForCode(student.code3))
        all_codes.add(staffForCode(student.code4))

    all_codes = list(all_codes)

    for code in all_codes:
        if code != "":
            if Staff.query.filter_by(name=code).first() is None:
                staff_member = Staff(name=code, max_load=10, current_load=0)
                db.session.add(staff_member)
                db.session.commit()

    return redirect(url_for('staff'))

@app.route("/projects")
def projects():
    projects = Project.query.all()
    return render_template('projectTable.html', projects=projects)

@app.route('/projects/update', methods=['POST'])
def update_projects():
    data = request.get_json()
    for row in data:
        projects = Project.query.filter_by(id=row['id']).first()
        projects.code = row['code']
        projects.title = row['title']
        projects.staff_member = row['staff_member']
        projects.max_load = row['max_load']
        projects.current_load = row['current_load']
        projects.popularity = row['popularity']
        db.session.commit()
    return 'Data updated successfully!'

@app.route("/projects/refresh")
def refresh_projects():
    # Delete all records in the Project table
    Project.query.delete()

    # Create two empty lists for unique codes and titles
    all_codes = []
    all_titles = []

    # Loop through all students and add their project codes and titles to the lists
    for student in Student.query.all():
        for i in range(1, 5):
            code = getattr(student, f"code{i}")
            title = getattr(student, f"title{i}")
            if code and code not in all_codes:
                all_codes.append(code)
                all_titles.append(title)

    # Create a new Project record for each unique code
    for i, code in enumerate(all_codes):
        title = all_titles[i]
        popularity = Student.query.filter((Student.code1 == code) | (Student.code2 == code) | (Student.code3 == code) | (Student.code4 == code)).count()
        project = Project(code=code, title=title, staff_member=staffForCode(code), max_load=0, current_load=0, popularity=popularity)
        db.session.add(project)

    # Commit changes to the database
    db.session.commit()
    return redirect(url_for('projects'))

@app.route("/allocate")
def allocate():
    students = Student.query.all()
    staff = Staff.query.all()
    projects = Project.query.all()

    # newStudents, newStaff, newProjects, start_energy, final_energy = allocation(students, staff, projects)
    #
    # # Update the database with the new student data
    # for newStudent in newStudents:
    #     student = Student.query.filter_by(id=newStudent.id).first()
    #     student.allocated_preference = newStudent.allocated_preference
    #     student.allocated_code = newStudent.allocated_code
    #     student.allocated_staff = newStudent.allocated_staff
    #
    # # Commit changes to the database
    # db.session.commit()

    students, staff, projects, start_energy, final_energy = allocation(students, staff, projects)

    return render_template('allocationOutput.html', start_energy=start_energy, students=students, final_energy=final_energy)
