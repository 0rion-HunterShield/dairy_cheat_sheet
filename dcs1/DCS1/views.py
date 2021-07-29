from django.shortcuts import render
from rest_framework import generics
from rest_framework import response
from .models import *
# Create your views here.
from io import BytesIO
import sqlite3
import barcode
from barcode.writer import ImageWriter
import base64
import django
from pathlib import Path
from django.views.generic import TemplateView
from django import forms
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
import csv

class UploadFileForm(forms.Form):
    file = forms.FileField()

@method_decorator(ensure_csrf_cookie,name="dispatch")
class FileParser(TemplateView):
    template_name="parser.html"
    def get(self,request):
        context=dict()
        context['upload_form']=UploadFileForm()
        return render(request,self.template_name,context=context)
    def post(self,request):
        context={}
        context['upload_form']=UploadFileForm(request.POST,request.FILES)
        if context['upload_form'].is_valid():
            data=request.FILES['file']
            context['results']=[]
            with open("tmp.csv","w") as x:
                x.write(data.read().decode('utf-8'))
            with open('tmp.csv','r') as x:
                try:
                    csvReader=csv.reader(x,delimiter=',')
                    line=0
                    for num,row in enumerate(csvReader):
                        if num > 0:
                            print(row)
                    try:
                        obj=DairyProducts.objects.get(barcode=row[0])
                        context['results'].append((obj,row[1]))
                    except Exception as e:
                        print(" {code} - does not exist".format(code=row[0]))

                except Exception as e:
                    raise e
            Path('tmp.csv').unlink()
            
        return render(request,self.template_name,context=context)

    
class DataReceiver(generics.GenericAPIView):
    authentication_classes=()
    permission_classes=()

    def put(self,request,section,file):
        data={}
        status=200
        if request.user.is_authenticated:
            pass

        #print(request.body)
        def create_tmp():
            with open(file,'wb') as tmp:
                tmp.write(request.body)

        def db():
            db=sqlite3.connect(file)
            cursor=db.cursor()
            cursor.execute("select barcode,name,price from 'dairy products {section}'".format(section=section))
            rows=cursor.fetchall()
            return rows

        def process():
            for i in rows:
                imgio=BytesIO()
                barcode.Code128(i[0],writer=ImageWriter()).write(imgio)
                imgio.seek(0)
                b64=base64.b64encode(imgio.read()).decode('utf-8')
                b64='data:image/png;base64,'+b64
                price=i[2].replace(' ','')
                try:
                    dairy_products=DairyProducts.objects.create(
                            barcode=i[0],name=i[1],price=price,bar_img=b64)
                except django.db.utils.IntegrityError as e:
                    print("{dup} is a duplicate entry, skipping!".format(dup=i[0]))
                except Exception as e:
                    print(e)

        def cleanup():
            if Path(file).exists():
                Path(file).unlink()

        create_tmp()
        rows=db()
        process()
        cleanup()

        return response.Response(data=data,status=status)

