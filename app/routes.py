import pandas as pd

from app import app, db
from flask import render_template, flash
from .models import Student, Staff, Project
from .stakeholderFunctions import staffForCode

@app.route("/students")
def students():
    Student.query.delete()
    df = pd.read_csv('datafiles/anonymisedForms.csv')
    for i, row in df.iterrows():
        student = Student(
            name = row[4],
            username = row[3].split('@')[0],
            degree = row[7],
            code1 = row[9],
            title1 = row[10],
            reason1 = row[11],
            code2 = row[12],
            title2 = row[13],
            reason2 = row[14],
            code3 = row[15],
            title3 = row[16],
            reason3 = row[17],
            code4 = row[18],
            title4 = row[19],
            reason4 = row[20],
            allocated_code = '0',
            allocated_staff = '0'
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
            staff_member = Staff(name=code, max_load=0, current_load=0)
            db.session.add(staff_member)
            db.session.commit()

    staff = Staff.query.all()
    return render_template('staffTable.html', staff=staff)
