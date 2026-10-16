import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging

#only initialise firebase once for push notifications 
def initialise_firebase():
    
    if firebase_admin._apps:
        print("Firebase is already initialised")
        return firebase_admin.get_app()

    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path:
        raise RuntimeError(
            "GOOGLE_APPLICATION_CREDENTIALS is not set"
        )

    cred = credentials.Certificate(credentials_path)
    print("Firebase initialised successfully")
    return firebase_admin.initialize_app(cred)

def firebase_test_notification():
    message = messaging.Message(
        notification=messaging.Notification(
            title="Test Notification",
            body="Firebase is connected to your backend!"
        ),
        
        token="REPLACE_WITH_REAL_FCM_TOKEN"
    )
    response = messaging.send(message)
    print(f"Test notification sent successfully! Message ID: {response}")

#use try catch when calling this fn in case it fails 
def send_firebase_notification(_title, _body, _token, _data):
    message = messaging.Message(
        notification=messaging.Notification(
            title=_title,
            body=_body
        ),
        data=_data,
        token=_token
    )
    response = messaging.send(message)
    return response



