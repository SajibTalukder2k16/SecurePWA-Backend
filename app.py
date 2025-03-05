quotes = [
    {"quote": "The only limit to our realization of tomorrow is our doubts of today.", "author": "Franklin D. Roosevelt"},
    {"quote": "The purpose of our lives is to be happy.", "author": "Dalai Lama"},
    {"quote": "Life is what happens when you're busy making other plans.", "author": "John Lennon"},
    {"quote": "Get busy living or get busy dying.", "author": "Stephen King"},
    {"quote": "You have within you right now, everything you need to deal with whatever the world can throw at you.", "author": "Brian Tracy"},
    {"quote": "Do what you can, with what you have, where you are.", "author": "Theodore Roosevelt"},
    {"quote": "Success is not final, failure is not fatal: It is the courage to continue that counts.", "author": "Winston Churchill"},
    {"quote": "Believe you can and you're halfway there.", "author": "Theodore Roosevelt"},
    {"quote": "It does not matter how slowly you go as long as you do not stop.", "author": "Confucius"},
    {"quote": "Act as if what you do makes a difference. It does.", "author": "William James"},
    {"quote": "What lies behind us and what lies before us are tiny matters compared to what lies within us.", "author": "Ralph Waldo Emerson"},
    {"quote": "Happiness depends upon ourselves.", "author": "Aristotle"},
    {"quote": "Turn your wounds into wisdom.", "author": "Oprah Winfrey"},
    {"quote": "It is never too late to be what you might have been.", "author": "George Eliot"},
    {"quote": "The best way to predict the future is to create it.", "author": "Peter Drucker"},
    {"quote": "Everything you can imagine is real.", "author": "Pablo Picasso"},
    {"quote": "Do what you feel in your heart to be right – for you’ll be criticized anyway.", "author": "Eleanor Roosevelt"},
    {"quote": "To be yourself in a world that is constantly trying to make you something else is the greatest accomplishment.", "author": "Ralph Waldo Emerson"},
    {"quote": "Do what you love and the money will follow.", "author": "Marsha Sinetar"},
    {"quote": "Opportunities don't happen. You create them.", "author": "Chris Grosser"},
    {"quote": "I never dreamed about success. I worked for it.", "author": "Estee Lauder"},
    {"quote": "Don't watch the clock; do what it does. Keep going.", "author": "Sam Levenson"},
    {"quote": "If everything seems under control, you're not going fast enough.", "author": "Mario Andretti"},
    {"quote": "Everything has beauty, but not everyone sees it.", "author": "Confucius"},
    {"quote": "It’s not whether you get knocked down, it’s whether you get up.", "author": "Vince Lombardi"},
    {"quote": "Dream big and dare to fail.", "author": "Norman Vaughan"},
    {"quote": "We become what we think about.", "author": "Earl Nightingale"},
    {"quote": "Nothing is impossible, the word itself says ‘I’m possible’!", "author": "Audrey Hepburn"},
    {"quote": "Don’t count the days, make the days count.", "author": "Muhammad Ali"},
    {"quote": "Be yourself; everyone else is already taken.", "author": "Oscar Wilde"},
    {"quote": "A journey of a thousand miles begins with a single step.", "author": "Lao Tzu"},
    {"quote": "The way to get started is to quit talking and begin doing.", "author": "Walt Disney"},
    {"quote": "Keep your face always toward the sunshine—and shadows will fall behind you.", "author": "Walt Whitman"},
    {"quote": "Success is getting what you want. Happiness is wanting what you get.", "author": "Dale Carnegie"},
    {"quote": "Your time is limited, so don’t waste it living someone else’s life.", "author": "Steve Jobs"},
    {"quote": "Success usually comes to those who are too busy to be looking for it.", "author": "Henry David Thoreau"},
    {"quote": "Failure is simply the opportunity to begin again, this time more intelligently.", "author": "Henry Ford"},
    {"quote": "Do not go where the path may lead, go instead where there is no path and leave a trail.", "author": "Ralph Waldo Emerson"},
    {"quote": "To succeed in life, you need two things: ignorance and confidence.", "author": "Mark Twain"},
    {"quote": "I attribute my success to this: I never gave or took any excuse.", "author": "Florence Nightingale"},
    {"quote": "You must be the change you wish to see in the world.", "author": "Mahatma Gandhi"},
    {"quote": "Quality means doing it right when no one is looking.", "author": "Henry Ford"},
    {"quote": "When you reach the end of your rope, tie a knot in it and hang on.", "author": "Franklin D. Roosevelt"},
    {"quote": "If you really look closely, most overnight successes took a long time.", "author": "Steve Jobs"},
    {"quote": "Don’t let yesterday take up too much of today.", "author": "Will Rogers"},
    {"quote": "Hardships often prepare ordinary people for an extraordinary destiny.", "author": "C.S. Lewis"},
    {"quote": "The mind is everything. What you think you become.", "author": "Buddha"},
    {"quote": "People who are crazy enough to think they can change the world, are the ones who do.", "author": "Rob Siltanen"},
    {"quote": "Do what you can, with what you have, where you are.", "author": "Theodore Roosevelt"},
    {"quote": "What you get by achieving your goals is not as important as what you become by achieving your goals.", "author": "Zig Ziglar"},
    {"quote": "It always seems impossible until it’s done.", "author": "Nelson Mandela"},
    {"quote": "Success is not how high you have climbed, but how you make a positive difference to the world.", "author": "Roy T. Bennett"},
    {"quote": "A person who never made a mistake never tried anything new.", "author": "Albert Einstein"},
    {"quote": "If opportunity doesn’t knock, build a door.", "author": "Milton Berle"},
    {"quote": "Success is a journey, not a destination.", "author": "Arthur Ashe"},
    {"quote": "Do what you feel in your heart to be right—for you’ll be criticized anyway.", "author": "Eleanor Roosevelt"},
    {"quote": "Everything you’ve ever wanted is on the other side of fear.", "author": "George Addair"},
    {"quote": "Live as if you were to die tomorrow. Learn as if you were to live forever.", "author": "Mahatma Gandhi"},
    {"quote": "Success is not in what you have, but who you are.", "author": "Bo Bennett"},
    {"quote": "Small deeds done are better than great deeds planned.", "author": "Peter Marshall"}
]



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





