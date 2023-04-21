from app import db

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    username = db.Column(db.String(64), index=True)
    degree = db.Column(db.String(64))
    code1 = db.Column(db.String(10))
    title1 = db.Column(db.String(64))
    reason1 = db.Column(db.String(256))
    code2 = db.Column(db.String(10))
    title2 = db.Column(db.String(64))
    reason2 = db.Column(db.String(256))
    code3 = db.Column(db.String(10))
    title3 = db.Column(db.String(64))
    reason3 = db.Column(db.String(256))
    code4 = db.Column(db.String(10))
    title4 = db.Column(db.String(64))
    reason4 = db.Column(db.String(256))
    allocated_preference = db.Column(db.Integer, default=None)
    allocated_code = db.Column(db.String(10), db.ForeignKey('project.code'))
    allocated_staff = db.Column(db.String(64), db.ForeignKey('staff.name'))
    pinned = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '{}{}{}{}'.format(self.id, self.name, self.username, self.allocated_code)

class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    max_load = db.Column(db.Integer)
    current_load = db.Column(db.Integer)
    students = db.relationship('Student', backref='staff', lazy='dynamic')
    projects = db.relationship('Project', backref='staff', lazy='dynamic')

    def __repr__(self):
        return '{}{}{}'.format(self.id, self.name, self.current_load, self.max_load)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), index=True, unique=True)
    title = db.Column(db.String(64))
    max_load = db.Column(db.Integer)
    current_load = db.Column(db.Integer)
    popularity = db.Column(db.Integer)
    students = db.relationship('Student', backref='project', lazy='dynamic')
    staff_member = db.Column(db.String(64), db.ForeignKey('staff.name'))

    def __repr__(self):
        return '{}{}{}{}'.format(self.id, self.code, self.popularity, self.staff_member)
