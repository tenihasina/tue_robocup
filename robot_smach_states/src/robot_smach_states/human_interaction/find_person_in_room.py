#! /usr/bin/env python

# System
import math

import geometry_msgs
# ROS
import PyKDL as kdl
import rospy
import smach
import robot_smach_states as states
import robot_smach_states.util.designators as ds
from robot_skills.util import kdl_conversions
from robocup_knowledge import load_knowledge
import sys
from robot_smach_states.util.startup import startup

challenge_knowledge = load_knowledge('challenge_help_me_carry')

##########################################################################################################################################
class Person(object):
    """
    :param person.name: available learned persons. Supported are: Janno, Rein, Ramon, Rokus, Henk, Max,
    Loy, Matthijs, Kevin, Josja, Lars, Ainse.
    """
class LearnOperator(smach.State):
    def __init__(self, robot, operator_timeout=20, ask_follow=True, learn_face=True, learn_person_timeout = 10.0):
        smach.State.__init__(self, outcomes=['follow', 'Failed', 'Aborted'],
                             input_keys=['operator_learn_in'],
                             output_keys=['operator_learn_out'])
        self._robot = robot
        self._operator_timeout = operator_timeout
        self._ask_follow = ask_follow
        self._learn_face = learn_face
        self._learn_person_timeout = learn_person_timeout
        self._operator_name = "Loy"

    def execute(self, userdata):
        start_time = rospy.Time.now()
        self._robot.head.look_at_standing_person()
        operator = userdata.operator_learn_in

        while not operator:
            r = rospy.Rate(1.0)
            if self.preempt_requested():
                return 'Failed'

            if(rospy.Time.now() - start_time).to_sec() > self._operator_timeout:
                return 'Failed'

            operator = self._robot.ed.get_closest_laser_entity(
                radius=0.5,
                center_point=kdl_conversions.VectorStamped(x=1.0, y=0, z=1,
                                                           frame_id="/%s/base_link" % self._robot.robot_name))
            rospy.loginfo("Operator: {op}".format(op=operator))
            if not operator:
                self._robot.speech.speak("Please stand in front of me")
            else:
                if self._learn_face:
                    self._robot.speech.speak("Please look at me while I learn to recognize you.",
                                             block=True)
                    self._robot.head.look_at_standing_person()
                    learn_person_start_time = rospy.Time.now()
                    num_detections = 0
                    while num_detections < 5: # 5:
                        if self._robot.perception.learn_person(self._operator_name):
                            print("Succesfully detected you %i times" % (num_detections + 1))
                            num_detections += 1
                        elif (rospy.Time.now() - learn_person_start_time).to_sec() > self._learn_person_timeout:
                            self._robot.speech.speak("Please stand in front of me and look at me")
                            operator = None
                            break
            r.sleep()
        print "We have a new operator: %s" % operator.id
        self._robot.speech.speak("Gotcha! I will follow you!", block=False)
        self._robot.head.close()
        userdata.operator_learn_out = operator
        return 'follow'

#########################################################################################################################

class FindPerson(smach.State):
    def __init__(self, robot, person_label='operator', lost_timeout=60, look_distance=2.0, probability_threshold=1.5):

        smach.State.__init__(self, outcomes=['found', 'failed'])

        self._robot = robot
        self.person_label = person_label
        self._lost_timeout = lost_timeout
        self._look_distance = look_distance
        self._face_pos_pub = rospy.Publisher(
            '/%s/find_person/person_detected_face' % robot.robot_name,
            geometry_msgs.msg.PointStamped, queue_size=10)
        self._probability_threshold = probability_threshold

    def execute(self, userdata=None):
        # person = loadPerson(person_label=self.person_label)
        rospy.loginfo("Trying to find {}".format(self.person_label)) #person.name))
        self._robot.head.look_at_standing_person()
        self._robot.speech.speak("{}, please look at me while I am looking for you".format(self.person_label), # person.name),
                                 block=False)
        start_time = rospy.Time.now()

        look_distance = 2.0  # magic number 4
        look_angles = [0.0,  # magic numbers
                       math.pi / 6,
                       math.pi / 4,
                       math.pi / 2.3,
                       0.0,
                       -math.pi / 6,
                       -math.pi / 4,
                       -math.pi / 2.3]
        head_goals = [kdl_conversions.VectorStamped(x=look_distance * math.cos(angle),
                                                    y=look_distance * math.sin(angle), z=1.7,
                                                    frame_id="/%s/base_link" % self._robot.robot_name)
                      for angle in look_angles]

        i = 0
        while (rospy.Time.now() - start_time).to_sec() < self._lost_timeout:
            if self.preempt_requested():
                return 'failed'

            self._robot.head.look_at_point(head_goals[i])
            i += 1
            if i == len(head_goals):
                i = 0
            self._robot.head.wait_for_motion_done()
            raw_detections = self._robot.perception.detect_faces()
            best_detection = self._robot.perception.get_best_face_recognition(
                raw_detections, self.person_label, probability_threshold=self._probability_threshold)

            rospy.loginfo("best_detection = {}".format(best_detection))
            if not best_detection:
                continue
            roi = best_detection.roi
            try:
                person_pos_kdl = self._robot.perception.project_roi(roi=roi, frame_id="map")
            except Exception as e:
                rospy.logerr("head.project_roi failed: %s", e)
                return 'failed'
            person_pos_ros = kdl_conversions.kdl_vector_stamped_to_point_stamped(person_pos_kdl)
            self._face_pos_pub.publish(person_pos_ros)

            found_person = self._robot.ed.get_closest_laser_entity(radius=self._look_distance,
                                                                   center_point=person_pos_kdl)
            if found_person:
                self._robot.speech.speak("I found {}".format(self.person_label), block=False, mood="excited")
                self._robot.head.close()

                self._robot.ed.update_entity(
                    id=self.person_label,
                    frame_stamped=kdl_conversions.FrameStamped(kdl.Frame(person_pos_kdl.vector), "/map"),
                    type="waypoint")

                return 'found'
            else:
                print "Could not find {} in the {}".format(self.person_label, self.area)

        self._robot.head.close()
        rospy.sleep(2.0)
        return 'failed'


