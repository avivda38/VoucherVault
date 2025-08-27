import sqlite3
import uuid
from coupon import Coupon
from datetime import date
from database import (
    get_user_coupons as db_get_user_coupons,
    get_deleted_coupons as db_get_deleted_coupons,
    add_coupon as db_add_coupon,
    update_coupon as db_update_coupon,
    soft_delete_coupon as db_soft_delete_coupon,
    restore_coupon as db_restore_coupon,
    permanent_delete_coupon as db_permanent_delete_coupon,
    toggle_favorite as db_toggle_favorite,
    get_user_logs,
    filter_and_sort_coupons as db_filter_sort,
    add_log
)
from database import get_user_logs
import json

class CouponManager:
    def __init__(self, user_id):
        self.user_id = user_id

    def log(self, action, details):
        add_log(self.user_id, action, details)

    def get_all_coupons(self):
        return db_get_user_coupons(self.user_id)

    def get_deleted_coupons(self):
        return db_get_deleted_coupons(self.user_id)

    def add_new_coupon(self, code, business_name, purchase_source, discount, coupon_type, code_type, category,
                       description, terms, is_favorite, cvv, expiry, balance, image_path):
        coupon_id = db_add_coupon(
            user_id=self.user_id, code=code, business_name=business_name,
            purchase_source=purchase_source, discount=discount, coupon_type=coupon_type,
            code_type=code_type, category=category, description=description, terms=terms,
            is_favorite=is_favorite, cvv=cvv, expiry=expiry, balance=balance,
            image_path=image_path
        )
        details = f"קוד: {code}, בית עסק: {business_name}, יתרה: {balance:.2f} ₪"
        self.log("הוספת שובר", details)
        return coupon_id

    def remove_coupon(self, coupon_id):
        """Soft delete a coupon"""
        if db_soft_delete_coupon(coupon_id):
            # Get coupon details before deletion
            coupon = next((c for c in self.get_all_coupons() if c.id == coupon_id), None)
            if coupon:
                details = f" בית עסק: {coupon.business_name}, יתרה: {coupon.balance:.2f} ₪"
                self.log("מחיקת שובר", details)
            return True
        return False

    def redeem_coupon(self, coupon_id):
        """Mark a coupon as redeemed"""
        coupon = next((c for c in self.get_all_coupons() if c.id == coupon_id), None)
        if coupon:
            coupon.is_redeemed = True
            coupon.balance = 0
            if self.update_coupon(coupon):
                details = f" בית עסק: {coupon.business_name}, יתרה: {coupon.balance:.2f} ₪"
                self.log("מימוש שובר", details)
                return True
        return False

    def restore_coupon(self, coupon_id):
        """Restore a soft-deleted coupon"""
        if db_restore_coupon(coupon_id):
            # Get coupon details before restoration
            coupon = next((c for c in self.get_deleted_coupons() if c.id == coupon_id), None)
            if coupon:
                details = f" בית עסק: {coupon.business_name}, יתרה: {coupon.balance:.2f} ₪"
                self.log("שחזור שובר", details)
            return True
        return False

    def permanent_delete_coupon(self, coupon_id):
        """Permanently delete a coupon"""
        if db_permanent_delete_coupon(coupon_id):
            # Get coupon details before permanent deletion
            coupon = next((c for c in self.get_deleted_coupons() if c.id == coupon_id), None)
            if coupon:
                details = f" בית עסק: {coupon.business_name}, יתרה: {coupon.balance:.2f} ₪"
                self.log("מחיקה סופית", details)
            return True
        return False

    def update_coupon(self, coupon: Coupon):
        conn = sqlite3.connect("voucher_vault.db")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE coupons SET
                business_name=?, purchase_source=?, code=?, discount=?,
                coupon_type=?, code_type=?, category=?, description=?, terms=?, 
                cvv=?, expiry=?, balance=?, is_favorite=?, image_path=?, is_redeemed=?
            WHERE id=? AND user_id=?
        """, (
            coupon.business_name, coupon.purchase_source, coupon.code, coupon.discount,
            coupon.coupon_type, coupon.code_type, coupon.category, coupon.description, coupon.terms,
            coupon.cvv, coupon.expiry.isoformat() if coupon.expiry else None, coupon.balance,
            int(coupon.is_favorite), coupon.image_path, int(coupon.is_redeemed),
            coupon.id, self.user_id
        ))
        conn.commit()
        updated_rows = cursor.rowcount
        conn.close()
        if updated_rows > 0:
            details = f" בית עסק: {coupon.business_name}, יתרה: {coupon.balance:.2f} ₪"
            self.log("עדכון שובר", details)
        return updated_rows > 0

    def mark_favorite(self, coupon_id, is_favorite):
        coupon = next((c for c in self.get_all_coupons() if c.id == coupon_id), None)
        result = db_toggle_favorite(self.user_id, coupon_id)
        if result and coupon:
            action = "סימון שובר כמועדף" if is_favorite else "הסרת מועדף"
            details = f" בית עסק: {coupon.business_name}, יתרה: {coupon.balance:.2f} ₪"
            self.log(action, details)
        return result

    def mark_redeemed(self, coupon_id, is_redeemed):
        coupon = next((c for c in self.get_all_coupons() if c.id == coupon_id), None)
        result = db_update_coupon(coupon_id, {"is_redeemed": int(is_redeemed)})
        if result and coupon:
            action = "סימון כשובר מומש" if is_redeemed else "ביטול מימוש"
            details = f" בית עסק: {coupon.business_name}, יתרה: {coupon.balance:.2f} ₪"
            self.log(action, details)
        return result

    def get_logs(self):
        response = get_user_logs(self.user_id)
        if response.get("status") == "ok":
            return response.get("logs", [])
        return []


    def filter_coupons(self, filters, sort_by="business_name ASC"):
        return db_filter_sort(self.user_id, filters, sort_by)

    def export_to_csv(self, filename):
        import csv
        coupons = self.get_all_coupons()
        with open(filename, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "ID", "UserID", "Code", "Business Name", "Purchase Source", "Discount", "Coupon Type",
                "Code Type", "Description", "Terms", "Favorite", "CVV", "Expiry", "Balance", "Image Path", "Redeemed"
            ])
            for c in coupons:
                writer.writerow([
                    c.id, c.user_id, c.code, c.business_name, c.purchase_source, c.discount, c.coupon_type, c.code_type,
                    c.description, c.terms, int(c.is_favorite), c.cvv, c.expiry.isoformat() if c.expiry else "",
                    c.balance, c.image_path, int(c.is_redeemed)
                ])
        self.log("ייצוא קובץ CSV", filename)

    def duplicate_coupon(self, coupon: Coupon):
        # Duplicate coupon logic (assumes Coupon object is passed)
        new_code = coupon.code + "_copy"  # Or generate a new unique code as needed
        coupon_id = db_add_coupon(
            user_id=self.user_id, code=new_code, business_name=coupon.business_name,
            purchase_source=coupon.purchase_source, discount=coupon.discount, coupon_type=coupon.coupon_type,
            code_type=coupon.code_type, category=coupon.category, description=coupon.description, terms=coupon.terms,
            is_favorite=coupon.is_favorite, cvv=coupon.cvv, expiry=coupon.expiry, balance=coupon.balance,
            image_path=coupon.image_path
        )
        details = f" בית עסק: {coupon.business_name}, יתרה: {coupon.balance:.2f} ₪"
        self.log("שכפול שובר", details)
        return coupon_id

    def update_coupon_fields(self, coupon_id, fields: dict):
        return db_update_coupon(coupon_id, fields)

