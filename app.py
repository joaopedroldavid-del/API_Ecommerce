from flask import Flask

# Instaciamento do objeto Flask
app = Flask(__name__)

# Definição da rota raiz ( Página inicial ) e a função que será executada ao requisitar
@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True) # Nao utilizar em producao
