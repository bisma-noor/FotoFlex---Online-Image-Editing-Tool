# pip3 install flask opencv-python
from flask import Flask, render_template, request, flash
from werkzeug.utils import secure_filename
import cv2
import os

UPLOAD_FOLDER = 'uploads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def processImage(filename, operation):
    print(f"The operation is {operation} and filename is {filename}")
    img_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(img_path):
        print(f"Error: File {img_path} not found.")
        return None
    img = cv2.imread(img_path)
    if img is None:
        print(f"Error: Could not read the image {img_path}.")
        return None
    newFilename = ""
    match operation:
        case "cgray":
            imgProcessed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            newFilename = f"static/{filename}"
        case "cwebp":
            newFilename = f"static/{filename.split('.')[0]}.webp"
        case "cjpg":
            newFilename = f"static/{filename.split('.')[0]}.jpg"
        case "cpng":
            newFilename = f"static/{filename.split('.')[0]}.png"
        case _:
            print(f"Error: Unknown operation '{operation}'")
            return None
    success = cv2.imwrite(newFilename, imgProcessed if operation == "cgray" else img)
    if success:
        print(f"Processed image saved at: {newFilename}")
        return newFilename
    else:
        print(f"Error: Could not save processed image {newFilename}.")
        return None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/guide")
def guide():
    return render_template("guide.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        operation = request.form.get("operation")

        if 'file' not in request.files:
            flash('No file part')
            print("No file part in request")  # Debugging
            return "error"

        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            print("No file selected")  # Debugging
            return "error no selected file"

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            print(f"Saving file to: {save_path}")  # Debugging Print
            file.save(save_path)

            if os.path.exists(save_path):
                print(f"File saved successfully at: {save_path}")
            else:
                print(f"Error: File was NOT saved at {save_path}")
                return "File save error"

            new = processImage(filename, operation)

            if new:
                # Generate a download link for the processed image
                download_link = f"<a href='/{new}' download='processed_image.{new.split('.')[-1]}'>Download Here</a>"
                flash(f"Your image has been processed and is available <a href='/{new}' target='_blank'>here</a>. {download_link}")
            else:
                flash("Error processing image.")

            return render_template("index.html")

    return render_template("index.html")

app.run(debug=True, port=5001)