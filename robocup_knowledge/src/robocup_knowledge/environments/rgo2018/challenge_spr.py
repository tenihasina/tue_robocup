from robocup_knowledge import knowledge_loader
common = knowledge_loader.load_knowledge("common")

not_understood_sentences = [
        "I'm so sorry! Can you please speak louder and slower? And wait for the ping!",
        "I am deeply sorry. Please try again, but wait for the ping!",
        "You and I have communication issues. Speak up!",
        "All this noise is messing with my audio. Try again"
    ]
grammar_target = "T"

##############################################################################
#
# Actions
#
##############################################################################

grammar = """
T[{actions : <A1>}] -> C[A1]
T[{actions : <A1, A2>}] -> C[A1] and C[A2]
T[{actions : <A1, A2, A3>}] -> C[A1] C[A2] and C[A3]

C[{A}] -> Q[A]
"""

##############################################################################
#
# Verbs & shared stuff
#
##############################################################################

grammar += """
V_GUIDE -> guide | escort | take | lead | accompany

DET -> the | a | an | some
MANIPULATION_AREA_DESCRIPTIONS -> on top of | at | in | on
"""

for room in common.location_rooms:
    grammar += '\nROOMS[%s] -> %s' % (room, room)
for loc in common.get_locations():
    grammar += '\nLOCATIONS[%s] -> %s' % (loc, loc)
grammar += '\n ROOMS_AND_LOCATIONS[X] -> ROOMS[X] | LOCATIONS[X]'
for obj in common.object_names:
    grammar += '\nOBJECT_NAMES[%s] -> %s' % (obj, obj)
for loc in common.get_locations(pick_location=True, place_location=True):
    grammar += '\nMANIPULATION_AREA_LOCATIONS[%s] -> MANIPULATION_AREA_DESCRIPTIONS the %s' % (loc, loc)
for cat in common.object_categories:
    grammar += '\nOBJECT_CATEGORIES[%s] -> %s' % (cat, cat)

##############################################################################
#
# Predefined questions
#
##############################################################################

grammar += '''
Q['answer': "the scientific study of robot"] -> what is robotics
Q['answer': "joseph engelberger"] -> who is considered as the father of industrial robot	
Q['answer': "aml a manufacturing language"] -> give one example for a computer programming language that can be used for robot programming
Q['answer': "heavy investment"] -> what is the major disadvantage of using a robot
Q['answer': "lisp and prolog"] -> name the language used in expert system
Q['answer': "knowledge base"] -> name one of the most important parts in expert system
Q['answer': "mycin"] -> which system was designed for diagnosis and therapy recommendation for infectious disease
Q['answer': "human intelligence have certain limit in speed and accuracy it is interrupted due to the lack of presence of mind mood etc but a i systems have their own superb abilities"] -> what is the importance of a i
Q['answer': "tim burners lee"] -> weaving the web was written by
Q['answer': "trial test of a computer or software before the commercial launch"] -> what is beta test
Q['answer': "portable document format"] -> what is the extension of pdf
Q['answer': "relational data base management system"] -> expand rdbms
Q['answer': "charles babbage"] -> difference engine was developed by
Q['answer': "google"] -> orkut dot com is now owned by
Q['answer': "intel 4004"] -> worlds first microprocessor is
Q['answer': "structured query language"] -> what is sql
Q['answer': "short message service"] -> what is the expansion of sms	 
Q['answer': "ibm"] -> which it companys nickname is the big blue
Q['answer': "institute of electric and electronic engineers"] -> what is the full form of ieee
Q['answer': "raymond samuel tomlinson"] -> email was developed by
Q['answer': "net citizen citizen who uses internet"] -> who is netizen
Q['answer': "fake antivirus softwares"] -> what is scareware

WHATWHICH -> what | which

'''
	
#Q['answer': "george devol"] -> who holds the patent for the first industrial robot
#Q['answer': "manipulator, brain, power supply."] -> what are the three major components of a robot?
#Q['answer': "manipulator."] -> which part controls the movement of robots hand
#Q['answer': "as its controller"] -> what is the purpose of a computer in a robot system
#Q['answer': " memory, cpu, a d and d a converters"] -> what are the hardwares essential in a computer controlled robot

#Q['answer': "a combination of cad cam and robotics"] -> what is flexible manufacturing system or computerized manufacturing system

#Q['answer': "1958"] -> the expert system was introduced in
#Q['answer': "stanford."] -> the expert system was developed by which university
#Q['answer': "dendral"] -> the first expert system was
#Q['answer': "artificial intelligence"] -> in which field the expert system has application areas of a i

#Q['answer': "research chemists"] -> dendral system is widely used by
#Q['answer': "macsyma"] -> which system has been designed for solving mathematical problems
#Q['answer': "prospector"] -> which system has been designed to assist geologist in mineral exploration
#Q['answer': "artificial intelligence is a branch of computer science concerned with the study and creation of systems that exhibit some form of human intelligence"] -> what is artificial intelligence

