from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .models import Club, UserProfile 
from django.contrib import messages
from .forms import RegistrationForm
from .models import Payment, Club, TrialRecord
from django.contrib.auth.decorators import login_required


def login_view(request):
    if request.method == 'POST':
        club_id = request.POST.get('club_id')
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            club = Club.objects.get(club_id=club_id)
        except Club.DoesNotExist:
            messages.error(request, "Club ID không tồn tại.")
            return redirect('login')

        user = authenticate(request, username=username, password=password)
        if user:
            if hasattr(user, 'userprofile') and user.userprofile.club == club:
                login(request, user)
                return redirect('dashboard')  # trang sau đăng nhập
            else:
                messages.error(request, "Tài khoản không thuộc về Club này.")
        else:
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không đúng.")
    return render(request, 'login.html')


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            club_name = form.cleaned_data['club_name']
            club_id = form.cleaned_data['club_id']
            phone = form.cleaned_data['phone']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            purchase_type = form.cleaned_data['purchase_type']
            purchase_years = form.cleaned_data.get('purchase_years')
            payment_method = form.cleaned_data.get('payment_method')
            
            # Tạo Club nếu chưa tồn tại
            club, created = Club.objects.get_or_create(
                club_id=club_id,
                defaults={'name': club_name}
            )
            if not created:
                club.name = club_name
                club.save()
            
            # Kiểm tra xem email (sử dụng làm username) đã tồn tại hay chưa
            if User.objects.filter(username=email).exists():
                messages.error(request, "Tài khoản với email này đã tồn tại.")
                return redirect('register')
            
            # Tạo tài khoản người dùng
            user = User.objects.create_user(username=email, email=email, password=password)
            
            # Tạo profile cho người dùng với role mặc định (ở đây mặc định là 'owner', có thể tùy chỉnh)
            UserProfile.objects.create(user=user, club=club, role='owner')
            
            # Xử lý logic mua trial hoặc mua
            if purchase_type == 'trial':
                # Lưu thông tin trial: tạo bản ghi TrialRecord
                TrialRecord.objects.create(phone=phone)
                # Tiếp theo có thể lưu thông tin trial trong giao dịch, tính thời hạn 14 ngày, v.v.
            elif purchase_type == 'purchase':
                # Xử lý logic mua: tính discount dựa vào số năm mua
                discount = 0
                if purchase_years == 1:
                    discount = 2
                elif purchase_years == 3:
                    discount = 5
                elif purchase_years == 5:
                    discount = 10
                # Với mua vĩnh viễn, bạn có thể thiết lập điều kiện riêng (ví dụ: discount = 15)
                # Lưu thông tin giao dịch mua và chuyển đến trang thanh toán.
                pass
            
            # Sau khi đăng ký thành công, chuyển đến trang thanh toán
            return redirect('payment_page')
        else:
            messages.error(request, "Vui lòng kiểm tra lại thông tin đăng ký.")
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})



PURCHASE_TYPE_CHOICES = (
    ('trial', 'Trial 14 ngày'),
    ('purchase', 'Mua'),
)
PAYMENT_METHOD_CHOICES = (
    ('qr', 'Quét QR code'),
    ('visa', 'Thẻ Visa'),
    )
@login_required
def payment_page(request):
    if request.method == 'POST':
        # Giả sử các thông tin thanh toán được gửi từ form
        payment_method = request.POST.get('payment_method')
        purchase_type = request.POST.get('purchase_type')
        purchase_years = request.POST.get('purchase_years') or None
        
        # Tính toán amount và discount (ví dụ đơn giản)
        amount = 1000.00  # Giá gốc, ví dụ
        discount = 0
        if purchase_type == 'purchase' and purchase_years:
            purchase_years = int(purchase_years)
            if purchase_years == 1:
                discount = 2
            elif purchase_years == 3:
                discount = 5
            elif purchase_years == 5:
                discount = 10
            # Giả sử, amount giảm theo phần trăm discount
            amount = amount * (1 - discount / 100)
        elif purchase_type == 'trial':
            amount = 0  # Trial miễn phí, nhưng cần lưu thông tin trial
        
        # Ở đây bạn tích hợp logic thanh toán thật (gọi API của cổng thanh toán)
        # Giả lập thành công:
        Payment.objects.create(
            user=request.user,
            club=request.user.userprofile.club,
            purchase_type=purchase_type,
            purchase_years=purchase_years,
            discount=discount,
            amount=amount,
            payment_method=payment_method,
        )
        messages.success(request, "Thanh toán thành công!")
        return redirect('dashboard')  # Chuyển về trang dashboard hoặc trang chủ
    else:
        # Nếu phương thức thanh toán là QR code, bạn có thể hiển thị hình QR code (ví dụ từ URL tĩnh hoặc sinh mã QR động)
        context = {
            'payment_methods': dict(PAYMENT_METHOD_CHOICES),
        }
        return render(request, 'payment_page.html', context)