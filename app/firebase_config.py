import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("skyted-test-firebase-adminsdk-86xas-f6b24b09f2.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://skyted-test-default-rtdb.europe-west1.firebasedatabase.app/"
})
