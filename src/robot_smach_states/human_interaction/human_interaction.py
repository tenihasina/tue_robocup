#! /usr/bin/env python
import roslib;
import rospy
import smach
import random
import ed_perception.msg
import actionlib
from robot_smach_states.state import State

import robot_smach_states.util.designators as ds
from robot_smach_states.utility import WaitForDesignator
import robot_skills.util.msg_constructors as gm
from smach_ros import SimpleActionState
from ed_perception.msg import FaceLearningGoal, FaceLearningResult #
from dragonfly_speech_recognition.srv import GetSpeechResponse
import time

# Say: Immediate say
# Hear: Immediate hear
# Ask: Interaction, say + hear

##########################################################################################################################################

class Say(smach.State):
    """Say a sentence or pick a random one from a list.

    >>> from mock import MagicMock
    >>> robot = MagicMock()
    >>> robot.speech = MagicMock()
    >>> robot.speech.speak = MagicMock()
    >>>
    >>> sf = Say(robot, ["a", "b", "c"])
    >>> #Repeat command 50 times, every time it should succeed and return "spoken"
    >>> outcomes = [sf.execute() for i in range(50)]
    >>> assert all(outcome == "spoken" for outcome in outcomes)
    >>>
    >>> #After many calls, all options in the list will very likely have been called at least one.
    >>> #robot.speech.speak.assert_any_call('a', 'us', 'kyle', 'default', 'excited', True)
    >>> #robot.speech.speak.assert_any_call('b', 'us', 'kyle', 'default', 'excited', True)
    >>> #robot.speech.speak.assert_any_call('c', 'us', 'kyle', 'default', 'excited', True)"""
    def __init__(self, robot, sentence=None, language=None, personality=None, voice=None, mood=None, block=True):
        smach.State.__init__(self, outcomes=["spoken"])
        ds.check_type(sentence, str, list)
        #ds.check_type(language, str)
        #ds.check_type(personality, str)
        #ds.check_type(voice, str)
        #ds.check_type(mood, str)
        ds.check_type(block, bool)

        self.robot = robot
        self.sentence = sentence
        self.language = language
        self.personality = personality
        self.voice = voice
        self.mood = mood
        self.block = block

    def execute(self, userdata=None):
        #robot.head.look_at_standing_person()

        if not self.sentence:
            rospy.logerr("sentence = None, not saying anything...")
            return "spoken"

        if not isinstance(self.sentence, str) and isinstance(self.sentence, list):
            self.sentence = random.choice(self.sentence)

        sentence = str(self.sentence.resolve() if hasattr(self.sentence, "resolve") else self.sentence)

        self.robot.speech.speak(sentence, self.language, self.personality, self.voice, self.mood, self.block)

        #robot.head.cancel_goal()

        return "spoken"

##########################################################################################################################################

class Hear(smach.State):
    def __init__(self, robot, spec, time_out = rospy.Duration(10), look_at_standing_person=True):
        smach.State.__init__(self, outcomes=["heard", "not_heard"])
        self.robot = robot
        self.spec = spec
        self.time_out = time_out
        self.look_at_standing_person = look_at_standing_person

    def execute(self, userdata=None):
        if self.look_at_standing_person:
            self.robot.head.look_at_standing_person()

        answer = self.robot.ears.recognize(self.spec, {}, self.time_out)

        if self.look_at_standing_person:
            self.robot.head.cancel_goal()

        if answer:
            if answer.result:
                return "heard"
        else:
            self.robot.speech.speak("Something is wrong with my ears, please take a look!")

        return "not_heard"

class HearOptions(smach.State):
    def __init__(self, robot, options, timeout = rospy.Duration(10), look_at_standing_person=True):
        outcomes = options
        outcomes.append("no_result")
        smach.State.__init__(self, outcomes=outcomes)
        self._options = options
        self._robot = robot
        self._timeout = timeout
        self.look_at_standing_person = look_at_standing_person

    def execute(self, userdata):
        if self.look_at_standing_person:
            self._robot.head.look_at_standing_person()

        answer = self._robot.ears.recognize("<option>", {"option":self._options}, self._timeout)

        if self.look_at_standing_person:
            self._robot.head.cancel_goal()

        if answer:
            if answer.result:
                if "option" in answer.choices:
                    return answer.choices["option"]
        else:
            self._robot.speech.speak("Something is wrong with my ears, please take a look!")

        return "no_result"

