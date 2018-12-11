# ROS
import PyKDL as kdl
from kdl_conversions import point_msg_to_kdl_vector


class Volume(object):
    """ Represents an area of an entity

    Points are defined relative to the object they belong to
    """

    def __init__(self):
        """ Constructor

        """
        pass

    @property
    def center_point(self):
        """Get the center of the Volume"""
        return self._calc_center_point()

    def _calc_center_point(self):
        raise NotImplementedError("_calc_center_point must be implemented by subclasses")

    def contains(self, point):
        """ Checks if the point is inside this volume
        :param point: kdl Vector w.r.t. the same frame as this volume
        :return: True if inside, False otherwise
        """
        raise NotImplementedError("contains must be implemented by subclasses")


class BoxVolume(Volume):
    """ Represents a box shaped volume """

    def __init__(self, min_corner, max_corner):
        """ Constructor.

        Points are defined relative to the object they belong to

        :param min_corner: PyKDL.Vector with the minimum bounding box corner
        :param max_corner: PyKDL.Vector with the minimum bounding box corner
        """
        super(BoxVolume, self).__init__()

        assert isinstance(min_corner, kdl.Vector)
        assert isinstance(max_corner, kdl.Vector)

        self._min_corner = min_corner
        self._max_corner = max_corner

    def _calc_center_point(self):
        """Calculate where the center of the box is located
        >>> b = BoxVolume(kdl.Vector(0,0,0), kdl.Vector(1,1,1))
        >>> b.center_point
        [         0.5,         0.5,         0.5]
        """
        return kdl.Vector(0.5 * (self._min_corner.x() + self._max_corner.x()),
                          0.5 * (self._min_corner.y() + self._max_corner.y()),
                          0.5 * (self._min_corner.z() + self._max_corner.z()))

    @property
    def min_corner(self):
        return self._min_corner

    @property
    def max_corner(self):
        return self._max_corner

    @property
    def bottom_area(self):
        convex_hull = []
        convex_hull.append(kdl.Vector(self.min_corner.x(), self.min_corner.y(), self.min_corner.z()))  # 1
        convex_hull.append(kdl.Vector(self.max_corner.x(), self.min_corner.y(), self.min_corner.z()))  # 2
        convex_hull.append(kdl.Vector(self.max_corner.x(), self.max_corner.y(), self.min_corner.z()))  # 3
        convex_hull.append(kdl.Vector(self.min_corner.x(), self.max_corner.y(), self.min_corner.z()))  # 4
        return convex_hull

    def contains(self, point):
        """ Checks if the point is inside this volume
        :param point: kdl Vector w.r.t. the same frame as this volume
        :return: True if inside, False otherwise
        """
        return self._min_corner.x() < point.x() < self._max_corner.x() and \
               self._min_corner.y() < point.y() < self._max_corner.y() and \
               self._min_corner.z() < point.z() < self._max_corner.z()

    def __repr__(self):
        return "BoxVolume(min_corner={}, max_corner={})".format(self.min_corner, self.max_corner)


