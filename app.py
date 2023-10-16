from flask import Flask, request, redirect, session, url_for, render_template
from requests_oauthlib import OAuth2Session
import requests
import os
import argparse

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

parser = argparse.ArgumentParser(description='Descrição do seu script.')
parser.add_argument('--secret_key', type=str)
parser.add_argument('--client_id', type=str)
parser.add_argument('--client_secret', type=str)

args = parser.parse_args()

app = Flask(__name__)
app.secret_key = args.secret_key

client_id = args.client_id
client_secret = args.client_secret
authorization_base_url = 'https://github.com/login/oauth/authorize'
token_url = 'https://github.com/login/oauth/access_token'


def clear_session():
    session.clear()


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/github_login')
def github_login():
    if 'oauth_token' in session:
        return redirect(url_for('callback'))

    github = OAuth2Session(client_id)
    authorization_url, state = github.authorization_url(authorization_base_url)

    session['oauth_state'] = state

    return redirect(authorization_url)


@app.route('/callback', methods=['GET'])
def callback():
    if 'oauth_state' not in session:
        return redirect(url_for('index'))

    github = OAuth2Session(client_id, state=session['oauth_state'])
    token = github.fetch_token(token_url, client_secret=client_secret,
                               authorization_response=request.url)

    print(token)
    user_info_response = github.get('https://api.github.com/user')

    if user_info_response.status_code == 200:
        user_info = user_info_response.json()
        session['oauth_token'] = token
        return render_template('welcome.html', user_info=user_info)
    else:
        return redirect(url_for('github_login'))


@app.route('/logout')
def logout():
    session.pop('oauth_state', None)
    session.pop('oauth_token', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
