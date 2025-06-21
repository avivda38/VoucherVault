import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from datetime import date
import os
from database import add_log
from coupon_manager import CouponManager
from coupon import Coupon
from tkcalendar import DateEntry

class CouponsFrame:
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.frame = tk.Frame(parent)
        
        # Initialize coupon-related frames
        self.list_frame = tk.Frame(self.frame)
        self.add_frame = tk.Frame(self.frame)
        self.search_frame = tk.Frame(self.frame)
        self.expiring_frame = tk.Frame(self.frame)
        self.favorites_frame = tk.Frame(self.frame)
        
        self.selected_image_path = None
        
    def show(self):
        self.frame.pack(fill="both", expand=True)
        self.frame.tkraise()
        self.show_main()
        
    def hide(self):
        self.frame.pack_forget()
        
    def check_manager(self):
        if not self.main_window.manager:
            messagebox.showerror("שגיאה", "יש להתחבר תחילה")
            self.main_window.show_auth()
            return False
        return True
        
    def show_main(self):
        if not self.check_manager():
            return
            
        for widget in self.frame.winfo_children():
            widget.destroy()
            
        username = self.main_window.current_user[1] if self.main_window.current_user else ""
        tk.Label(self.frame, text=f"ברוך/ה הבא/ה, {username}!", 
                font=('Arial', 22, 'bold')).pack(pady=15)
        tk.Label(self.frame, text="מה תרצה לעשות היום?", 
                font=('Arial', 14)).pack(pady=10)
                
        tiles = [
            ("הוסף שובר חדש", self.show_add_coupon, "#52c6e6"),
            ("הקופונים שלי", self.show_coupons, "#f2a940"),
            ("חיפוש קופונים", self.show_search, "#52cc98"),
            ("עומדים לפוג בקרוב", self.show_expiring, "#e86c5e"),
            ("מועדפים", self.show_favorites, "#ffd700"),
            ("יומן פעילות", lambda: self.main_window.extras_frame.show_logs(), "#7d7df2"),
        ]
        
        main_tiles = tk.Frame(self.frame)
        main_tiles.pack(expand=True)
        rows = [tiles[i:i+3] for i in range(0, len(tiles), 3)]
        
        for row in rows:
            fr = tk.Frame(main_tiles)
            fr.pack(pady=20)
            for title, func, color in row:
                btn = tk.Button(
                    fr, text=title, width=23, height=5, 
                    font=('Arial', 17, 'bold'),
                    bg=color, fg="black", command=func, 
                    relief="raised", bd=4, 
                    activebackground="#e0e0e0", cursor="hand2"
                )
                btn.pack(side="right", padx=20)

    def show_add_coupon(self):
        if not self.check_manager():
            return
            
        win = tk.Toplevel(self.parent)
        win.title("הוספת שובר חדש")
        win.geometry("500x900")
        win.grab_set()
        win.transient(self.parent)
        
        # Create a frame for the form
        form_frame = tk.Frame(win, padx=20, pady=20)
        form_frame.pack(fill="both", expand=True)
        
        # Business name
        tk.Label(form_frame, text="שם העסק:").pack(pady=5)
        business_name = tk.Entry(form_frame)
        business_name.pack()
        
        # Purchase source
        tk.Label(form_frame, text="מקור רכישה:").pack(pady=5)
        purchase_source = tk.Entry(form_frame)
        purchase_source.pack()
        
        # Code
        tk.Label(form_frame, text="קוד:").pack(pady=5)
        code = tk.Entry(form_frame, width=30)  # Wider field for codes
        code.pack()
        
        # Discount
        tk.Label(form_frame, text="הנחה:").pack(pady=5)
        discount = tk.Entry(form_frame)
        discount.pack()
        
        # Coupon type
        tk.Label(form_frame, text="סוג שובר:").pack(pady=5)
        coupon_type = ttk.Combobox(form_frame, values=["תו נטען", "מימוש מלא", "מימוש חלקי", "אחר"], state="readonly")
        coupon_type.pack()
        
        # Code type
        tk.Label(form_frame, text="סוג קוד:").pack(pady=5)
        code_type = ttk.Combobox(form_frame, values=["QR", "מספר", "אלפאנומרי", "כרטיס מגנטי", "אחר"], state="readonly")
        code_type.pack()
        
        # Category
        tk.Label(form_frame, text="קטגוריה:").pack(pady=5)
        category = ttk.Combobox(form_frame, values=["מזון", "ביגוד", "הנעלה", "אלקטרוניקה", "תיירות", "בריאות", "פנאי", "אחר"], state="readonly")
        category.pack()
        
        # Description
        tk.Label(form_frame, text="תיאור:").pack(pady=5)
        description = tk.Entry(form_frame)  # Changed to Entry
        description.pack()
        
        # Terms
        tk.Label(form_frame, text="תנאים:").pack(pady=5)
        terms = tk.Entry(form_frame)  # Changed to Entry
        terms.pack()
        
        # Favorite
        is_favorite = tk.BooleanVar()
        tk.Checkbutton(form_frame, text="★ הוספה למועדפים", variable=is_favorite).pack(pady=5)
        
        # CVV
        tk.Label(form_frame, text="CVV:").pack(pady=5)
        cvv = tk.Entry(form_frame)
        cvv.pack()
        
        # Expiry date
        tk.Label(form_frame, text="תוקף:").pack(pady=5)

        expiry_date = DateEntry(
            form_frame,
            mindate=date.today(),
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='dd/mm/yy'
        )
        expiry_date.pack(pady=4)


        # Balance
        tk.Label(form_frame, text="יתרה:").pack(pady=5)
        balance = tk.Entry(form_frame)
        balance.pack()
        
        # Image
        self.selected_image_path = None
        def select_image():
            file_path = filedialog.askopenfilename(
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
            )
            if file_path:
                self.selected_image_path = file_path
                image_label.config(text=f"נבחר: {os.path.basename(file_path)}")
                
        tk.Button(form_frame, text="בחר תמונה", command=select_image).pack(pady=5)
        image_label = tk.Label(form_frame, text="לא נבחרה תמונה")
        image_label.pack()
        
        def save_coupon():
            try:
                # Validate required fields
                if not business_name.get().strip():
                    messagebox.showerror("שגיאה", "חובה להזין שם עסק", parent=win)
                    return
                    
                if not code.get().strip():
                    messagebox.showerror("שגיאה", "חובה להזין קוד", parent=win)
                    return
                    
                if not coupon_type.get():
                    messagebox.showerror("שגיאה", "חובה לבחור סוג שובר", parent=win)
                    return
                    
                if not code_type.get():
                    messagebox.showerror("שגיאה", "חובה לבחור סוג קוד", parent=win)
                    return
                    
                if not category.get():
                    messagebox.showerror("שגיאה", "חובה לבחור קטגוריה", parent=win)
                    return
                    
                # Get values
                code_val = code.get().strip()
                business_name_val = business_name.get().strip()
                purchase_source_val = purchase_source.get().strip()
                discount_val = float(discount.get()) if discount.get().strip() else None
                coupon_type_val = coupon_type.get()
                code_type_val = code_type.get()
                category_val = category.get()
                description_val = description.get().strip()  # Changed to get() for Entry
                terms_val = terms.get().strip()  # Changed to get() for Entry
                is_favorite_val = is_favorite.get()
                cvv_val = cvv.get().strip()
                expiry_date_val = expiry_date.get_date()
                balance_val = float(balance.get()) if balance.get().strip() else None
                
                self.main_window.manager.add_new_coupon(
                    code=code_val, business_name=business_name_val, purchase_source=purchase_source_val, 
                    discount=discount_val, coupon_type=coupon_type_val, code_type=code_type_val, category=category_val,
                    description=description_val, terms=terms_val, is_favorite=is_favorite_val, cvv=cvv_val, 
                    expiry=expiry_date_val, balance=balance_val, image_path=self.selected_image_path
                )
                messagebox.showinfo("הצלחה", "השובר נוסף בהצלחה!", parent=win)
                win.grab_release()
                win.destroy()
                self.show_coupons()
            except ValueError as e:
                messagebox.showerror("שגיאה", f"שגיאה בערך מספרי: {str(e)}", parent=win)
            except Exception as e:
                messagebox.showerror("שגיאה", f"אירעה שגיאה בעת הוספת השובר: {str(e)}", parent=win)

        tk.Button(form_frame, text="הוסף קופון", command=save_coupon,
                  font=('Arial', 12, 'bold'), width=20, height=2,
                  bg="#7d7df2", fg="white").pack(pady=15)

    def show_coupons(self):
        if not self.check_manager():
            return
            
        for widget in self.frame.winfo_children():
            widget.destroy()
            
        tk.Label(self.frame, text="הקופונים שלי", 
                font=('Arial', 16, 'bold')).pack(pady=10)

        headers = ["מועדפים", "שם עסק", "מקור רכישה", "קוד", "סוג", "תיאור", "תנאים", "CVV", "תוקף", "יתרה", "מחיקה", "עדכון", "מימוש", "שכפל"]
        fr_table = tk.Frame(self.frame)
        fr_table.pack(pady=7, fill="x", padx=10)
        
        # Define column widths
        col_widths = {
            "מועדפים": 5,  # Increased from 3 to 5
            "שם עסק": 15,
            "מקור רכישה": 15,
            "קוד": 20,
            "סוג": 12,
            "תיאור": 15,
            "תנאים": 15,
            "CVV": 8,
            "תוקף": 12,
            "יתרה": 10,
            "מחיקה": 8,
            "עדכון": 8,
            "מימוש": 8,
            "שכפל": 8
        }
        
        # Create headers with consistent widths
        for col, h in enumerate(headers):
            width = col_widths[h]
            tk.Label(fr_table, text=h, width=width,
                    font=('Arial', 10, 'bold'),
                    borderwidth=2, relief="groove").grid(row=0, column=col, sticky="ew")

        coupons = self.main_window.manager.get_all_coupons()
        for row, coupon in enumerate(coupons, 1):
            star = "★" if coupon.is_favorite else "☆"
            btn_star = tk.Button(fr_table, text=star, width=2, 
                               command=lambda c=coupon: self.toggle_favorite(c))
            btn_star.grid(row=row, column=0, sticky="ew")
            
            # Add tooltip for favorite star
            def create_tooltip(widget, text):
                def show_tooltip(event):
                    tooltip = tk.Toplevel()
                    tooltip.wm_overrideredirect(True)
                    tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
                    label = tk.Label(tooltip, text=text, justify='right',
                                   background="#ffffe0", relief='solid', borderwidth=1)
                    label.pack()
                    def hide_tooltip():
                        tooltip.destroy()
                    widget.tooltip = tooltip
                    widget.bind('<Leave>', lambda e: hide_tooltip())
                widget.bind('<Enter>', show_tooltip)
            
            create_tooltip(btn_star, "הוספה למועדפים")
            
            vals = [
                coupon.business_name, coupon.purchase_source, coupon.code, 
                coupon.coupon_type, coupon.description, coupon.terms, coupon.cvv,
                coupon.expiry.strftime("%Y-%m-%d") if coupon.expiry else "",
                f"{coupon.balance:.2f}" if coupon.balance is not None else "0.00"
            ]

            for col, (v, h) in enumerate(zip(vals, headers[1:10]), 1):
                width = col_widths[h]
                tk.Label(fr_table, text=str(v), width=width,
                         borderwidth=1, relief="solid", anchor="center").grid(row=row, column=col, sticky="ew")

            # Action buttons with consistent widths
            tk.Button(fr_table, text="מחק", fg="red", width=col_widths["מחיקה"],
                     command=lambda c=coupon: self.delete_coupon(c)).grid(row=row, column=10, sticky="ew")
            tk.Button(fr_table, text="עדכן", fg="blue", width=col_widths["עדכון"],
                     command=lambda c=coupon: self.show_update_coupon(c)).grid(row=row, column=11, sticky="ew")
            tk.Button(fr_table, text="ממש", fg="green", width=col_widths["מימוש"],
                     command=lambda c=coupon: self.redeem_coupon(c)).grid(row=row, column=12, sticky="ew")
            tk.Button(fr_table, text="שכפל", fg="purple", width=col_widths["שכפל"],
                     command=lambda c=coupon: self.duplicate_coupon(c)).grid(row=row, column=13, sticky="ew")

        # Configure grid weights for consistent column widths
        for i in range(len(headers)):
            fr_table.grid_columnconfigure(i, weight=1)

    def toggle_favorite(self, coupon):
        if not self.check_manager():
            return
            
        self.main_window.manager.mark_favorite(coupon.id, not coupon.is_favorite)
        self.show_coupons()

    def delete_coupon(self, coupon):
        if not self.check_manager():
            return
            
        if messagebox.askyesno("מחיקת שובר", "האם אתה בטוח שברצונך למחוק את השובר? הוא יועבר לרשימת השוברים שנמחקו."):
            user_id = self.main_window.current_user[0]
            details = f"קוד: {coupon.code}, בית עסק: {coupon.business_name}, יתרה: {coupon.balance:.2f} ₪"
            self.main_window.manager.remove_coupon(coupon.id)
            self.show_deleted_coupons()

    def show_update_coupon(self, coupon):
        if not self.check_manager():
            return
            
        win = tk.Toplevel(self.parent)
        win.title("עדכון שובר")
        win.geometry("450x800")
        win.grab_set()
        win.transient(self.parent)

        form_frame = tk.Frame(win)
        form_frame.pack(padx=10, pady=10, fill="both", expand=True)

        entries = {}
        
        update_form_fields = [
            ("שם עסק", "entry", coupon.business_name),
            ("מקור רכישה", "entry", coupon.purchase_source),
            ("קוד", "entry", coupon.code),
            ("אחוז הנחה", "entry", coupon.discount),
            ("סוג שובר", "combobox", (["תו נטען", "מימוש מלא", "מימוש חלקי", "אחר"], coupon.coupon_type)),
            ("סוג קוד", "combobox", (["QR", "מספר", "אלפאנומרי", "כרטיס מגנטי", "אחר"], coupon.code_type)),
            ("קטגוריה", "combobox", (["מזון", "ביגוד", "הנעלה", "אלקטרוניקה", "תיירות", "בריאות", "פנאי", "אחר"], coupon.category)),
            ("תיאור", "entry", coupon.description),
            ("תנאים", "entry", coupon.terms),
            ("CVV", "entry", coupon.cvv),
            ("תוקף", "date", coupon.expiry),
            ("יתרה", "entry", coupon.balance)
        ]

        for label, field_type, current_value_data in update_form_fields:
            tk.Label(form_frame, text=label, font=('Arial', 11)).pack(anchor="w", padx=5, pady=2)
            current_value = current_value_data
            options = None

            if field_type == "combobox":
                options, current_value = current_value_data

            if field_type == "entry":
                e = tk.Entry(form_frame, width=40)
                e.insert(0, str(current_value) if current_value is not None else "")
                e.pack(anchor="w", padx=5, fill="x", pady=2)
                entries[label] = e
            elif field_type == "date":
                date_entry = DateEntry(form_frame, 
                                     mindate=date.today(),
                                     width=12,
                                     background='darkblue',
                                     foreground='white',
                                     borderwidth=2,
                                     date_pattern='dd/mm/yy')
                if isinstance(current_value, date):
                    date_entry.set_date(current_value)
                elif isinstance(current_value, str) and current_value:
                    try: 
                        date_entry.set_date(date.fromisoformat(current_value))
                    except ValueError: 
                        pass
                date_entry.pack(anchor="w", padx=5, pady=4)
                date_entry.lift()
                entries[label] = date_entry
            elif field_type == "combobox":
                cb = ttk.Combobox(form_frame, values=options, state="readonly", width=38)
                if current_value and options and current_value in options:
                    cb.set(current_value)
                cb.pack(anchor="w", padx=5, fill="x", pady=2)
                entries[label] = cb
        
        save_update_lambda = lambda w=win, e=entries, c_obj=coupon: self.perform_update_coupon_validation_and_submit(w,e,c_obj)
        tk.Button(form_frame, text="שמור שינויים", command=save_update_lambda,
                  bg="#7d7df2", fg="white", font=('Arial', 12, 'bold')).pack(pady=20)
        win.lift()
        win.focus_force()
        win.protocol("WM_DELETE_WINDOW", lambda w=win: (w.grab_release(), w.destroy()))

    def perform_update_coupon_validation_and_submit(self, win, entries, coupon):
        required_map_update = {
            "שם עסק": "שם השובר", "קוד": "קוד השובר",
            "תוקף": "תאריך תפוגה", "יתרה": "סכום השובר",
            "סוג שובר": "סוג שובר", "סוג קוד": "סוג קוד", "קטגוריה": "קטגוריה"
        }
        for field_key, display_name in required_map_update.items():
            value_widget = entries[field_key]
            value_str = ""
            if isinstance(value_widget, DateEntry):
                value_str = value_widget.get()
                if not value_str:
                    messagebox.showerror("שגיאה בעדכון", f"שדה '{display_name}' הוא שדה חובה.", parent=win)
                    return
                try: value_widget.get_date()
                except Exception:
                    messagebox.showerror("שגיאה בעדכון", f"תאריך '{display_name}' אינו חוקי.", parent=win)
                    return
            else:
                value_str = value_widget.get()
                if not value_str:
                    messagebox.showerror("שגיאה בעדכון", f"שדה '{display_name}' הוא שדה חובה.", parent=win)
                    return
            
        discount_str_update = entries["אחוז הנחה"].get()
        discount_update = 0.0
        if discount_str_update:
            try:
                discount_update = float(discount_str_update)
                if not (0 <= discount_update <= 100):
                    messagebox.showerror("שגיאה בעדכון", "אחוז ההנחה חייב להיות בין 0 ל-100.", parent=win)
                    return
            except ValueError:
                messagebox.showerror("שגיאה בעדכון", "אחוז ההנחה חייב להיות מספר תקין.", parent=win)
                return
        
        balance_str_update = entries["יתרה"].get()
        try:
            balance_update = float(balance_str_update)
            if balance_update <= 0:
                messagebox.showerror("שגיאה בעדכון", "סכום השובר חייב להיות מספר חיובי.", parent=win)
                return
        except ValueError:
            messagebox.showerror("שגיאה בעדכון", "סכום השובר חייב להיות מספר תקין.", parent=win)
            return

        # Create details string for the log
        details = f"קוד: {entries['קוד'].get()}, בית עסק: {entries['שם עסק'].get()}, יתרה: {balance_update:.2f} ₪"

        coupon.business_name = entries["שם עסק"].get()
        coupon.purchase_source = entries["מקור רכישה"].get()
        coupon.code = entries["קוד"].get()
        coupon.discount = discount_update
        coupon.coupon_type = entries["סוג שובר"].get()
        coupon.code_type = entries["סוג קוד"].get()
        coupon.category = entries["קטגוריה"].get()
        coupon.description = entries["תיאור"].get()
        coupon.terms = entries["תנאים"].get()
        coupon.cvv = entries["CVV"].get()
        coupon.expiry = entries["תוקף"].get_date()
        coupon.balance = balance_update

        self.main_window.manager.update_coupon(coupon)
        messagebox.showinfo("הצלחה", "השובר עודכן בהצלחה!", parent=win)
        win.grab_release()
        win.destroy()
        self.show_coupons()

    def redeem_coupon(self, coupon):
        if not self.check_manager():
            return
            
        if messagebox.askyesno("מימוש שובר", "האם אתה בטוח שברצונך לממש את השובר?"):
            user_id = self.main_window.current_user[0]
            details = f"קוד: {coupon.code}, בית עסק: {coupon.business_name}, יתרה: {coupon.balance:.2f} ₪"
            self.main_window.manager.redeem_coupon(coupon.id)
            self.show_coupons()

    def show_search(self):
        if not self.check_manager():
            return
            
        for widget in self.frame.winfo_children():
            widget.destroy()
            
        tk.Label(self.frame, text="חיפוש וסינון שוברים", 
                font=('Arial', 16, 'bold')).pack(pady=10)

        search_controls_frame = tk.Frame(self.frame)
        search_controls_frame.pack(pady=5, padx=10, fill="x")

        filter_entries = {}

        tk.Label(search_controls_frame, text="חיפוש טקסט חופשי:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        search_text_var = tk.StringVar()
        tk.Entry(search_controls_frame, textvariable=search_text_var, width=30).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        filter_entries['text_query'] = search_text_var

        all_option = ["הכל"]
        coupon_type_options_search = all_option + ["תו נטען", "מימוש מלא", "מימוש חלקי", "אחר"]
        code_type_options_search = all_option + ["QR", "מספר", "אלפאנומרי", "כרטיס מגנטי", "אחר"]
        category_options_search = all_option + ["מזון", "ביגוד", "הנעלה", "אלקטרוניקה", "תיירות", "בריאות", "פנאי", "אחר"]

        filter_fields = [
            ("סוג שובר:", "coupon_type", coupon_type_options_search, 1),
            ("סוג קוד:", "code_type", code_type_options_search, 2),
            ("קטגוריה:", "category", category_options_search, 3)
        ]

        for label_text, key, options, row_num in filter_fields:
            tk.Label(search_controls_frame, text=label_text).grid(row=row_num, column=0, padx=5, pady=5, sticky="w")
            cb = ttk.Combobox(search_controls_frame, values=options, state="readonly", width=28)
            cb.set("הכל")
            cb.grid(row=row_num, column=1, padx=5, pady=5, sticky="ew")
            filter_entries[key] = cb
        
        search_controls_frame.grid_columnconfigure(1, weight=1)

        results_frame = tk.Frame(self.frame)
        results_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Define column widths for search results - matching the main coupons view
        col_widths = {
            "מועדפים": 5,
            "שם עסק": 15,
            "קוד": 20,
            "סוג שובר": 12,
            "סוג קוד": 12,
            "קטגוריה": 12,
            "תיאור": 15,
            "תנאים": 15,
            "CVV": 8,
            "תוקף": 12,
            "יתרה": 10
        }

        results_headers = ["מועדפים", "שם עסק", "קוד", "סוג שובר", "סוג קוד", "קטגוריה", "תיאור", "תנאים", "CVV", "תוקף", "יתרה"]
        
        # Create a frame for the table
        table_frame = tk.Frame(results_frame)
        table_frame.pack(fill="both", expand=True)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(table_frame)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create headers with grid
        for col, h_text in enumerate(results_headers):
            width = col_widths[h_text]
            tk.Label(scrollable_frame, text=h_text, font=('Arial', 10, 'bold'), 
                     borderwidth=2, relief="groove", width=width, anchor="center").grid(row=0, column=col, sticky="nsew")

        def display_results(coupons_list):
            for widget in scrollable_frame.winfo_children():
                if int(widget.grid_info().get('row', 1)) > 0:  # Don't destroy header row
                    widget.destroy()
            
            if not coupons_list:
                tk.Label(scrollable_frame, text="לא נמצאו שוברים התואמים את החיפוש.", font=('Arial', 12)).grid(row=1, column=0, columnspan=len(results_headers), pady=20)
                return

            for i, coupon in enumerate(coupons_list):
                star = "★" if coupon.is_favorite else "☆"
                vals = [
                    star, coupon.business_name, coupon.code, coupon.coupon_type, coupon.code_type,
                    coupon.category, coupon.description, coupon.terms, coupon.cvv,
                    coupon.expiry.strftime("%Y-%m-%d") if coupon.expiry else "-",
                    f"{coupon.balance:.2f}" if coupon.balance is not None else "0.00"
                ]
                for col, (val_text, h_text) in enumerate(zip(vals, results_headers)):
                    width = col_widths[h_text]
                    tk.Label(scrollable_frame, text=str(val_text), width=width, 
                             borderwidth=1, relief="solid", anchor="center").grid(row=i+1, column=col, sticky="nsew")
            # Make columns expand evenly
            for col in range(len(results_headers)):
                scrollable_frame.grid_columnconfigure(col, weight=1)
        
        def perform_search():
            filters = {}
            for key, widget in filter_entries.items():
                if key == 'text_query': 
                    continue 
                value = widget.get()
                if value != "הכל":
                    filters[key] = value
            
            coupons_result = self.main_window.manager.filter_coupons(filters, sort_by="expiry ASC")
            text_query = filter_entries['text_query'].get().lower()
            if text_query:
                final_results = []
                for coupon in coupons_result:
                    if (text_query in str(coupon.business_name).lower() or 
                        text_query in str(coupon.code).lower() or 
                        text_query in str(coupon.description).lower() or 
                        text_query in str(coupon.terms).lower() or
                        text_query in str(coupon.category).lower()):
                        final_results.append(coupon)
                coupons_result = final_results
            display_results(coupons_result)

        search_button = tk.Button(search_controls_frame, text="חפש", command=perform_search, 
                                  bg="#3498db", fg="white", font=('Arial', 10, 'bold'))
        search_button.grid(row=len(filter_fields) + 1, column=0, columnspan=2, pady=10, sticky="ew")
        perform_search()

    def show_favorites(self):
        if not self.check_manager():
            return
            
        for widget in self.frame.winfo_children():
            widget.destroy()
            
        tk.Label(self.frame, text="מועדפים", 
                font=('Arial', 16, 'bold')).pack(pady=10)
                
        coupons = [c for c in self.main_window.manager.get_all_coupons() if c.is_favorite]
        fr = tk.Frame(self.frame)
        fr.pack(fill="x", padx=10)
        
        # Define headers and their widths
        headers = ["מועדפים", "שם עסק", "קוד", "סוג", "CVV", "תוקף", "יתרה"]
        col_widths = {
            "מועדפים": 5,
            "שם עסק": 15,
            "קוד": 20,
            "סוג": 12,
            "CVV": 8,
            "תוקף": 12,
            "יתרה": 10
        }
        
        # Create headers
        for col, h in enumerate(headers):
            width = col_widths[h]
            tk.Label(fr, text=h, width=width,
                    font=('Arial', 10, 'bold'),
                    borderwidth=2, relief="groove").grid(row=0, column=col, sticky="ew")
        
        for row, coupon in enumerate(coupons, 1):
            star = "★"
            tk.Label(fr, text=star, width=col_widths["מועדפים"]).grid(row=row, column=0, sticky="ew")
            
            vals = [
                coupon.business_name,
                coupon.code,
                coupon.coupon_type,
                coupon.cvv,
                coupon.expiry.strftime("%Y-%m-%d") if coupon.expiry else "",
                f"{coupon.balance:.2f}" if coupon.balance is not None else "0.00"
            ]
            
            for col, (v, h) in enumerate(zip(vals, headers[1:]), 1):
                width = col_widths[h]
                tk.Label(fr, text=str(v), width=width,
                         borderwidth=1, relief="solid", anchor="center").grid(row=row, column=col, sticky="ew")
        
        # Configure grid weights for consistent column widths
        for i in range(len(headers)):
            fr.grid_columnconfigure(i, weight=1)

    def show_expiring(self):
        if not self.check_manager():
            return
            
        for widget in self.frame.winfo_children():
            widget.destroy()
            
        tk.Label(self.frame, text="שוברים שעומדים לפוג", 
                font=('Arial', 16, 'bold')).pack(pady=10)
                
        from datetime import timedelta
        days_alert = 14
        fr = tk.Frame(self.frame)
        fr.pack(fill="x", padx=10)
        
        # Define headers and their widths
        headers = ["שם עסק", "קוד", "סוג", "CVV", "תוקף", "יתרה"]
        col_widths = {
            "שם עסק": 15,
            "קוד": 20,
            "סוג": 12,
            "CVV": 8,
            "תוקף": 12,
            "יתרה": 10
        }
        
        # Create headers
        for col, h in enumerate(headers):
            width = col_widths[h]
            tk.Label(fr, text=h, width=width,
                    font=('Arial', 10, 'bold'),
                    borderwidth=2, relief="groove").grid(row=0, column=col, sticky="ew")
        
        now = date.today()
        expiring = []
        for c in self.main_window.manager.get_all_coupons():
            if c.expiry and 0 <= (c.expiry - now).days <= days_alert:
                expiring.append(c)
                
        for row, coupon in enumerate(expiring, 1):
            msg = f"שים לב! שובר זה עומד לפוג בעוד {(coupon.expiry-now).days} ימים" if coupon.expiry else ""
            tk.Label(fr, text=msg, fg="red", 
                    font=('Arial', 10)).grid(row=row, column=0, columnspan=len(headers), sticky="ew")
            
            vals = [
                coupon.business_name,
                coupon.code,
                coupon.coupon_type,
                coupon.cvv,
                coupon.expiry.strftime("%Y-%m-%d") if coupon.expiry else "",
                f"{coupon.balance:.2f}" if coupon.balance is not None else "0.00"
            ]
            
            for col, (v, h) in enumerate(zip(vals, headers)):
                width = col_widths[h]
                tk.Label(fr, text=str(v), width=width,
                         borderwidth=1, relief="solid", anchor="center").grid(row=row, column=col, sticky="ew")
        
        # Configure grid weights for consistent column widths
        for i in range(len(headers)):
            fr.grid_columnconfigure(i, weight=1)

    def show_deleted_coupons(self):
        if not self.check_manager():
            return
            
        for widget in self.frame.winfo_children():
            widget.destroy()
            
        tk.Label(self.frame, text="שוברים שנמחקו", 
                font=('Arial', 16, 'bold')).pack(pady=10)

        headers = ["שם עסק", "קוד", "תוקף", "יתרה", "שחזור", "מחיקה סופית"]
        fr_table = tk.Frame(self.frame)
        fr_table.pack(pady=7, fill="x", padx=10)
        
        for col, h in enumerate(headers):
            tk.Label(fr_table, text=h, width=15 if col < (len(headers) - 2) else 10,
                    font=('Arial', 10, 'bold'), 
                    borderwidth=1, relief="solid").grid(row=0, column=col, sticky="ew")

        coupons = self.main_window.manager.get_deleted_coupons()
        
        for r, coupon_data in enumerate(coupons, 1):
            coupon = coupon_data if isinstance(coupon_data, Coupon) else Coupon(**coupon_data)

            vals_to_display = [
                coupon.business_name, 
                coupon.code, 
                coupon.expiry.strftime("%Y-%m-%d") if coupon.expiry else "אין",
                f"{coupon.balance:.2f}" if coupon.balance is not None else "0.00"
            ]
            
            for c, v_text in enumerate(vals_to_display):
                tk.Label(fr_table, text=str(v_text), width=15, 
                        borderwidth=1, relief="sunken", anchor="w").grid(row=r, column=c, sticky="ew", padx=1, pady=1)
                        
            tk.Button(fr_table, text="שחזר", fg="green", 
                     command=lambda c_id=coupon.id: self.restore_coupon_action(c_id)).grid(row=r, column=len(vals_to_display), sticky="ew")
            tk.Button(fr_table, text="מחק סופית", fg="red", 
                     command=lambda c_id=coupon.id: self.permanent_delete_coupon_action(c_id)).grid(row=r, column=len(vals_to_display)+1, sticky="ew")
            
        for i in range(len(headers)):
            fr_table.grid_columnconfigure(i, weight=1)

    def restore_coupon_action(self, coupon_id):
        if not self.check_manager(): return
        if messagebox.askyesno("שחזור שובר", "האם אתה בטוח שברצונך לשחזר את השובר?"):
            user_id = self.main_window.current_user[0]
            # Get coupon details before restoring
            coupon = next((c for c in self.main_window.manager.get_deleted_coupons() if c.id == coupon_id), None)
            if coupon:
                details = f"קוד: {coupon.code}, בית עסק: {coupon.business_name}, יתרה: {coupon.balance:.2f} ₪"
            self.main_window.manager.restore_coupon(coupon_id)
            self.show_deleted_coupons()

    def permanent_delete_coupon_action(self, coupon_id):
        if not self.check_manager(): return
        if messagebox.askyesno("מחיקה סופית", "האם אתה בטוח שברצונך למחוק את השובר לצמיתות? הפעולה אינה הפיכה."):
            user_id = self.main_window.current_user[0]
            # Get coupon details before permanent deletion
            coupon = next((c for c in self.main_window.manager.get_deleted_coupons() if c.id == coupon_id), None)
            if coupon:
                details = f"קוד: {coupon.code}, בית עסק: {coupon.business_name}, יתרה: {coupon.balance:.2f} ₪"
            self.main_window.manager.permanent_delete_coupon(coupon_id)
            self.show_deleted_coupons()

    def choose_image_for_coupon(self, parent_win, entries_dict):
        path = filedialog.askopenfilename(
            parent=parent_win, 
            title="בחר תמונה",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if path:
            self.selected_image_path = path
            if "העלה תמונה" in entries_dict and isinstance(entries_dict["העלה תמונה"], tk.Label):
                entries_dict["העלה תמונה"].config(text=os.path.basename(path))

    def duplicate_coupon(self, coupon):
        if not self.check_manager():
            return
            
        # Generate a new unique code
        import random
        import string
        new_code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        try:
            self.main_window.manager.add_new_coupon(
                code=new_code,
                business_name=coupon.business_name,
                purchase_source=coupon.purchase_source,
                discount=coupon.discount,
                coupon_type=coupon.coupon_type,
                code_type=coupon.code_type,
                category=coupon.category,
                description=coupon.description,
                terms=coupon.terms,
                is_favorite=False,  # Start as not favorite
                cvv=coupon.cvv,
                expiry=coupon.expiry,
                balance=coupon.balance,
                image_path=coupon.image_path
            )
            messagebox.showinfo("הצלחה", "השובר שוכפל בהצלחה!")
            self.show_coupons()
        except Exception as e:
            messagebox.showerror("שגיאה", f"אירעה שגיאה בעת שכפול השובר: {str(e)}")
