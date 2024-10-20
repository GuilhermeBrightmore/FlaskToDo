from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)
a_fazeres = {
}


@app.route('/', methods=["POST",'GET'])
def index():
    if request.method == 'POST':
        nome = request.form['criaritem']
        data = request.form['dataitem']
        if nome =='':
            return redirect(url_for('index'))
        a_fazeres[len(a_fazeres) + 1] = {"nome": nome, "data": f'{data}'}
        return redirect(url_for('index'))
    elif request.method== 'GET':
        return render_template('index.html', a_fazeres=a_fazeres)
    
@app.route('/deletar/<id>')
def deletar(id):
    if request.method == 'GET':
        del a_fazeres[int(id)]
        return redirect(url_for('index'))
    elif request.method == 'POST':
        del a_fazeres[int(id)]
        return redirect(url_for('index'))
    
@app.route('/editar/<id>', methods = ['POST', 'GET'])
def editar(id):
    
    
    if request.method == 'GET':
        nome_form = a_fazeres[int(id)]['nome']
        data_form=a_fazeres[int(id)]['data']
        return render_template('edit.html', nome_form=nome_form, data_form=data_form)
    if request.method == 'POST':
        nome = request.form['editarnomeitem']
        data = request.form['editardataitem']
        a_fazeres[int(id)] = {"nome": nome, "data": f'{data}'}
        return redirect(url_for('index'))
    
        
    
@app.errorhandler(500)
def key_error(e):
    erro_status = 500
    erro_name = 'Erro Interno do Servidor'
    erro_message = 'Desculpe, ocorreu um erro inesperado. Por favor, tente novamente mais tarde.'
    return render_template('errointerno.html', erro_status=erro_status, erro_message=erro_message, erro_name=erro_name)

@app.errorhandler(404)
def key_error(e):
    erro_status = 404
    erro_name = 'Página Não Encontrada'
    erro_message = 'Você está procurando por uma página que não existe'
    return render_template('errointerno.html', erro_status=erro_status, erro_message=erro_message, erro_name=erro_name)

@app.errorhandler(405)
def key_error(e):
    erro_status = 405
    erro_name = 'Método De Requisição Não Autorizado'
    erro_message = 'Você está utilizando um método de requisição não autorizado'
    return render_template('errointerno.html', erro_status=erro_status, erro_message=erro_message, erro_name=erro_name)
    

    

if __name__ == '__main__':
    app.run(debug=True)
