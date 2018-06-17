# COMMON KNOWLEDGE FILE RWC2018

female_names = ["alex", "charlie", "elizabeth", "francis", "jennifer", "linda", "mary", "patricia", "robin", "skyler"]
male_names = ["alex", "charlie", "francis", "james", "john", "michael", "robert", "robin", "skyler", "william"]

names = female_names + male_names

# This dict holds all locations
locations = [
    {'name': 'side_table',      'room': 'bedroom',          'category': 'table',        'manipulation': 'yes'},
    {'name': 'bed',             'room': 'bedroom',          'category': 'utility',      'manipulation': 'no'},
    {'name': 'desk',            'room': 'bedroom',          'category': 'table',        'manipulation': 'yes'},
    
    {'name': 'cupboard',        'room': 'kitchen',          'category': 'shelf',        'manipulation': 'yes'},
    {'name': 'storage_table',   'room': 'kitchen',          'category': 'table',        'manipulation': 'yes'},
    {'name': 'sink',            'room': 'kitchen',          'category': 'utility',      'manipulation': 'no'},
    {'name': 'dishwasher',      'room': 'kitchen',          'category': 'utility',      'manipulation': 'no'},
    {'name': 'counter',         'room': 'kitchen',          'category': 'shelf',        'manipulation': 'yes'},

    {'name': 'dining_table',    'room': 'dining_room',      'category': 'table',        'manipulation': 'yes'},
    
    {'name': 'end_table',       'room': 'living_room',      'category': 'table',        'manipulation': 'yes'},
    {'name': 'couch',           'room': 'living_room',      'category': 'utility',      'manipulation': 'no'},
    {'name': 'bookcase',        'room': 'living_room',      'category': 'shelf',        'manipulation': 'yes'}
]

location_rooms = list(set([ o["room"] for o in locations ]))
location_categories = list(set([ o["category"] for o in locations ]))
location_names = list(set([ o["name"] for o in locations ]))
manipulation_locations = list(set([ o["name"] for o in locations if o["manipulation"] == "yes" ]))

rooms = location_rooms + ['corridor']

objects = [
    {'category': 'cleaning_stuff',      'name': 'cloth',            'color': 'purple',      'volume': 315,      'weight': 37},
    {'category': 'cleaning_stuff',      'name': 'scrubby',          'color': 'yellowish',   'volume': 161,      'weight': 22},
    {'category': 'cleaning_stuff',      'name': 'sponge',           'color': 'blue',        'volume': 314,      'weight': 15},

    {'category': 'containers',          'name': 'basket',           'color': 'beige',       'volume': 3487,     'weight': 43},
    {'category': 'containers',          'name': 'tray',             'color': 'white',       'volume': 617,      'weight': 65},

    {'category': 'cuttlery',            'name': 'fork',             'color': 'green',       'volume': 388,      'weight': 10},
    {'category': 'cuttlery',            'name': 'knife',            'color': 'green',       'volume': 376,      'weight': 10},
    {'category': 'cuttlery',            'name': 'spoon',            'color': 'green',       'volume': 378,      'weight': 10},

    {'category': 'drinks',              'name': 'chocolate_drink',  'color': 'brownish',    'volume': 388,      'weight': 325},
    {'category': 'drinks',              'name': 'coke',             'color': 'red',         'volume': 376,      'weight': 330},
    {'category': 'drinks',              'name': 'grape_juice',      'color': 'purplish',    'volume': 378,      'weight': 200},
    {'category': 'drinks',              'name': 'orange_juice',     'color': 'orange',      'volume': 376,      'weight': 200},
    {'category': 'drinks',              'name': 'sprite',           'color': 'bluegreen',   'volume': 376,      'weight': 330},

    {'category': 'food',                'name': 'cereal',           'color': 'blue',        'volume': 301,      'weight': 21},
    {'category': 'food',                'name': 'noodles',          'color': 'yellowish',   'volume': 320,      'weight': 85},
    {'category': 'food',                'name': 'sausages',         'color': 'blue',        'volume': 254,      'weight': 113},

    {'category': 'fruits',              'name': 'apple',            'color': 'greenred',    'volume': 1485,     'weight': 85},
    {'category': 'fruits',              'name': 'orange',           'color': 'orange',      'volume': 352,      'weight': 140},
    {'category': 'fruits',              'name': 'paprika',          'color': 'red',         'volume': 240,      'weight': 90},

    {'category': 'snacks',              'name': 'crackers',         'color': 'orange',      'volume': 300,      'weight': 28},
    {'category': 'snacks',              'name': 'potato_chips',     'color': 'black',       'volume': 239,      'weight': 200},
    {'category': 'snacks',              'name': 'pringles',         'color': 'green',       'volume': 1125,     'weight': 156},

    {'category': 'tableware',           'name': 'bowl',             'color': 'green',       'volume': 300,      'weight': 28},
    {'category': 'tableware',           'name': 'cup',              'color': 'green',       'volume': 239,      'weight': 200},
    {'category': 'tableware',           'name': 'dish',             'color': 'green',       'volume': 1125,     'weight': 156}
]

