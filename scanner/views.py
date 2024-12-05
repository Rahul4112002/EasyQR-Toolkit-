from django.shortcuts import render
from .models import QRCode
import qrcode
from django.core.files.storage import FileSystemStorage
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from pyzbar.pyzbar import decode
from pathlib import Path
from PIL import Image


def validate_mobile_number(mobile_number):
    """Validates that the mobile number is exactly 10 digits."""
    return mobile_number and len(mobile_number) == 10 and mobile_number.isdigit()


def generate_qr(request):
    qr_image_url = None

    if request.method == 'POST':
        mobile_number = request.POST.get('mobile_number')
        data = request.POST.get('qr_data')

        if not validate_mobile_number(mobile_number):
            return render(request, 'scanner/generate.html', {'error': 'Invalid Mobile Number'})

        qr_content = f"{data}|{mobile_number}"
        qr = qrcode.make(qr_content)
        qr_image_io = BytesIO()
        qr.save(qr_image_io, 'PNG')
        qr_image_io.seek(0)

        qr_storage_path = Path(settings.MEDIA_ROOT) / 'qr_codes'
        fs = FileSystemStorage(location=qr_storage_path, base_url='/media/qr_codes/')
        filename = f"{data}_{mobile_number}.png"
        qr_image_content = ContentFile(qr_image_io.read(), name=filename)
        filepath = fs.save(filename, qr_image_content)
        qr_image_url = fs.url(filename)

        QRCode.objects.create(data=data, mobile_number=mobile_number)

    return render(request, 'scanner/generate.html', {'qr_image_url': qr_image_url})


def scan_qr(request):
    result = None

    if request.method == "POST" and request.FILES.get('qr_image'):
        mobile_number = request.POST.get('mobile_number')
        qr_image = request.FILES['qr_image']

        if not validate_mobile_number(mobile_number):
            return render(request, 'scanner/scan.html', {'error': 'Invalid Mobile Number'})

        fs = FileSystemStorage()
        filename = fs.save(qr_image.name, qr_image)
        image_path = Path(fs.location) / filename

        try:
            image = Image.open(image_path)
            decoded_objects = decode(image)

            if decoded_objects:
                qr_content = decoded_objects[0].data.decode('utf-8').strip()
                qr_data, qr_mobile_number = qr_content.split('|')

                qr_entry = QRCode.objects.filter(data=qr_data, mobile_number=qr_mobile_number).first()

                if qr_entry and qr_mobile_number == mobile_number:
                    result = "Scan Success: Valid QR code"
                    qr_entry.delete()

                    qr_image_path = Path(settings.MEDIA_ROOT) / 'qr_codes' / f"{qr_data}_{qr_mobile_number}.png"
                    if qr_image_path.exists():
                        qr_image_path.unlink()
                else:
                    result = "Scan Failed: Invalid QR code"
            else:
                result = "Scan Failed: Unable to decode QR code"
        except Exception as e:
            result = f"Error processing the image: {e}"
        finally:
            if image_path.exists():
                image_path.unlink()

    return render(request, 'scanner/scan.html', {'result': result})
