from django.shortcuts import render
from django.conf import settings
import os
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage





# Create your views here.
def bienvenida(request):
    return render(request, 'index.html')

def cargar_archivo(request):
    #aqui va el back de cargar archivo
    if request.method == 'POST' and request.FILES['file']:
        archivo_pdf = request.FILES['file']
        # Guardar el archivo en la carpeta local
        file_path = os.path.join(settings.MEDIA_ROOT, 'lectura.pdf')
        if os.path.exists(file_path):
            os.remove(file_path)
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        filename = fs.save('lectura.pdf', archivo_pdf)
        print(filename)
        file_url = os.path.join(settings.MEDIA_URL, filename)
        print(file_url)
        return render(request, 'leer.html', {'file_url': file_url})
    return render(request, 'index.html')

def subir_foto(request):
    #aqui va el back de subir foto
    if request.method == 'POST' and request.FILES.get('photo'):
        photo = request.FILES['photo']
        save_path = os.path.join(settings.MEDIA_ROOT, 'fotos', photo.name)

        # Guarda la foto en la carpeta media/fotos
        with open(save_path, 'wb+') as destination:
            for chunk in photo.chunks():
                destination.write(chunk)

        # Genera la URL para acceder al archivo
        photo_url = os.path.join(settings.MEDIA_URL, 'fotos', photo.name)
        return render(request, 'foto.html', {'photo_url': photo_url})

    photo_url = os.path.join(settings.MEDIA_URL, 'fotos', 'captured_photo.png')
    return render(request, 'foto.html', {'photo_url': photo_url})