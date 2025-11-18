from flask import Flask, render_template, request, jsonify, session
import random
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # For session management

# Game configuration
MIN_NUMBER = 1
MAX_NUMBER = 100
MAX_ATTEMPTS = 10

@app.route('/')
def index():
    """Serve the game HTML page"""
    return render_template('game.html')

@app.route('/start_game', methods=['POST'])
def start_game():
    """Start a new game by generating a random number"""
    secret_number = random.randint(MIN_NUMBER, MAX_NUMBER)
    session['secret_number'] = secret_number
    session['attempts'] = 0
    session['game_over'] = False
    session['guesses'] = []
    
    return jsonify({
        'message': f'New game started! Guess a number between {MIN_NUMBER} and {MAX_NUMBER}',
        'max_attempts': MAX_ATTEMPTS,
        'min_number': MIN_NUMBER,
        'max_number': MAX_NUMBER
    })

@app.route('/guess', methods=['POST'])
def make_guess():
    """Process a user's guess"""
    try:
        data = request.get_json()
        guess = int(data.get('guess'))
        
        # Check if game has been started
        if 'secret_number' not in session:
            return jsonify({'error': 'Please start a new game first'}), 400
        
        # Check if game is already over
        if session.get('game_over', False):
            return jsonify({'error': 'Game is over. Please start a new game'}), 400
        
        # Validate guess range
        if guess < MIN_NUMBER or guess > MAX_NUMBER:
            return jsonify({
                'error': f'Please guess a number between {MIN_NUMBER} and {MAX_NUMBER}'
            }), 400
        
        # Increment attempts
        session['attempts'] = session.get('attempts', 0) + 1
        attempts_left = MAX_ATTEMPTS - session['attempts']
        
        # Add guess to history
        guesses = session.get('guesses', [])
        guesses.append(guess)
        session['guesses'] = guesses
        
        secret_number = session['secret_number']
        
        # Check if guess is correct
        if guess == secret_number:
            session['game_over'] = True
            return jsonify({
                'result': 'correct',
                'message': f'🎉 Congratulations! You guessed it in {session["attempts"]} attempts!',
                'secret_number': secret_number,
                'attempts': session['attempts'],
                'game_over': True
            })
        
        # Check if out of attempts
        elif session['attempts'] >= MAX_ATTEMPTS:
            session['game_over'] = True
            return jsonify({
                'result': 'game_over',
                'message': f'😔 Game Over! The number was {secret_number}',
                'secret_number': secret_number,
                'attempts': session['attempts'],
                'game_over': True
            })
        
        # Provide feedback
        else:
            if guess < secret_number:
                feedback = '📈 Too low! Try a higher number.'
            else:
                feedback = '📉 Too high! Try a lower number.'
            
            # Add hint for closeness
            difference = abs(guess - secret_number)
            if difference <= 5:
                hint = '🔥 You\'re very close!'
            elif difference <= 10:
                hint = '🌡️ Getting warmer!'
            elif difference <= 20:
                hint = '❄️ Getting colder...'
            else:
                hint = '🧊 Way off!'
            
            return jsonify({
                'result': 'continue',
                'message': feedback,
                'hint': hint,
                'attempts': session['attempts'],
                'attempts_left': attempts_left,
                'game_over': False
            })
    
    except ValueError:
        return jsonify({'error': 'Please enter a valid number'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/get_stats', methods=['GET'])
def get_stats():
    """Get current game statistics"""
    return jsonify({
        'attempts': session.get('attempts', 0),
        'attempts_left': MAX_ATTEMPTS - session.get('attempts', 0),
        'guesses': session.get('guesses', []),
        'game_over': session.get('game_over', False)
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)

