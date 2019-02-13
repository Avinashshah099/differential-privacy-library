import abc
import sys

from .. import DPMachine
from .laplace import Laplace, LaplaceTruncated, LaplaceFolded, LaplaceBounded
from .geometric import Geometric, GeometricTruncated
from .exponential import Exponential, ExponentialHierarchical
from .binary import Binary

# Ensure compatibility with Python 2 and 3 when using ABCMeta
if sys.version_info >= (3, 4):
    ABC = abc.ABC
else:
    ABC = abc.ABCMeta(str('ABC'), (), {})


class DPMechanism(DPMachine, ABC):
    def __init__(self):
        self.epsilon = None
        self.delta = None

    def __repr__(self):
        output = str(self.__module__) + "." + str(self.__class__.__name__) + "()"
        output += ".setEpsilon(" + str(self.epsilon) + ")" if self.epsilon is not None else ""

        return output

    @abc.abstractmethod
    def randomise(self, value):
        pass

    def get_bias(self, value):
        """

        :param value:
        :return:
        :rtype: Union[None, float]
        """
        return None

    def get_variance(self, value):
        return None

    def get_mse(self, value):
        if self.get_variance(value) is None or self.get_bias(value) is None:
            return None

        return self.get_variance(value) + (self.get_bias(value)) ** 2

    def set_epsilon(self, epsilon):
        if self.epsilon is not None:
            raise ValueError("Epsilon cannot be reset; initiate a new mechanism instance instead.")

        if epsilon <= 0:
            raise ValueError("Epsilon must be strictly positive")

        self.epsilon = epsilon
        return self

    def set_epsilon_delta(self, epsilon, delta):
        self.set_epsilon(epsilon)

        if 0 <= delta <= 1:
            self.delta = delta
        else:
            raise ValueError("Delta must be in [0, 1]")

        return self

    def check_inputs(self, value):
        if self.epsilon is None:
            raise ValueError("Epsilon must be set")
        return True


class TruncationMachine:
    def __init__(self):
        self.lower_bound = None
        self.upper_bound = None

    def __repr__(self):
        output = ".setBounds(" + str(self.lower_bound) + ", " + str(self.upper_bound) + ")" \
            if self.lower_bound is not None else ""

        return output

    def set_bounds(self, lower, upper):
        if (not isinstance(lower, int) and not isinstance(lower, float)) or\
                (not isinstance(upper, int) and not isinstance(upper, float)):
            raise TypeError("Bounds must be numeric")

        if lower > upper:
            raise ValueError("Lower bound must not be greater than upper bound")

        self.lower_bound = lower
        self.upper_bound = upper

        return self

    def check_inputs(self, value):
        if (self.lower_bound is None) or (self.upper_bound is None):
            raise ValueError("Upper and lower bounds must be set")
        return True

    def truncate(self, value):
        if value > self.upper_bound:
            return self.upper_bound
        elif value < self.lower_bound:
            return self.lower_bound

        return value


class FoldingMachine:
    def __init__(self):
        self.lower_bound = None
        self.upper_bound = None

    def __repr__(self):
        output = ".setBounds(" + str(self.lower_bound) + ", " + str(self.upper_bound) + ")" \
            if self.lower_bound is not None else ""

        return output

    def set_bounds(self, lower, upper):
        if (not isinstance(lower, int) and not isinstance(lower, float)) or\
                (not isinstance(upper, int) and not isinstance(upper, float)):
            raise TypeError("Bounds must be numeric")

        if lower > upper:
            raise ValueError("Lower bound must not be greater than upper bound")

        self.lower_bound = lower
        self.upper_bound = upper

        return self

    def check_inputs(self, value):
        if (self.lower_bound is None) or (self.upper_bound is None):
            raise ValueError("Upper and lower bounds must be set")
        return True

    def fold(self, value):
        if value < self.lower_bound:
            return self.fold(2 * self.lower_bound - value)
        if value > self.upper_bound:
            return self.fold(2 * self.upper_bound - value)

        return value