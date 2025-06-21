import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import date

class ExtrasFrame:
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.frame = tk.Frame(parent)
        self.user_alert_days = tk.IntVar(value=14)
        
    def show(self):
        self.frame.pack(fill="both", expand=True)
        self.frame.tkraise()
        
    def hide(self):
        self.frame.pack_forget()
        
    def check_manager(self):
        if not self.main_window.manager:
            messagebox.showerror("שגיאה", "יש להתחבר תחילה")
            self.main_window.show_auth()
            return False
        return True

    def show_logs(self):

        self.main_window.hide_all_frames()  # Hide all other frames first
        # Only clear the contents of self.frame, not the frame itself
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.pack(fill="both", expand=True)
        self.frame.tkraise()
        if not self.check_manager():
            return
        # Main container that will fill the entire frame
        main_container = tk.Frame(self.frame)
        main_container.pack(fill="both", expand=True)
        # Title at the top
        tk.Label(main_container, text="יומן פעילות", font=('Arial', 16, 'bold')).pack(pady=10)
        logs = self.main_window.manager.get_logs()
        logs = list(reversed(logs))  # Show latest first
        if not logs:
            tk.Label(main_container, text="אין לוגים להציג.", font=('Arial', 12)).pack(pady=20)
            return
        # Container for canvas and scrollbar
        container = tk.Frame(main_container)
        container.pack(fill="both", expand=True, padx=20, pady=10)
        # Canvas and scrollbar setup
        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        # Headers (use grid)
        headers = ["תאריך ושעה", "פעולה", "פרטים"]
        for col, h in enumerate(headers):
            width = 50 if h == "פרטים" else 20
            anchor = "w" if h == "פרטים" else "center"
            tk.Label(scrollable_frame, text=h, font=("Arial", 12, "bold"), width=width, anchor=anchor, borderwidth=2, relief="groove").grid(row=0, column=col, sticky="nsew")
        # Log entries (use grid)
        for row, log in enumerate(logs, 1):
            try:
                log_id, user_id, action, timestamp, details = log
                values = [timestamp[:19].replace("T", " "), action, details]
                for col, value in enumerate(values):
                    width = 50 if col == 2 else 20
                    anchor = "w" if col == 2 else "center"
                    tk.Label(scrollable_frame, text=value, font=("Arial", 11), width=width, anchor=anchor, borderwidth=1, relief="solid").grid(row=row, column=col, sticky="nsew")
            except Exception as e:
                print("שגיאה בהצגת לוג:", e)
        # Make columns expand evenly
        for col in range(len(headers)):
            scrollable_frame.grid_columnconfigure(col, weight=1)
        # Refresh button at the bottom
        tk.Button(main_container, text="רענן יומן", command=self.show_logs, bg="#7d7df2", fg="white").pack(pady=10)

    def show_summary(self):
        # Removed as requested
        pass
        
    def show_settings(self):
        # Removed as requested
        pass
        
    def export_csv_gui(self):
        if not self.check_manager():
            return
            
        filename = filedialog.asksaveasfilename(
            title="שמור קובץ", 
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if filename:
            self.main_window.manager.export_to_csv(filename)
            messagebox.showinfo("הצלחה", f"הקובץ נשמר ב: {filename}")
            
    def export_excel_gui(self):
        if not self.check_manager():
            return
            
        filename = filedialog.asksaveasfilename(
            title="שמור קובץ", 
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if filename:
            try:
                import pandas as pd
                import openpyxl
                coupons = self.main_window.manager.get_all_coupons()
                data = []
                for c in coupons:
                    data.append({
                        'שם עסק': c.business_name,
                        'מקור רכישה': c.purchase_source,
                        'קוד': c.code,
                        'סוג שובר': c.coupon_type,
                        'סוג קוד': c.code_type,
                        'תיאור': c.description,
                        'תנאים': c.terms,
                        'תוקף': c.expiry.strftime("%Y-%m-%d") if c.expiry else "",
                        'יתרה': c.balance,
                        'מועדף': "כן" if c.is_favorite else "לא",
                        'מומש': "כן" if c.is_redeemed else "לא"
                    })
                df = pd.DataFrame(data)
                df.to_excel(filename, index=False, engine='openpyxl')
                messagebox.showinfo("הצלחה", f"הקובץ נשמר ב: {filename}")
            except ImportError as e:
                missing_package = "pandas" if "pandas" in str(e) else "openpyxl"
                install_cmd = f"pip install {missing_package}"
                messagebox.showerror(
                    "שגיאה", 
                    f"חסר חבילת {missing_package}.\n\n"
                    f"כדי להתקין, הרץ בטרמינל:\n{install_cmd}"
                )
            except Exception as e:
                messagebox.showerror("שגיאה", f"שגיאה בייצוא לאקסל: {str(e)}")
            
    def show_alerts(self):
        if not self.check_manager():
            return
            
        now = date.today()
        expiring = []
        for c in self.main_window.manager.get_all_coupons():
            if c.expiry and 0 <= (c.expiry - now).days <= self.user_alert_days.get():
                expiring.append(c)
                
        if not expiring:
            messagebox.showinfo("התראות", "אין שוברים שעומדים לפוג בקרוב.")
            return
            
        msg = "\n".join([
            f"{c.business_name} | {c.expiry.strftime('%Y-%m-%d')} | {c.balance}₪"
            for c in expiring
        ])
        messagebox.showinfo("שוברים שעומדים לפוג", msg)
        
    def show_statistics(self):
        if not self.check_manager():
            return
            
        coupons = self.main_window.manager.get_all_coupons()
        
        # Calculate statistics
        total_coupons = len(coupons)
        total_value = sum(float(c.balance) for c in coupons if c.balance)
        active_coupons = sum(1 for c in coupons if not c.is_expired() and not c.is_redeemed)
        expired_coupons = sum(1 for c in coupons if c.is_expired())
        favorite_coupons = sum(1 for c in coupons if c.is_favorite)
        
        # Create statistics window
        win = tk.Toplevel(self.parent)
        win.title("סטטיסטיקות")
        
        tk.Label(win, text="סטטיסטיקות שוברים", 
                font=('Arial', 14, 'bold')).pack(pady=10)
                
        stats = [
            f"סה\"כ שוברים: {total_coupons}",
            f"ערך כולל: ₪{total_value}",
            f"שוברים פעילים: {active_coupons}",
            f"שוברים שפג תוקפם: {expired_coupons}",
            f"שוברים מועדפים: {favorite_coupons}"
        ]
        
        for stat in stats:
            tk.Label(win, text=stat, font=('Arial', 12)).pack(pady=5)
            
        tk.Button(win, text="סגור", 
                 command=win.destroy, 
                 bg="#7d7df2", fg="white").pack(pady=10)
