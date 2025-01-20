import firebase_admin
from firebase_admin import credentials, auth, db
import datetime
import logging
import re
import requests

# Initialize Firebase Admin
cred = credentials.Certificate('skyted-test-firebase-adminsdk-86xas-fed93af2c5.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://skyted-test-default-rtdb.europe-west1.firebasedatabase.app/'
})

logger = logging.getLogger(__name__)

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

# Function to login or register user
def login_or_register(email, password):
    try:
        if not is_valid_email(email):
            raise ValueError("Invalid email format.")
        
        # Check if the user already exists in Firebase Authentication
        try:
            user = auth.get_user_by_email(email)
            logger.info(f"User {email} found in Firebase Authentication.")

            # Check if the user exists in database
            ref = db.reference('users')
            user_data = ref.child(user.uid).get()
            
            if not user_data:
                # Add user to the database if missing
                ref.child(user.uid).set({
                    'email': email,
                    'uid': user.uid
                })
                logger.info(f"User {email} added to Firebase Realtime Database.")
                
            return user
        except auth.UserNotFoundError:
            # If user doesn't exist, create a new one
            logger.info(f"User {email} not found. Creating a new account.")
            user = auth.create_user(email=email, password=password)
            
            # Add the new user to the database
            ref = db.reference('users')
            ref.child(user.uid).set({
                'email': email,
                'uid': user.uid
            })
            logger.info(f"User {email} registered and added to Firebase Realtime Database.")
            return user
    except Exception as e:
        logger.error(f"Error in login_or_register: {e}")
        raise e

# Firebase Database Operations
def get_users_from_firebase():
    try:
        ref = db.reference('users')
        users = ref.get()  # Fetch all users from database
        
        if users:
            user_list = []
            for uid, user_data in users.items():
                user_list.append({
                    'email': user_data.get('email', 'No email found'),
                    'uid': uid
                })
            print(f"Fetched users: {user_list}")
            return user_list
        else:
            print("No users found in Firebase.")
            return []
    except Exception as e:
        print(f"Error fetching users: {str(e)}")
        return []


def get_articles_from_firebase():
    try:
        ref = db.reference('Articles')
        return ref.get() or {}
    except Exception as e:
        print(f"Error fetching articles: {e}")
        return {}

def add_article_to_firebase(title, content):
    try:
        ref = db.reference('Articles')
        article_data = {
            "title": title,
            "content": content,
            "timestamp": datetime.datetime.now().isoformat(),
        }
        new_article = ref.push(article_data)
        return new_article.key
    except Exception as e:
        print(f"Error adding article: {e}")
        raise e

def delete_article_from_firebase(article_id):
    try:
        ref = db.reference(f'Articles/{article_id}')
        ref.delete()
        print(f"Deleted article with ID: {article_id}")
    except Exception as e:
        print(f"Error deleting article: {e}")
        raise e

def modify_article_in_firebase(article_id, new_title, new_content):
    try:
        ref = db.reference(f'Articles/{article_id}')
        updated_data = {
            "title": new_title,
            "content": new_content,
            "timestamp": datetime.datetime.now().isoformat(),
        }
        ref.update(updated_data)
        print(f"Article {article_id} updated successfully.")
    except Exception as e:
        print(f"Error modifying article: {e}")
        raise e
