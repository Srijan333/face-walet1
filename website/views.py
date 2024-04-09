from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for,session

from flask_login import login_required, current_user

import random
import smtplib


from . import db

import json
import cv2

from datetime import datetime
from .models import User

import tkinter as tk
from tkinter import messagebox

from werkzeug.security import generate_password_hash, check_password_hash


views = Blueprint('views', __name__)








otp_storage = {}
amount_storage={}




nameList=[]
def draw_boundary(img, classifier, scaleFactor, minNeighbors, color, text, clf):
    # Converting image to gray-scale
    nameList=[]
    
    
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # detecting features in gray-scale image, returns coordinates, width and height of features
    features = classifier.detectMultiScale(gray_img, scaleFactor, minNeighbors)
    coords = []


    # drawing rectangle around the feature and labeling it
    for (x, y, w, h) in features:
        cv2.rectangle(img, (x,y), (x+w, y+h), color, 2)
        # Predicting the id of the userq
        id, _ = clf.predict(gray_img[y:y+h, x:x+w])
        #print(id)
        nameList.append(id)
        

        if id==4567:
            cv2.putText(img, "sanjiv", (x, y-4), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 1, cv2.LINE_AA)
           
            if id not in nameList:
                nameList.append(id)
        if id==98:
            cv2.putText(img, "srijan", (x, y-4), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 1, cv2.LINE_AA)
        

        coords = [x, y, w, h]

    return coords,nameList

# Method to recognize the person
def recognize(img, clf, faceCascade):
    
    color = {"blue": (255, 0, 0), "red": (0, 0, 255), "green": (0, 255, 0), "white": (255, 255, 255)}
    coords,nameList = draw_boundary(img, faceCascade, 1.1, 10, color["white"], "Face", clf)
    return img,nameList













@views.route('/otp', methods=['GET', 'POST'])
@login_required
def checkotp():
    id=session['id']
    print("first"+str(otp_storage[id]))
    otp=otp_storage[id]
    amount=amount_storage[id]
    
    if request.method == 'POST': 
        
        
       

        user_otp=request.form.get("otp")
        
        

        if(otp==user_otp):
            flash("successssss") 
            x=db.session.query(User).get(id)
            current_user.balance=current_user.balance+amount
            x.balance=x.balance-amount
            db.session.commit()
            flash('payment successful\n'+ "vendor balance : "+str(current_user.balance)+ "\nuser balance : "+str(x.balance), category='success')
                
            db.session.close()
            session.pop('id', None)
            return render_template("vendor.html", user=current_user)
        else:
            flash("fail"+str(otp)+str(user_otp)) 
            print(otp)
        
        
        
    

        
    return render_template("otp.html", user=current_user)
    

        
        








@views.route('/addmoney', methods=['GET', 'POST'])
@login_required
def manager():
    if request.method == 'POST': 
        id=request.form.get("id")
        amount=int(request.form.get('amount'))

        stud = User.query.filter_by(id=id).first()
        

        if (stud) :
            x=db.session.query(User).get(stud.id)
            x.balance=x.balance+amount
            db.session.commit()
            flash(str(x.balance) + " "+ str(current_user.email)) 
        else:
           #
            flash('user not found!', category='success')

    return render_template("addmoney.html", user=current_user)


@views.route('/vendor', methods=['GET', 'POST'])
@login_required
def vendor():
    return render_template("payment.html", user=current_user)


@views.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    if request.method == 'POST': 
        id=request.form.get("id")
        password=request.form.get("password")
        amount=int(request.form.get("amount"))
        

        

        user = User.query.filter_by(id=id).first()
        #email=user.email
        if(user):
            
            if check_password_hash(user.password, password):
                


                faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

                # Loading custom classifier to recognize
                clf = cv2.face.LBPHFaceRecognizer_create()
                parent="C:/Users/srijan/OneDrive/Desktop/flaskkk/flask5-facerec-new-new/website/data/"

                clf.read( parent + "classifier.xml")

                # Capturing real time video stream. 0 for built-in web-cams, 0 or -1 for external web-cams

                video_capture = cv2.VideoCapture(0)
                #video_capture.set(3,640)
                #video_capture.set(4,480)
                #img_bg=cv2.imread("carbg.jpg")
                nl=[]

                while True:
                    # Reading image from video stream
                    _, img = video_capture.read()
                    #img_bg[162:162+480,55:55+640]=img
                    # Call method we defined above
                    img,nameList = recognize(img, clf, faceCascade)
                    nl=nl+nameList
                    # Writing processed image in a new window
                    
                    cv2.imshow("face recognition", img)
                    cv2.imshow("face recognition", img)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                # releasing web-cam
                video_capture.release()
                # Destroying output window
                cv2.destroyAllWindows()

                if(len(nl)>=1 and (user.id in nl)):

                    print(nl)
                    

                    server=smtplib.SMTP('smtp.gmail.com',587)
                    server.starttls()
                    server.login("facewallet333@gmail.com","uuzr bdco pvfc opjl")

                    otp=''.join([str(random.randint(0,9)) for i in range(6)])
                    msg="your otp is "+otp

                    server.sendmail("facewallet333@gmail.com","srijansrijan6796@gmail.com",msg)
                    server.quit()
                    session['id'] = user.id
                    otp_storage[user.id]=otp
                    amount_storage[user.id]=amount

                    print(otp_storage)

                    return render_template("otp.html",user=current_user)

                    
                    

                    x=db.session.query(User).get(id)
                    current_user.balance=current_user.balance+amount
                    x.balance=x.balance-amount
                    db.session.commit()
                    flash('payment successful\n'+ "vendor balance : "+str(current_user.balance)+ "\nuser balance : "+str(x.balance), category='success')
                
                    db.session.close()
                else:
                    flash('face does not match', category='success')



        



    

    return render_template("vendor.html",user=current_user)
@views.route('/faculty', methods=['GET', 'POST'])
@login_required
def faculty():
    if request.method == 'POST': 
        email=request.form.get("email")
        amount=int(request.form.get('amount'))

        user = User.query.filter_by(email=email).first()
        x=db.session.query(User).get(21272008010866)
        x.balance=x.balance+amount
        db.session.commit()

        if (1) :
            flash(x.balance) 
        else:
            new_trans = transaction(data=amount, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_trans) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("faculty.html", user=current_user)

@views.route('/student', methods=['GET', 'POST'])
@login_required
def student():
    if request.method == 'POST': 
        email=request.form.get("email")
        amount=int(request.form.get('amount'))

        user = User.query.filter_by(email=email).first()
        x=db.session.query(User).get(212720080108866)
        x.balance=x.balance+amount
        db.session.commit()

        if (1) :
            flash("x.balance") 
        else:
            new_trans = transaction(data=amount, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_trans) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("student.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():  
    trans = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = trans['noteId']
    note = transaction.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session[balance]=50
            db.session.commit()

    return jsonify({})


