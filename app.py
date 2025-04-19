import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
from Crypto.Cipher import AES
import base64
import time
import random
from datetime import timedelta
from Crypto.Util.Padding import unpad

app = Flask(__name__)
CORS(app)

SECRET_KEY = b'lhoiyrtevcyrtfvs'
IV = b'usrqutsvbxcjpoyt'
API_REQUEST_LIMIT = 30
DATABASE = 'quotes.db'
DEVICE_ACCESS_DB = 'device_access.db'

# Database initialization
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Create quotes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote TEXT NOT NULL,
            author TEXT NOT NULL
        )
    ''')

    # Insert initial quotes if the table is empty
    cursor.execute('SELECT COUNT(*) FROM quotes')
    if cursor.fetchone()[0] == 0:
        initial_quotes = [
            {"quote": "The only limit to our realization of tomorrow is our doubts of today.", "author": "Franklin D. Roosevelt"},
            {"quote": "The purpose of our lives is to be happy.", "author": "Dalai Lama"},
            # Add more quotes as needed
        ]
        for q in initial_quotes:
            cursor.execute('INSERT INTO quotes (quote, author) VALUES (?, ?)', (q['quote'], q['author']))

    conn.commit()
    conn.close()

def init_device_access_db():
    conn = sqlite3.connect(DEVICE_ACCESS_DB)
    cursor = conn.cursor()

    # Create device_access table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS device_access (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            access_time INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Function to add device access
def add_device_access(device_id, access_time):
    conn = sqlite3.connect(DEVICE_ACCESS_DB)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO device_access (device_id, access_time) VALUES (?, ?)', (device_id, access_time))
    conn.commit()
    conn.close()

# Function to get device access count
def get_device_access_count(device_id, current_time):
    conn = sqlite3.connect(DEVICE_ACCESS_DB)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM device_access WHERE access_time < ?', (current_time - 86400000,))
    conn.commit()
    cursor.execute('SELECT COUNT(*) FROM device_access WHERE device_id = ?', (device_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

# Function to get time until reset
def get_time_until_reset(device_id, current_time):
    conn = sqlite3.connect(DEVICE_ACCESS_DB)
    cursor = conn.cursor()
    cursor.execute('SELECT MIN(access_time) FROM device_access WHERE device_id = ?', (device_id,))
    first_access_time = cursor.fetchone()[0]
    conn.close()
    if first_access_time:
        time_until_reset = (first_access_time + 86400000) - current_time
        return timedelta(milliseconds=time_until_reset)
    return None

# Function to fetch a random quote from the database
def get_random_quote():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, quote, author FROM quotes ORDER BY RANDOM() LIMIT 1')
    row = cursor.fetchone()
    conn.close()
    if row:
        return {'id': row[0], 'quote': row[1], 'author': row[2]}
    return None

# Encryption/Decryption functions
def is_hex(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False

def decrypt_v1(encrypted_text):
    if not is_hex(encrypted_text):
        raise ValueError("Non-base16 digit found in encrypted text")

    cipher = AES.new(SECRET_KEY, AES.MODE_CBC, IV)
    decrypted = cipher.decrypt(base64.b16decode(encrypted_text.upper()))
    try:
        decrypted = unpad(decrypted, AES.block_size)
    except ValueError:
        raise ValueError("Decryption error: Invalid padding")
    return decrypted.decode('utf-8').strip()

def decrypt(encrypted_text):
    if not is_hex(encrypted_text):
        raise ValueError("Non-base16 digit found in encrypted text")

    cipher = AES.new(SECRET_KEY, AES.MODE_CBC, IV)
    decrypted = cipher.decrypt(base64.b16decode(encrypted_text.upper()))
    return decrypted.decode('utf-8').strip()

# API endpoint to get a quote
@app.route('/getQuote', methods=['POST'])
def decrypt_payload():
    data = request.json
    param = data.get('param')
    try:
        decryptedMsg = decrypt(param).strip()
    except Exception as e:
        return jsonify({'error': 'Invalid Data'}), 400
    decrypted_time, decrypted_device_id = decryptedMsg.split('@PWA')

    reSubmit = data.get('reSubmit')

    if not decrypted_time or not decrypted_device_id:
        return jsonify({'error': 'Invalid payload'}), 400

    current_time = int(time.time() * 1000)
    threshold = 1 * 48 * 60 * 60 * 1000

    if current_time - int(decrypted_time) > threshold:
        return jsonify({'error': 'Expired'}), 400

    conn = sqlite3.connect(DEVICE_ACCESS_DB)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM device_access WHERE device_id = ? AND access_time = ?', (decrypted_device_id, decrypted_time))
    count = cursor.fetchone()[0]
    conn.close()

    if count > 0 and not reSubmit:
        return jsonify({'error': 'Already Existing Data'}), 400

    access_count = get_device_access_count(decrypted_device_id, current_time)
    if access_count >= API_REQUEST_LIMIT:
        time_until_reset = get_time_until_reset(decrypted_device_id, current_time)
        if time_until_reset:
            hours, remainder = divmod(time_until_reset.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return jsonify({
                'error': 'Access limit reached',
                'retry_after': f'{hours} hours {minutes} minutes'
            }), 429

    add_device_access(decrypted_device_id, decrypted_time)

    selected_quote = get_random_quote()
    if selected_quote:
        return jsonify({
            'message': 'Success',
            'quote': selected_quote['quote'],
            'writer': selected_quote['author']
        })
    else:
        return jsonify({'error': 'No quotes found'}), 500

if __name__ == '__main__':
    init_db()  # Initialize the quotes database
    init_device_access_db()  # Initialize the device_access database
    app.run(host='0.0.0.0', port=5001, debug=True)