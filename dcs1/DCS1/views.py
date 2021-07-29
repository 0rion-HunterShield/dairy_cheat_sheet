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
                b64=base64.b64encode(imgio.read())
                
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

