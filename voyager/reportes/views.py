from django.shortcuts import render, get_object_or_404
from .models import OrdenInterna
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views import generic
from django.core import serializers
from .models import OrdenInterna
from .models import AnalisisCotizacion,Cotizacion,AnalisisMuestra,Muestra,Analisis
from cuentas.models import IFCUsuario
from django.http import Http404
import datetime
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required   #Redireccionar a login si no ha iniciado sesión
def ingreso_cliente(request):
    if request.session._session:   #Revisión de sesión iniciada
        user_logged = IFCUsuario.objects.get(user = request.user)   #Obtener el usuario logeado
        if not user_logged.rol.nombre=="Cliente":   #Si el rol del usuario no es cliente no puede entrar a la página
            raise Http404
        return render(request, 'reportes/ingreso_cliente.html')   #Cargar la plantilla necesaria
    else:
        raise Http404

@login_required   #Redireccionar a login si no ha iniciado sesión
def ingresar_muestras(request):
    if (request.session._session   #Revisión de sesión iniciada
            and request.POST.get('nombre')   #Los post son enviados desde la página anterior
            and request.POST.get('direccion')   #Checar todos los post necesarios para continuar con la forma
            and request.POST.get('pais')
            and request.POST.get('idioma')
            and (request.POST.get('estado1') or (request.POST.get('estado2'))
)
    ):
        user_logged = IFCUsuario.objects.get(user = request.user)    #Obtener el usuario logeado
        if not user_logged.rol.nombre=="Cliente":   #Si el rol del usuario no es cliente no puede entrar a la página
            raise Http404
        if request.POST.get('pais')=="México":   #Condicional sobre seleccionar la variable indicada con del Post
            estado = request.POST.get('estado1')
        else:
            estado = request.POST.get('estado2')
        all_analysis = AnalisisCotizacion.objects.all().filter(cantidad__gte=1,cotizacion__usuario_c=user_logged)   #Obtener todas las cotizaciones del usuario loggeado
        return  render(request, 'reportes/ingresar_muestra.html',{'all_analysis': all_analysis,   #Cargar todas las variables POST dentro de la siguiente plantilla
                                                                  'nombre': request.POST.get('nombre'),
                                                                  'direccion': request.POST.get('direccion'),
                                                                  'pais': request.POST.get('pais'),
                                                                  'estado': estado,
                                                                  'idioma': request.POST.get('idioma'),
                                                                  })
    else:
        raise Http404

@login_required
def indexView(request):
    return render(request, 'reportes/index.html')


@login_required
def ordenes_internas(request):
    ordenes = OrdenInterna.objects.all()
    context = {
        'ordenes': ordenes,
    }
    return render(request, 'reportes/ordenes_internas.html', context)

