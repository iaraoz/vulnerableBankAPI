from flask import jsonify, request, render_template, redirect, url_for, abort, make_response
from models import User, Account, Transaction
from app import db
from auth import generate_token, decode_token, requires_auth
from util import execute_raw_query
import json

def register_routes(app):
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/login', methods=['GET'])
    def login_page():
        return render_template('login.html')
    
    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')
    
    @app.route('/transfer')
    def transfer_page():
        return render_template('transfer.html')
    
    @app.route('/profile')
    def profile_page():
        return render_template('profile.html')
    
    @app.route('/api/login', methods=['POST'])
    def login():
        try:
            print("Login attempt received")
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            
            print(f"Login attempt for username: {username}")
            
            query = f"SELECT * FROM User WHERE username = '{username}' AND password = '{password}'"
            print(f"Executing query: {query}")
            
            try:
                user = execute_raw_query(query)
                print(f"Query result: {user}")
                
                if user:
                    token = generate_token(user[0]['id'])
                    return jsonify({"token": token, "user_id": user[0]['id']})
                
                return jsonify({"error": "Invalid credentials"}), 401
            except Exception as e:
                print(f"Database error: {str(e)}")
                return jsonify({"error": f"Database error: {str(e)}"}), 500
        except Exception as e:
            print(f"Login error: {str(e)}")
            return jsonify({"error": f"Login error: {str(e)}"}), 500
    
    
    @app.route('/api/accounts/<int:account_id>', methods=['GET'])
    def get_account(account_id):
        account = Account.query.get(account_id)
        
        if account:
            return jsonify(account.to_dict())
        
        return jsonify({"error": "Account not found"}), 404
    
    @app.route('/api/users/<int:user_id>/accounts', methods=['GET'])
    @requires_auth
    def get_user_accounts(user_id):
        accounts = Account.query.filter_by(user_id=user_id).all()
        return jsonify([account.to_dict() for account in accounts])
    
    @app.route('/api/users/<int:user_id>', methods=['GET'])
    @requires_auth
    def get_user(user_id):
        user = User.query.get(user_id)
        
        if user:
            return jsonify(user.to_dict())
        
        return jsonify({"error": "User not found"}), 404
    
    @app.route('/api/v1/transfer', methods=['POST'])
    @requires_auth
    def transfer_money_v1():
        data = request.get_json()
        from_account_id = data.get('from_account')
        to_account_id = data.get('to_account')
        amount = data.get('amount')
        
        from_account = Account.query.get(from_account_id)
        to_account = Account.query.get(to_account_id)
        
        if not from_account or not to_account:
            return jsonify({"error": "One or both accounts not found"}), 404
        
        from_account.balance -= float(amount)
        to_account.balance += float(amount)
        
        from_transaction = Transaction(
            account_id=from_account_id,
            transaction_type='transfer',
            amount=-float(amount),
            description=f"Transfer to account {to_account.account_number}",
            recipient_account_id=to_account_id
        )
        
        to_transaction = Transaction(
            account_id=to_account_id,
            transaction_type='transfer',
            amount=float(amount),
            description=f"Transfer from account {from_account.account_number}",
            recipient_account_id=from_account_id
        )
        
        db.session.add(from_transaction)
        db.session.add(to_transaction)
        db.session.commit()
        
        return jsonify({"status": "Transfer completed"})
    
    @app.route('/api/transfer', methods=['POST'])
    @requires_auth
    def transfer_money():
        current_user_id = decode_token(request.headers.get('Authorization').split()[1])
        data = request.get_json()
        from_account_id = data.get('from_account')
        to_account_id = data.get('to_account')
        amount = data.get('amount')
        from_account = Account.query.get(from_account_id)
        
        if not from_account or from_account.user_id != current_user_id:
            return jsonify({"error": "Account not found or unauthorized"}), 403
        
        to_account = Account.query.get(to_account_id)
        if not to_account:
            return jsonify({"error": "Recipient account not found"}), 404
        try:
            amount = float(amount)
            if amount <= 0:
                return jsonify({"error": "Amount must be positive"}), 400
        except ValueError:
            return jsonify({"error": "Invalid amount"}), 400
        
        if from_account.balance < amount:
            return jsonify({"error": "Insufficient funds"}), 400
        
        from_account.balance -= amount
        to_account.balance += amount
        
        from_transaction = Transaction(
            account_id=from_account_id,
            transaction_type='transfer',
            amount=-amount,
            description=f"Transfer to account {to_account.account_number}",
            recipient_account_id=to_account_id
        )
        
        to_transaction = Transaction(
            account_id=to_account_id,
            transaction_type='transfer',
            amount=amount,
            description=f"Transfer from account {from_account.account_number}",
            recipient_account_id=from_account_id
        )
        
        db.session.add(from_transaction)
        db.session.add(to_transaction)
        db.session.commit()
        
        return jsonify({"status": "Transfer completed", "new_balance": from_account.balance})
    
    @app.route('/api/transactions/<int:account_id>', methods=['GET'])
    @requires_auth
    def get_transactions(account_id):
        try:
            transactions = Transaction.query.filter_by(account_id=account_id).all()
            filter_type = request.args.get('type')
            if filter_type:
                transactions = [t for t in transactions if t.transaction_type == filter_type]
            
            return jsonify([transaction.to_dict() for transaction in transactions])
            
        except Exception as e:
            return jsonify({"error": str(e), "trace": str(e.__traceback__)}), 500
    
    @app.route('/api/search', methods=['GET'])
    @requires_auth
    def search_transactions():
        query = request.args.get('q', '')
        transactions = Transaction.query.filter(
            Transaction.description.like(f'%{query}%')
        ).all()
        
        return jsonify([t.to_dict() for t in transactions])
    
    @app.route('/api/check_website', methods=['POST'])
    @requires_auth
    def check_website():
        import requests
        
        data = request.get_json()
        url = data.get('url')
        
        try:
            response = requests.get(url, timeout=5)
            return jsonify({
                "status": response.status_code,
                "content_length": len(response.content)
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/debug/users', methods=['GET'])
    def debug_users():
        users = User.query.all()
        return jsonify([user.to_dict() for user in users])
    
    @app.route('/api/import_data', methods=['POST'])
    @requires_auth
    def import_data():
        import pickle
        import base64
        
        data = request.get_json()
        serialized_data = data.get('data')
    
        try:
            decoded_data = base64.b64decode(serialized_data)
            imported_data = pickle.loads(decoded_data)
            
            return jsonify({"status": "Data imported", "data": imported_data})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/admin/execute', methods=['POST'])
    @requires_auth
    def admin_execute():
        current_user_id = decode_token(request.headers.get('Authorization').split()[1])
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'admin':
            return jsonify({"error": "Unauthorized"}), 403
        
        data = request.get_json()
        sql_query = data.get('query')
        
        try:
            result = execute_raw_query(sql_query)
            return jsonify({"result": result})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/process_xml', methods=['POST'])
    @requires_auth
    def process_xml():
        import xml.etree.ElementTree as ET
        from io import StringIO
        
        xml_data = request.data.decode('utf-8')
        
        try:
            tree = ET.parse(StringIO(xml_data))
            root = tree.getroot()
            
            result = {}
            for child in root:
                result[child.tag] = child.text
                
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/admin/create_user', methods=['POST'])
    def create_user():
        data = request.get_json()
        
        new_user = User(
            username=data.get('username'),
            email=data.get('email'),
            password=data.get('password'),  
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            date_of_birth=data.get('date_of_birth'),
            ssn=data.get('ssn'),
            address=data.get('address'),
            phone=data.get('phone'),
            role=data.get('role', 'customer')
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({"status": "User created", "user_id": new_user.id})
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Endpoint not found"}), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": str(e)}), 500