class HearOptionsExtra(smach.State):
    """Listen to what the user said, based on a pre-constructed sentence

    Keyword arguments:
    spec_designator -- sentence that is supposed to be heard
    choices_designator -- list of choices for words in the sentence
    speech_result_designator -- variable where the result is stored
    time_out -- timeout in case nothing is heard

    Example of usage:
        from dragonfly_speech_recognition.srv import GetSpeechResponse
        spec = ds.Designator("((<prefix> <name>)|<name>)")
        choices = ds.Designator({"name"  : names_list,
                              "prefix": ["My name is", "I'm called"]})
        answer = ds.VariableDesignator(resolve_type = GetSpeechResponse)
        state = HearOptionsExtra(self.robot, spec, choices, answer.writeable)
        outcome = state.execute()

        if outcome == "heard":
            name = answer.resolve().choices["name"]

    >>> from robot_skills.mockbot import Mockbot
    >>> mockbot = Mockbot()
    >>> import robot_smach_states.util.designators as ds
    >>> spec = ds.Designator("I will go to the <table> in the <room>")
    >>> choices = ds.Designator({  "room"  : ["livingroom", "bedroom", "kitchen" ], "table" : ["dinner table", "couch table", "desk"]})
    >>> answer = ds.VariableDesignator(resolve_type=GetSpeechResponse)
    >>> state = HearOptionsExtra(mockbot, spec, choices, answer.writeable)
    >>> outcome = state.execute()
    """
    def __init__(self, robot, spec_designator,
                        choices_designator,
                        speech_result_designator,
                        time_out=rospy.Duration(10),
                        look_at_standing_person=True):
        smach.State.__init__(self, outcomes=["heard", "no_result"])

        self.robot = robot

        ds.check_resolve_type(spec_designator, str)
        ds.check_resolve_type(choices_designator, dict)
        ds.check_resolve_type(speech_result_designator, GetSpeechResponse)
        ds.is_writeable(speech_result_designator)

        self.spec_designator = spec_designator
        self.choices_designator = choices_designator
        self.speech_result_designator = speech_result_designator
        self.time_out = time_out
        self.look_at_standing_person = look_at_standing_person

    def execute(self, userdata=None):
        spec = self.spec_designator.resolve()
        choices = self.choices_designator.resolve()

        if not spec:
            rospy.logerr("Could not resolve spec")
            return "no_result"
        if not choices:
            rospy.logerr("Could not resolve choices")
            return "no_result"

        if self.look_at_standing_person:
            self.robot.head.look_at_standing_person()

        answer = self.robot.ears.recognize(spec, choices, self.time_out)

        if self.look_at_standing_person:
            self.robot.head.cancel_goal()

        if answer:
            if answer.result:
                self.speech_result_designator.write(answer)
                return "heard"
        else:
            self.robot.speech.speak("Something is wrong with my ears, please take a look!")

        return "no_result"


##########################################################################################################################################


class HearYesNo(smach.State):
    def __init__(self, robot):
        smach.State.__init__(   self,
                                outcomes=['heard_yes', 'heard_no', 'heard_failed'])

        self.robot = robot

    def execute(self, userdata):
        # define answer format
        spec = ds.Designator("(<positive_answer>|<negative_answer>)")

        # define choices
        choices = ds.Designator({  "positive_answer": ["Yes", "Correct", "Right", "Yup"],
                                "negative_answer": ["No", "Incorrect", "Wrong", "Nope"]})

        answer = ds.VariableDesignator(resolve_type=GetSpeechResponse)

        state = HearOptionsExtra(self.robot, spec, choices, answer.writeable)

        # execute listen
        outcome = state.execute()

        if not outcome == "heard":
            # if there was no answer
            print "HearYesNo: did not hear anything!"
            return 'heard_failed'
        else:
            response_negative = ""
            response_positive = ""

            # test if the answer was positive, if its empty it will return excepton and continue to negative answer
            try:
                response_positive = answer.resolve().choices["positive_answer"]

                print "HearYesNo: answer is positive, heard: '" + response_positive + "'"
                return 'heard_yes'
            except KeyError, ke:
                print "KeyError resolving the answer heard: " + str(ke)
                pass

            try:
                response_negative = answer.resolve().choices["negative_answer"]

                print "HearYesNo: answer is negative, heard: '" + response_negative + "'"
                return 'heard_no'
            except KeyError, ke:
                print "KeyError resolving the answer heard: " + str(ke)
                pass

        print "HearYesNo: could not resolve answer!"

        return 'heard_failed'


##########################################################################################################################################