@login_required
def oi_guardar(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        id = id
        oi = OrdenInterna.objects.get(idOI=id)
        if oi:
            data = serializers.serialize("json", [oi], ensure_ascii=False)
            data = data[1:-1]
            return JsonResponse({"data": data})
        else:
            #objeto ya no existe
            data = 'null'
            return JsonResponse({"data": data})


def consultar_orden(request, id):
    if request.method == 'POST':
        oi = OrdenInterna.objects.get(idOI=id)
        #muestras = Muestra.objects.get(oi = oi)
        if oi:
            data = serializers.serialize("json", [oi], ensure_ascii=False)
            data = data[1:-1]

        """   
        if muestras:
            muestras = serializers.serialize("json", [muestras], ensure_ascii=False)
            muestras = muestras[1:-1]
        else: 
            muestras = {'fields': None}
        """
        return JsonResponse({"data": data})

def actualizar_orden(request):
    if request.method == 'POST':
        oi = OrdenInterna.objects.get(idOI = request.POST['idOI'])
        if oi:
            #Actualizar campos
            oi.estatus = request.POST['estatus']
            oi.localidad = request.POST['localidad']

            #Para las fechas checar si están vacías o formato incorrecto
            if request.POST['fecha_envio'] == "":
                oi.fecha_envio = None    
            else: #falta checar formato incorrecto, se hace en front
                oi.fecha_envio = request.POST['fecha_envio']

            oi.guia_envio = request.POST['guia_envio']
            oi.link_resultados = request.POST['link_resultados']
            oi.formato_ingreso_muestra = request.POST['formato_ingreso_muestra']
            oi.idioma_reporte = request.POST['idioma_reporte']
            oi.mrl = request.POST['mrl']

            #Para las fechas checar si están vacías o formato incorrecto
            if request.POST['fecha_eri'] == "":
                oi.fecha_eri = None    
            else: #falta checar formato incorrecto, se hace en front
                oi.fecha_eri = request.POST['fecha_eri']

            #Para las fechas checar si están vacías o formato incorrecto
            if request.POST['fecha_lab'] == "":
                oi.fecha_lab = None    
            else: #falta checar formato incorrecto, se hace en front
                oi.fecha_lab = request.POST['fecha_lab']


            #Para las fechas checar si están vacías o formato incorrecto
            if request.POST['fecha_ei'] == "":
                oi.fecha_ei = None    
            else: #falta checar formato incorrecto, se hace en front
                oi.fecha_ei = request.POST['fecha_ei']

            oi.notif_e = request.POST['notif_e']
            oi.envio_ti = request.POST['envio_ti']
            oi.cliente_cr = request.POST['cliente_cr']
            #Guardar
            oi.save()
            
            # Cargar de nuevo la orden interna
            oi_actualizada = OrdenInterna.objects.get(idOI = request.POST['idOI'])
            data = serializers.serialize("json", [oi_actualizada], ensure_ascii = False)
            data = data[1:-1]
            # Regresamos información actualizada
            return JsonResponse({"data": data})

@login_required
def muestra_enviar(request): #guia para guardar muestras
    if request.session._session:
        if request.method=='POST':
            if (request.POST.get('nombre')
                    and request.POST.get('direccion')
                    and request.POST.get('pais')
                    and request.POST.get('estado')
                    and request.POST.get('idioma')
                    and request.POST.get('producto')
                    and request.POST.get('variedad')
                    and request.POST.get('parcela')
                    and request.POST.get('pais_destino')
                    and request.POST.get('clave_muestra')
                    and request.POST.get('enviar')
                    and request.POST.get('fecha_muestreo')
            ): #verificar que toda la información necesaria se envíe por POST
                user_logged = IFCUsuario.objects.get(user=request.user) #obtener usuario que inició sesión
                if not user_logged.rol.nombre == "Cliente": #verificar que el usuario pertenezca al grupo con permisos
                    raise Http404
                all_analysis_cot = AnalisisCotizacion.objects.all().filter(cantidad__gte=1,
                                                                       cotizacion__usuario_c=user_logged) #obtener todos los análisis disponibles en las cotizaciones
                phantom_user = IFCUsuario.objects.get(apellido_paterno="Phantom",apellido_materno="Phantom")#obtener usuario fantasma (dummy) para crear las ordenes internas
                muestras_hoy=Muestra.objects.filter(fecha_forma=datetime.datetime.now().date()) #verificar si se ha registrado una muestra en el día
                if muestras_hoy:
                    oi = muestras_hoy[0].oi #si se ha registrado una muestra en el mismo día, usar la misma orden interna
                else: #crear orden interna si no se ha registrado una
                    oi = OrdenInterna()
                    oi.usuario = phantom_user
                    if request.POST.get('enviar') == "1": #verificar si se envió información para guardar o para enviar
                        oi.estatus = 'fantasma'
                    else:
                        oi.estatus = 'invisible'
                    oi.idioma_reporte = request.POST.get('idioma')
                    oi.save()
                muestra = Muestra() #crear muestra a guardar
                muestra.usuario = IFCUsuario.objects.get(user = request.user)
                muestra.oi = oi
                muestra.producto = request.POST.get('producto')
                muestra.variedad = request.POST.get('variedad')
                muestra.pais_origen = request.POST.get('pais')
                muestra.codigo_muestra = request.POST.get('clave_muestra')
                muestra.agricultor = request.POST.get('nombre')
                muestra.ubicacion = request.POST.get('direccion')
                muestra.estado = request.POST.get('estado')
                muestra.parcela = request.POST.get('parcela')
                muestra.fecha_muestreo = request.POST.get('fecha_muestreo')
                muestra.destino = request.POST.get('pais_destino')
                muestra.idioma = request.POST.get('idioma')
                if request.POST.get('enviar')=="1": #verificar si se envió información para guardar o para enviar
                    muestra.estado_muestra = True
                else:
                    muestra.estado_muestra = False
                muestra.fecha_forma = datetime.datetime.now().date()
                muestra.save()
                #guardar en tabla analisis_muestra
                prefix = "analisis"
                for key,value in request.POST.items(): #iterar para toda la información enviada para buscar análisis
                    if key.startswith(prefix): #buscar todos los campos relacionados con análisis (todos los campos que empiezan con análisis)
                        if request.POST.get(key,'') == 'on': #verificar que se ha seleccionado el análisis
                            id_analisis = int(key[len(prefix):]) #obtener id del análisis
                            analisis = Analisis.objects.get(id_analisis=id_analisis) #obtener análisis a partir del id
                            am = AnalisisMuestra() #crear una nueva entrada en la tabla análisis muestra
                            am.analisis = analisis
                            am.muestra = muestra
                            am.fecha = datetime.datetime.now()
                            if request.POST.get('enviar')=="1": #verificar que la información se haya enviado para guardar o enviar
                                am.estado = True
                                a = all_analysis_cot.get(analisis__id_analisis=id_analisis)
                                a.cantidad = a.cantidad-1 #disminuir cantidad de análisis disponibles
                                a.save()
                            else:
                                am.estado = False
                            am.save()
                if request.POST.get('otro'): #verificar si se seleccionó la opción otro análisis
                    am=AnalisisMuestra() #crear nueva entrada con el tipo de análisis otro
                    am.analisis=Analisis.objects.get(nombre='Otro')
                    am.muestra=muestra
                    am.fecha = datetime.datetime.now()
                    if request.POST.get('enviar') == "1": #verificar que la información se haya enviado para guardar o enviar
                        am.estado = True
                    else:
                        am.estado = False
                    am.save()
                return HttpResponseRedirect("ingreso_cliente") #redireccionar para volver a ingresar muestra
            else:
                raise Http404
        else:
            raise Http404
    else:
        raise Http404

