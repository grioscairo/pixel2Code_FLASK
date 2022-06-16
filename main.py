from distutils.log import debug
from runpy import run_path
from flask import Flask, render_template ,request, flash, jsonify, send_file
from werkzeug.utils import secure_filename
import os
from PIL import Image as imagen

#Run on PS
#   $env:FLASK_APP = "main"
#   $env:FLASK_ENV = "development"
#   flask run

main = Flask(__name__)
main.secret_key = "asdf"


UPLOAD_FOLDER = 'static/uploads'
main.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
main.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg'])

def allowed_file(filename):
 return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/')
def index():
    flash("Arrastra el pixel art a convertir" )
    msj2 = "> AQUÍ <"
    return render_template("index.html", msj2=msj2)

@main.route("/upload", methods=["POST","GET"])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)  
        if file and allowed_file(file.filename):
            global ruta
            ruta = os.path.join(main.config['UPLOAD_FOLDER'], filename)
            file.save(ruta)
            print('Archivo ' + file.filename + ' cargado correctamente.')
        else:
           print('Inválido. Agregue solo archivos png o jpg.')
    return jsonify(ruta)

@main.route("/conversion", methods = ["POST"])
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

@main.route('/download')
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
    nom = "sprite.txt"
    creaSprite = open(nom, "w")
    creaSprite.close()    
    escrSprite = open(nom, "a")

    dimx = int(numCuadX)
    dimy = int(numCuadY)
    espacio = float(numEspacio)
    inix = float(numIniX)
    iniy = float(numIniY)

    vx=0
    vy=0
    v = pixel_rgb(img, vx, vy)                                         #Envía ruta habia rgb scanner

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

if __name__ == "__main__":   
    main.run(debug = True)