#Q['answer': "allen turing"] -> who is the father of artificial intelligence
#Q['answer': "ipl"] -> which is the first test programming language
#Q['answer': "1958"] -> the beginning of artificial intelligence in
#Q['answer': "1 lisp 2 prolog 3 small talk and actor."] -> what are the languages used for artificial intelligence programming
#Q['answer': "list programming language"] -> lisp is
#Q['answer': "logic programming language"] -> prolog is
#Q['answer': "object oriented programming language"] -> small talk and actor are
#Q['answer': "1 expert system 2 natural language system 3 perception system"] -> what are the branches of artificial intelligence
#['answer': "james t russel"] -> who invented compact disc 
#Q['answer': "december 2"] -> which day is celebrated as world computer literacy day
#Q['answer': "james a gosling"] -> who invented java
#Q['answer': "windows vista"] -> longhorn was the code name of 	 
#Q['answer': "shakunthala devi"] -> who is known as the human computer of india
#Q['answer': "people who work with the computer"] -> what is mean by liveware
#Q['answer': "jm coetzee"] -> which computer engineer got nobel prize for literature in 2003

#Q['answer': "google"] -> do no evil is tag line of	 
#Q['answer': "vivah"] -> first indian cinema released through internet is	 
#Q['answer': "ajith balakrishnan and manish agarwal"] -> rediff dot com was founded by

#Q['answer': "physically handicapped people"] -> mows is a type of mouse for dot dot dot people	 

#Q['answer': "common business oriented language"] -> what is the expansion of cobol	 

#Q['answer': "grace murry hopper"] -> who developed cobol

#Q['answer': "web filter"] -> green dam is
#Q['answer': "complementary metal oxide semoconductor"] -> what is the expanded form of cmos  	 

#Q['answer': "1992 the ibm simon"] -> when was the first smart phone launched 	 	 


##############################################################################
#
# Counting People
#
##############################################################################

grammar += '''
CP[{"action" : "count", "entity" : P}] -> COUNT PEOPLE[P] are in the crowd | tell me COUNT PEOPLE[P] in the crowd
'''

##############################################################################
#
# Arena questions
#
##############################################################################

grammar += '''
COUNT -> how many | the number of
SEARCH -> where is | in WHATWHICH room is

Q[{"action" : "a_find", "entity" : AP}] -> SEARCH the PLACEMENT[AP]
Q[{"action" : "a_find", "entity" : AB}] -> SEARCH the BEACON[AB]
Q[{"action" : "a_count", "entity" : Y, "location" : R}] -> how many PLACEMENT[Y] are in the ROOM[R]
Q[{"action" : "a_count", "entity" : Z, "location" : R}] -> how many BEACON[Z] are in the ROOM[R]
'''

##############################################################################
#
# Object / Category questions
#
##############################################################################

grammar += '''
Q[{"action" : "o_find", "entity" : O}] -> where can i find a OBJECT[O]
Q[{"action" : "c_find", "entity" : C}] -> where can i find a CATEGORY[C]
Q[{"action" : "return_category", "entity" : O}] -> to WHATWHICH category belong the OBJECT[O]
'''

##############################################################################
#
# Data
#
##############################################################################

