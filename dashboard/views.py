from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore   
from collections import defaultdict
from django.views.decorators.csrf import csrf_exempt

import json

cred = credentials.Certificate("C:/Users/DELL/Desktop/odeiodjango/dashboard/park-iot-firebase-adminsdk-8cvie-9b9ae532a7.json")

if not firebase_admin._apps:
    app = firebase_admin.initialize_app(cred)

db = firestore.client()


def get_card_name(card_id):

    users_ref = db.collection('users')
    user_doc = users_ref.where('card', '==', card_id).limit(1).stream()
    
    for doc in user_doc:
        user_data = doc.to_dict()
        return user_data.get('name')  
    
    return None


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

            card_name = get_card_name(card)

            if card_name:
                card = card_name

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


def get_vaga_1(vagas, vaga1, vaga2):

    vagos = 0

    doc_ref = db.collection(vagas).document(vaga1)
    doc = doc_ref.get()
    if doc.exists:
        doc_data = doc.to_dict()
        if(doc_data.get('vaga') == True):
            vagos = vagos+1
    
    doc_ref = db.collection(vagas).document(vaga2)
    doc = doc_ref.get()
    if doc.exists:
        doc_data = doc.to_dict()
        if(doc_data.get('vaga') == True):
            vagos = vagos+1
    return vagos

def vagar1(vagas, vaga1):

    doc_ref = db.collection(vagas).document(vaga1)
    doc = doc_ref.get()
    if doc.exists:
        doc_data = doc.to_dict()
        if(doc_data.get('vaga') == True):
            return 1
    return 0

def vagar2(vagas, vaga2):

    doc_ref = db.collection(vagas).document(vaga2)
    doc = doc_ref.get()
    if doc.exists:
        doc_data = doc.to_dict()
        if(doc_data.get('vaga') == True):
            return 1
    return 0

def get_vaga_2(vagas, vaga2):

    doc_ref = db.collection(vagas).document(vaga2)
    doc = doc_ref.get()
    if doc.exists:
        doc_data = doc.to_dict()
        if(doc_data.get('vaga') == True):
            return 1
    return 0

def get_vagas(vagas):
    collection_ref = db.collection(vagas)  
    docs = collection_ref.stream()
    vagas_disponiveis = 0

    for doc in docs:
        doc_data = doc.to_dict()
        if doc_data.get('vaga') == True: 
            vagas_disponiveis += 1  
    
    return vagas_disponiveis

def get_unite_cards(cards):
    collection_ref = db.collection(cards)
    docs = collection_ref.stream()

    seen_cards = set()  
    unique_cards = []   

    for doc in docs:
        doc_data = doc.to_dict()
        doc_data['id'] = doc.id  

        
        card_value = doc_data.get('card')
        if card_value not in seen_cards:
            seen_cards.add(card_value)  
            unique_cards.append(doc_data)  

    return unique_cards

def get_all_vagas(vagas):
    collection_ref = db.collection(vagas)  
    docs = collection_ref.stream()
    listavagas = []

    for doc in docs:
        doc_data = doc.to_dict()
        vaga_nome = doc.id 
        status = doc_data.get('vaga')

        listavagas.append({
            'vaga': vaga_nome,  # Nome da vaga (ID do documento)
            'status': status,  # Status da vaga (livre ou ocupada)
        })  
    
    return listavagas



def index(request):
    try:

        data = get_cards('cards')  

        tempos_totais = calcular_tempo_total_por_usuario(data)

        tempos_por_dia = calcular_tempo_total_por_dia(data)

        dias = [str(dia) for dia in sorted(tempos_por_dia.keys())]  # array de dias
        tempos = [tempo for tempo in tempos_por_dia.values()] #normal segundos, /60 minutos e /3600 horas

        dias_json = json.dumps(dias)
        temps_json = json.dumps(tempos)

        vagas_disponiveis = get_vagas('vagas')  

        vaga1 = get_vaga_1('vagas', 'vaga1', 'vaga2') 
        vaga2 = get_vaga_2('vagas', 'vaga3')
        
        
        meses = [item['card'] for item in data]
        valores = [item['enter'] for item in data]

        meses_json = json.dumps(meses)
        valores_json = json.dumps(valores)
        tempos_totais_lista = [{"card": card, "tempo": tempo } for card, tempo in tempos_totais.items()]
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



def collaborators(request):
    
    received_cards = get_unite_cards('cards')  
    users_ref = db.collection('users')
    existing_users_docs = users_ref.stream()

    
    existing_cards = {doc.to_dict().get('card') for doc in existing_users_docs}

    
    received_card_values = {card.get('card') for card in received_cards if 'card' in card}

    
    new_cards = [card for card in received_card_values if card not in existing_cards]

    
    for card in new_cards:
        users_ref.add({
            'card': card,
            'name': ""  
        })

    
    updated_users = users_ref.stream()
    data = [{"id": doc.id, **doc.to_dict()} for doc in updated_users]

    
    return render(request, 'dashboard/collaborators.html', {
        "cards": data
    })

def update_name(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        doc_id = data.get('id')
        new_name = data.get('name')

        # Atualiza o Firestore com os novos dados
        db = firestore.client()
        try:
            db.collection('users').document(doc_id).update({'name': new_name})
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def park(request):

    vagas = get_all_vagas('vagas')

    vagas_disponiveis = get_vagas('vagas')  

    vaga1 = vagar1('vagas', 'vaga1')

    vaga2 = vagar2('vagas', 'vaga2')

    area_a = get_vaga_1('vagas', 'vaga1', 'vaga2') 
    area_b = get_vaga_2('vagas', 'vaga3')
    

    return render(request, 'dashboard/park.html', {
            "vagas_disponiveis": vagas_disponiveis, 
            "area_a": area_a, 
            "area_b": area_b,
            "vaga1": vaga1,
            "vaga2": vaga2,
            "vagas": vagas })