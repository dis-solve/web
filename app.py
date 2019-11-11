"""
kissit website.
"""

import flask
import yaml
from hashlib import sha1
from datetime import date
import traceback
import os

app = flask.Flask(__name__)
app.jinja_env.globals['current_year'] = date.today().year + 1
app.secret_key = os.urandom(24)

app.config['aprilsfool'] = False
app.config['companies'] = ['cie/sm/'+path for path in os.listdir('static/cie/sm')]
for name in ('global', 'projects'):
    with open(f'content/{name}.yaml') as f:
        app.config[name] = yaml.load(f, Loader=yaml.FullLoader)

def shorthash(text):
    return sha1(text.encode("utf-8")).hexdigest()[:3]

@app.errorhandler(Exception)
def handle_error(e):
    http_status = getattr(e, 'code', 500)
    description = getattr(e, 'description', None)
    if http_status == 500:
        print(''.join(line for line in traceback.format_exception(
            type(e), e, e.__traceback__, chain=False)))
    return flask.render_template('error.html',
        description=description,
        http_status=http_status,
        error=e.__class__.__name__,
        cause=str(e)), http_status

@app.route('/')
def entrypoint():
    return flask.render_template('entrypoint.html')

@app.route('/we-created')
def projects():
    return flask.render_template('projects.html',
        companies=app.config['companies'],
        projects=app.config['projects'],
        hashes={name: shorthash(name) for name in app.config['projects'].keys()})  # short hash for urls

@app.route('/we-created/<hash>')
def project(hash):
    try:
        name, project = [(name, project) for name, project
            in app.config['projects'].items()
            if shorthash(name) == hash].pop()
        return flask.render_template('project.html',
            name=name,
            project=project)
    except IndexError:
        flask.abort(404,
            f"We looked everywhere, we could not find track of a project with hash code '{hash}'."
            f"\nYou are more than welcome to "
            f'<a href="{flask.url_for("projects")}">look at a selection of our work</a>.')

@app.route('/contact-us')
def contact():
    email = app.config['global']['contact']['email']
    return flask.redirect(f'mailto:{email}')
    #return()

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config.get('DEBUG'),
        use_reloader=True)
