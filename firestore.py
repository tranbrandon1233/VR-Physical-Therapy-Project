import firebase_admin
from firebase_admin import credentials, db
from firebase_admin import firestore
from firebase_admin import initialize_app
from dotenv import load_dotenv
import os

load_dotenv()

FIREBASE_URL = os.getenv("FIREBASE_URL")

data = {
  "game_type": "Forearm Flexors",
}

cred = credentials.Certificate("cred.json")
firebase_admin.initialize_app(cred, {
  'databaseURL':FIREBASE_URL
  })

ref = db.reference('/api')
ref.update(data)

print(ref.get())