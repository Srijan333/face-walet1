from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
import cv2
import hashlib

import cv2
import os
import numpy as np
from PIL import Image

from datetime import date
from datetime import datetime
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import pandas as pd
import joblib




auth = Blueprint('auth', __name__)




def train_classifer(email):
    
    dir = "C:/Users/srijan/OneDrive/Desktop/flaskkk/flask5-facerec-new-tobeupdated/website/data/collected-faces"


    #path = "data/chumma"
    
    path = [os.path.join(dir, f) for f in os.listdir(dir)]
    faces = []
    ids = []


    for image in path:
        id = int(os.path.split(image)[1].split(".")[1])
        img = Image.open(image).convert('L')
        imageNp = np.array(img, 'uint8')
            #id = int(os.path.split(image)[1].split(".")[1])

        faces.append(imageNp)
        ids.append(id)

    ids = np.array(ids)

    # Train and save classifier
    clf = cv2.face.LBPHFaceRecognizer_create()
    clf.train(faces, ids)
    clf.write("C:/Users/srijan/OneDrive/Desktop/flaskkk/flask5-facerec-new-tobeupdated/website/data/"+"classifier.xml")



def generate_dataset(img,user_id,email,first_name,img_id):
    
    print("write1")
    parent="C:/Users/srijan/OneDrive/Desktop/flaskkk/flask4-facerec/website/data/"+str(email)
    print(parent)
    if not os.path.exists(parent):
        os.mkdir(parent)
    else:
        print("folder exists")
    
    if not os.path.exists("C:/Users/srijan/OneDrive/Desktop/flaskkk/flask5-facerec-new-tobeupdated/website/data/collected-faces"):
        os.mkdir("C:/Users/srijan/OneDrive/Desktop/flaskkk/flask5-facerec-new-tobeupdated/website/data/collected-faces")
    else:
        print("folder exists")
    
    
    
    if not cv2.imwrite("C:/Users/srijan/OneDrive/Desktop/flaskkk/flask5-facerec-new-tobeupdated/website/data/collected-faces/user."+ str(user_id)+"."+str(img_id)+".jpg", img):
        print("all pic")
    if not cv2.imwrite(parent+"/"+ str(user_id)+"."+str(img_id)+".jpg", img):
        print("helloo")






# Method to draw boundary around the detected feature
def draw_boundary(img, classifier, scaleFactor, minNeighbors, color, text):
    # Converting image to gray-scale
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # detecting features in gray-scale image, returns coordinates, width and height of features
    features = classifier.detectMultiScale(gray_img, scaleFactor, minNeighbors)
    coords = []
    # drawing rectangle around the feature and labeling it
    for (x, y, w, h) in features:
        cv2.rectangle(img, (x,y), (x+w, y+h), color, 2)
        cv2.putText(img, text, (x, y-4), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 1, cv2.LINE_AA)
        coords = [x, y, w, h]
    return coords

# Method to detect the features
def detect(img,img_id, faceCascade,email,first_name,id):
    color = {"blue":(255,0,0), "red":(0,0,255), "green":(0,255,0), "white":(255,255,255)}
    coords = draw_boundary(img, faceCascade, 1.1, 10, color['blue'], "Face")
    # If feature is detected, the draw_boundary method will return the x,y coordinates and width and height of rectangle else the length of coords will be 0
    if len(coords)==4:
        # Updating region of interest by cropping image
        roi_img = img[coords[1]:coords[1]+coords[3], coords[0]:coords[0]+coords[2]]
        # Assign unique id to each user
        user_id = id
        # img_id to make the name of each image unique
        generate_dataset(roi_img,user_id,email,first_name,img_id)

    return img
















@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                if(user.type=='m'):
                    return render_template("manager.html", user=current_user)
                elif(user.type=='f'):
                    return render_template("faculty.html", user=current_user)
                elif(user.type=='v'):
                    return render_template("vendor.html", user=current_user)
                elif(user.type=='s'):
                    return render_template("student.html", user=current_user)
                

                
            else:
                flash('Incorrect password, try again.'+str(user.query.all()), category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        id=request.form.get('id')
        user_type=request.form.get('type')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
           
            new_user = User(id=id,email=email, first_name=first_name, password=generate_password_hash(password1) ,balance=0,type=user_type)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')


            #faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

            faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


            video_capture = cv2.VideoCapture(0)

            # Initialize img_id with 0
            img_id = 1

            while True:
                if img_id % 11 == 0:
                    print(10)
                # Reading image from video stream
                _, img = video_capture.read()
                # Call method we defined above
                img = detect(img,img_id,faceCascade,email,first_name,id)
                # Writing processed image in a new window
                cv2.imshow("face detection", img)
                img_id += 1
                if img_id==50:
                    break

            # releasing web-cam
            video_capture.release()
            # Destroying output window
            cv2.destroyAllWindows()

            train_classifer(email)


            

    return render_template("sign_up.html", user=current_user)








