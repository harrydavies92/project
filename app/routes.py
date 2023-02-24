import pandas as pd

from app import app, db
from flask import render_template
from .models import Student, Staff, Project
from .stakeholderFunctions import staffForCode,normaliseCode

@app.route("/students")
def students():
    Student.query.delete()
    df = pd.read_csv('datafiles/anonymisedForms.csv')
    for i, row in df.iterrows():
        student = Student(
            name = row[4],
            username = row[3].split('@')[0],
            degree = row[7],
            code1 = normaliseCode(row[9]),
            title1 = row[10],
            reason1 = row[11],
            code2 = normaliseCode(row[12]),
            title2 = row[13],
            reason2 = row[14],
            code3 = normaliseCode(row[15]),
            title3 = row[16],
            reason3 = row[17],
            code4 = normaliseCode(row[18]),
            title4 = row[19],
            reason4 = row[20],
            allocated_code = '0',
            allocated_staff = "blank"
        )
        db.session.add(student)
    db.session.commit()

    students = Student.query.all()
    return render_template('studentTable.html', students=students)

@app.route("/staff")
def staff():
    Staff.query.delete()

    all_codes = set()
    for student in Student.query.all():
        all_codes.add(staffForCode(student.code1))
        all_codes.add(staffForCode(student.code2))
        all_codes.add(staffForCode(student.code3))
        all_codes.add(staffForCode(student.code4))

    all_codes = list(all_codes)

    for code in all_codes:
        if Staff.query.filter_by(name=code).first() is None:
            staff_member = Staff(name=code, max_load=10, current_load=0)
            db.session.add(staff_member)
            db.session.commit()

    staff = Staff.query.all()
    return render_template('staffTable.html', staff=staff)

@app.route("/project")
def project():
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

    # Query all Project records and pass them to the projectTable.html template for rendering
    projects = Project.query.order_by(Project.title).all()
    return render_template('projectTable.html', projects=projects)
