
import jwt
from datetime import datetime, timedelta

def create_token(user_id):
    exp = datetime.utcnow() + timedelta(hours=24)  # Fixed!
    return jwt.encode({'user_id': user_id, 'exp': exp}, 
                      os.getenv('JWT_SECRET'), algorithm='HS256')
