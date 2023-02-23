# All code inside of this file is code that came from David Head's original files that were provided to me as part of this project.
# They may be edited in some ways in order to suit my needs, but the credit goes to him for the original implementation

from .models import Student, Staff, Project

# This function takes a code as input and returns the staff member associated with that code
def staffForCode( code ):
	# Normalize the input code by removing any non-alphanumeric characters and converting to uppercase
	if code[0].isdigit():
		if "." in code:
			code = code[code.find(".")+1:]

	normed = ""
	for char in code:
		if char.isalnum():
			normed += char

	code = normed.strip().upper()

	for title in Student.query.all():

	# 'OWN' projects have no staff member.
	if code.lower().startswith("own")	: return "<unknown>"

	# Companies also have no staff member.
	if code.lower().startswith("herd")	: return "<unknown>"
	if code.lower().startswith("elder")	: return "<unknown>"

	# Staff initials. Check longer before shorter (e.g. Marc de Kamps before Mehmet Dogar).
	if code.lower().startswith("dimit")	: return "Vania Dimitrova"
	if code.lower().startswith("adler")	: return "Isolde Adler"
	if code.lower().startswith("cohen")	: return "Netta Cohen"
	if code.lower().startswith("stell")	: return "John Stell"

	if code.lower().startswith("twak")	: return "Tom Kelly"
	if code.lower().startswith("cohn")	: return "Tony Cohn"
	if code.lower().startswith("kwan")	: return "Raymond Kwan"
	if code.lower().startswith("jliu")	: return "Jian Liu"

	if code.lower().startswith("mdk")	: return "Marc de Kamps"
	if code.lower().startswith("dch")	: return "David Hogg"
	if code.lower().startswith("ajb")	: return "Andy Bulpitt"
	if code.lower().startswith("nde")	: return "Nick Efford"
	if code.lower().startswith("dah")	: return "David Head"
	if code.lower().startswith("mas")	: return "Ammar Alsalka"
	if code.lower().startswith("hac")	: return "Hamish Carr"
	if code.lower().startswith("oaj")	: return "Owen Johnson"
	if code.lower().startswith("rka")	: return "Rafael Kuffner dos Anjos"

	if code.lower().startswith("bb")	: return "Brandon Bennett"
	if code.lower().startswith("kv")	: return "Kristina Vuskovic"
	if code.lower().startswith("kd")	: return "Karim Djemame"
	if code.lower().startswith("rr")	: return "Roy Ruddle"
	if code.lower().startswith("ns")	: return "Natasha Shakhlevich"
	if code.lower().startswith("jx")	: return "Jie Xu"
	if code.lower().startswith("sw")	: return "Sam Wilson"
	if code.lower().startswith("kl")	: return "Kelvin Lau"
	if code.lower().startswith("fl")	: return "Farha Lakhani"
	if code.lower().startswith("zw")	: return "Zheng Wang"
	if code.lower().startswith("md")	: return "Mehmet Dogar"
	if code.lower().startswith("tl")	: return "Toni Lassila"
	if code.lower().startswith("hw")	: return "He Wang"
	if code.lower().startswith("mw")	: return "Mark Walkley"
	if code.lower().startswith("ea")	: return "Eric Atwell"
	if code.lower().startswith("aa")	: return "Abdulrahman Altahhan"
	if code.lower().startswith("tr")	: return "Thomas Ranner"
	if code.lower().startswith("al")	: return "Amy Lowe"
	if code.lower().startswith("so")	: return "Sebastian Ordyniak"
	if code.lower().startswith("jl")	: return "Joanna Leng"
	if code.lower().startswith("mb")	: return "Markus Billeter"
	if code.lower().startswith("sa")	: return "Sharib Ali"
	if code.lower().startswith("mc")	: return "Martin Callaghan"

	# Hard coding out some common mistakes
	if code.lower().startswith("dha")	: return "David Head"
	if code.lower().startswith("0aj")	: return "Owen Johnson"
	if code.lower().startswith("w01")	: return "Sam Wilson"
	if code.lower().startswith("he07")	: return "He Wang"

	return (code)
