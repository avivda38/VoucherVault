import tkinter as tk
from tkinter import messagebox
from gui.gui_auth import AuthFrame
from gui.gui_coupons import CouponsFrame
from gui.gui_extras import ExtrasFrame
from database import create_tables

class MainWindow:
    def __init__(self):
        # Initialize database
        create_tables()
        
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("VoucherVault - מערכת ניהול שוברים")
        self.root.geometry("1000x800")
        
        # Initialize user state
        self.current_user = None
        self.manager = None
        
        # Create main container frame
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill="both", expand=True)
        
        # Create top bar frame that will always be visible
        self.top_bar = tk.Frame(self.main_container, bg="#ffffff", height=50)
        self.top_bar.pack(fill="x", side="top")
        self.top_bar.pack_propagate(False)  # Prevent the frame from shrinking
        
        # Add hamburger button to top bar
        self.hamburger_btn = tk.Button(
            self.top_bar, text="☰", font=("Arial", 24, "bold"),
            command=self.toggle_side_menu,
            bg="#eaeaea", relief="flat", cursor="hand2",
            width=2, height=1
        )
        self.hamburger_btn.pack(side="right", padx=12, pady=7)
        
        # Create content frame that will hold the main content
        self.content_frame = tk.Frame(self.main_container)
        self.content_frame.pack(fill="both", expand=True)
        
        # Initialize frames
        self.auth_frame = AuthFrame(self.content_frame, self)
        self.coupons_frame = CouponsFrame(self.content_frame, self)
        self.extras_frame = ExtrasFrame(self.content_frame, self)
        
        # Side menu frame (will be placed on top of everything)
        self.side_menu = tk.Frame(self.root, bg="#f7f7f7", width=240)
        
        # Show initial frame
        self.show_auth()
        
    def show_auth(self):
        self.hide_all_frames()
        self.auth_frame.show()

    def clear_current_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_coupons(self):
        self.hide_all_frames()
        self.coupons_frame.show()
        
    def show_extras(self):
        self.hide_all_frames()
        self.extras_frame.show()
        
    def hide_all_frames(self):
        self.auth_frame.hide()
        self.coupons_frame.hide()
        self.extras_frame.hide()
        self.close_side_menu()
        
    def toggle_side_menu(self):
        if self.side_menu.winfo_ismapped():
            self.close_side_menu()
        else:
            self.open_side_menu()
            
    def open_side_menu(self):
        self.rebuild_side_menu()
        # Place the side menu on top of everything
        self.side_menu.place(relx=1.0, rely=0, anchor="ne", relheight=1.0)
        self.side_menu.lift()  # Ensure it's on top
        
    def close_side_menu(self):
        self.side_menu.place_forget()
        
    def rebuild_side_menu(self):
        # Clear existing widgets
        for widget in self.side_menu.winfo_children():
            widget.destroy()
            
        # Close button
        close_btn = tk.Button(
            self.side_menu, text="✖", font=("Arial", 16),
            command=self.close_side_menu,
            bg="#f7f7f7", relief="flat", cursor="hand2"
        )
        close_btn.pack(anchor="ne", pady=(8, 0), padx=7)
        
        # Title
        title_label = tk.Label(
            self.side_menu, text="תפריט",
            font=('Arial', 17, 'bold'), bg="#f7f7f7"
        )
        title_label.pack(pady=10, anchor="n")
        
        # Menu buttons
        menu_items = [
            ("דף הבית", self.show_coupons),
            ("הוסף שובר חדש", lambda: self.coupons_frame.show_add_coupon()),
            ("הקופונים שלי", lambda: self.coupons_frame.show_coupons()),
            ("חיפוש קופונים", lambda: self.coupons_frame.show_search()),
            ("עומדים לפוג בקרוב", lambda: self.coupons_frame.show_expiring()),
            ("מועדפים", lambda: self.coupons_frame.show_favorites()),
            ("נמחקו לאחרונה", lambda: self.coupons_frame.show_deleted_coupons()),
            ("יומן פעילות", lambda: self.extras_frame.show_logs()),
            ("ייצוא לאקסל", lambda: self.extras_frame.export_excel_gui()),
            ("התנתקות", self.logout)
        ]
        
        for text, command in menu_items:
            btn = tk.Button(
                self.side_menu, text=text, width=22, height=2,
                font=('Arial', 12), command=lambda cmd=command: [self.close_side_menu(), cmd()],
                anchor="center", bg="#f7f7f7", relief="flat",
                activebackground="#e0e0e0", cursor="hand2"
            )
            btn.pack(pady=2, anchor="n", padx=8)
            
    def logout(self):
        self.current_user = None
        self.manager = None
        self.show_auth()
        
    def show_deleted_coupons(self):
        self.coupons_frame.show_deleted_coupons()
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MainWindow()
    app.run()

