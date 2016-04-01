#! /usr/bin/python

# ------------------------------------------------------------------------------------------------------------------------
# By Sjoerd van den Dries, 2016

# TODO:
# - initial pose estimate
# - Enter arena
# - handover
# - Find person in different states
# - define in_front_of's, etc
# - also use the nav area for navigation
# - in "bring the lemon from the dinnertable to james who is in the kitchen", semantic key "from" is overwritten!
# - Fix constraint outside arena (quick fix: seal exit in heightmap)

# ------------------------------------------------------------------------------------------------------------------------

# Cannot deal with:
#    look for a person in the entrance and answer a question

        # go to the bookcase, find a person, and say your name

        # bookcase
        #      Locate at least three objects there.

# ------------------------------------------------------------------------------------------------------------------------

import os
import sys
import yaml
import cfgparser
import rospy
import random
import argparse

import robot_smach_states
from robot_smach_states.navigation import NavigateToObserve, NavigateToWaypoint, NavigateToSymbolic
from robot_smach_states import SegmentObjects, Grab, Place
from robot_smach_states.util.designators import EdEntityDesignator, EntityByIdDesignator, VariableDesignator, DeferToRuntime, analyse_designators, UnoccupiedArmDesignator, EmptySpotDesignator, OccupiedArmDesignator
from robot_skills.classification_result import ClassificationResult
from robocup_knowledge import load_knowledge
from command_recognizer import CommandRecognizer
from find_person import FindPerson
from datetime import datetime, timedelta
import robot_smach_states.util.designators as ds

from robot_smach_states import LookAtArea, StartChallengeRobust

challenge_knowledge = load_knowledge('challenge_gpsr')
speech_data = load_knowledge('challenge_speech_recognition')
starting_point = challenge_knowledge.starting_point

# ------------------------------------------------------------------------------------------------------------------------

class EntityDescription(object):
    def __init__(self, id=None, type=None, location=None):
        self.id = id
        self.type = type
        self.location = location

# ------------------------------------------------------------------------------------------------------------------------

def not_implemented(robot, parameters):
    rospy.logerr("This was not implemented, show this to Sjoerd: {}".format(parameters))
    robot.speech.speak("Not implemented! Warn Sjoerd", block=False)
    return

# ------------------------------------------------------------------------------------------------------------------------

