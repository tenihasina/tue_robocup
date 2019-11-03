import unittest
import mock

# Robot Skills
from robot_skills.mockbot import Mockbot
from robot_skills.util.entity import Entity

# Robot Smach States
import robot_smach_states as states
from robot_smach_states.util import designators as ds


class TestHandOverToHuman(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.robot = Mockbot()

    def setUp(self):
        entity = Entity("12345", "dummy", "/map", None, None, {}, None, 0)
        self.robot.arms["leftArm"].occupied_by = entity
        self.arm_ds = ds.OccupiedArmDesignator(self.robot, {"required_goals": ['handover_to_human', 'reset']})

    def test_handover_to_human(self):
        state = states.HandoverToHuman(self.robot, self.arm_ds)
        state.check_consistency()
        self.assertEqual(state.execute(), "succeeded")

        self.robot.arms["rightArm"].send_joint_goal.assert_not_called()
        self.robot.arms["rightArm"].send_gripper_goal.assert_not_called()

        self.robot.arms["leftArm"].send_joint_goal.assert_any_call('handover_to_human', max_joint_vel=mock.ANY, timeout=mock.ANY)
        self.robot.arms["leftArm"].send_joint_goal.assert_any_call('reset', max_joint_vel=mock.ANY, timeout=mock.ANY)

        self.robot.arms["leftArm"].send_gripper_goal.assert_any_call('open', mock.ANY, max_torque=mock.ANY)
        self.assertIsNone(self.robot.arms["leftArm"].occupied_by)


class TestOpenGripper(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.robot = Mockbot()

    def setUp(self):
        self.arm_ds = ds.ArmDesignator(self.robot, {'required_arm_name': 'leftArm'})

    def test_set_open(self):
        state = states.SetGripper(self.robot, self.arm_ds, 'open')
        self.assertEqual(state.execute(), "succeeded")
        self.robot.arms["leftArm"].send_gripper_goal.assert_called_once_with('open', mock.ANY, max_torque=mock.ANY)


class TestCloseGripper(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.robot = Mockbot()

    def setUp(self):
        self.arm_ds = ds.ArmDesignator(self.robot, {'required_arm_name': 'leftArm'})
        self.entity = Entity("12345", "dummy", "/map", None, None, {}, None, 0)
        self.entity_ds = ds.VariableDesignator(self.entity)

    def test_set_close(self):
        state = states.SetGripper(self.robot, self.arm_ds, 'close', self.entity_ds)
        self.assertEqual(state.execute(), "succeeded")
        self.robot.arms["leftArm"].send_gripper_goal.assert_called_once_with('close', mock.ANY, max_torque=mock.ANY)
        self.assertEqual(self.robot.arms["leftArm"].occupied_by, self.entity)


class TestSetGripperFail(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.robot = Mockbot()

    def setUp(self):
        self.arm_ds = ds.ArmDesignator(self.robot, {'required_arm_name': 'leftArm'})

    def test_invalid_arm_designator(self):
        invalid_arm_ds = ds.ArmDesignator(self.robot, {'required_arm_name': 'there_is_no_arm_with_this_name'})
        state = states.SetGripper(self.robot, invalid_arm_ds, 'close')
        self.assertEqual(state.execute(), "failed")


if __name__ == '__main__':
    unittest.main()
