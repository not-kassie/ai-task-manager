import customtkinter as ctk


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AI Task Manager")
        self.geometry("900x600")

        ctk.CTkLabel(
            self, text="AI Task Manager",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=20)


if __name__ == "__main__":
    ctk.set_appearance_mode("system")
    app = App()
    app.mainloop()