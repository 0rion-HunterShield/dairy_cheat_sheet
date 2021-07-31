from django.shortcuts import render,redirect
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
        if request.user and request.user.is_authenticated and request.user.is_staff:

            context=dict()
            context['title']="Parse Product CSV"
            context['upload_form']=UploadFileForm()
            return render(request,self.template_name,context=context)
        else:
            return redirect('/admin')
    def post(self,request):
        if request.user and request.user.is_authenticated and request.user.is_staff:

            context={}
            context['title']="Parse Product CSV"
            context['upload_form']=UploadFileForm(request.POST,request.FILES)
            if context['upload_form'].is_valid():
                data=request.FILES['file']
                context['results']=[]
                def writeTMP():
                    try:
                        with open("tmp.csv","w") as x:
                            x.write(data.read().decode('utf-8'))
                    except Exception as e:
                        return e

                def readTMP():
                    with open('tmp.csv','r') as x:
                        try:
                            csvReader=csv.reader(x,delimiter=',')
                            line=0
                            for num,row in enumerate(csvReader):
                                if num > 0:
                                    print(row)
                                    try:
                                        obj=Products.objects.get(barcode=row[0])
                                        context['results'].append((obj,row[1]))
                                    except Exception as e:
                                        print(" {code} - does not exist".format(code=row[0]))

                        except Exception as e:
                            return e
                def cleanup():
                    try:
                        Path('tmp.csv').unlink()
                    except Exception as e:
                        return e
                context['errors']=dict(writeTMP=None,readTMP=None,cleanup=None)
                context['errors']['writeTMP']=writeTMP()
                context['errors']['readTMP']=readTMP()
                context['errors']['cleanup']=cleanup()

            return render(request,self.template_name,context=context)
        else:
            return redirect('/admin')
def process(rows):
            duplicates=[]
            for i in rows:
                try:
                    imgio=BytesIO()
                    barcode.Code128(i[0],writer=ImageWriter()).write(imgio)
                    imgio.seek(0)
                    b64=base64.b64encode(imgio.read()).decode('utf-8')
                    b64='data:image/png;base64,'+b64
                    price=i[2].replace(' ','')
                except Exception as e:
                    return e
                try:
                    dairy_products=Products.objects.create(
                            barcode=i[0],name=i[1],price=price,bar_img=b64)
                except django.db.utils.IntegrityError as e:
                    duplicates.append("{dup} is a duplicate entry, skipping!".format(dup=i[0]))

                except Exception as e:
                    return e
            return duplicates

@method_decorator(ensure_csrf_cookie,name="dispatch")
class DataReciever_viewable(TemplateView):
    template_name="csv_uploader.html"
    def get(self,request):
        if request.user and request.user.is_authenticated and request.user.is_staff and request.user.is_superuser:
            context={}
            context['title']="Upload CSV of Product Info"
            context['csv_form']=UploadFileForm()
            context['status']='Ready'


            return render(request,self.template_name,context=context)
        return redirect("/admin")

    def post(self,request):
        if request.user and request.user.is_authenticated and request.user.is_staff:

            context={}
            context['title']="Upload CSV of Product Info"
            context['csv_form']=UploadFileForm(request.POST,request.FILES)
            if context['csv_form'].is_valid():
                print(request.FILES)
                def mktemp():
                    try:
                        with open("tmp.csv","wb") as out:
                            out.write(request.FILES['file'].read())
                    except Exception as e:
                        return e

                def readTmp():
                    try:
                        with open("tmp.csv","r") as in_:
                            reader=csv.reader(in_,delimiter=',')
                            for i in reader:
                                if len(i) < 3:
                                    raise Exception("too few columns")
                                break
                            context['duplicates']=process(reader)
                    except Exception as e:
                        return e
                context['errors']=dict(mktemp=None,readTMP=None)
                context['errors']['mktemp']=mktemp()
                context['errors']['readTMP']=readTmp()
                context['status']='Done'

            return render(request,self.template_name,context=context)
        else:
            return redirect("/admin")


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
            try:
                with open(file,'wb') as tmp:
                    tmp.write(request.body)
            except Exception as e:
                return e

        def db():
            db=sqlite3.connect(file)
            cursor=db.cursor()
            cursor.execute("select barcode,name,price from 'dairy products {section}'".format(section=section))
            rows=cursor.fetchall()
            return rows

        process(rows)
        def cleanup():
            try:
                Path(file).unlink()
            except Exception as e:
                return e


        data['errors']=dict(create_tmp=None,process=None,cleanup=None)
        data['errors']['create_tmp']=create_tmp()
        rows=db()
        data['errors']['process']=process()
        data['errors']['cleanup']=cleanup()

        return response.Response(data=data,status=status)