{'category': 'help_me_carry', 'name': 'bag', 'color': 'pink'},

object_names = list(set([ o["name"] for o in objects ]))
object_categories = list(set([ o["category"] for o in objects ]))
object_color = list(set([ o["color"] for o in objects ]))
object_size = list(set([ o["volume"] for o in objects ]))
object_weight = list(set([ o["weight"] for o in objects ]))
# object_groups = list(set([ o["group"] for o in objects ]))
# object_known_objects = list(set([ o["name"] for o in objects ]))

category_locations = {
    "drinks": {"counter": "on_top_of"},
    "cleaning_stuff": {"side_table": "on_top_of"},
    "snacks": {"bookcase": "shelf3"},
    "fruits": {"bookcase": "shelf2"},
    "container": {"end_table": "on_top_of"},
    "food": {"cupboard": "shelf2"},
    "kitchen_stuff": {"storage_table": "on_top_of"}
}

inspect_areas = {
    "bookcase": ["shelf2", "shelf3", "shelf4"],
    "cupboard": ["shelf2", "shelf3", "shelf4"]
}

inspect_positions = {
}

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

most_probable_location_in_room_map = {
    'bedroom': 'side_table',
    'kitchen': 'cupboard',
    'dining_room': 'dining_table',
    'living_room': 'end_table'
}

def get_location_from_room(room_id):
    if room_id in most_probable_location_in_room_map:
        return most_probable_location_in_room_map[room_id]
    return None

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

''' colors from printing on screen '''
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


'''
General function for printing shortcuts
name: name of the program that instantiates make_prints
sentence: sentence to be displayed

Ex: "[<EXECUTIVE NAME>] <SENTENCE TO BE DISPLAYED>"
'''


def make_prints(name):

    prefix = bcolors.HEADER + name + bcolors.ENDC

    def printOk(sentence):
        print prefix + bcolors.OKBLUE + sentence + bcolors.ENDC

    def printError(sentence):
        print prefix + bcolors.FAIL + sentence + bcolors.ENDC

    def printWarning(sentence):
        print prefix + bcolors.WARNING + sentence + bcolors.ENDC

    return printOk, printError, printWarning

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def is_location(location):
    for loc in locations:
        if loc["name"] == location:
            return True
    return False


def get_room(location):
    for loc in locations:
        if loc["name"] == location:
            return loc["room"]
    return None


def is_room(entity_id):
    return (entity_id in rooms)


def get_inspect_areas(location):
    if location in inspect_areas:
        return inspect_areas[location]
    else:
        return ["on_top_of"]


def get_inspect_position(location, area=""):
    if location in inspect_positions and area in inspect_positions[location]:
        return inspect_positions[location][area]
    else:
        return "in_front_of"


def is_pick_location(location):
    for loc in locations:
        if loc["name"] == location and loc["manipulation"] == "yes":
            return True
    return False


def is_place_location(location):
    for loc in locations:
        if loc["name"] == location and (loc["manipulation"] == "yes" or loc["manipulation"] == "only_putting"):
            return True
    return False


def get_locations(room=None, pick_location=None, place_location=None):
    return [loc["name"] for loc in locations
                if (room == None or loc["room"] == room) and \
                   (pick_location == None or pick_location == is_pick_location(loc["name"])) and \
                   (place_location == None or place_location == is_place_location(loc["name"]))]


def get_objects(category=None):
    return [obj["name"] for obj in objects
                if category == None or category == obj["category"]]


def get_object_category(obj):
    for o in objects:
        if o["name"] == obj:
            return o["category"]
    return None

def get_object_color(obj):
    for o in objects:
        if o["name"] == obj:
            return o["color"]
    return None

def get_object_size(obj):
    for o in objects:
        if o["name"] == obj:
            return o["volume"]
    return None

def get_object_weight(obj):
    for o in objects:
        if o["name"] == obj:
            return o["weight"]
    return None

# Returns (location, area_name)
def get_object_category_location(obj_cat):
    location = category_locations[obj_cat].keys()[0]
    area_name = category_locations[obj_cat].values()[0]
    return (location, area_name)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

if __name__ == "__main__":
    print "\n-----------------------------------------------------------------------------"
    for obj in get_objects():
        cat = get_object_category(obj)
        (location, area_name) = get_object_category_location(cat)
        print "object '{}'".format(obj)
        print "    category: '{}'".format(cat)
        print "    found '{} {}'".format(area_name, location)

    print "\n-----------------------------------------------------------------------------"
    for loc in get_locations():
        print "location '{}', room: '{}'".format(loc, get_room(loc))

    print "\n-----------------------------------------------------------------------------"
    print "Pick locations:"
    for loc in get_locations(pick_location=True):
        print "    {}".format(loc)

    print "\n-----------------------------------------------------------------------------"
    print "Place locations:"
    for loc in get_locations(place_location=True):
        print "    {}".format(loc)


    print "\n-----------------------------------------------------------------------------"
    print "None-manipulation locations:"
    for loc in get_locations(pick_location=False, place_location=False):
        print "    {}".format(loc)
