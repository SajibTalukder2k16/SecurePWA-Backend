from flask import Flask, request, jsonify
from flask_cors import CORS
from Crypto.Cipher import AES
import base64
import time
import random
import sqlite3
from datetime import timedelta


def init_db():
    conn = sqlite3.connect('device_access.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS device_access (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            access_time INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def add_device_access(device_id, access_time):
    conn = sqlite3.connect('device_access.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO device_access (device_id, access_time) VALUES (?, ?)', (device_id, access_time))
    conn.commit()
    conn.close()

def get_device_access_count(device_id, current_time):
    conn = sqlite3.connect('device_access.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM device_access WHERE access_time < ?', (current_time - 86400000,))
    conn.commit()
    cursor.execute('SELECT COUNT(*) FROM device_access WHERE device_id = ?', (device_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_time_until_reset(device_id, current_time):
    conn = sqlite3.connect('device_access.db')
    cursor = conn.cursor()
    cursor.execute('SELECT MIN(access_time) FROM device_access WHERE device_id = ?', (device_id,))
    first_access_time = cursor.fetchone()[0]
    conn.close()
    if first_access_time:
        time_until_reset = (first_access_time + 86400000) - current_time
        return timedelta(milliseconds=time_until_reset)
    return None

app = Flask(__name__)
CORS(app)

SECRET_KEY = b'lhoiyrtevcyrtfvs'
IV = b'usrqutsvbxcjpoyt'
API_REQUEST_LIMIT = 30

def is_hex(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False

def decrypt_v0(encrypted_text):
    if not is_hex(encrypted_text):
        raise ValueError("Non-base16 digit found in encrypted text")

    cipher = AES.new(SECRET_KEY, AES.MODE_CBC, IV)
    decrypted = cipher.decrypt(base64.b16decode(encrypted_text.upper()))
    return decrypted.decode('utf-8').strip()

quotes = [
    {"quote": "The only limit to our realization of tomorrow is our doubts of today.", "author": "Franklin D. Roosevelt"},
    {"quote": "The purpose of our lives is to be happy.", "author": "Dalai Lama"},
    {"quote": "Life is what happens when you're busy making other plans.", "author": "John Lennon"},
    {"quote": "Get busy living or get busy dying.", "author": "Stephen King"},
    {"quote": "You have within you right now, everything you need to deal with whatever the world can throw at you.", "author": "Brian Tracy"}
]

from Crypto.Util.Padding import unpad  # Import unpad function

def decrypt(encrypted_text):
    if not is_hex(encrypted_text):
        raise ValueError("Non-base16 digit found in encrypted text")

    cipher = AES.new(SECRET_KEY, AES.MODE_CBC, IV)
    decrypted = cipher.decrypt(base64.b16decode(encrypted_text.upper()))

    # Properly remove AES PKCS7 padding
    try:
        decrypted = unpad(decrypted, AES.block_size)  # Remove padding
    except ValueError:
        raise ValueError("Decryption error: Invalid padding")

    return decrypted.decode('utf-8').strip()  #

@app.route('/getQuote', methods=['POST'])
def decrypt_payload():
    data = request.json
    encryptMsg = data.get('enM')
    encryptID = data.get('enI')
    reSubmit = data.get('reSubmit')

    if not encryptMsg or not encryptID:
        return jsonify({'error': 'Invalid payload'}), 400

    try:
        decrypted_time = decrypt(encryptMsg).strip()
        decrypted_device_id = decrypt(encryptID).strip()
        #print(f"Decrypted Device ID: {decrypted_device_id}")
        #print(f"Decrypted Timestamp: {decrypted_time}")
    except Exception as e:
        return jsonify({'error': 'Invalid device ID or timestamp'}), 400

    current_time = int(time.time() * 1000)
    #print(type(decrypted_time))
    #print(type(current_time))
    #print(len(decrypted_time))
    #print(len(str(current_time)))
    if current_time > int(decrypted_time):
        return jsonify({'error': 'Timestamp expired'}), 400

    conn = sqlite3.connect('device_access.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM device_access WHERE device_id = ? AND access_time = ?', (decrypted_device_id, decrypted_time))
    count = cursor.fetchone()[0]
    conn.close()

    if count > 0 and not reSubmit:
        return jsonify({'error': 'Exists'}), 400

    access_count = get_device_access_count(decrypted_device_id, current_time)
    if access_count >= API_REQUEST_LIMIT:
        time_until_reset = get_time_until_reset(decrypted_device_id, current_time)
        if time_until_reset:
            hours, remainder = divmod(time_until_reset.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return jsonify({
                'error': 'API access limit reached',
                'retry_after': f'{hours} hours {minutes} minutes'
            }), 429

    add_device_access(decrypted_device_id, decrypted_time)

    selected_quote = random.choice(quotes)

    return jsonify({
        'message': 'Success',
        'device_id': decrypted_device_id,
        'timestamp': decrypted_time,
        'quote': selected_quote['quote'],
        'writer': selected_quote['author']
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)