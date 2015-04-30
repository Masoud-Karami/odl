# Copyright 2014, 2015 Holger Kohr, Jonas Adler
#
# This file is part of RL.
#
# RL is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RL is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with RL.  If not, see <http://www.gnu.org/licenses/>.


from __future__ import unicode_literals, print_function, division
from __future__ import absolute_import

import numpy as np

from RL.space.space import *
from RL.space.euclidean import *
from RL.space.function import *

from future import standard_library
standard_library.install_aliases()


class SequenceSpace(FunctionSpace):
    """The space of sequences
    """

    def __init__(self):
        FunctionSpace.__init__(self, Integers())

    def equals(self, other):
        return (isinstance(other, SequenceSpace) and
                FunctionSpace.equals(self, other))


class TruncationDiscretization(EuclidianSpace, Discretization):
    """ Truncation discretization of the integers
    Represents vectors by RN elements
    """

    def __init__(self, parent, n):
        if not isinstance(parent.domain, Integers):
            raise NotImplementedError("Can only discretize the integers")

        self.parent = parent
        EuclidianSpace.__init__(self, n)

    def innerImpl(self, v1, v2):
        return EuclidianSpace.innerImpl(self, v1, v2)

    def zero(self):
        return self.makeVector(np.zeros(self.n), copy=False)

    def empty(self):
        return self.makeVector(np.empty(self.n), copy=False)

    def equals(self, other):
        return (isinstance(other, TruncationDiscretization) and
                EuclidianSpace.equals(self, other))

    def makeVector(self, *args, **kwargs):
        return TruncationDiscretization.Vector(self, *args, **kwargs)

    def integrate(self, vector):
        return vector.values.sum()

    def points(self):
        return np.arange(self.n)

    class Vector(EuclidianSpace.Vector):
        def __init__(self, space, *args, **kwargs):
            if ((len(args) == 1 and
                 isinstance(args[0], SequenceSpace.Vector) and
                 args[0].space == space.parent)):

                data = EuclidianSpace.Vector.__init__(self, space,
                                                      args[0](space.points()),
                                                      copy=False)
            else:
                data = EuclidianSpace.Vector.__init__(self, space, *args,
                                                      **kwargs)