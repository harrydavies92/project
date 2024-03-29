# This code is inspired by the autoAllocate.py in the original stakeholder code, but is rewritten for my own setup

import random, math
from app import db
from .stakeholderFunctions import staffForCode

# Calculates the energy of the current allocation
def calculateEnergy(students, staff, projects, PREFERENCE_ENERGY, STAFF_OVERLOAD_ENERGY, NO_PROJECT_ENERGY, PROJECT_OVERLOAD_ENERGY):

    # Initialise the energy
    energy = 0.0

    # Go through each student and check their allocation
    for student in students:

        # Penalty for not assigned a project yet
        if student.allocated_code == "0":
            energy += NO_PROJECT_ENERGY
        else:
            # Grab the data for the allocated project and staff
            project = None
            for p in projects:
                if p.code == student.allocated_code:
                    project = p
                    break
            staff_member = None
            for s in staff:
                if s.name == student.allocated_staff:
                    staff_member = s
                    break

            # Penalty for overloaded member of staff
            if staff_member is not None:
                if staff_member.current_load > staff_member.max_load:
                    energy += STAFF_OVERLOAD_ENERGY * (staff_member.max_load - staff_member.current_load) * staff_member.max_load

            # Penalty for overloaded project
            if project is not None:
                if project.current_load > project.max_load:
                    energy += PROJECT_OVERLOAD_ENERGY * (project.max_load - project.current_load)

            # Penalty for preference lower than first
            if student.allocated_preference is not None:
                if int(student.allocated_preference) != 1:
                    energy += PREFERENCE_ENERGY * (int(student.allocated_preference) - 1)

    # Return the total energy
    return energy

# Runs the allocation algorithm
def allocation(students, staff, projects, startT, endT, PREFERENCE_ENERGY, STAFF_OVERLOAD_ENERGY, NO_PROJECT_ENERGY, PROJECT_OVERLOAD_ENERGY):

    # Calculates the inital energy
    start_energy = calculateEnergy(students, staff, projects, PREFERENCE_ENERGY, STAFF_OVERLOAD_ENERGY, NO_PROJECT_ENERGY, PROJECT_OVERLOAD_ENERGY)

    # Loops through an allocation process a large number of times, relative to the number of students
    numSteps = len(students)**2

    # Add energy log to track energy as we go along
    energy_log = []

    for step in range(numSteps):

        # Pick a random student who isn't pinned
        student = None
        while student is None or student.pinned:
            student = random.choice(students)

        # Store the old allocation for later
        oldPreference = student.allocated_preference
        oldCode = student.allocated_code
        oldStaff = None
        for s in staff:
            if s.name == student.allocated_staff:
                oldStaff = s
                break
        oldProject = None
        for p in projects:
            if p.code == student.allocated_code:
                oldProject = p
                break

        # Pick a random project from the preference list that's different than the current allocation
        newPreference = random.randint(1, 4)
        while (oldPreference == newPreference):
            newPreference = random.randint(1, 4)
        newCode = getattr(student, f'code{newPreference}')
        newStaff = None
        for s in staff:
            if s.name == staffForCode(newCode):
                newStaff = s
                break
        newProject = None
        for p in projects:
            if p.code == newCode:
                newProject = p
                break

        # Calculate change in energy (quicker than calculating entire energy again)
        d_energy = 0.0

        # If not yet assigned, decrease the energy. Otherwise change energy based on preference change
        if oldPreference == -1:
            d_energy -= NO_PROJECT_ENERGY
        elif oldPreference is None:
            d_energy -= NO_PROJECT_ENERGY
        else:
            d_energy += (newPreference - oldPreference) * PREFERENCE_ENERGY

        # Reduce penalty if this change reduces the number of students for a staff member at their maximum
        if oldPreference != -1:
            if oldStaff is not None:
                if (oldStaff.max_load - oldStaff.current_load) <= 0:
                    d_energy -= STAFF_OVERLOAD_ENERGY * oldStaff.max_load

        # Increase penalty if this change increases or starts a staff work overload
        if (newStaff.max_load - newStaff.current_load) < 0:
            d_energy += STAFF_OVERLOAD_ENERGY * newStaff.max_load

        # Reduce penalty if this change reduces excess students on the old project
        if oldPreference != -1:
            if oldProject is not None:
                if (oldProject.max_load - oldProject.current_load) <= 0:
                    d_energy -= PROJECT_OVERLOAD_ENERGY * oldProject.max_load

        # Increase penalty if this change starts or increases a project overload
        if (newProject.max_load - newProject.current_load) < 0:
            d_energy += PROJECT_OVERLOAD_ENERGY * newProject.max_load

        # Decide whether or not to accept the new change
        currentT = startT + (endT-startT) * float(step)/numSteps
        accept = (True if d_energy < 0.0 else False)
        if (d_energy > 0.0) and (d_energy < 30.0 * currentT):
            if random.random() < math.exp(-d_energy/currentT):
                accept = True

        # If we are accepting it, carry on. If not, reiterate the loop
        if not accept: continue

        # Make the change
        student.allocated_code = newCode
        student.allocated_staff = newStaff.name
        student.allocated_preference = newPreference
        if oldStaff is not None:
            oldStaff.current_load -= 1
        newStaff.current_load += 1
        if oldProject is not None:
            oldProject.current_load -= 1
        newProject.current_load += 1

        # energy_log.append(calculateEnergy(students, staff, projects, PREFERENCE_ENERGY, STAFF_OVERLOAD_ENERGY, NO_PROJECT_ENERGY, PROJECT_OVERLOAD_ENERGY))

    # Commit the changes to the database
    db.session.commit()

    final_energy = calculateEnergy(students, staff, projects, PREFERENCE_ENERGY, STAFF_OVERLOAD_ENERGY, NO_PROJECT_ENERGY, PROJECT_OVERLOAD_ENERGY)
    return students, staff, projects, start_energy, final_energy, energy_log
