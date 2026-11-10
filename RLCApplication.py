import tkinter as tk
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from CircuitElements import Resistor, Inductor, Capacitor


class RLCModel:
    def __init__(self):
        self.s, self.t = sp.symbols('s t')

    def Calculate(self, R, L, C, V):
        s = self.s
        t = self.t

        elements = [
            Resistor(R),
            Inductor(L),
            Capacitor(C)
        ]

        Ztotal = sum(element.Impedance(s) for element in elements)
        Ztotal = sp.simplify(Ztotal)

        Vs = V * sp.Heaviside(t)
        Vs_s = sp.laplace_transform(Vs, t, s, noconds=True)

        I_s = sp.simplify(Vs_s / Ztotal)
        VR_s = sp.simplify(I_s * R)
        VL_s = sp.simplify(I_s * s * L)
        VC_s = sp.simplify(I_s / (s * C))

        current = sp.simplify(
            sp.inverse_laplace_transform(I_s, s, t)
        )
        resistor_voltage = sp.simplify(
            sp.inverse_laplace_transform(VR_s, s, t)
        )
        inductor_voltage = sp.simplify(
            sp.inverse_laplace_transform(VL_s, s, t)
        )
        capacitor_voltage = sp.simplify(
            sp.inverse_laplace_transform(VC_s, s, t)
        )

        omega0 = 1 / np.sqrt(L * C)
        alpha = R / (2 * L)
        zeta = alpha / omega0
        Rcritical = 2 * np.sqrt(L / C)

        if np.isclose(alpha, omega0):
            damping = "Critically Damped"
        elif alpha < omega0:
            damping = "Underdamped"
        else:
            damping = "Overdamped"

        time = np.linspace(0, 0.002, 1000)

        current_func = sp.lambdify(t, current, modules="numpy")
        vr_func = sp.lambdify(t, resistor_voltage, modules="numpy")
        vl_func = sp.lambdify(t, inductor_voltage, modules="numpy")
        vc_func = sp.lambdify(t, capacitor_voltage, modules="numpy")

        
        current_values = np.real_if_close(current_func(time))
        vr_values = np.real_if_close(vr_func(time))
        vl_values = np.real_if_close(vl_func(time))
        vc_values = np.real_if_close(vc_func(time))

        return {
            "time": time,
            "current": current_values,
            "VR": vr_values,
            "VL": vl_values,
            "VC": vc_values,
            "VS": np.full(len(time), V),
            "Ztotal": Ztotal,
            "I_s": I_s,
            "VR_s": VR_s,
            "VL_s": VL_s,
            "VC_s": VC_s,
            "omega0": omega0,
            "alpha": alpha,
            "zeta": zeta,
            "Rcritical": Rcritical,
            "damping": damping
        }


class RLCView:
    def __init__(self, root, controller):
        self.root = root
        self.root.title("Interactive RLC Series Circuit")
        self.root.geometry("1000x750")

        self.controller = controller
        input_frame = tk.Frame(root)
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Resistance (Ohms):").grid(row=0, column=0, padx=5)
        self.R_entry = tk.Entry(input_frame, width=10)
        self.R_entry.insert(0, "100")
        self.R_entry.grid(row=0, column=1, padx=5)
        tk.Label(input_frame, text="Inductance (H):").grid(row=0, column=2, padx=5)
        self.L_entry = tk.Entry(input_frame, width=10)
        self.L_entry.insert(0, "0.01")
        self.L_entry.grid(row=0, column=3, padx=5)

        tk.Label(input_frame, text="Capacitance (F):").grid(row=1, column=0, padx=5)
        self.C_entry = tk.Entry(input_frame, width=10)
        self.C_entry.insert(0, "0.000001")
        self.C_entry.grid(row=1, column=1, padx=5)

        tk.Label(input_frame, text="Source Voltage (V):").grid(row=1, column=2, padx=5)
        self.V_entry = tk.Entry(input_frame, width=10)
        self.V_entry.insert(0, "10")
        self.V_entry.grid(row=1, column=3, padx=5)
        self.update_button = tk.Button(
            root,
            text="Update Circuit",
            command=self.controller.Update
        )
        self.update_button.pack(pady=10)
        self.info_label = tk.Label(root, text="Enter circuit values and update.")
        self.info_label.pack(pady=5)

        self.figure, (self.ax1, self.ax2) = plt.subplots(
            2, 1, figsize=(9, 6)
        )

        self.figure.tight_layout(pad=3)

        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def GetInputs(self):
        R = float(self.R_entry.get())
        L = float(self.L_entry.get())
        C = float(self.C_entry.get())
        V = float(self.V_entry.get())

        return R, L, C, V

    def UpdatePlots(self, results):
        time_ms = results["time"] * 1000

        self.ax1.clear()
        self.ax2.clear()

        self.ax1.plot(time_ms, results["VS"], label="Source Voltage")
        self.ax1.plot(time_ms, results["VR"], label="Resistor Voltage")
        self.ax1.plot(time_ms, results["VL"], label="Inductor Voltage")
        self.ax1.plot(time_ms, results["VC"], label="Capacitor Voltage")

        self.ax1.set_title("RLC Circuit Voltages")
        self.ax1.set_xlabel("Time (ms)")
        self.ax1.set_ylabel("Voltage (V)")
        self.ax1.grid(True)
        self.ax1.legend()

        self.ax2.plot(
            time_ms,
            results["current"] * 1000,
            label="Circuit Current"
        )
        self.ax2.set_title("RLC Circuit Current")
        self.ax2.set_xlabel("Time (ms)")
        self.ax2.set_ylabel("Current (mA)")
        self.ax2.grid(True)
        self.ax2.legend()

        self.info_label.config(
            text="Damping: " + results["damping"] +
            " | Critical Resistance: " +
            str(round(results["Rcritical"], 2)) + " Ohms"
        )

        self.figure.tight_layout()
        self.canvas.draw()

class RLCController:
    def __init__(self, root):
        self.model = RLCModel()
        self.view = RLCView(root, self)

        self.Update()

    def Update(self):
        try:
            R, L, C, V = self.view.GetInputs()
        except ValueError:
            self.view.info_label.config(
                text="Error: Enter valid numerical values."
            )
            return

        if R <= 0 or L <= 0 or C <= 0:
            self.view.info_label.config(
                text="Error: R, L, and C must be greater than zero."
            )
            return
        results = self.model.Calculate(R, L, C, V)
        self.view.UpdatePlots(results)
