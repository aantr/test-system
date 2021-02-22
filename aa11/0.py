import json
import random
from flask import Flask, request, render_template
from flask import Flask

app = Flask(__name__)
app.secret_key = "secret_key"


@app.route('/member')
def index():
    with open('templates/member.json', encoding='utf-8') as f:
        data = json.load(f)
    return render_template('index.html', member=random.choice(data))


if __name__ == "__main__":
    app.run(port=8080, host='127.0.0.1')
