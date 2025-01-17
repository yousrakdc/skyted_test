import firebase_admin
from firebase_admin import credentials, auth, db
import datetime

# Initialize Firebase Admin
cred = credentials.Certificate('skyted-test-firebase-adminsdk-86xas-f6b24b09f2.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://skyted-test-default-rtdb.europe-west1.firebasedatabase.app/'
})

# Function to login or register user
def login_or_register(email, password):
    try:
        # Try to get user from Firebase Authentication
        user = auth.get_user_by_email(email)
        
        # Check if the user exists in the Firebase Realtime Database
        ref = db.reference('users')
        user_data = ref.child(user.uid).get()

        if not user_data:
            # If user doesn't exist in the database, create a new entry
            ref.child(user.uid).set({
                'email': email,
                'uid': user.uid
            })
            print(f"User {email} added to Firebase Realtime Database.")
        
        return user
    except auth.UserNotFoundError:
        # If the user doesn't exist in Firebase Authentication, create a new user
        user = auth.create_user(email=email, password=password)

        # Store the new user in Firebase Realtime Database
        ref = db.reference('users')
        ref.child(user.uid).set({
            'email': email,
            'uid': user.uid
        })
        print(f"User {email} registered and added to Firebase Realtime Database.")
        return user
    except Exception as e:
        print(f"Error in login_or_register: {e}")
        raise e


# Firebase Database Operations
def get_users_from_firebase():
    try:
        ref = db.reference('users')
        users = ref.get()  # Fetch all users from the Firebase 'users' node
        
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
