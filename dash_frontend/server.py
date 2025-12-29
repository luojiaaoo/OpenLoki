import dash
from configure import conf
from blueprint import conversion_api
from flask import jsonify, request
from utils.digest_auth import digest_auth
import tomllib

app = dash.Dash(
    __name__,
    title=conf.app_title,
    update_title=None,
    suppress_callback_exceptions=True,
)

server = app.server
server.register_blueprint(
    conversion_api.component_bp,
    url_prefix='/component',
)


@server.route('/export_data', methods=['get'])
def get_backend_url():
    return jsonify(
        dict(
            backend_url=conf.backend_url,
        )
    ), 200


@server.before_request
def protected_resource():
    def get_user_password(username):
        with open(conf.digest_user_auth_filepath, 'rb') as f:
            user_auth_config = tomllib.load(f)
        return user_auth_config.get(username, {}).get('password')

    # 1. 检查请求头中是否有Authorization信息
    auth_header = request.headers.get('Authorization')

    # 2. 尝试认证
    username = digest_auth.authenticate(auth_header, request.method, request.path, get_user_password)

    if username == ...:
        return jsonify(error='Stale nonce, please retry'), 401, {'WWW-Authenticate': digest_auth.generate_challenge(is_stale=True)}

    # 3. 如果认证失败，返回401挑战
    if username is None:
        challenge = digest_auth.generate_challenge()
        return jsonify(error='Authentication required'), 401, {'WWW-Authenticate': challenge}


if __name__ == '__main__':
    app.run(debug=True)
