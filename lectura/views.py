from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def bienvenida(request):
    return render(request, 'index.html')

def cargar_archivo(request):
    #aqui va el back de cargar archivo
    return render(request, 'leer.html')

def subir_foto(request):
    #aqui va el back de subir foto
    return render(request, 'foto.html')