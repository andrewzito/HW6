#region imports
from abc import ABC, abstractmethod
from scipy.optimize import fsolve
import sympy as sym
import numpy as np
import matplotlib.pyplot as plt

from CircuitElements import Resistor, Inductor, Capacitor, VoltageSource, Loop
#endregion


#region Resistor Network Classes

class Resistor_Network(ABC):
    def __init__(self):
        self.Loops = []
        self.Resistors = []
        self.Inductors = []
        self.Capacitors = []
        self.VSources = []

    def BuildNetworkFromFile(self, filename):
        self.Resistors = []
        self.Inductors = []
        self.Capacitors = []
        self.VSources = []
        self.Loops = []

        with open(filename, "r") as file:
            lines = file.readlines()

        index = 0

        while index < len(lines):
            line = lines[index].strip()

            if not line or line.startswith("#"):
                index += 1
                continue

            if line.startswith("<") and not line.startswith("</"):
                section = line[1:-1].strip().lower()
                values = {}
                index += 1

                while index < len(lines):
                    line = lines[index].strip()

                    if line.startswith("</"):
                        break

                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        values[key.strip().lower()] = value.strip()

                    index += 1

                name = values.get("name", "ab").lower()

                if section == "resistor":
                    resistance = float(values.get("resistance", 1.0))
                    self.Resistors.append(Resistor(R=resistance, name=name))

                elif section == "inductor":
                    inductance = float(
                        values.get("inductance", values.get("l", 1.0))
                    )
                    self.Inductors.append(Inductor(L=inductance, name=name))

                elif section == "capacitor":
                    capacitance = float(
                        values.get(
                            "capacitance",
                            values.get("capacitence", values.get("c", 1e-6))
                        )
                    )
                    self.Capacitors.append(Capacitor(C=capacitance, name=name))

                elif section in ("source", "voltagesource"):
                    source_type = values.get("type", "voltage").lower()

                    if source_type == "voltage":
                        voltage = float(values.get("value", 12.0))
                        self.VSources.append(
                            VoltageSource(V=voltage, name=name)
                        )

                elif section == "loop":
                    loop = Loop()
                    loop.Name = values.get("name", "loop1").lower()
                    nodes = values.get("nodes", "")

                    loop.Nodes = [
                        node.strip().lower()
                        for node in nodes.split(",")
                        if node.strip()
                    ]

                    if loop.Nodes and loop.Nodes[-1] != loop.Nodes[0]:
                        loop.Nodes.append(loop.Nodes[0])

                    self.Loops.append(loop)

            index += 1

        print("Circuit loaded from", filename)
        print("Number of resistors:", len(self.Resistors))
        print("Number of inductors:", len(self.Inductors))
        print("Number of capacitors:", len(self.Capacitors))
        print("Number of voltage sources:", len(self.VSources))
        print("Number of loops:", len(self.Loops))

    def MakeResistor(self, N, Txt):
        resistor = Resistor()
        N += 1

        while N < len(Txt) and "</resistor>" not in Txt[N].lower():
            line = Txt[N].strip().lower()

            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                if key == "name":
                    resistor.Name = value
                elif key == "resistance":
                    resistor.R = float(value)

            N += 1

        self.Resistors.append(resistor)
        return N

    def MakeInductor(self, N, Txt):
        inductor = Inductor()
        N += 1

        while N < len(Txt) and "</inductor>" not in Txt[N].lower():
            line = Txt[N].strip().lower()

            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                if key == "name":
                    inductor.Name = value
                elif key in ("inductance", "l"):
                    inductor.L = float(value)

            N += 1

        self.Inductors.append(inductor)
        return N

    def MakeCapacitor(self, N, Txt):
        capacitor = Capacitor()
        N += 1

        while N < len(Txt) and "</capacitor>" not in Txt[N].lower():
            line = Txt[N].strip().lower()

            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                if key == "name":
                    capacitor.Name = value
                elif key in ("capacitance", "capacitence", "c"):
                    capacitor.C = float(value)

            N += 1

        self.Capacitors.append(capacitor)
        return N

    def MakeVSource(self, N, Txt):
        source = VoltageSource()
        N += 1

        while N < len(Txt) and "</source>" not in Txt[N].lower():
            line = Txt[N].strip().lower()

            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                if key == "name":
                    source.Name = value
                elif key == "value":
                    source.Voltage = float(value)
                elif key == "type":
                    source.Type = value

            N += 1

        self.VSources.append(source)
        return N

    def MakeLoop(self, N, Txt):
        loop = Loop()
        N += 1

        while N < len(Txt) and "</loop>" not in Txt[N].lower():
            line = Txt[N].strip().lower()

            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                if key == "name":
                    loop.Name = value
                elif key == "nodes":
                    loop.Nodes = [
                        node.strip().lower() for node in value.split(",")
                    ]

            N += 1

        if loop.Nodes and loop.Nodes[-1] != loop.Nodes[0]:
            loop.Nodes.append(loop.Nodes[0])

        self.Loops.append(loop)
        return N

    def ComputeLoopVoltageDrops(self):
        devices = self.Resistors + self.VSources
        loop_voltages = []

        for loop in self.Loops:
            loop_voltages.append(loop.KVL(devices))

        return loop_voltages

    def PrintLoopVoltageDrops(self):
        for loop in self.Loops:
            print(
                "Loop {}: Net Voltage Drop = {:0.2f} V".format(
                    loop.Name, loop.DeltaV
                )
            )

    def GetResistorByName(self, name):
        for resistor in self.Resistors:
            if resistor.Name == name.lower():
                return resistor
        return None

    @abstractmethod
    def AnalyzeCircuit(self):
        pass

    @abstractmethod
    def GetCurrentResiduals(self, i):
        pass


