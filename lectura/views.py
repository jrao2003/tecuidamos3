from django.shortcuts import render
from django.conf import settings
import os
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from PyPDF2 import PdfReader  # Para extraer texto de PDFs
    # import pdfplumber  # Para una extracción más precisa
from docx import Document  # Para manejar archivos .docx
import easyocr  # Para realizar OCR en imágenes
from paddleocr import PaddleOCR 
from gtts import gTTS   


def texto_a_audio(texto, archivo_salida):
        """Convierte texto a un archivo de audio MP3."""
        tts = gTTS(text=texto, lang="es", slow=False)
        tts.save(archivo_salida)
        print(f"Audio guardado en: {archivo_salida}")    


def read_image_with_paddleocr(file_path):
        """Realiza OCR en una imagen usando PaddleOCR."""
        ocr = PaddleOCR(use_angle_cls=True, lang="es")
        result = ocr.ocr(file_path, cls=True)
        texto_extraido = [line[1][0] for line in result[0]]
        return " ".join(texto_extraido)    


def read_pdf(file_path):
        """Lee texto de un PDF usando PyPDF2."""
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text    


def read_docx(file_path):
        """Lee texto de un documento Word (.docx)."""
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text    


# Create your views here.
def bienvenida(request):
        return render(request, 'index.html')        

def cargar_archivo(request):
        """Procesa el archivo subido y genera un MP3 con el contenido."""
        if request.method == "POST" and request.FILES["file"]:
            archivo = request.FILES["file"]

            # Guardar el archivo en la carpeta local
            file_path = os.path.join(settings.MEDIA_ROOT, archivo.name)
            if os.path.exists(file_path):
                os.remove(file_path)
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            filename = fs.save(archivo.name, archivo)
            file_url = os.path.join(settings.MEDIA_URL, filename)

            # Determinar el tipo de archivo
            file_type = archivo.content_type

            # Procesar el archivo y extraer el contenido
            if file_type == "application/pdf":
                print("El archivo subido es un PDF.")
                contenido = read_pdf(file_path)
            elif file_type in ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
                print("El archivo subido es un documento Word.")
                contenido = read_docx(file_path)
            elif file_type.startswith("image/"):
                print("El archivo subido es una imagen.")
                contenido = read_image_with_paddleocr(file_path)
            else:
                print("El tipo de archivo subido no está reconocido.")
                contenido = "Tipo de archivo no soportado."

            print(contenido)

            # Crear el archivo MP3 del contenido
            audio_path = os.path.join(settings.MEDIA_ROOT, f"{os.path.splitext(archivo.name)[0]}.mp3")
            texto_a_audio(contenido, audio_path)

            # Generar la URL del MP3
            audio_url = os.path.join(settings.MEDIA_URL, f"{os.path.splitext(archivo.name)[0]}.mp3")

            # Renderizar la página con las URLs del archivo y audio
            return render(request, "leer.html", {"file_url": file_url, "contenido": contenido, "audio_url": audio_url})

        return render(request, "index.html")    


def subir_foto(request):
    """Procesa la foto subida, realiza OCR y genera un MP3 del texto extraído."""
    if request.method == 'POST' and 'photo' in request.FILES:
        photo = request.FILES['photo']
        save_path = os.path.join(settings.MEDIA_ROOT, 'fotos', photo.name)

        # Guarda la foto en la carpeta media/fotos
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'fotos'), exist_ok=True)  # Asegurarse de que la carpeta exista
        with open(save_path, 'wb+') as destination:
            for chunk in photo.chunks():
                destination.write(chunk)

        # Realizar OCR en la foto
        contenido = read_image_with_paddleocr(save_path)
        print(f"Texto extraído de la foto: {contenido}")

        # Crear el archivo MP3 del texto extraído
        audio_path = os.path.join(settings.MEDIA_ROOT, 'fotos', f"{os.path.splitext(photo.name)[0]}.mp3")
        texto_a_audio(contenido, audio_path)

        # Generar las URLs para la foto y el audio
        photo_url = f"{settings.MEDIA_URL}fotos/{photo.name}"
        audio_url = f"{settings.MEDIA_URL}fotos/{os.path.splitext(photo.name)[0]}.mp3"
        print(photo_url, audio_url)

        # Renderizar la página con las URLs y el texto extraído
        return render(request, 'foto.html', {'photo_url': photo_url, 'contenido': contenido, 'audio_url': audio_url})

    elif request.method == 'GET':
        # Buscar el archivo de imagen más reciente en la carpeta media/fotos
        folder_path = os.path.join(settings.MEDIA_ROOT, 'fotos')
        if os.path.exists(folder_path):
            image_files = sorted(
                [f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))],
                key=lambda x: os.path.getmtime(os.path.join(folder_path, x)),
                reverse=True
            )
            audio_files = sorted(
                [f for f in os.listdir(folder_path) if f.endswith('.mp3')],
                key=lambda x: os.path.getmtime(os.path.join(folder_path, x)),
                reverse=True
            )

            # Si hay archivos disponibles, obtener el más reciente
            photo_url = f"{settings.MEDIA_URL}fotos/{image_files[0]}" if image_files else None
            audio_url = f"{settings.MEDIA_URL}fotos/{audio_files[0]}" if audio_files else None
        else:
            photo_url = None
            audio_url = None

        return render(request, 'foto.html', {'photo_url': photo_url, 'audio_url': audio_url, 'contenido': None})
