# test_gui.py
import tkinter as tk

def main():
    print("Starting application...")
    root = tk.Tk()
    root.title("Test Window")
    label = tk.Label(root, text="Hello World!")
    label.pack()
    print("GUI initialized, starting mainloop...")
    root.mainloop()
    print("Application closed.")

if __name__ == "__main__":
    print("Script started")
    main()