class ResistorNetwork(Resistor_Network):
    def __init__(self):
        super().__init__()

    def AnalyzeCircuit(self):
        i0 = [1, 1, 1]
        currents = fsolve(self.GetCurrentResiduals, i0)

        for idx in range(len(currents)):
            print("I{} = {:0.1f}".format(idx + 1, currents[idx]))

        return currents

    def GetCurrentResiduals(self, i):
        self.GetResistorByName("ad").I = i[0]
        self.GetResistorByName("bc").I = i[0]
        self.GetResistorByName("cd").I = i[2]
        self.GetResistorByName("ce").I = i[1]

        node_c_current = sum([i[0], i[1], -i[2]])
        KVL = self.ComputeLoopVoltageDrops()
        KVL.append(node_c_current)
        return KVL


class ResistorNetwork_2(Resistor_Network):
    def __init__(self):
        super().__init__()

    def AnalyzeCircuit(self):
        i0 = [1, 1, 1, 1, 1]
        currents = fsolve(self.GetCurrentResiduals, i0)

        for idx in range(len(currents)):
            print("I{} = {:0.1f}".format(idx + 1, currents[idx]))

        return currents

    def GetCurrentResiduals(self, i):
        self.GetResistorByName("ad").I = i[0]
        self.GetResistorByName("bc").I = i[0]
        self.GetResistorByName("cd").I = i[2]
        self.GetResistorByName("ce").I = i[4]
        self.GetResistorByName("de").I = i[3]

        node_c_current = sum([i[0], -i[2], i[4]])
        node_d_current = sum([i[3], i[2], -i[0], -i[1]])

        KVL = self.ComputeLoopVoltageDrops()
        KVL.append(node_c_current)
        KVL.append(node_d_current)
        return KVL


#endregion


#region RLC Circuit