grammar +='''

PEOPLE['people'] -> people
PEOPLE['children'] -> children
PEOPLE['adults'] -> adults
PEOPLE['elders'] -> elders
PEOPLE['males'] -> males
PEOPLE['females'] -> females
PEOPLE['men'] -> men
PEOPLE['women'] -> women
PEOPLE['boys'] -> boys
PEOPLE['girls'] -> girls

PLACEMENT['bookshelf'] -> bookshelf | bookshelfs
PLACEMENT['couch_table'] -> couch table | couch tables
PLACEMENT['side_table'] -> side table | side_table
PLACEMENT['kitchencounter'] -> kitchen counter | kitchen counters | kitchencounter | kitchencounters
PLACEMENT['stove'] -> stove | stoves
PLACEMENT['desk'] -> desk |desks
PLACEMENT['bar'] -> bar | bars
PLACEMENT['closet'] -> closet | closets
PLACEMENT['dinner_table'] -> dinner table | dinner tables
PLACEMENT['cabinet'] -> cabinet | cabinets

BEACON['tv_stand'] -> tv stand | tv stands
BEACON['bed'] -> bed | beds
BEACON['sofa'] -> sofa | sofas
BEACON['cupboard'] -> cupboard | cupboards
BEACON['sink'] -> sink | sinks
BEACON['counter'] -> counter | counters

ROOM['dining'] -> dining room
ROOM['living'] -> living room
ROOM['kitchen'] -> kitchen
ROOM['bedroom'] -> bedroom

OBJECT['apple'] -> apple
OBJECT['bread'] -> bread
OBJECT['cereals'] -> cereals
OBJECT['cornflakes'] -> cornflakes
OBJECT['crackers'] -> crackers
OBJECT['lemon'] -> lemon
OBJECT['noodles'] -> noodles
OBJECT['paprika'] -> paprika
OBJECT['peas'] -> peas
OBJECT['pepper'] -> pepper
OBJECT['potato'] -> potato
OBJECT['potato_soup'] -> potato soup
OBJECT['salt'] -> salt
OBJECT['tomato_pasta'] -> tomato pasta
OBJECT['bag'] -> bag
OBJECT['basket'] -> basket
OBJECT['coffecup'] -> coffecup
OBJECT['plate'] -> plate
OBJECT['red_bowl'] -> red bowl
OBJECT['white_bowl'] -> white bowl
OBJECT['banana_milk'] -> banana milk
OBJECT['cappucino'] -> cappucino
OBJECT['coke'] -> coke
OBJECT['orange_drink'] -> orange drink
OBJECT['water'] -> water
OBJECT['chocolate_cookies'] -> chocolate cookies
OBJECT['egg'] -> egg
OBJECT['party_cracker'] -> party cracker
OBJECT['pringles'] -> pringles
OBJECT['cloth'] -> cloth
OBJECT['paper'] -> paper
OBJECT['sponge'] -> sponge
OBJECT['towel'] -> towel
OBJECT['fork'] -> fork
OBJECT['spoon'] -> spoon
OBJECT['knife'] -> knife

CATEGORY['food'] -> food | foods
CATEGORY['container'] -> container | containers
CATEGORY['drink'] -> drink | drinks
CATEGORY['cleaning_stuff'] -> cleaning stuff | cleaning stuffs
CATEGORY['cutlery'] -> cutlery | cutleries
'''

old_grammar = """

# People Positions/Gestures/Genders

PP[{"action" : "c_count", "entity" : X}] -> how many people in the crowd are POSITION[X]
PG[{"action" : "c_count", "entity" : W}] -> how many people in the crowd are GESTURE[W]
PPG[{"action" : "random_gender", "entity" : X}] -> the POSITION[X] person was GENDER | tell me if the POSITION[X] person was a GENDER
PPGG[{"action" : "random_gender", "entity" : X}] -> the POSITION[X] person was GENDER or GENDER | tell me if the POSITION[X] person was a GENDER or GENDER
PGG[{"action" : "random_gender", "entity" : W}] -> tell me if the GESTURE[W] person was a GENDER
PGGG[{"action" : "random_gender", "entity" : W}] -> tell me if the GESTURE[W] person was a GENDER or GENDER
PC[{"action" : "c_count", "entity" : L}] -> tell me how many people were wearing COLOR[L]

# - - - - - - - - - - - - - - - - - - - - - - - - -
# Object questions
# - - - - - - - - - - - - - - - - - - - - - - - - -

CCOUNT[{"action" : "o_count", "entity" : C}] -> how many CATEGORY[C] there are

OCOLOR[{"action" : "find_color", "entity" : O}] -> whats the colour of the OBJECT[O]
OCAT[{"action" : "compare_category", "entity_a" : O, "entity_b" : A}] -> do the OBJECT[O] and OBJECT[A] belong to the same category

CATPLACE[{"action" : "o_count", "entity" : C, "location" : PL}] -> how many CATEGORY[C] are in the PLACEMENT[PL]
OBJPLACE[{"action" : "o_count", "entity" : O, "location" : PL}] -> how many OBJECT[O] are in the PLACEMENT[PL]
CATLOC[{"action" : "category_at_loc", "location" : PL}] -> what objects are stored in the PLACEMENT[PL]

OBJCOMP[{"action" : "compare", "entity_a" : O, "entity_b" : A}] -> between the OBJECT[O] and OBJECT[A] WHATWHICH one is ADJR

ADJA -> smallest | biggest
ADJR -> smaller | bigger

# - - - - - - - - - - - - - - - - - - - - - - - - -
# D A T A
# - - - - - - - - - - - - - - - - - - - - - - - - -

POSITION['standing'] -> standing
POSITION['sitting'] -> sitting
POSITION['lying'] -> lying

GENDER['male'] -> male
GENDER['female'] -> female
GENDER['man'] -> man
GENDER['woman'] -> woman
GENDER['boy'] -> boy
GENDER['girl'] -> girl

GESTURE['waving'] -> waving
GESTURE['rise_l_arm'] -> rising left arm
GESTURE['rise_r_arm'] -> rising right arm
GESTURE['left'] -> pointing left
GESTURE['right'] -> pointing right

COLOR['red'] -> red
COLOR['blue'] -> blue
COLOR['white'] -> white
COLOR['black'] -> black
COLOR['green'] -> green
COLOR['yellow'] -> yellow

"""

if __name__ == "__main__":
	print grammar
