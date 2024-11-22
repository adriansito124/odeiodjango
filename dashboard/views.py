from django.shortcuts import render
from django.http import JsonResponse

import firebase_admin
from firebase_admin import credentials, firestore   

import json

cred = credentials.Certificate("C:/Users/DELL/Desktop/odeiodjango/dashboard/park-iot-firebase-adminsdk-8cvie-bcdbe35de5.json")

if not firebase_admin._apps:
    app = firebase_admin.initialize_app(cred)

db = firestore.client()

def get_firestore(codigo):
    collection_ref = db.collection(codigo)  
    docs = collection_ref.stream()
    data = []

    for doc in docs:
        doc_data = doc.to_dict()
        doc_data['id'] = doc.id
        data.append(doc_data)
    
    return data

def index(request):
    try:
        
        data = get_firestore('codigo')  
        
        
        meses = [item['mes'] for item in data]
        valores = [item['valor'] for item in data]

        meses_json = json.dumps(meses)
        valores_json = json.dumps(valores)
        

        return render (request, 'dashboard/home.html', {"labels": meses_json, "data": valores_json})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

