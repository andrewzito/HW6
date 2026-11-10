
import E96
import sympy
from abc import ABC, abstractmethod


class CircuitElement:
    def __init__(self, name='ab'):
        self.Name = name

    @property
    def Name(self):
        return self._Name

    @Name.setter
    def Name(self, value):
        self._Name = min(value[0], value[1]) + max(value[0], value[1])

    def MatchName(self, name):
        return self.Name == min(name[0], name[1]) + max(name[0], name[1])


class PassiveElement(CircuitElement, ABC):
    def __init__(self, name='ab'):
        super().__init__(name)

    @abstractmethod
    def Impedance(self, s):
        pass


class Resistor(PassiveElement):
    def __init__(self, R=1.0, name='ab', closestE96=False):
        super().__init__(name)
        self._I = 0.0
        self._V = 0.0
        self.SetResistance(R, closestE96)

    @property
    def I(self):
        return self._I

    @I.setter
    def I(self, value):
        self._I = value
        self._V = self._I * self._resistance if self._resistance != 0 else 0.0

    @property
    def V(self):
        return self._V

    @V.setter
    def V(self, value):
        self._V = value
        self._I = self._V / self._resistance if self._resistance != 0 else 0.0

    @property
    def R(self):
        return self.E96R if self.closestE96 else self._resistance

    @R.setter
    def R(self, value):
        self.E96R = E96.getClosestE96(value)[0]
        self.E96ColorBands = E96.getColors(value)
        self._resistance = self.E96R if self.closestE96 else value

    def Impedance(self, s):
        return sympy.sympify(self.R)

    def SetResistance(self, value, closestE96=False):
        self.closestE96 = closestE96
        self.R = value

    def MatchName(self, name):
        return 1 if self.Name == min(name[0], name[1]) + max(name[0], name[1]) else 0


class Inductor(PassiveElement):
    def __init__(self, L=1.0, name='ab'):
        super().__init__(name)
        self.L = L

    @property
    def L(self):
        return self._L

    @L.setter
    def L(self, value):
        value = float(value)
        if value <= 0:
            raise ValueError("Inductance must be positive.")
        self._L = value

    def Impedance(self, s):
        return s * self.L


class Capacitor(PassiveElement):
    def __init__(self, C=1e-6, name='ab'):
        super().__init__(name)
        self.C = C

    @property
    def C(self):
        return self._C

    @C.setter
    def C(self, value):
        value = float(value)
        if value <= 0:
            raise ValueError("Capacitance must be positive.")
        self._C = value

    def Impedance(self, s):
        return 1 / (s * self.C)


class VoltageSource(CircuitElement):
    def __init__(self, V=12.0, name='ab'):
        super().__init__(name)
        self.Voltage = V


class Loop:
    def __init__(self, nodes=None):
        self.Nodes = nodes if nodes is not None else []
        self.DeltaV = 0.0
        self.Current = 0.0

    def KVL(self, devices):
        self.DeltaV = 0.0

        for i in range(len(self.Nodes) - 1):
            for device in devices:
                direction = device.MatchName(self.Nodes[i] + self.Nodes[i + 1])

                if direction != 0:
                    if isinstance(device, Resistor):
                        self.DeltaV -= device.R * device.I * direction
                    elif isinstance(device, VoltageSource):
                        self.DeltaV += device.Voltage * direction

        return self.DeltaV


def main():
    pass


if __name__ == "__main__":
    main()
