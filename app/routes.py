import pandas as pd
import random, math

from app import app, db
from flask import render_template, request, redirect, url_for, jsonify
from .models import Student, Staff, Project
from .stakeholderFunctions import staffForCode, normaliseCode
from .autoAllocation import allocation

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
    return render_template('staffTable.html', staff=staff, request=request)

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
                staff_member = Staff(name=code, max_load=8, current_load=0)
                db.session.add(staff_member)
                db.session.commit()

    return redirect(url_for('staff'))

@app.route("/projects")
def projects():
    projects = Project.query.all()
    return render_template('projectTable.html', projects=projects, request=request)

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

    # Read the max_load values from the datafiles/projectWorkloadColumn.txt file
    with open('datafiles/projectWorkloadColumn.txt', 'r') as f:
        max_load_values = [int(line.strip()) for line in f.readlines()]

    print(max_load_values)

    # Create a new Project record for each unique code
    for i, code in enumerate(all_codes):
        title = all_titles[i]
        max_load = max_load_values[i] if i < len(max_load_values) else 0
        popularity = Student.query.filter((Student.code1 == code) | (Student.code2 == code) | (Student.code3 == code) | (Student.code4 == code)).count()
        project = Project(code=code, title=title, staff_member=staffForCode(code), max_load=max_load, current_load=0, popularity=popularity)
        db.session.add(project)

    # Commit changes to the database
    db.session.commit()
    return redirect(url_for('projects'))


@app.route('/students/pin')
def pin_students():
    students_with_own = []
    students = Student.query.filter((Student.code1 == 'OWN') | (Student.code2 == 'OWN') | (Student.code3 == 'OWN') | (Student.code4 == 'OWN')).all()
    for student in students:
        for i in range(1, 5):
            code = getattr(student, f"code{i}")
            if code == 'OWN':
                title = getattr(student, f"title{i}")
                reason = getattr(student, f"reason{i}")
                students_with_own.append((student, title, reason))
                break
    staff_members = Staff.query.all()
    calculate_staff_popularity(staff_members)
    staff_dicts = [{'name': staff.name, 'max_load': staff.max_load, 'current_load': staff.current_load} for staff in staff_members]
    return render_template('pinSelfProposed.html', students=students_with_own, staff_members=staff_members, staff_dicts=staff_dicts, request=request)

def calculate_staff_popularity(staff_members):
    for staff in staff_members:
        staff.popularity = sum([project.popularity for project in staff.projects.all()])
    staff_members.sort(key=lambda x: x.popularity)

@app.route('/students/pin/update', methods=['POST'])
def update_pinned_students():
    data = request.get_json()
    for row in data:
        student = Student.query.filter_by(id=row['id']).first()
        student.pinned = row['pinned']

        if student.pinned == 1:
            student.allocated_code = row['allocated_code']
            student.allocated_preference = row['allocated_preference']
        else:
            student.allocated_code = None
            student.allocated_preference = None

        if row['allocated_staff']:
            staff = Staff.query.filter_by(name=row['allocated_staff']).first()
            if staff:
                if student.allocated_staff != staff.name:
                    if student.allocated_staff:
                        old_staff = Staff.query.filter_by(name=student.allocated_staff).first()
                        if old_staff is not None:
                            old_staff.current_load -= 1
                    student.allocated_staff = staff.name
                    staff.current_load += 1
        else:
            if student.allocated_staff:
                old_staff = Staff.query.filter_by(name=student.allocated_staff).first()
                if old_staff is not None:
                    old_staff.current_load -= 1
            student.allocated_staff = None
        db.session.commit()
    return 'Pinned students updated successfully!'

@app.route("/allocate", methods=['POST'])
def allocate():
    startT = float(request.form.get('startT'))
    endT = float(request.form.get('endT'))
    PREFERENCE_ENERGY = float(request.form.get('PREFERENCE_ENERGY'))
    STAFF_OVERLOAD_ENERGY = float(request.form.get('STAFF_OVERLOAD_ENERGY'))
    NO_PROJECT_ENERGY = float(request.form.get('NO_PROJECT_ENERGY'))
    PROJECT_OVERLOAD_ENERGY = float(request.form.get('PROJECT_OVERLOAD_ENERGY'))
    students = Student.query.all()
    staff = Staff.query.all()
    projects = Project.query.all()

    students, staff, projects, start_energy, final_energy = allocation(
        students, staff, projects, startT, endT,
        PREFERENCE_ENERGY, STAFF_OVERLOAD_ENERGY, NO_PROJECT_ENERGY, PROJECT_OVERLOAD_ENERGY
    )

    # Update the database with the new allocations
    for student in students:
        db_student = Student.query.filter_by(id=student.id).first()
        db_student.allocated_code = student.allocated_code
        db_student.allocated_staff = student.allocated_staff
        db_student.allocated_preference = student.allocated_preference

    for staff_member in staff:
        db_staff = Staff.query.filter_by(id=staff_member.id).first()
        db_staff.current_load = staff_member.current_load

    for project in projects:
        db_project = Project.query.filter_by(id=project.id).first()
        db_project.current_load = project.current_load

    db.session.commit()

    return redirect(url_for('allocation_output'))

def get_students_with_own():
    students_with_own = []
    possible_students = Student.query.filter((Student.code1 == 'OWN') | (Student.code2 == 'OWN') | (Student.code3 == 'OWN') | (Student.code4 == 'OWN')).all()
    for student in possible_students:
        for i in range(1, 5):
            code = getattr(student, f"code{i}")
            if code == 'OWN':
                title = getattr(student, f"title{i}")
                reason = getattr(student, f"reason{i}")
                students_with_own.append((student, title, reason))
                break
    return students_with_own


@app.route('/allocationInput')
def allocationInput():
    return render_template('allocationInput.html', request=request)

@app.route("/allocationOutput")
def allocation_output():
    students = Student.query.all()
    staff = Staff.query.all()
    projects = Project.query.all()
    students_with_own = get_students_with_own()

    return render_template('allocationOutput.html', students=students, staff=staff, projects=projects, students_with_own=students_with_own, request=request)

@app.route('/statistics')
def statistics():
    return render_template('statistics.html', request=request)

@app.route('/api/staff_statistics')
def api_staff_statistics():
    staff = Staff.query.all()
    staff_statistics = [{'name': s.name, 'current_load': s.current_load, 'max_load': s.max_load} for s in staff]
    return jsonify(staff_statistics)
