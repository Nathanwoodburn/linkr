from flask import Flask, make_response, redirect, request, jsonify, render_template, send_from_directory
import os
import dotenv
import requests
import json
import db
import varo_auth
import account
import render
import re

app = Flask(__name__)
dotenv.load_dotenv()

# Database connection
dbargs = {
    'host':os.getenv('DB_HOST'),
    'user':os.getenv('DB_USER'),
    'password':os.getenv('DB_PASSWORD'),
    'database':os.getenv('DB_NAME')
}
ADMIN_DOMAIN = os.getenv('ADMIN_DOMAIN')
if ADMIN_DOMAIN == None:
    ADMIN_DOMAIN = "nathan.woodburn"

#Assets routes
@app.route('/assets/<path:path>')
def assets(path):
    return send_from_directory('templates/assets', path)


def error(message):
    if 'linkr' not in request.cookies:
        return redirect('/')

    token = request.cookies['linkr']
    domain = account.get_user(token)
    if domain == False:
        resp = make_response(redirect('/'))
        resp.set_cookie('linkr', '', expires=0)
        return resp
        
    avatar=account.get_avatar(domain)
    host = request.host
    links = db.get_users_links(domain)
    link_count = len(links)
    if links == False:
        links = "<h1>No links created yet</h1>"
    else:
        links = render.links(links,host)
    return render_template('dash.html',domain=domain,avatar=avatar,host=host,links=links,link_count=link_count,message=message)

@app.route('/')
def index():
    if 'linkr' in request.cookies:
        token = request.cookies['linkr']
        domain = account.get_user(token)
        if domain != False:
            return redirect('/dash')
        else:
            resp = make_response(redirect('/'))
            resp.set_cookie('linkr', '', expires=0)
            return resp
        
    links = db.get_link_count()
    accounts = db.get_account_count()
    
    return render_template('index.html',links=links,accounts=accounts)

@app.route('/dash')
def edit():
    if 'linkr' not in request.cookies:
        return redirect('/')

    token = request.cookies['linkr']
    domain = account.get_user(token)
    if domain == False:
        resp = make_response(redirect('/'))
        resp.set_cookie('linkr', '', expires=0)
        return resp
        
    avatar=account.get_avatar(domain)
    host = request.host
    admin=False
    if domain.lower() == ADMIN_DOMAIN:
        links = db.get_all_links()
        admin=True
    else:
        links = db.get_users_links(domain)
    link_count = len(links)
    if links == False:
        links = "<h1>No links created yet</h1>"
    else:
        links = render.links(links,host,admin)
    return render_template('dash.html',domain=domain,avatar=avatar,host=host,links=links,link_count=link_count)

@app.route('/dash', methods=['POST'])
def add_link():
    if 'linkr' not in request.cookies:
        return redirect('/')

    token = request.cookies['linkr']
    domain = account.get_user(token)
    if domain == False:
        resp = make_response(redirect('/'))
        resp.set_cookie('linkr', '', expires=0)
        return resp

    link=request.form['link']
    url=request.form['url'].lower()

    # Verify link is valid
    if not (url.startswith('http://') or url.startswith('https://')):
        url = 'https://' + url

    regexmatch = re.match(r"^https?://([a-z0-9]+(-[a-z0-9]+)*\.)*([a-z0-9]+(-[a-z0-9]+)*)(/([a-z0-9.])+(-([a-z0-9.])+)?)*$", url)
    if not regexmatch:
        return error('Invalid domain')
    
    if len(link) > 32:
        return error('Link too long')
    if len(link) < 5:
        return error('Link too short')
    
    regexmatch = re.match(r"^[a-zA-Z0-9]+$", link)
    if not regexmatch:
        return error('Invalid link')
    
    # Verify link is not taken
    if db.get_link(link) != False:
        return error('Link already taken')
    
    # Add link
    db.add_link(link,url,domain)
    return redirect('/dash')

@app.route('/delete/<path:path>')
def delete(path):
    if 'linkr' not in request.cookies:
        return redirect('/')

    token = request.cookies['linkr']
    domain = account.get_user(token)
    if domain == False:
        resp = make_response(redirect('/'))
        resp.set_cookie('linkr', '', expires=0)
        return resp

    db.delete_link(path,domain)
    return redirect('/dash')
    

@app.route('/logout')
def logout():
    if 'linkr' not in request.cookies:
        return redirect('/')

    token = request.cookies['linkr']
    account.remove_user(token)
    
    # Remove cookie
    resp = make_response(redirect('/'))
    resp.set_cookie('linkr', '', expires=0)
    return resp

@app.route('/login', methods=['POST'])
def login():
    auth = varo_auth.flask_login(request)
    if auth == False:
        return redirect('/')
    resp = make_response(redirect('/dash'))
    # Gen cookie
    auth_cookie = account.generate_token()
    account.add_user(auth, auth_cookie)
    resp.set_cookie('linkr', auth_cookie)
    return resp


@app.route('/<path:path>')
def catch_all(path):
    link = db.get_link(path)
    if link != False:
        return redirect(link)
    return redirect('/404') # 404 catch all

# 404 catch all
@app.errorhandler(404)
@app.route('/404')
def not_found(e=None):
    return render_template('404.html'), 404

if __name__ == '__main__':
    db.check_tables()
    app.run(debug=False, port=5000, host='0.0.0.0')