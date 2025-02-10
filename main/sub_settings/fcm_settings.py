import firebase_admin
from firebase_admin import credentials

# Firebase Admin SDK 초기화
FIREBASE_CRED = credentials.Certificate("wasso-de97b-990d2916925c.json")
firebase_admin.initialize_app(FIREBASE_CRED)
