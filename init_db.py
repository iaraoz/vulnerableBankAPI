from app import app, db
from models import User, Account, Transaction
from datetime import datetime, date
import random
import string

def generate_account_number():
    """Generate a random 10-digit account number"""
    return ''.join(random.choice(string.digits) for _ in range(10))

def initialize_database():
    """Initialize the database with sample data"""
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        print("Creating sample users...")
        
        # Create admin user
        admin = User(
            username="admin",
            email="admin@vulnerablebank.com",
            password="admin123", 
            first_name="Admin",
            last_name="User",
            date_of_birth=date(1980, 1, 1),
            ssn="123-45-6789",
            address="123 Admin St, Secure City, SC 12345",
            phone="555-123-4567",
            role="admin"
        )
        db.session.add(admin)
        
        users = [
            User(
                username="john.doe",
                email="john.doe@example.com",
                password="password123", 
                first_name="John",
                last_name="Doe",
                date_of_birth=date(1985, 5, 15),
                ssn="987-65-4321",
                address="456 Main St, Anytown, AT 67890",
                phone="555-987-6543",
                role="customer"
            ),
            User(
                username="jane.smith",
                email="jane.smith@example.com",
                password="password456",
                first_name="Jane",
                last_name="Smith",
                date_of_birth=date(1990, 8, 21),
                ssn="456-78-9012",
                address="789 Oak St, Somewhere, SW 13579",
                phone="555-456-7890",
                role="customer"
            ),
            User(
                username="bob.johnson",
                email="bob.johnson@example.com",
                password="password789",
                first_name="Bob",
                last_name="Johnson",
                date_of_birth=date(1975, 3, 10),
                ssn="789-01-2345",
                address="101 Pine St, Nowhere, NW 24680",
                phone="555-789-0123",
                role="customer"
            ),
            User(
                username="alice.williams",
                email="alice.williams@example.com",
                password="passwordabc",  
                first_name="Alice",
                last_name="Williams",
                date_of_birth=date(1995, 11, 30),
                ssn="234-56-7890",
                address="202 Maple St, Elsewhere, EW 97531",
                phone="555-234-5678",
                role="customer"
            ),
            User(
                username="manager",
                email="manager@vulnerablebank.com",
                password="manager456",
                first_name="Bank",
                last_name="Manager",
                date_of_birth=date(1970, 7, 7),
                ssn="567-89-0123",
                address="303 Manager Blvd, Banktown, BT 13579",
                phone="555-567-8901",
                role="manager"
            )
        ]
        
        for user in users:
            db.session.add(user)
        
        db.session.commit()
        
        print("Creating accounts for users...")
        
        all_users = User.query.all()
        for user in all_users:
            checking = Account(
                account_number=generate_account_number(),
                account_type="checking",
                balance=random.uniform(1000, 10000),
                user_id=user.id
            )
            
            savings = Account(
                account_number=generate_account_number(),
                account_type="savings",
                balance=random.uniform(5000, 50000),
                user_id=user.id
            )
            
            db.session.add(checking)
            db.session.add(savings)
        
        db.session.commit()
        
        print("Creating sample transactions...")
        
        accounts = Account.query.all()
        
        
        for _ in range(50):
        
            account = random.choice(accounts)
            
            if random.choice([True, False]): 
                transaction = Transaction(
                    account_id=account.id,
                    transaction_type="deposit",
                    amount=random.uniform(100, 1000),
                    description="Deposit",
                    timestamp=datetime.utcnow()
                )
            else:
                transaction = Transaction(
                    account_id=account.id,
                    transaction_type="withdrawal",
                    amount=random.uniform(50, 500),
                    description="Withdrawal",
                    timestamp=datetime.utcnow()
                )
            
            db.session.add(transaction)
        
        for _ in range(30):
            from_account = random.choice(accounts)
            to_account = random.choice([a for a in accounts if a.id != from_account.id])
            amount = random.uniform(100, 1000)
        
            from_transaction = Transaction(
                account_id=from_account.id,
                transaction_type="transfer",
                amount=-amount,
                description=f"Transfer to account {to_account.account_number}",
                recipient_account_id=to_account.id,
                timestamp=datetime.utcnow()
            )
            
            to_transaction = Transaction(
                account_id=to_account.id,
                transaction_type="transfer",
                amount=amount,
                description=f"Transfer from account {from_account.account_number}",
                recipient_account_id=from_account.id,
                timestamp=datetime.utcnow()
            )
            
            db.session.add(from_transaction)
            db.session.add(to_transaction)
        
        db.session.commit()
        
        print("Database initialization complete!")

if __name__ == "__main__":
    initialize_database()
