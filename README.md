[![Build Status](https://travis-ci.org/tue-robotics/robot_smach_states.svg?branch=master)](https://travis-ci.org/tue-robotics/robot_smach_states)

robot_smach_states
==================

Robot_smach_states is a library of, indeed, smach states and state machine, built using the SMACH state machine library from ROS.

There are states concerning navigation, perception, world modeling/reasoning, complex and simple arm movements, speech recognition, and some more.
Each state is passed an instance of the Robot-class from the tue-robotics/robot_skills-package.
The actions called via the robot_smach_states are implemented and executed via such a Robot-object. 

![Alt text](http://g.gravizo.com/g?
@startuml
class robot_skills.Robot
class robot_skills.Arm
class robot_skills.Amigo --|> robot_skills.Robot
class robot_skills.Sergio --|> robot_skills.Robot
robot_skills.Robot *-- robot_skills.Arm
class smach.State
class robot_smach_states.State --|> smach.State
class robot_smach_states.Grab --|> robot_smach_states.State
class robot_smach_states.Place --|> robot_smach_states.State
class robot_smach_states.NavigateToObserve --|> robot_smach_states.State
class robot_smach_states.designators.Designator {
    +resolve() : T
}
class robot_smach_states.designators.EdEntityDesignator {
    +resolve() : Entity
}
class robot_smach_states.designators.ArmDesignator {
    +resolve() : robot_skills.Arm
}
robot_smach_states.designators.EdEntityDesignator --|> robot_smach_states.designators.Designator
robot_smach_states.designators.ArmDesignator --|> robot_smach_states.designators.Designator
class tue_robocup.challenge_manipulation.Manipulation *-- robot_smach_states.Grab
class tue_robocup.challenge_manipulation.Manipulation *-- robot_smach_states.Place
class tue_robocup.challenge_manipulation.Manipulation *-- robot_smach_states.NavigateToObserve
class tue_robocup.challenge_manipulation.Restaurant *-- robot_smach_states.Grab
class tue_robocup.challenge_manipulation.Restaurant *-- robot_smach_states.Place
class tue_robocup.challenge_manipulation.Restaurant *-- robot_smach_states.NavigateToObserve
robot_smach_states.Grab *-- robot_skills.Robot : execute_with
robot_smach_states.Grab *-- class robot_smach_states.designators.EdEntityDesignator : item_to_grab
robot_smach_states.Grab *-- robot_smach_states.designators.ArmDesignator : arm_to_grab_with
robot_smach_states.designators.ArmDesignator ..> robot_skills.Arm : returns
@enduml