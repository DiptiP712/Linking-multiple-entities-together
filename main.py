import random
from google.cloud import datastore
import os
import google.oauth2.id_token
from flask import Flask, render_template, request, redirect
from google.auth.transport import requests
from google.cloud.datastore import entity

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "test.json"

app = Flask(__name__)
datastore_client = datastore.Client()


def retrieveUserInfo(claims):
    entity_key = datastore_client.key('userinfo1', claims['email'])
    entity = datastore_client.get(entity_key)
    return entity


def createUserInfo1(claims):
    entity_key = datastore_client.key('userinfo1', claims['email'])
    entity = datastore.Entity(key=entity_key)
    entity.update({
        'email': claims['email'],
        'name': claims['name'],
        'address_list': []
    })
    datastore_client.put(entity)


def retrieveAddresses(user_info1):
    # make key objects out of all the keys and retrieve them
    address_ids = user_info1['address_list']
    address_keys = []
    for i in range(len(address_ids)):
        address_keys.append(datastore_client.key('Address', address_ids[i]))
    address_list = datastore_client.get_multi(address_keys)
    return address_list


def createAddress(address1, address2, address3, address4):
     entity = datastore.Entity()
     entity.update({
         'address1': address1,
         'address2': address2,
         'address3': address3,
         'address4': address4
     })
     return entity


def addAddressToUser(user_info1, address_entity):
     addresses = user_info1['address_list']
     addresses.append(address_entity)
     user_info1.update({
        'address_list': addresses
     })
     datastore_client.put(user_info1)


@app.route('/add_address', methods=['POST'])
def addAddress():
     id_token = request.cookies.get("token")
     claims = None
     user_info1 = None
     if id_token:
         try:
             claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
             user_info1 = retrieveUserInfo(claims)
             address = createAddress(request.form['address1'], request.form['address2'], request.form['address3'], request.form['address4'])
             addAddressToUser(user_info1, address)
         except ValueError as exc:
            error_message = str(exc)
     return redirect('/')


def deleteAddress(claims, id):
     user_info1 = retrieveUserInfo(claims)
     address_list = user_info1['address_list']
     del address_list[id]
     user_info1.update({
        'address_list' : address_list
     })
     datastore_client.put(user_info1)


@app.route('/delete_address/<int:id>', methods=['POST'])
def deleteAddressFromUser(id):
     id_token = request.cookies.get("token")
     error_message = None
     if id_token:
         try:
             claims = google.oauth2.id_token.verify_firebase_token(id_token,  firebase_request_adapter)
             deleteAddress(claims, id)
         except ValueError as exc:
            error_message = str(exc)
     return redirect('/')



def updateUserInfo(claims, new_string, new_int, new_float):
    entity_key = datastore_client.key('user_info1', claims['email'])
    entity = datastore_client.get(entity_key)
    entity.update({
        'string_value': new_string,
        'int_value': new_int,
        'float_value': new_float
    })
    datastore_client.put(entity)


@app.route('/edit_user_info', methods=['POST'])
def editUserInfo():
    firebase_request_adapter = requests.Request()
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    user_info1 = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            new_string = request.form['string_update']
            new_int = request.form['int_update']
            new_float = request.form['float_update']
            updateUserInfo(claims, new_string, new_int, new_float)
        except ValueError as exc:
            error_message = str(exc)
    return redirect("/")


firebase_request_adapter = requests.Request()


@app.route('/')
def root():
     id_token = request.cookies.get("token")
     error_message = None
     claims = None
     user_info1 = None
     if id_token:
         try:
             claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
             user_info1 = retrieveUserInfo(claims)
             if user_info1 == None:
                 createUserInfo1(claims)
                 user_info1 = retrieveUserInfo(claims)
         except ValueError as exc:
             error_message = str(exc)
     return render_template('index.html', user_data=claims, error_message=error_message, user_info1=user_info1)


if __name__ == '__main__':
     app.run(host='127.0.0.1', port=8080, debug=True)
