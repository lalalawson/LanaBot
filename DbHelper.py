import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
from dotenv import load_dotenv

load_dotenv()

cert = {
  "type": os.getenv("type"),
  "project_id": os.getenv("project_id"),
  "private_key_id": os.getenv("private_key_id"),
  "private_key": os.getenv("private_key"),
  "client_email": os.getenv("client_email"),
  "client_id": os.getenv("client_id"),
  "auth_uri": os.getenv("auth_uri"),
  "token_uri": os.getenv("token_uri"),
  "auth_provider_x509_cert_url": os.getenv("auth_provider_x509_cert_url"),
  "client_x509_cert_url": os.getenv("client_x509_cert_url")
}

# Use a service account
cred = credentials.Certificate(cert)
firebase_admin.initialize_app(cred)

# database instance
db = firestore.client()

doc_ref = db.collection(u'memories').document(u'1')

doc = doc_ref.get()

if doc.exists:
    print(f'Document data: {doc.to_dict()}')
else:
    print(u'No such document!')