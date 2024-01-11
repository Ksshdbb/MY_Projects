import numpy as np
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from flask import Flask, render_template, request, redirect, session
from flask_mail import Mail, Message
from google_auth_oauthlib.flow import Flow
from google.auth.exceptions import RefreshError
from werkzeug.utils import secure_filename



app = Flask(__name__)
app.secret_key = '925a25014ad6e71d6ad2698268a43fb2'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'crimevision66@gmail.com'  # Update with your email
app.config['MAIL_PASSWORD'] = 'tuktcqlggmcnnzqf'  # Update with your password
# Set the authorized JavaScript origins
app.config['AUTHORIZED_JAVASCRIPT_ORIGINS'] = ['http://localhost:5000']
# Set the authorized redirect URIs
app.config['AUTHORIZED_REDIRECT_URIS'] = ['http://localhost:5000/callback']

mail = Mail(app)

model = load_model("crime.h5", compile=False)

# OAuth 2.0 configuration
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # For testing purposes only, remove in production
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'  # For testing purposes only, remove in production
os.environ['GOOGLE_CLIENT_ID'] = '423181472364-83krh88g8240k4efgstnervuckhbgc9v.apps.googleusercontent.com'
os.environ['GOOGLE_CLIENT_SECRET'] = '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'

# home page
@app.route('/')
def index():
    return render_template("home.html")

# Prediction page
@app.route('/predict') 
def prediction():
    return render_template('predict.html')

# contact page
@app.route('/contact') 
def contact():
    return render_template('contact.html')
# about page
@app.route('/about') 
def about():
    return render_template('about.html')

from flask import jsonify

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        # Get the file from the POST request
        f = request.files['image']
        
        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)
        
        # Load and preprocess the image
        img = image.load_img(file_path, target_size=(64, 64))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        
        # Perform the prediction
        pred = np.argmax(model.predict(x), axis=1)
        op = ["Abuse", "Arrest", "Arson", "Assault", "Burglary", "Explosion", "Fighting", "NormalVideos", "RoadAccidents", "Robbery", "Shooting", "Shoplifting", "Stealing", "Vandalism"]
        result = op[pred[0]]
        
        # Prepare the result message
        result = 'The predicted output is {}'.format(result)
        print(result)
        
        # Return the predicted result as a JSON response
        return jsonify({'result': result})



@app.route('/send_message', methods=['GET', 'POST'])
def send_message():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    
    msg = Message('New Message from CrimeVision Contact Form', sender='your-email@gmail.com', recipients=['tamilg2523@gmail.com'])  # Update with admin email
    msg.body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
    
    mail.send(msg)
    return render_template('contact.html', success_message='Message sent successfully')
   

# OAuth 2.0 routes
@app.route('/login')
def login():
    client_secrets_path = os.path.join(os.path.dirname(__file__), '/client_secrets.json')
    flow = Flow.from_client_secrets_file(
        client_secrets_path,
        scopes=['openid', 'email', 'profile']
    )
    authorization_url, state = flow.authorization_url(access_type='offline')

    session['state'] = state

    return redirect(authorization_url)

@app.route('/callback')
def callback():
    state = session.pop('state', '')

    client_secrets_path = os.path.join(os.path.dirname(__file__), '/client_secrets.json')
    flow = Flow.from_client_secrets_file(
        client_secrets_path,
        scopes=['openid', 'email', 'profile'],
        state=state
    )
    flow.fetch_token(authorization_response=request.url)

    try:
        id_token = flow.credentials.id_token
        email = id_token['email']
        # Perform authentication and authorization logic here
        # You can store the authenticated user's email in session or database

        # Redirect to a protected route after successful authentication
        return redirect('/protected')
    except RefreshError:
        return 'Error: Failed to authenticate user'

@app.route('/protected')
def protected():
    # Access the authenticated user's email from session or database
    # Perform any additional logic for protected routes
    return 'Protected route'

if __name__ == '__main__':
    app.run(debug=True)