class RLC_Circuit(Resistor_Network):
    def __init__(self):
        super().__init__()
        self.t = sym.symbols("t", real=True, nonnegative=True)
        self.s = sym.symbols("s")
        self.results = {}

    def GetCurrentResiduals(self, i):
        return []

    def AnalyzeCircuit(self):
        if len(self.Resistors) != 1:
            raise ValueError("The circuit needs one resistor.")
        if len(self.Inductors) != 1:
            raise ValueError("The circuit needs one inductor.")
        if len(self.Capacitors) != 1:
            raise ValueError("The circuit needs one capacitor.")
        if len(self.VSources) != 1:
            raise ValueError("The circuit needs one voltage source.")

        resistor = self.Resistors[0]
        inductor = self.Inductors[0]
        capacitor = self.Capacitors[0]
        source = self.VSources[0]

        t = self.t
        s = self.s

        R = sym.sympify(resistor.R)
        L = sym.sympify(inductor.L)
        C = sym.sympify(capacitor.C)

        source_time = source.Voltage * sym.Heaviside(t)
        source_laplace = sym.laplace_transform(
            source_time, t, s, noconds=True
        )

        # Polymorphism: each passive element calculates its own impedance.
        passive_elements = self.Resistors + self.Inductors + self.Capacitors

        Ztotal = sym.simplify(
            sum(element.Impedance(s) for element in passive_elements)
        )

        current_laplace = sym.simplify(source_laplace / Ztotal)
        resistor_voltage_laplace = sym.simplify(
            current_laplace * resistor.Impedance(s)
        )
        inductor_voltage_laplace = sym.simplify(
            current_laplace * inductor.Impedance(s)
        )
        capacitor_voltage_laplace = sym.simplify(
            current_laplace * capacitor.Impedance(s)
        )

        print("\nLAPLACE-DOMAIN RESULTS")
        print("Vs(s) =", sym.simplify(source_laplace))
        print("Ztotal(s) =", Ztotal)
        print("I(s) =", current_laplace)
        print("VR(s) =", resistor_voltage_laplace)
        print("VL(s) =", inductor_voltage_laplace)
        print("VC(s) =", capacitor_voltage_laplace)

        current_time = sym.simplify(
            sym.inverse_laplace_transform(current_laplace, s, t)
        )
        resistor_voltage_time = sym.simplify(
            sym.inverse_laplace_transform(
                resistor_voltage_laplace, s, t
            )
        )
        inductor_voltage_time = sym.simplify(
            sym.inverse_laplace_transform(
                inductor_voltage_laplace, s, t
            )
        )
        capacitor_voltage_time = sym.simplify(
            sym.inverse_laplace_transform(
                capacitor_voltage_laplace, s, t
            )
        )

        print("\nTIME-DOMAIN RESULTS")
        print("i(t) =", current_time)
        print("vR(t) =", resistor_voltage_time)
        print("vL(t) =", inductor_voltage_time)
        print("vC(t) =", capacitor_voltage_time)

        omega0 = sym.N(1 / sym.sqrt(L * C))
        alpha = sym.N(R / (2 * L))
        zeta = sym.N(alpha / omega0)
        critical_resistance = sym.N(2 * sym.sqrt(L / C))

        print("\nDAMPING ANALYSIS")
        print("Natural frequency =", omega0, "rad/s")
        print("Alpha =", alpha, "1/s")
        print("Damping ratio =", zeta)
        print("Critical resistance =", critical_resistance, "ohms")

        if float(zeta) < 1:
            damping = "Underdamped"
        elif float(zeta) == 1:
            damping = "Critically damped"
        else:
            damping = "Overdamped"

        print("Circuit is", damping)

        self.results = {
            "source_laplace": source_laplace,
            "Ztotal": Ztotal,
            "current_laplace": current_laplace,
            "resistor_voltage_laplace": resistor_voltage_laplace,
            "inductor_voltage_laplace": inductor_voltage_laplace,
            "capacitor_voltage_laplace": capacitor_voltage_laplace,
            "current_time": current_time,
            "resistor_voltage_time": resistor_voltage_time,
            "inductor_voltage_time": inductor_voltage_time,
            "capacitor_voltage_time": capacitor_voltage_time,
            "omega0": omega0,
            "alpha": alpha,
            "zeta": zeta,
            "critical_resistance": critical_resistance,
            "damping": damping
        }

        return self.results

    def PlotCurrent(self, t=0.002):
        if not self.results:
            self.AnalyzeCircuit()

        results = self.results
        time_values = np.linspace(0, float(t), 2000)

        source_function = sym.lambdify(
            self.t,
            self.VSources[0].Voltage * sym.Heaviside(self.t, 1),
            modules="numpy"
        )
        resistor_function = sym.lambdify(
            self.t, results["resistor_voltage_time"], modules="numpy"
        )
        inductor_function = sym.lambdify(
            self.t, results["inductor_voltage_time"], modules="numpy"
        )
        capacitor_function = sym.lambdify(
            self.t, results["capacitor_voltage_time"], modules="numpy"
        )
        current_function = sym.lambdify(
            self.t, results["current_time"], modules="numpy"
        )

        source_values = np.full_like(time_values, float(self.VSources[0].Voltage))
        resistor_values = np.asarray(
            resistor_function(time_values), dtype=float
        )
        inductor_values = np.asarray(
            inductor_function(time_values), dtype=float
        )
        capacitor_values = np.asarray(
            capacitor_function(time_values), dtype=float
        )
        current_values = np.asarray(
            current_function(time_values), dtype=float
        )

        figure, (ax_voltage, ax_current) = plt.subplots(
            2, 1, figsize=(10, 8), sharex=True
        )

        ax_voltage.plot(
            time_values * 1000, source_values, label="Source voltage"
        )
        ax_voltage.plot(
            time_values * 1000, resistor_values, label="Resistor voltage"
        )
        ax_voltage.plot(
            time_values * 1000, inductor_values, label="Inductor voltage"
        )
        ax_voltage.plot(
            time_values * 1000, capacitor_values, label="Capacitor voltage"
        )

        ax_voltage.set_title("Series RLC Step Response")
        ax_voltage.set_ylabel("Voltage (V)")
        ax_voltage.grid(True)
        ax_voltage.legend()

        ax_current.plot(
            time_values * 1000,
            current_values * 1000,
            label="Circuit current"
        )
        ax_current.set_xlabel("Time (ms)")
        ax_current.set_ylabel("Current (mA)")
        ax_current.grid(True)
        ax_current.legend()

        figure.tight_layout()
        plt.show()

        return figure


#endregion


def main():
    circuit = RLC_Circuit()
    circuit.BuildNetworkFromFile("RLCNetwork.txt")
    circuit.AnalyzeCircuit()
    circuit.PlotCurrent(0.002)


if __name__ == "__main__":
    main()
