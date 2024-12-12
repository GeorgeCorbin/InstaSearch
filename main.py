from flask import Flask, render_template, request, jsonify
import requests
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# Instagram Graph API credentials
ACCESS_TOKEN = os.getenv("token")  # Set this in your environment variables
BASE_URL = "https://graph.instagram.com"
# HANDLE = "goob_u2"  # Instagram handle for the specific user
HANDLE = "george_corbin_"  # Instagram handle for the specific user

# Database initialization
def init_db():
    conn = sqlite3.connect('posts.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            caption TEXT,
            media_type TEXT,
            media_url TEXT,
            timestamp TEXT,
            permalink TEXT
        )
    ''')
    conn.commit()
    conn.close()


# Fetch user ID by username
# def get_user_id(username):
#     url = f"{BASE_URL}/me/accounts?access_token={ACCESS_TOKEN}"
#     response = requests.get(url)
#     if response.status_code == 200:
#         accounts = response.json().get("data", [])
#         for account in accounts:
#             if account.get("username") == username:
#                 return account.get("id")
#     print(f"Error fetching user ID: {response.status_code}", response.json())
#     return None

# Fetch posts from Instagram and store in the database
def fetch_posts():
    # user_id = get_user_id(HANDLE)
    # if not user_id:
    #     print(f"User ID for handle {HANDLE} not found.")
    #     return

    url = f"{BASE_URL}/me/media?fields=id,caption,media_type,media_url,timestamp&access_token={ACCESS_TOKEN}"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            data = response.json().get("data", [])
            conn = sqlite3.connect('posts.db')
            cursor = conn.cursor()
            for post in data:
                # print("Inserting post:", post)  # Debug each post
                cursor.execute('''
                    INSERT OR REPLACE INTO posts (id, caption, media_type, media_url, timestamp, permalink)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (post.get("id"), post.get("caption"), post.get("media_type"), post.get("media_url"), post.get("timestamp"), post.get("permalink")))
            conn.commit()
            conn.close()
            print("Posts inserted successfully.")
        except ValueError as e:
            print("Error parsing JSON:", str(e))
            print("Response text:", response.text)

    else:
        print(f"Failed to fetch posts. HTTP Status Code: {response.status_code}")
        print("Response text:", response.text)

def check_posts():
    conn = sqlite3.connect('posts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts")
    rows = cursor.fetchall()
    conn.close()
    print("Posts in database:")
    for row in rows:
        print(row)

# Home route
@app.route('/')
def home():
    init_db()
    fetch_posts()
    # check_posts()
    return render_template('search.html')

# Search route
@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    conn = sqlite3.connect('posts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE caption LIKE ?", ('%' + query + '%',))
    results = cursor.fetchall()
    conn.close()

    formatted_results = []
    for post in results:
        formatted_post = list(post)
        formatted_post[4] = datetime.strptime(post[4], '%Y-%m-%dT%H:%M:%S+0000').strftime('%d/%m/%Y')
        formatted_results.append(formatted_post)

    return render_template('results.html', results=formatted_results)

'''
# Fetch posts (manual trigger for this demo)
@app.route('/fetch_posts', methods=['GET'])
def fetch():
    fetch_posts()
    return jsonify({"status": "success", "message": "Posts fetched and stored."})

# Enhanced functionality: sorting and filtering
@app.route('/filter', methods=['GET'])
def filter_results():
    sort_by = request.args.get('sort_by')
    conn = sqlite3.connect('posts.db')
    cursor = conn.cursor()
    if sort_by == "date":
        cursor.execute("SELECT * FROM posts ORDER BY timestamp DESC")
    elif sort_by == "media_type":
        cursor.execute("SELECT * FROM posts ORDER BY media_type")
    results = cursor.fetchall()
    conn.close()
    return render_template('results.html', results=results)

# Fun enhancement: Dynamic search animation and live updates
@app.route('/live_search', methods=['POST'])
def live_search():
    query = request.form['query']
    conn = sqlite3.connect('posts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE caption LIKE ?", ('%' + query + '%',))
    results = cursor.fetchall()
    conn.close()
    return jsonify(results)

# Autocomplete functionality
@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('query', '').lower()
    conn = sqlite3.connect('posts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT caption FROM posts WHERE caption LIKE ?", ('%' + query + '%',))
    captions = cursor.fetchall()
    conn.close()
    suggestions = [caption[0] for caption in captions if caption[0]]
    return jsonify(suggestions)
'''
if __name__ == '__main__':
    app.run(debug=True)