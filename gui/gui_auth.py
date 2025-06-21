import tkinter as tk
from tkinter import messagebox
import re
from database import add_user, add_log
from coupon_manager import CouponManager
from user import User
import sqlite3


class AuthFrame:
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.frame = tk.Frame(parent)
        
        # Initialize login/register frames
        self.login_frame = tk.Frame(self.frame)
        self.register_frame = tk.Frame(self.frame)
        
        self.setup_login()
        self.setup_register()
        
    def setup_login(self):
        for widget in self.login_frame.winfo_children():
            widget.destroy()
            
        # Create login form
        login_inner = tk.Frame(self.login_frame, bd=3, relief="ridge", padx=32, pady=28, bg="#ffffff")
        login_inner.pack(expand=True)
        
        # Title
        tk.Label(login_inner, text="ברוך/ה הבא/ה! התחברות", 
                font=('Arial', 19, 'bold'), bg="#ffffff").pack(pady=10)
        
        # Username
        tk.Label(login_inner, text="שם משתמש:", 
                font=('Arial', 13), bg="#ffffff").pack(pady=5)
        self.entry_login_username = tk.Entry(login_inner, font=('Arial', 13))
        self.entry_login_username.pack(pady=2)
        
        # Password
        tk.Label(login_inner, text="סיסמה:", 
                font=('Arial', 13), bg="#ffffff").pack(pady=5)
        self.entry_login_password = tk.Entry(login_inner, show="*", font=('Arial', 13))
        self.entry_login_password.pack(pady=2)
        
        # Show password checkbox
        self.show_pass_var_login = tk.BooleanVar()
        tk.Checkbutton(login_inner, text="הצג סיסמה", 
                      variable=self.show_pass_var_login,
                      command=lambda: self.toggle_password(self.entry_login_password, self.show_pass_var_login),
                      bg="#ffffff").pack(pady=5)
        
        # Login button
        tk.Button(login_inner, text="התחבר", 
                 font=('Arial', 13, 'bold'),
                 command=self.login,
                 bg="#5db0ff", fg="white").pack(pady=13)
        
        # Register link
        tk.Button(login_inner, text="להרשמה", 
                 font=('Arial', 11),
                 command=self.show_register).pack()
        
    def setup_register(self):
        for widget in self.register_frame.winfo_children():
            widget.destroy()
            
        # Create register form
        register_inner = tk.Frame(self.register_frame, bd=3, relief="ridge", padx=32, pady=28, bg="#ffffff")
        register_inner.pack(expand=True)
        
        # Title
        tk.Label(register_inner, text="הרשמה", 
                font=('Arial', 19, 'bold'), bg="#ffffff").pack(pady=10)
        
        # Username
        tk.Label(register_inner, text="שם משתמש:", 
                font=('Arial', 13), bg="#ffffff").pack(pady=5)
        self.entry_register_username = tk.Entry(register_inner, font=('Arial', 13))
        self.entry_register_username.pack(pady=2)
        
        # Password
        tk.Label(register_inner, text="סיסמה:", 
                font=('Arial', 13), bg="#ffffff").pack(pady=5)
        self.entry_register_password = tk.Entry(register_inner, show="*", font=('Arial', 13))
        self.entry_register_password.pack(pady=2)
        
        # Show password checkbox
        self.show_pass_var_register = tk.BooleanVar()
        tk.Checkbutton(register_inner, text="הצג סיסמה", 
                      variable=self.show_pass_var_register,
                      command=lambda: self.toggle_password(self.entry_register_password, self.show_pass_var_register),
                      bg="#ffffff").pack(pady=5)
        
        # Register button
        tk.Button(register_inner, text="הרשמה", 
                 font=('Arial', 13, 'bold'),
                 command=self.register,
                 bg="#5db0ff", fg="white").pack(pady=13)
        
        # Login link
        tk.Button(register_inner, text="לעמוד התחברות", 
                 font=('Arial', 11),
                 command=self.show_login).pack()
        
    def show(self):
        self.frame.pack(fill="both", expand=True)
        self.frame.tkraise()
        self.show_login()
        
    def hide(self):
        self.frame.pack_forget()
        
    def show_login(self):
        self.register_frame.pack_forget()
        self.login_frame.pack(fill="both", expand=True)
        self.login_frame.tkraise()
        self.clear_entries()
        
    def show_register(self):
        self.login_frame.pack_forget()
        self.register_frame.pack(fill="both", expand=True)
        self.register_frame.tkraise()
        self.clear_entries()
        
    def clear_entries(self):
        try:
            self.entry_login_username.delete(0, tk.END)
            self.entry_login_password.delete(0, tk.END)
            self.entry_register_username.delete(0, tk.END)
            self.entry_register_password.delete(0, tk.END)
        except:
            pass
            
    def toggle_password(self, entry, var):
        entry.config(show="" if var.get() else "*")
        
    def is_valid_username(self, username):
        return len(username) >= 4 and username.isalnum()
        
    def is_valid_password(self, password):
        if len(password) < 6:
            return False
        if not re.search(r'[A-Za-z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        return True
        
    def login(self):
        username = self.entry_login_username.get()
        password = self.entry_login_password.get()
        
        if not username or not password:
            messagebox.showerror("שגיאה", "חובה למלא שם משתמש וסיסמה")
            return
            
        conn = sqlite3.connect("voucher_vault.db")
        cursor = conn.cursor()
        cursor.execute('SELECT id, password FROM users WHERE username=?', (username,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            messagebox.showerror("שגיאה", "המשתמש לא קיים")
            return
            
        user_id, db_password = result
        if User.hash_password(password) == db_password:
            self.main_window.current_user = (user_id, username)
            self.main_window.manager = CouponManager(user_id)
            add_log(user_id, "התחברות", f"שם משתמש: {username}")
            self.main_window.show_coupons()
        else:
            messagebox.showerror("שגיאה", "סיסמה שגויה")
            
    def register(self):
        username = self.entry_register_username.get()
        password = self.entry_register_password.get()
        
        if not self.is_valid_username(username):
            messagebox.showerror("שגיאה", 
                "שם משתמש חייב להיות לפחות 4 תווים וללא רווחים או תווים מיוחדים.")
            return
            
        if not self.is_valid_password(password):
            messagebox.showerror("שגיאה", 
                "סיסמה חייבת להיות לפחות 6 תווים ולכלול אות ומספר.")
            return
            
        user = User(username, password)
        add_user(user.id, user.username, user.password)
        messagebox.showinfo("הרשמה", "נרשמת בהצלחה! עכשיו תתחבר/י.")
        self.show_login()