class CompositeBoxVolume(Volume):
    """ Represents a composite box shaped volume """
    def __init__(self, min_corners, max_corners):
        """
        Constructor

        Points are defined relative to the object they belong to

        :param min_corners: list of PyKDL.Vector with the minimum bounding box corners
        :param max_corners: list of PyKDL.Vector with the maximum bounding box corners
        """
        super(CompositeBoxVolume, self).__init__()

        assert isinstance(min_corners, list)
        assert isinstance(max_corners, list)
        assert len(min_corners) == len(max_corners)

        self._min_corners = min_corners
        self._max_corners = max_corners

    def _calc_center_point(self):
        """Calculate where the center of the box is located
        >>> b = CompositeBoxVolume([kdl.Vector(0,0,0)], [kdl.Vector(1,1,1)])
        >>> b.center_point
        [         0.5,         0.5,         0.5]
        """
        min_x = min([v.x() for v in self._min_corners])
        min_y = min([v.y() for v in self._min_corners])
        min_z = min([v.z() for v in self._min_corners])
        max_x = max([v.x() for v in self._max_corners])
        max_y = max([v.y() for v in self._max_corners])
        max_z = max([v.z() for v in self._max_corners])
        return kdl.Vector(0.5 * (min_x + max_x),
                          0.5 * (min_y + max_y),
                          0.5 * (min_z + max_z))

    @property
    def min_corner(self):
        min_x = min([v.x() for v in self._min_corners])
        min_y = min([v.y() for v in self._min_corners])
        min_z = min([v.z() for v in self._min_corners])
        return kdl.Vector(min_x, min_y, min_z)

    @property
    def max_corner(self):
        max_x = max([v.x() for v in self._max_corners])
        max_y = max([v.y() for v in self._max_corners])
        max_z = max([v.z() for v in self._max_corners])
        return kdl.Vector(max_x, max_y, max_z)

    @property
    def bottom_area(self):
        convex_hull = []
        convex_hull.append(kdl.Vector(self.min_corner.x(), self.min_corner.y(), self.min_corner.z()))  # 1
        convex_hull.append(kdl.Vector(self.max_corner.x(), self.min_corner.y(), self.min_corner.z()))  # 2
        convex_hull.append(kdl.Vector(self.max_corner.x(), self.max_corner.y(), self.min_corner.z()))  # 3
        convex_hull.append(kdl.Vector(self.min_corner.x(), self.max_corner.y(), self.min_corner.z()))  # 4
        return convex_hull

    def contains(self, point):
        """ Checks if the point is inside this volume
        :param point: kdl Vector w.r.t. the same frame as this volume
        :return: True if inside, False otherwise
        """
        return self._min_corner.x() < point.x() < self._max_corner.x() and \
               self._min_corner.y() < point.y() < self._max_corner.y() and \
               self._min_corner.z() < point.z() < self._max_corner.z()

    def __repr__(self):
        return "BoxVolume(min_corner={}, max_corner={})".format(self.min_corner, self.max_corner)


class OffsetVolume(Volume):
    """ Represents a volume with a certain offset from the convex hull of the entity """
    def __init__(self, offset):
        """ Constructor

        :param offset: float with offset [m]
        """
        super(OffsetVolume, self).__init__()
        self._offset = offset

    def __repr__(self):
        return "OffsetVolume(offset={})".format(self._offset)


def volume_from_entity_area_msg(msg):
    """ Creates a dict mapping strings to Volumes from the EntityInfo data dictionary

    :param msg: ed_msgs.msg.Area
    :return: dict mapping strings to Volumes
    """
    # Check if we have data and if it contains areas
    if not msg:
        return None, None

    # Check if the volume has a name. Otherwise: skip
    if not msg.name:
        return None, None
    name = msg.name

    # Check if we have a shape
    center_point = point_msg_to_kdl_vector(msg.center_point)
    if len(msg.geometry == 1):
        if not msg.geometry.type == msg.geometry.BOX:
            return None, None

        size = msg.geometry.dimensions
        size = kdl.Vector(size[0], size[1], size[2])

        min_corner = center_point - size / 2
        max_corner = center_point + size / 2

        return name, BoxVolume(min_corner, max_corner)
    else:
        min_corners = []
        max_corners = []
        for subarea in msg.geometry:
            if not subarea.type == subarea.BOX:
                continue

            size = subarea.dimensions
            size = kdl.Vector(size[0], size[1], size[2])

            sub_min = center_point - size / 2
            sub_max = center_point + size / 2
            min_corners.append(sub_min)
            max_corners.append(sub_max)

        return name, CompositeBoxVolume(min_corners, max_corners)


def volumes_from_entity_areas_msg(msg):
    if not msg:
        return {}

    volumes = {}
    for a in msg:
        if not a.name:
            continue

        name, area = volume_from_entity_area_msg(a)
        if name and area:
            volumes[name] = area

    return volumes


if __name__ == "__main__":
    import doctest

    doctest.testmod()