class _DecideNavigateState(smach.State):
    """ Helper state to decide whether to use a NavigateToWaypoint or a NavigateToRoom state
    """
    def __init__(self, robot, waypoint_designator, room_designator):
        """ Initialize method

        :param robot: Robot API object
        :param waypoint_designator: EdEntityDesignator that should resolve to a waypoint
        :param room_designator: EdEntityDesignator that should resolve to the room in which the waypoint is located
        """
        smach.State.__init__(self, outcomes=["waypoint", "room", "none"])
        self._robot = robot
        self._waypoint_designator = waypoint_designator
        self._room_designator = room_designator

    def execute(self, ud):

        # First: see if the waypoint exists
        entity = self._waypoint_designator.resolve()
        if entity:
            return "waypoint"

        # If not: try the room
        entity = self._room_designator.resolve()
        if entity:
            return "room"

        return "none"


class FindPersoninRoom(smach.StateMachine):
    """ Uses NavigateToWaypoint or NavigateToRoom and subsequently tries to find a person
    in that room.

    """

    def __init__(self, robot, area, name):
        """ Constructor
        :param robot: robot object
        :param area: (str) if a waypoint "<area>_waypoint" is present in the world model, the robot will navigate
        to this waypoint. Else, it will navigate to the room called "<area>"
        :param name: (str) Name of the person to look for
        """
        smach.StateMachine.__init__(self, outcomes=["found", "not_found"])

        waypoint_designator = ds.EntityByIdDesignator(robot=robot, id=area + "_waypoint")
        room_designator = ds.EntityByIdDesignator(robot=robot, id=area)

        with self:
            smach.StateMachine.add("DECIDE_NAVIGATE_STATE",
                                   _DecideNavigateState(robot=robot, waypoint_designator=waypoint_designator,
                                                        room_designator=room_designator),
                                   transitions={"waypoint": "NAVIGATE_TO_WAYPOINT",
                                                "room": "NAVIGATE_TO_ROOM",
                                                "none": "not_found"})

            smach.StateMachine.add("NAVIGATE_TO_WAYPOINT",
                                   states.NavigateToWaypoint(robot=robot,
                                                             waypoint_designator=waypoint_designator, radius=0.15),
                                   transitions={"arrived": "FIND_PERSON",
                                                "unreachable": "not_found",
                                                "goal_not_defined": "not_found"})

            smach.StateMachine.add("NAVIGATE_TO_ROOM", states.NavigateToRoom(robot=robot,
                                                                             entity_designator_room=room_designator),
                                   transitions={"arrived": "FIND_PERSON",
                                                "unreachable": "not_found",
                                                "goal_not_defined": "not_found"})

            # Wait for the operator to appear and detect what he's pointing at
            smach.StateMachine.add("FIND_PERSON", FindPerson(robot=robot, person_label=name),
                                   transitions={"found": "found",
                                                "failed": "not_found"})


if __name__ == "__main__":
    if len(sys.argv) > 1:
        robot_name = sys.argv[1]
        area = sys.argv[2]
        name = sys.argv[3]
    else:
        print "Please provide robot name as argument."
        exit(1)

    if robot_name == "amigo":
        from robot_skills.amigo import Amigo as Robot
    elif robot_name == "sergio":
        from robot_skills.sergio import Sergio as Robot

    rospy.init_node('test_follow_operator')
    robot = Robot()
    sm = FindPersoninRoom(robot, area, name)
    sm.execute()
