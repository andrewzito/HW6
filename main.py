
import tkinter as tk
from RLCApplication import RLCController


def main():
    root = tk.Tk()
    app = RLCController(root)
    root.mainloop()


if __name__ == "__main__":
    main()
