from flask import Flask, render_template, request, url_for, redirect
import secrets
import requests
import time
import qrcode
import os
from config import token_mp, email_payer

app = Flask(__name__)

import mercadopago
import random

# Inicializar SDK com seu access token
sdk = mercadopago.SDK(token_mp)

# Gerar um ID de pagamento aleatório para idempotência
pay_id = random.randint(1, 99999999999999)

request_options = mercadopago.config.RequestOptions()
request_options.custom_headers = {
    'x-idempotency-key': str(pay_id)
}

produtos = {
}

payment_data = {
    "transaction_amount": 1,  # Valor da transação
    "description": "Pagamento via PIX",
    "payment_method_id": "pix",  # Método de pagamento PIX
    "payer": {
        "email": email_payer  # Email do pagador
    }
}

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        nome = request.form.get('nomeproduto')
        quantidade = request.form.get('quantidadeproduto')
        preco = request.form.get('precoproduto')

        # Verifica se os valores estão vazios ou inválidos
        if not nome or not quantidade or not preco:
            return redirect(url_for('index'))

        # Converte os valores para inteiros, se possível
        try:
            quantidade = int(quantidade)
            preco = float(preco)
        except ValueError:
            return redirect(url_for('index'))

        if quantidade < 0:
            quantidade = 0
        
        produtos[f'{len(produtos) + 1}'] = {'nome': nome, 'preco': preco, 'quantidade': quantidade}
        print(produtos)
        return redirect(url_for('index'))

    return render_template('index.html', produtos=produtos)



@app.route('/increment/<id>', methods=['POST', 'GET'])
def increment(id):
    if id in produtos:
        produtos[id]["quantidade"] += 1
    else:
        print(f'produto {id} nao encontrado')
    return redirect(url_for('index'))

@app.route('/desincrement/<id>', methods=['POST', 'GET'])
def desincrement(id):
    if id in produtos:
        if produtos[id]["quantidade"] == 0:
            produtos[id]["quantidade"] = 0
        else:
            produtos[id]["quantidade"] -= 1
    return redirect(url_for('index'))


@app.route('/deletar/<id>')
def deletar(id):
    if id in produtos:
        del produtos[id]
    return redirect(url_for('index'))


@app.route('/comprar')
def comprar():
    
    return render_template('loja.html', produtos=produtos)

@app.route('/comprar/pagamento/<id>')
def pagamento(id):
    global id_produto
    id_produto = id
    if id in produtos:
        preco = produtos[id]['preco']

        # Gerar um novo ID de pagamento aleatório para idempotência
        pay_id = random.randint(1, 99999999999999)

        # Criar uma nova instância de RequestOptions
        request_options = mercadopago.config.RequestOptions()
        request_options.custom_headers = {
            'x-idempotency-key': str(pay_id)
        }

        # Atualizar os dados do pagamento
        payment_data = {
            "transaction_amount": preco,  # Valor da transação
            "description": f"{id}",
            "payment_method_id": "pix",  # Método de pagamento PIX
            "payer": {
                "email": email_payer  # Email do pagador
            }
        }

        # Criar o pagamento
        result = sdk.payment().create(payment_data, request_options)
        payment = result["response"]

        # Verificar se o pagamento foi criado com sucesso
        if result["status"] == 201:
            pix_code = payment['point_of_interaction']['transaction_data']['qr_code']

            # Criar uma instância do gerador de QR Code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(pix_code)
            qr.make(fit=True)

            # Cria uma imagem do QR Code
            img = qr.make_image(fill='black', back_color='white')
            img.save(f'./static/{payment['id']}.png')

            print(f"ID do pagamento: {payment['id']}")
            id_compra = payment['id']
            return render_template('pagamento.html', qrcode=f'{payment['id']}.png', id=id_compra)
        else:
            print("Erro ao criar pagamento:", result["response"])
            return render_template('pagamento.html', error="Erro ao criar pagamento.")
    return redirect(url_for('index'))


@app.route('/comprar/validarpagamento/<id>')
def validarpagamento(id):
    header = {
        'Authorization': f'Bearer {token_mp}'
    }
    response = requests.get(url=f"https://api.mercadopago.com/v1/payments/{id}", headers=header)

    status_pagamento = response.json().get("status")
    if status_pagamento == 'approved':
        produtos[response.json().get("description")]["quantidade"] -= 1
        return render_template("pago.html")
    elif status_pagamento == 'pending':
        return render_template('pagamento.html', qrcode=f'{id}.png', id=id)



if __name__ == '__main__':
    app.run(debug=True)
