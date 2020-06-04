from tkinter import Tk
root = Tk()
import file_ui as UI



def main():
    app = UI.Login(root)
    root.mainloop()


if __name__ == "__main__":
    main()