from Crypto.Util.Padding import unpad  # Import unpad function

def decrypt(encrypted_text):
    if not is_hex(encrypted_text):
        raise ValueError("Non-base16 digit found in encrypted text")

    cipher = AES.new(SECRET_KEY, AES.MODE_CBC, IV)
    decrypted = cipher.decrypt(base64.b16decode(encrypted_text.upper()))

    # Properly remove AES PKCS7 padding
    #try:
    #decrypted = unpad(decrypted, AES.block_size)  # Remove padding
    # except ValueError:
    #     raise ValueError("Decryption error: Invalid padding")

    return decrypted.decode('utf-8').strip()  #

@app.route('/getQuote', methods=['POST'])
def decrypt_payload():
    data = request.json
    param = data.get('param')
    try:
        decryptedMsg = decrypt(param).strip()
        print(f"Decrypted Param: {decryptedMsg}")
    except Exception as e:
        return jsonify({'error': 'Invalid Data'}), 400
    decrypted_time, decrypted_device_id = decryptedMsg.split('@PWA')

    print(f"Decrypted Time: {decrypted_time}")
    print(f"Decrypted Device ID: {decrypted_device_id}")

    reSubmit = data.get('reSubmit')

    if not decrypted_time or not decrypted_device_id:
        return jsonify({'error': 'Invalid payload'}), 400



    current_time = int(time.time() * 1000)

    threshold = 1*24*60*60 * 1000
    print("Current Time: ", current_time)
    print("After adding threshold", (int(decrypted_time) + threshold))
    print ("value: ", current_time  - (int(decrypted_time) + threshold ))
    if current_time  - int(decrypted_time) > threshold :
        return jsonify({'error': 'Expired'}), 400

    conn = sqlite3.connect('device_access.db')
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

    selected_quote = random.choice(quotes)

    return jsonify({
        'message': 'Success',
        'quote': selected_quote['quote'],
        'writer': selected_quote['author']
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)