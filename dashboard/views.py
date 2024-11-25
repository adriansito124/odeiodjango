from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore   
from collections import defaultdict

import json

cred = credentials.Certificate("C:/users/DELL/Desktop/odeiodjango/dashboard/park-iot-firebase-adminsdk-8cvie-2ae0b4b185.json")

if not firebase_admin._apps:
    app = firebase_admin.initialize_app(cred)

db = firestore.client()

def calcular_tempo_total_por_usuario(data):
    tempos_por_usuario = {}

    for item in data:
        card = item.get('card')
        enter = item.get('enter')
        exit = item.get('exit')

        if card and enter and exit:
            # Conversao da string
            formato = "%Y-%m-%d %H:%M:%S.%f"
            entrada = datetime.strptime(enter, formato)
            saida = datetime.strptime(exit, formato)

            # Calculo do tempo 
            tempo_permanencia = (saida - entrada).total_seconds()

            # Adicione ao total para este usuário
            if card in tempos_por_usuario:
                tempos_por_usuario[card] += tempo_permanencia
            else:
                tempos_por_usuario[card] = tempo_permanencia

    return tempos_por_usuario

def get_firestore(codigo):
    collection_ref = db.collection(codigo)  
    docs = collection_ref.stream()
    data = []

    for doc in docs:
        doc_data = doc.to_dict()
        doc_data['id'] = doc.id
        data.append(doc_data)
    
    return data


def get_cards(cards):
    collection_ref = db.collection(cards)
    docs = collection_ref.stream()
    data = []

    for doc in docs:
        doc_data = doc.to_dict()
        doc_data['id'] = doc.id  # Incluímos o ID do documento
        data.append(doc_data)  # Adiciona o documento à lista final

    return data

def calcular_tempo_total_por_dia(data):
    tempos_por_dia = defaultdict(float)  

    for item in data:
        enter = item.get('enter')
        exit = item.get('exit')

        if enter and exit:
 
            formato = "%Y-%m-%d %H:%M:%S.%f"
            entrada = datetime.strptime(enter, formato)
            saida = datetime.strptime(exit, formato)


            tempo_permanencia = (saida - entrada).total_seconds()

            # Obter data 
            data_entrada = entrada.date()

            # Adiciona ao total
            tempos_por_dia[data_entrada] += tempo_permanencia

    return tempos_por_dia


def get_vaga_1(vagas, vaga1):

    doc_ref = db.collection(vagas).document(vaga1)
    doc = doc_ref.get()
    if doc.exists:
        doc_data = doc.to_dict()
        return doc_data.get('vaga') 
    return None

def get_vaga_2(vagas, vaga2):

    doc_ref = db.collection(vagas).document(vaga2)
    doc = doc_ref.get()
    if doc.exists:
        doc_data = doc.to_dict()
        return doc_data.get('vaga') 
    return None

def get_vagas(vagas):
    collection_ref = db.collection(vagas)  
    docs = collection_ref.stream()
    vagas_disponiveis = 0

    for doc in docs:
        doc_data = doc.to_dict()
        if doc_data.get('vaga') == True: 
            vagas_disponiveis += 1  
    
    return vagas_disponiveis

def index(request):
    try:


        data = get_cards('cards')  

        tempos_totais = calcular_tempo_total_por_usuario(data)

        tempos_por_dia = calcular_tempo_total_por_dia(data)

        dias = [str(dia) for dia in tempos_por_dia.keys()]  # array de dias
        tempos = [tempo  for tempo in tempos_por_dia.values()] #normal segundos, /60 minutos e /3600 horas

        dias_json = json.dumps(dias)
        temps_json = json.dumps(tempos)

        vagas_disponiveis = get_vagas('vagas')  

        vaga1 = get_vaga_1('vagas', 'vaga1') 
        vaga2 = get_vaga_2('vagas', 'vaga2')
        
        
        meses = [item['card'] for item in data]
        valores = [item['enter'] for item in data]

        meses_json = json.dumps(meses)
        valores_json = json.dumps(valores)
        tempos_totais_lista = [{"card": card, "tempo": tempo} for card, tempo in tempos_totais.items()]
        tempos_json = json.dumps(tempos_totais_lista)

        

        return render (request, 'dashboard/home.html', {
            "labels": dias_json, 
            "data": temps_json, 
            "vagas_disponiveis": vagas_disponiveis, 
            "vaga1": vaga1, 
            "vaga2": vaga2,
            "tempos_totais": tempos_json})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

