from flask import Flask, render_template, request, redirect, url_for, session, request
import json
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "1234"  # Change this to a secure secret key

# Define user data (in a production environment, use a database)
with open('users.json') as f:
    users = json.load(f)

UPLOAD_FOLDER = 'prescriptions'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ... (your existing code)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_prescription', methods=['POST'])
def upload_prescription():
    if 'prescription_file' not in request.files:
        return "No file part"
    
    file = request.files['prescription_file']
    
    if file.filename == '':
        return "No selected file"
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return "Prescription uploaded successfully"
    else:
        return "Invalid file format. Please upload a PDF, JPG, JPEG, or PNG file."
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return "Login failed. Please try again."

    return render_template('login.html')

@app.route('/home')
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    else:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/medical_folder')
def medical_folder():
    # You can retrieve old prescriptions and other medical data here
    old_prescriptions = ["Prescription 1", "Prescription 2", "Prescription 3"]
    
    return render_template('medical_folder.html', prescriptions=old_prescriptions)

@app.route('/profile')
def profile():
    # Assuming you have patient data
    username = session.get('username')
    
    # Read user data from userdata.json
    user_data = {}
    with open('userdata.json', 'r') as f:
        for line in f:
            data = json.loads(line)
            user_data.update(data)

    patient_data = user_data.get(username, {})

    return render_template('profile.html', patient=patient_data)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Retrieve user data from the signup form
        name = request.form['name']
        dob = request.form['dob']
        address = request.form['address']
        contact = request.form['contact']
        medical_history = request.form['medical_history']
        weight = request.form['weight']
        username = request.form['username']
        password = request.form['password']
        
        # Save the username and password in users.json
        users = {}
        try:
            with open('users.json', 'r') as user_file:
                users = json.load(user_file)
        except FileNotFoundError:
            pass  # If the file doesn't exist yet

        users[username] = password

        with open('users.json', 'w') as user_file:
            json.dump(users, user_file)
        
        # Save the additional user data in userdata.json
        user_data = {
            'name': name,
            'dob': dob,
            'address': address,
            'contact': contact,
            'medical_history': medical_history,
            'weight': weight,
        }
        
        with open('userdata.json', 'a') as userdata_file:
            userdata_file.write(json.dumps({username: user_data}) + '\n')

        return render_template('login.html')

    return render_template('signup.html')
with open('doctors_data.json') as f:
    doctors_data = json.load(f)
@app.route('/doctors', methods=['GET', 'POST'])
def available_doctors():
    if request.method == 'POST':
        selected_doctor = request.form['doctor_name']
        selected_specialty = request.form['specialty']
        print(f"Selected doctor: {selected_doctor}, Specialty: {selected_specialty}")
        # Create a dictionary to hold the data
        data = {
            "doctor_name": selected_doctor,
            "specialty": selected_specialty
        }

        print(f"Selected doctor: {selected_doctor}, Specialty: {selected_specialty}")


        return redirect(url_for('checkout', doctor_name=selected_doctor, specialty=selected_specialty))
    return render_template('doctors.html', doctors=doctors_data)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    doctor_name = request.form['doctor_name']
    specialty = request.form['specialty']
    id = request.form['id']
      # Corrected to get time from form

    doctor = {
        'name': doctor_name,
        'specialty': specialty,
        'id': id,
    }

    return render_template('checkout.html', doctors=doctors_data, doctor_name=doctor_name, specialty=specialty, id=id)

@app.route('/confirmation', methods=['GET', 'POST'])
def confirmation():
    doctor_name = request.form['doctor_name']
    specialty = request.form['specialty']
    date = request.form['date']
    time = request.form['time']

    if request.method == 'POST':
        user_name = session['username']
        confirmed_data = {
            "user_name": user_name,
            "doctor_name": doctor_name,
            "specialty": specialty,
            "date": date,
            "time": time,
        }

        # Read existing data from confirmed.json (if it exists)
        existing_data = []
        try:
            with open('confirmed.json', 'r') as confirmed_file:
                existing_data = json.load(confirmed_file)
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # If the file doesn't exist or is empty or invalid JSON

        existing_data.append(confirmed_data)

        # Write the updated data back to confirmed.json
        with open('confirmed.json', 'w') as confirmed_file:
            json.dump(existing_data, confirmed_file, indent=2)

        return render_template('confirmation.html', user_name=user_name, doctor_name=doctor_name, specialty=specialty, date=date, time=time)

    return "Please confirm your booking for Dr. {} ({}) on {} at {}".format(doctor_name, specialty, date, time)

if __name__ == '__main__':
    app.run(debug=True)