class AskContinue(smach.StateMachine):
    def __init__(self, robot, timeout=rospy.Duration(10)):
        smach.StateMachine.__init__(self, outcomes=['continue','no_response'])
        self.robot = robot
        self.timeout = timeout

        with self:
            smach.StateMachine.add('SAY',
                                    Say(self.robot,
                                        random.choice([ "I will continue my task if you say continue.",
                                                        "Please say continue so that I can continue my task.",
                                                        "I will wait until you say continue."])),
                                    transitions={'spoken':'HEAR'})

            smach.StateMachine.add('HEAR',
                                    Hear(self.robot, 'continue', self.timeout),
                                    transitions={   'heard':'continue',
                                                    'not_heard':'no_response'})

##########################################################################################################################################


class WaitForPersonInFront(WaitForDesignator):
    """
    Waits for a person to be found in fron of the robot. Attempts to wait a number of times with a sleep interval
    """

    def __init__(self, robot, attempts = 1, sleep_interval = 1):
        # TODO: add center_point in front of the robot and radius of the search on ds.EdEntityDesignator
        # human_entity = ds.EdEntityDesignator(robot, center_point=gm.PointStamped(x=1.0, frame_id="base_link"), radius=1, id="human")
        human_entity = ds.EdEntityDesignator(robot, type="human")
        ds.WaitForDesignator.__init__(self, robot, human_entity, attempts, sleep_interval)


##########################################################################################################################################


class LearnPerson(smach.State):
    """
        
    """
    def __init__(self, robot, person_name = "", name_designator = None, n_samples = 10):
        smach.State.__init__(self, outcomes=['succeeded_learning', 'failed_learning', 'timeout_learning'])
        
        self.robot = robot
        self.person_name = person_name
        if name_designator:
            ds.check_resolve_type(name_designator, str)
        self.name_designator = name_designator
        self.n_samples = n_samples

    def execute(self, userdata=None):

        # if person_name is empty then try to get it from designator
        if not self.person_name:
            person_name = self.name_designator.resolve()

            # if there is still no name, quit the learning
            if not person_name:
                print ("[LearnPerson] " + "No name was provided. Quitting the learning!")
                return

        samples_completed = learn_person_procedure(self.robot, person_name = person_name, n_samples = self.n_samples)

        if samples_completed == 0:
            return 'failed_learning'
        if samples_completed < self.n_samples:
            return 'timeout_learning'
        else:
            return 'succeeded_learning'


##########################################################################################################################################


class LookAtPersonInFront(smach.State):
    """
        Look at the face of the person in front of the Robot. If no person is found just look forward.
        Robot will look front and search for a face. Using the lookDown argument you can also 
            look down, to search for example of shorter or sitting down people
    """
    def __init__(self, robot, lookDown = False):
        smach.State.__init__(self, outcomes=['succeeded', 'failed'])
        self.robot = robot
        self.lookDown = lookDown

    def execute(self, userdata=None):

        # initialize variables
        foundFace = False
        result = None
        entityData = None
        faces_front = None
        desgnResult = None

        self.robot.head.cancel_goal()

        # look front, 2 meters high
        self.robot.head.look_at_point(point_stamped=gm.PointStamped(3, 0, 1.5,self.robot.robot_name+"/base_link"), end_time=0, timeout=4)
        rospy.sleep(1)  # give time for the percetion algorithms to add the entity

        desgnResult = scanForHuman(self.robot)
        if not desgnResult:
            print "[LookAtPersonInFront] " + "Could not find a human while looking up"

        # if no person was seen at 2 meters high, look down, because the person might be sitting
        if not desgnResult and self.lookDown == True:
            # look front, 2 meters high
            self.robot.head.look_at_point(point_stamped=gm.PointStamped(3, 0, 0,self.robot.robot_name+"/base_link"), end_time=0, timeout=4)

            # try to resolve the designator
            desgnResult = scanForHuman(self.robot)
            if not desgnResult:
                print "[LookAtPersonInFront] " + "Could not find a human while looking down"
                pass

        # if there is a person in front, try to look at the face
        if desgnResult:
            print "[LookAtPersonInFront] " + "Designator resolved a Human!"

            # extract information from data
            faces_front = None
            try:
                #import ipdb; ipdb.set_trace()
                # get information on the first face found (cant guarantee its the closest in case there are many)
                faces_front = desgnResult[0].data["perception_result"]["face_detector"]["faces_front"][0]
            except KeyError, ke:
                print "[LookAtPersonInFront] " + "KeyError faces_front: " + str(ke)
                pass
            except IndexError, ke:
                print "[LookAtPersonInFront] " + "IndexError faces_front: " + str(ke)
                pass
            except TypeError, ke:
                print "[LookAtPersonInFront] " + "TypeError faces_front: " + str(ke)
                pass
            except AttributeError, ke:
                print "[LookAtPersonInFront]     " + "AttributeError faces_front: " + str(ke)
                pass

            if faces_front:
                headGoal = gm.PointStamped(x=faces_front["map_x"], y=faces_front["map_y"], z=faces_front["map_z"], frame_id="/map")

                print "[LookAtPersonInFront] " + "Sending head goal to (" + str(headGoal.point.x) + ", " + str(headGoal.point.y) + ", " + str(headGoal.point.z) + ")"
                self.robot.head.look_at_point(point_stamped=headGoal, end_time=0, timeout=4)

                foundFace == True            
            else:
                print "[LookAtPersonInFront] " + "Found a human but no faces."
                foundFace == False 

        if foundFace == True:
            return 'succeeded'
        else:
            print "[LookAtPersonInFront] " + "Could not find a face in front of the robot"
            return 'failed'


