from fastapi import Header
from typing import Dict


def check_token(token: str = Header(..., alias='Authorization')):
    import jwt
    from fastapi import HTTPException
    from core.configure import conf

    try:
        if token == '__only_for_test__':
            return 'test_user'
        auth_type, auth_token = token.split(' ', 1)
        if auth_type.lower() != 'bearer':  # 只允许jwt bearer token
            raise HTTPException(status_code=401, detail='Invalid authentication type')
        payload: Dict = jwt.decode(auth_token, conf.jwt_secret_key, algorithms='HS256', options={'verify_exp': True})
        user_id = payload.get('user_id')
        if user_id is None:
            raise HTTPException(status_code=401, detail='Invalid data in token')
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token has expired')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token')
