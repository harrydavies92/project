#
# Attempt to automatically allocate projects to students. Based on a simple Monte Carlo scheme
# with a Metroplis algorithm, and energies assign to undesirable features, i.e. penalties.
#
# 19/7/2022/DAH: Stopped attempting to auto-allocate projects to other staff, as it doesn't work
# and makes the eventual manual allocation a bit more work.
#


#
# Imports.
#
import random
import math


class autoAllocate:


	#
	#MARK: Penalties and energy calculations.
	#

	# The current energy.
	@classmethod
	def energy( cls, students, staff, projects ):

		E = 0.0

		# Increment energy for student-related penalties.
		for student in students:
			index = student.assignedIndex

			# If not assigned project yet, increment the energy and move to the next student.
			if student.assignedIndex == -1:
				E += cls.E_noSupervisor()
				continue

			# Small energy penalties for students not getting their first choice preference.
			E += student.priority * cls.E_preference() * student.assignedIndex

			# Also penalise for projects supervised by someone other than the proposer.
			code     = student.getPreference(index)["code"]
			proposer = staff.staffNameForCode(code)

			if proposer.casefold()!="<none>".casefold() and proposer.casefold()!=student.supervisor.casefold():
				E += cls.E_wrongSupervisor()

		# Apply penalties for members of staff taking on more students than their load suggests.
		# (Can negotiate with staff for e.g. reduced assessment load and/or reduced masters projects).
		# Penalty proportional to their maximum.
		for member in staff.fullList():
			maxSuper, actSuper = member["max"], len(member["supervising"])
			if actSuper > maxSuper:
				E += cls.E_excessSupervising() * ( actSuper - maxSuper ) * member["max"]

		# Large penalties for exceeding the number of students allowed on a project.
		# (Really shouldn't allow this at all).
		for project in projects:
			maxStud, actStud = project["max"], len(project["allocated"])
			if actStud > maxStud:
				E += cls.E_excessStudents() * ( actStud - maxStud )

		# Return with the total.
		return E

	# Parameters for energy penalties.
	@classmethod
	def E_preference( cls ):
		"""Absolute energy for each preference allocated to a student below their first."""
		return 0.25

	@classmethod
	def E_wrongSupervisor( cls ):
		"""Absolute energy for supervisor not being the proposer of a project, when that is allowed."""
		return 0.3

	@classmethod
	def E_excessSupervising( cls ):
		"""Relative energy for staff being assigned too many sudents, relative to their nominal maximum load."""
		return 2.0

	@classmethod
	def E_noSupervisor( clse ):
		"""Absolute energy for a student with no project or supervisor currently assigned."""
		return 5.0

	@classmethod
	def E_excessStudents( cls ):
		"""Absolute energy for too many students assigned to a project."""
		return 20.0

	#
	#MARK: Allocation.
	#

	# Simulated annealing.
	@classmethod
	def simulatedAnnealing( cls, students, staff, projects, numSteps=None, startT=2.0, endT=0.01 ):

		#
		# Sanity check.
		#

		# All students pinned? Then no point continuing (would hang at start of main loop).
		if len( [ s for s in students if not s.pinned ] )==0:
			print( "Cannot change allocation; all students pinned." )
			return

		# Need non-negative temperatures (allow zero; means only accept decreases in energy).
		if startT<0.0 or endT<0.0:
			print( "Both start and temperature must be non-negative." )
			return


		#
		# Initialise
		#
		if numSteps==None:
			numSteps = len(students)**2

		random.seed()
		initialE = cls.energy( students, staff, projects )

		#
		# Main loop.
		#
		for step in range(numSteps):

			#
			# Trial change.
			#

			# Select a non-pinned student.
			student = None
			while student==None or student.pinned:
				student = random.choice( students )

			# Store old values for calculating the change in energy later.
			oldIndex = student.assignedIndex
			if oldIndex != -1:
				oldCode    = student.getPreference(oldIndex)["code"]
				oldStaff   = student.supervisor
				oldProject = [ p for p in projects if p["code"].casefold()==oldCode.casefold() ][0]

			# Attempt a different project.
			newIndex = oldIndex
			while newIndex==oldIndex or student.getPreference(newIndex)["code"].casefold()=="NONE".casefold():
				newIndex = random.randrange( 0, student.numPreferences() )

			# Who would the member of staff be? Depends if this project allows any member of staff to supervise.
			# Changed 19/7/2022 to leave "any staff" projects to be dealt with manually; see comment at head of file.
			newCode    = student.getPreference(newIndex)["code"]
			newProject = [ p for p in projects if p["code"].casefold()==newCode.casefold() ][0]
			if newCode=="OWN":			# or ( newProject["any_staff"] and random.choice([True,False]) ): # Old version.
				newStaff = staff.randomStaffName()
			else:
				newStaff = staff.staffNameForCode( newCode )

			# Some coees (e.g. for external companies) do not have associated staff. These are ignored and should be
			# allocated manually prior to calling this method.
			if newStaff=="<none>": continue

			# Do not consider any changes involving a pinned member of staff.
			if (oldIndex!=-1 and staff.getStaff(oldStaff)["pinned"]) or staff.getStaff(newStaff)["pinned"]:
				continue

			# Do not consider any changes involving a pinned project.
			if (oldIndex!=-1 and oldProject["pinned"]) or newProject["pinned"]:
				continue

			# Only consider changing to an OWN project if it has been declared suitable.
			if newCode=="OWN" and student.suitableOWN != True:
				continue

			#
			# Potential change in energy. Don't recalculate the entire energy for speed, just the changes.
			#
			dE = 0.0

			# If not yet assigned, already a decrease in energy. Otherwise change energy based on change in preference.
			if oldIndex == -1:
				dE -= cls.E_noSupervisor()
			else:
				dE += student.priority * ( newIndex - oldIndex ) * cls.E_preference()

			# Remove penalty if current supervisor is not the proposer.
			if oldIndex != -1:
				oldProposer = staff.staffNameForCode(oldCode)
				if oldProposer.casefold()!="<none>".casefold() and oldStaff.casefold()!=oldProposer.casefold():
					dE -= cls.E_wrongSupervisor()

			# Apply penalty if new supervisor is not the proposer.
			newProposer = staff.staffNameForCode(newCode)
			if newProposer.casefold()!="<none>".casefold() and newStaff.casefold()!=newProposer.casefold():
				dE += cls.E_wrongSupervisor()

			# Reduce penalty if this reduces the number of students for a staff member at their maximum.
			if oldIndex != -1:
				if staff.untilMax( oldStaff ) < 0:
					dE -= cls.E_excessSupervising() * staff.maxForStaff( oldStaff )

			# Increase penalty if this change starts or increases a staff load beyond their maximum.
			if staff.untilMax( newStaff ) <= 0:										# Will start overloading, or increase the overloading,
				dE += cls.E_excessSupervising()	* staff.maxForStaff( newStaff )		# of the new member of staff.

			# Remove penalty if reduces excess students for the old project.
			if oldIndex != -1:
				if len(oldProject["allocated"]) > oldProject["max"]:
					dE -= cls.E_excessStudents()

			# Increase penalty if will start or increase overload for the new project.
			if len(newProject["allocated"]) >= newProject["max"]:
				dE += cls.E_excessStudents()

			#
			# Accept the change?
			#
			currentT = startT + (endT-startT) * float(step)/numSteps

			accept = ( True if dE<0.0 else False )
			if dE>0.0 and dE<30.0*currentT:											# Don't risk overflow for dE>>T when exponentiating.
				if random.random() < math.exp(-dE/currentT):
					accept = True

			if not accept: continue

			#
			# Make the change.
			#
			student.assignedIndex = newIndex
			student.supervisor    = newStaff

			# Swap student from old to new project.
			for project in projects:
				if oldIndex != -1:
					if project["code"]==oldCode:
						if student.username not in project["allocated"]:
							print( "Could not find student in allocation of old project." )
							return
						project["allocated"].remove( student.username )

				if project["code"]==newCode:
					project["allocated"].append( student.username )

			# Swap student from old to new staff member.
			for member in staff.fullList():
				if oldIndex != -1:
					if member["name"].casefold() == oldStaff.casefold():
						if student.username not in member["supervising"]:
							print( "Could not find student in staff member's supervision list." )
							return
						member["supervising"].remove( student.username )

				if member["name"].casefold() == newStaff.casefold():
					member["supervising"].append( student.username )


		#
		# Finalise and display the change in energy.
		#
		finalE = cls.energy( students, staff, projects )
		print( "Energy changed from {0} to {1}".format(initialE,finalE) )