##########################################################################################################################################


class WaitForPersonEntity(smach.State):
    """
        Wait until a person is seen/scanned in front of the robot.
            Use paramaterers to costumize number of retries and sleep between retries
    """
    def __init__(self, robot, attempts = 1, sleep_interval = 1):
        smach.State.__init__(self, outcomes=['succeeded', 'failed'])
        self.robot = robot
        self.attempts = attempts
        self.sleep_interval = sleep_interval

    def execute(self, userdata=None):
        counter = 0
        desgnResult = None

        while counter < self.attempts:
            print "WaitForPerson: waiting {0}/{1}".format(counter, self.attempts)

            desgnResult = scanForHuman(self.robot)
            if desgnResult:
                print "[WaitForPerson] " + "Found a human!"
                return 'succeeded'

            counter += 1
            rospy.sleep(self.sleep_interval)

        return 'failed'

class WaitForPersonDetection(smach.State):
    """
        Wait until a person is seen/scanned in front of the robot.
            Use paramaterers to costumize number of retries and sleep between retries
    """
    def __init__(self, robot, attempts = 1, sleep_interval = 1):
        smach.State.__init__(self, outcomes=['succeeded', 'failed'])
        self.robot = robot
        self.attempts = attempts
        self.sleep_interval = sleep_interval

    def execute(self, userdata=None):
        counter = 0
        desgnResult = None

        while counter < self.attempts:
            print "WaitForPerson: waiting {0}/{1}".format(counter, self.attempts)

            detections = self.robot.ed.detect_persons()
            if detections:
                print "[WaitForPersonDetection] " + "Found a human!"
                return 'succeeded'

            counter += 1
            rospy.sleep(self.sleep_interval)

        return 'failed'

##########################################################################################################################################


def scanForHuman(robot, background_padding = 0.3):
    """
        Scan for a human in the robots field of view. Return human entities
    """

    human_entities = []
    entity_list = []

    res_segm = robot.ed.update_kinect(background_padding = background_padding)
    entity_list = res_segm.new_ids + res_segm.updated_ids

    # Try to determine the types of the entities just segmented
    res_classify = robot.ed.classify(entity_list)

    # Get the ids of all humans
    human_entities = [e for e in res_classify if e.type == "human"]

    print "[scanForHuman] " + "Found {0} person(s) ({1} entities)".format(len(human_entities), len(entity_list))

    return human_entities


##########################################################################################################################################


def learn_person_procedure(robot, person_name = "", n_samples = 10, timeout = 5.0):
    """
    Starts the learning process that will save n_samples of the closest person's face.
    It ends when the number of snapshots is reached or when a timeout occurs

    Returns: number of samples saved. If smaller than what was requested, then a timeout occured
    """

    # if there is no name, quit the learning
    if not person_name:
        rospy.logwarn("No name was provided. Quitting the learning!")
        return

    count = 0
    timedout = False
    start_time = time.time()
    while (count < n_samples):

        if robot.ed.learn_person(person_name):
            # reset timer
            start_time = time.time()
           
            count = count + 1

            if count == n_samples/2:
                robot.speech.speak("Almost done, keep looking.", block=False)
        else:
            print ("[LearnPersonProcedure] " + "No person found.")
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                print ("[LearnPersonProcedure] " + "Learn procedure timed out!")
                return count            

        print ("[LearnPersonProcedure] " + "Completed {0}/{1}".format(count, n_samples))

    print ("[LearnPersonProcedure] " + "Learn procedure completed!")

    # print robot.ed.classify_person(human_id)
    return count


##########################################################################################################################################

if __name__ == "__main__":
    import doctest
    doctest.testmod()
