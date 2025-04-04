from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Club(models.Model):
    name = models.CharField(max_length=100)
    club_id = models.CharField(max_length=20, unique=True)  # Club ID
    address = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} ({self.club_id})"

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('owner', 'Chủ'),
        ('manager', 'Quản lý'),
        ('staff', 'Nhân viên'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff')

    def __str__(self):
        return f"{self.user.username} - {self.club.club_id} ({self.get_role_display()})"

# Model lưu thông tin số điện thoại đã dùng trial
class TrialRecord(models.Model):
    phone = models.CharField(max_length=15, unique=True)
    trial_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.phone


PURCHASE_TYPE_CHOICES = (
    ('trial', 'Trial 14 ngày'),
    ('purchase', 'Mua'),
)
PAYMENT_METHOD_CHOICES = (
    ('qr', 'Quét QR code'),
    ('visa', 'Thẻ Visa'),
    )
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey('Club', on_delete=models.CASCADE)
    purchase_type = models.CharField(max_length=10, choices=PURCHASE_TYPE_CHOICES)
    purchase_years = models.IntegerField(null=True, blank=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    payment_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.payment_method}"