class GPSR:

    def __init__(self):
        self.entity_ids = []
        self.entity_type_to_id = {}
        self.object_to_location = {}

        self.last_location = None
        self.last_entity = None

    def resolve_entity_description(self, parameters):
        descr = EntityDescription()

        if "special" in parameters:
            special = parameters["special"]
            if special =="it":
                descr = self.last_entity
            elif special == "operator":
                descr.id = "initial_pose"
                descr.type = "person"
        else:
            if "id" in parameters:
                descr.id = parameters["id"]
            if "type" in parameters:
                descr.type = parameters["type"]
            if "loc" in parameters:
                descr.location = parameters["loc"]

        return descr

    # ------------------------------------------------------------------------------------------------------------------------

    def navigate(self, robot, parameters):
        entity_descr = self.resolve_entity_id(parameters["entity"])

        if entity_descr.type == "person":
            robot.speech.speak("I cannot find people yet! Ask Janno to hurry up!")
            return

        self.last_location = entity_descr

        robot.speech.speak("I am going to the %s" % entity_descr.id, block=False)

        if entity_descr.type in challenge_knowledge.rooms:
            nwc =  NavigateToSymbolic(robot,
                                            { EntityByIdDesignator(robot, id=entity_descr.id) : "in" },
                                              EntityByIdDesignator(robot, id=entity_descr.id))
        else:
            # TODO
            nwc = NavigateToObserve(robot,
                                 entity_designator=EdEntityDesignator(robot, id=entity_descr.id),
                                 radius=.5)

        nwc.execute()

    # ------------------------------------------------------------------------------------------------------------------------

    def answer_question(self, robot, parameters):

        robot.head.look_at_standing_person()
        robot.head.wait_for_motion_done()
    
        robot.speech.speak("What is your question?")

        res = robot.ears.recognize(spec=speech_data.spec,
                                   choices=speech_data.choices,
                                   time_out=rospy.Duration(15))

        if not res:
            robot.speech.speak("My ears are not working properly, sorry!")

        if res:
            if "question" in res.choices:
                rospy.loginfo("Question was: '%s'?"%res.result)
                robot.speech.speak("The answer is %s" % speech_data.choice_answer_mapping[res.choices['question']])
            else:
                robot.speech.speak("Sorry, I do not understand your question")

    # ------------------------------------------------------------------------------------------------------------------------

    def say(self, robot, parameters):
        sentence = parameters["sentence"]
        rospy.loginfo('Answering %s', sentence)

        if sentence == 'TIME':
            hours = datetime.now().hour
            minutes = datetime.now().minute
            line = "The time is {} {}".format(hours, minutes)
        elif sentence == "ROBOT_NAME":
            line = 'My name is %s' % robot.robot_name
        elif sentence == 'TODAY':
            line = datetime.today().strftime('Today is %A %B %d')
        elif sentence == 'TOMORROW':
            line = (datetime.today() + timedelta(days=1)).strftime('Tomorrow is %A %B %d')
        elif sentence == 'DAY_OF_MONTH':
            line = datetime.now().strftime('It is day %d of the month')
        elif sentence == 'DAY_OF_WEEK':
            line = datetime.today().strftime('Today is a %A')
        else:
            line = sentence

        robot.speech.speak(line)

    # ------------------------------------------------------------------------------------------------------------------------

    def find_and_pick_up(self, robot, parameters, pick_up=True):
        entity_descr = self.resolve_entity_description(parameters["entity"])

        if entity_descr.type == "person":
            room_des = EdEntityDesignator(robot, id=entity_descr.loc)
            f = FindPerson(robot, room_des)
            result = f.execute()
            if result != 'succeeded':
                return

            robot.speech.speak("I found you!")
            return

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.last_entity = entity_descr

        if entity_descr.location or self.last_location:
            if entity_descr.location:
                room_or_location = entity_descr.location["id"]
            else:
                room_or_location = self.last_location.id            

            if room_or_location in challenge_knowledge.rooms:
                locations = [loc["name"] for loc in challenge_knowledge.common.locations
                             if loc["room"] == room_or_location and loc["manipulation"] == "yes"]
            else:
                locations = [room_or_location]

            locations_with_areas = []
            for location in locations:
                locations_with_areas += [(location, challenge_knowledge.common.get_inspect_areas(location))]
        else:
            obj_cat = None
            for obj in challenge_knowledge.common.objects:
                if obj["name"] == entity_descr.type:
                    obj_cat = obj["category"]

            location = challenge_knowledge.common.category_locations[obj_cat].keys()[0]
            area_name = challenge_knowledge.common.category_locations[obj_cat].values()[0]

            locations_with_areas = [(location, [area_name])]

            robot.speech.speak("The {} is a {}, which is stored on the {}".format(entity_descr.type, obj_cat, location), block=False)

        location_defined = (len(locations_with_areas) == 1)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

        for loc_and_areas in locations_with_areas:

            (location, area_names) = loc_and_areas

            robot.speech.speak("Going to the %s" % location, block=False)

            last_nav_area = None

            for area_name in area_names:

                nav_area = challenge_knowledge.common.get_inspect_position(location, area_name)

                if nav_area != last_nav_area:

                    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
                    # Move to the location

                    location_des = ds.EntityByIdDesignator(robot, id=location)
                    room_des = ds.EntityByIdDesignator(robot, id=challenge_knowledge.common.get_room(location))

                    nwc = NavigateToSymbolic( robot,
                                              {location_des : nav_area, room_des : "in"},
                                              location_des)
                    nwc.execute()

                    last_nav_area = nav_area

                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
                # Look at the area

                look_sm = LookAtArea(robot,
                                     EdEntityDesignator(robot, id=location),
                                     area_name)
                look_sm.execute()

                import time
                time.sleep(1)

                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
                # Segment

                segmented_entities = robot.ed.update_kinect("{} {}".format(area_name, location))

                found_entity_ids = segmented_entities.new_ids + segmented_entities.updated_ids

                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
                # Classify

                entity_types_and_probs = robot.ed.classify(ids=found_entity_ids,
                                                           types=challenge_knowledge.common.objects)

                best_prob = 0
                for det in entity_types_and_probs:
                    if det.type == entity_descr.type and det.probability > best_prob:
                        entity_descr.id = det.id
                        best_prob = det.probability

                if not entity_descr.id:
                    if len(locations_with_areas) == 1 and len(area_names) == 1:
                        robot.speech.speak("Oh no! The {} should be here, but I can't find it.".format(entity_descr.type), block=False)
                        # TODO: get the entity with highest prob!
                    else:
                        robot.speech.speak("Nope, the {} is not here.!".format(entity_descr.type), block=False)
                else:
                        robot.speech.speak("Found the {}!".format(entity_descr.type), block=False)

                if entity_descr.id:
                    break

            if entity_descr.id:
                break

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

        if pick_up and entity_descr.id:

            robot.speech.speak("Going to grab the {}".format(entity_descr.type))

            # grab it
            grab = Grab(robot, EdEntityDesignator(robot, id=entity_descr.id),
                 UnoccupiedArmDesignator(robot.arms, robot.leftArm, name="empty_arm_designator"))
            result = grab.execute()    

    # ------------------------------------------------------------------------------------------------------------------------

    def bring(self, robot, parameters):

        if "entity" in parameters:
            entity_descr = self.resolve_entity_description(parameters["entity"])

            if not self.last_entity or entity_descr.type != self.last_entity.type:
                self.find_and_pick_up(robot, parameters)

        to_descr = self.resolve_entity_description(parameters["to"])

        if to_descr.type == "person":

            if to_descr.id:
                # Move to the location
                nwc = NavigateToObserve(robot,
                             entity_designator=EdEntityDesignator(robot, id=to_descr.id),
                             radius=.5)
            else:
                not_implemented(robot, parameters)
                return

            # TODO: handover

        else:
            # Move to the location
            location_des = ds.EntityByIdDesignator(robot, id=to_descr.id)
            room_des = ds.EntityByIdDesignator(robot, id=challenge_knowledge.common.get_room(to_descr.id))

            nwc = NavigateToSymbolic( robot,
                                      {location_des: 'in_front_of', room_des: "in"},
                                      location_des)
            nwc.execute()

            # place
            arm = OccupiedArmDesignator(robot.arms, robot.leftArm)
            if not arm.resolve():
                robot.speech.speak("I don't have anything to place")
                return

            current_item = EdEntityDesignator(robot)
            place_position = EmptySpotDesignator(robot, location_des, area='on_top_of')
            p = Place(robot, current_item, place_position, arm)
            result = p.execute()

            if result != 'done':
                robot.speech.speak("Sorry, my fault")

        self.last_location = None
        self.last_entity = None

    # ------------------------------------------------------------------------------------------------------------------------

    def find(self, robot, parameters):
        self.find_and_pick_up(robot, parameters, pick_up=False)

    # ------------------------------------------------------------------------------------------------------------------------

    def start_challenge(self, robot):
        s = StartChallengeRobust(robot, starting_point)
        s.execute()

    # ------------------------------------------------------------------------------------------------------------------------

    def execute_command(self, robot, command_recognizer, action_functions, sentence=None):

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # If sentence is given on command-line

        if sentence:
            res = command_recognizer.parse(sentence)
            if not res:
                robot.speech.speak("Sorry, could not parse the given command")
                return False

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # When using text-to-speech

        else:
            import time
            time.sleep(1)
            robot.head.look_at_standing_person()
            robot.head.wait_for_motion_done()

            res = None
            while not res:
                robot.speech.speak("Give your command after the ping", block=False)
                res = command_recognizer.recognize(robot)
                if not res:
                    robot.speech.speak("Sorry, I could not understand", block=True)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - -                    

        (sentence, semantics_str) = res
        print "Sentence: %s" % sentence
        print "Semantics: %s" % semantics_str

        robot.speech.speak("You want me to %s" % sentence.replace(" your", " my").replace(" me", " you"), block=True)

        # TODO: ask for confirmation?

        semantics = yaml.load(semantics_str)

        actions = []
        if "action1" in semantics:
            actions += [semantics["action1"]]
        if "action2" in semantics:
            actions += [semantics["action2"]]
        if "action3" in semantics:
            actions += [semantics["action3"]]

        for a in actions:
            action_type = a["action"]

            if action_type in action_functions:
                action_functions[action_type](robot, a)
            else:
                print "Unknown action type: '%s'" % action_type

    # ------------------------------------------------------------------------------------------------------------------------

    def run(self):
        rospy.init_node("gpsr")

        parser = argparse.ArgumentParser()
        parser.add_argument('robot', help='Robot name')
        parser.add_argument('--forever', action='store_true', help='Turn on infinite loop')
        parser.add_argument('--skip', action='store_true', help='Skip enter/exit')
        parser.add_argument('sentence', nargs='*', help='Optional sentence')
        args = parser.parse_args()
        rospy.loginfo('args: %s', args)

        robot_name = args.robot
        run_forever = args.forever
        skip_init = args.skip
        sentence = " ".join([word for word in args.sentence if word[0] != '_'])

        if robot_name == 'amigo':
            from robot_skills.amigo import Amigo as Robot
        elif robot_name == 'sergio':
            from robot_skills.sergio import Sergio as Robot
        else:
            print "unknown robot"
            return 1

        robot = Robot()

        # wait for door etc.
        if not skip_init:
            self.start_challenge(robot)

        command_recognizer = CommandRecognizer(os.path.dirname(sys.argv[0]) + "/grammar.fcfg", challenge_knowledge)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # # Query world model for entities
        # entities = robot.ed.get_entities(parse=False)
        # for e in entities:
        #     self.entity_ids += [e.id]

        #     for t in e.types:
        #         if not t in self.entity_type_to_id:
        #             self.entity_type_to_id[t] = [e.id]
        #         else:
        #             self.entity_type_to_id[t] += [e.id]


        # for (furniture, objects) in challenge_knowledge.furniture_to_objects.iteritems():
        #     for obj in objects:
        #         self.object_to_location[obj] = furniture

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        action_functions = {}
        action_functions["navigate"] = self.navigate
        action_functions["find"] = self.find
        action_functions["answer-question"] = self.answer_question
        action_functions["pick-up"] = self.find_and_pick_up
        action_functions["bring"] = self.bring
        action_functions["say"] =  self.say

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        done = False
        while not done:
            self.execute_command(robot, command_recognizer, action_functions, sentence)
            if not run_forever:
                done = True

# ------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    gpsr = GPSR()
    sys.exit(gpsr.run())
