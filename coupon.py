from datetime import date

class Coupon:
    def __init__(self, id, user_id, code, business_name, purchase_source, discount, coupon_type, code_type, category,
                 description, terms, is_favorite, cvv, expiry, balance, image_path, is_redeemed=0, is_deleted=0):
        self.id = id
        self.user_id = user_id
        self.code = code
        self.business_name = business_name
        self.purchase_source = purchase_source
        self.discount = float(discount) if discount is not None else 0.0
        self.coupon_type = coupon_type
        self.code_type = code_type
        self.category = category
        self.description = description
        self.terms = terms
        self.is_favorite = bool(is_favorite)
        self.cvv = cvv
        try:
            self.expiry = date.fromisoformat(expiry) if isinstance(expiry, str) else (expiry if isinstance(expiry, date) else None)
        except ValueError:
            self.expiry = None # Handle cases where expiry might be an invalid date string
        self.balance = float(balance) if balance is not None else 0.0
        self.image_path = image_path
        self.is_redeemed = bool(is_redeemed)
        self.is_deleted = bool(is_deleted)

    def is_expired(self):
        if self.expiry is None:
            return False
        return self.expiry < date.today()
