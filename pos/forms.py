from django import forms
from .models import TrialRecord  # Import model TrialRecord để kiểm tra trial

class RegistrationForm(forms.Form):
    club_name = forms.CharField(label="Tên Club", max_length=100, required=True)
    club_id = forms.CharField(label="Club ID", max_length=20, required=True)
    phone = forms.CharField(label="SĐT", max_length=15, required=True)
    email = forms.EmailField(label="Email", required=True)
    password = forms.CharField(
        label="Password", 
        widget=forms.PasswordInput, 
        min_length=8, 
        required=True
    )
    confirm_password = forms.CharField(
        label="Confirm Password", 
        widget=forms.PasswordInput, 
        required=True
    )
    
    PURCHASE_CHOICES = (
        ('trial', 'Trial 14 ngày'),
        ('purchase', 'Mua'),
    )
    purchase_type = forms.ChoiceField(
        label="Loại mua", 
        choices=PURCHASE_CHOICES, 
        required=True
    )
    
    # Nếu chọn mua, nhập số năm mua (bắt buộc nếu purchase_type == 'purchase')
    purchase_years = forms.IntegerField(
        label="Số năm mua", 
        min_value=1, 
        required=False
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('qr', 'Quét QR code'),
        ('visa', 'Thẻ Visa'),
    )
    payment_method = forms.ChoiceField(
        label="Phương thức thanh toán", 
        choices=PAYMENT_METHOD_CHOICES, 
        required=False
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        purchase_type = cleaned_data.get("purchase_type")
        purchase_years = cleaned_data.get("purchase_years")
        phone = cleaned_data.get("phone")
        
        # Kiểm tra mật khẩu
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Mật khẩu không khớp.")
        
        # Nếu chọn mua, số năm mua là bắt buộc
        if purchase_type == 'purchase' and not purchase_years:
            self.add_error('purchase_years', "Vui lòng nhập số năm mua khi chọn 'Mua'.")
        
        # Nếu chọn trial, kiểm tra số điện thoại đã dùng trial chưa
        if purchase_type == 'trial' and phone:
            from .models import TrialRecord  # Import nội bộ để tránh lỗi vòng lặp import
            if TrialRecord.objects.filter(phone=phone).exists():
                self.add_error('phone', "SĐT này đã được sử dụng cho trial. Vui lòng chọn mua.")
                
        return cleaned_data

