from distutils.log import debug
from runpy import run_path
from flask import Flask, render_template ,request, flash, jsonify, send_file
from werkzeug.utils import secure_filename
import os
from PIL import Image as imagen
from pathlib import Path

#Run on PS
#   $env:FLASK_APP = "app"
#   $env:FLASK_ENV = "development"
#   flask run

app = Flask(__name__)
app.secret_key = "asdf"


UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg'])

def allowed_file(filename):
 return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    flash("Arrastra el pixel art a convertir" )
    msj2 = "> AQUÍ <"
    return render_template("index.html", msj2=msj2)

@app.route("/upload", methods=["POST","GET"])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)  
        if file and allowed_file(file.filename):
            global ruta
            ruta = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(ruta)
            print('Archivo ' + file.filename + ' cargado correctamente.')
        else:
           print('Inválido. Agregue solo archivos png o jpg.')
    return jsonify(ruta)

@app.route("/conversion", methods = ["POST"])
def greet():
    use = request.args.get("use")
    numCuadX = request.form.get("numCuadX")
    numCuadY = request.form.get("numCuadY")
    numEspacio = request.form.get("numEspacio")
    numIniX = request.form.get("numIniX")
    numIniY = request.form.get("numIniY")
    flash("Archivo generado.")
    if use:
        convert(numCuadX, numCuadY, numEspacio, numIniX, numIniY)           #Enviar a convert(ruta)
        #Recibir .txt y ofrecer como descarga        
    return render_template("conversion.html")

@app.route('/download')
def download_file():
    return send_file(nom, as_attachment=True)

def pixel_rgb(img_path, x, y):                                        #Toma ruta y realiza scan
    im = imagen.open(img_path).convert('RGB')
    r, g, b = im.getpixel((x, y))
    a = (r, g, b)
    return a

def convert(numCuadX, numCuadY, numEspacio, numIniX, numIniY):        #Recoge ruta de imagen
    img = ruta
    global nom
    nume = 'nume.txt'
    ruta_nume = Path('nume.txt')
    filesize = os.path.getsize(nume)


    if not ruta_nume.is_file():
            creaNume = open(nume,'x')
            with creaNume as num:
                num.write(str(1)+"\n")
            creaNume.close()
    else:   
        if filesize == 0:
            escrNume = open(nume,'a')
            escrNume.write(str(1)+"\n")
            escrNume.close()
    
    escrNume = open(nume,'a')
    leeNume = open(nume,'r')    
    n = int(leeNume.readlines()[-1])
    nom = "sprite" + str(n) +".txt"
    path2 = Path(nom)
    leeNume.close()

    
    
    if not path2.is_file():
        creaSprite = open(nom, "x")
        creaSprite.close()    
        escrSprite = open(nom, "a")
    else:
        n += 1
        nom = "sprite"+ str(n) +".txt"
        creaSprite = open(nom, "x")
        creaSprite.close()
        escrSprite = open(nom, "a")

    dimx = int(numCuadX)
    dimy = int(numCuadY)
    espacio = float(numEspacio)
    inix = float(numIniX)
    iniy = float(numIniY)

    vx=0
    vy=0
    v = pixel_rgb(img, vx, vy)                                         #Envía ruta hacia rgb scanner

    for ix in range(0, dimy):    
        for ix in range(0, dimx):
            if (v != (0,0,0)):
                str_v = repr(v)
                escrSprite.write("color_rgb"+str_v+";"+"\n")
                escrSprite.write("rectangulo_lleno("+str(inix)+"+x,"+str(iniy)+"+y,"+str(inix+espacio)+"+x,"+str(iniy+espacio)+"+y);"+"\n")
            inix = inix + espacio
            vx += 1
            if vx < dimx:
                v = pixel_rgb(img, vx, vy)            
            else:
                if vy < (dimy - 1):
                    v = pixel_rgb(img, 0, vy+1)
        inix = float(numIniX)
        iniy += espacio
        vx = 0
        vy += 1
    
    escrSprite.close()   
    n +=1
    escrNume.write(str(n)+"\n")
    escrNume.close()    

if __name__ == "__main__":   
    app.run(debug = True)