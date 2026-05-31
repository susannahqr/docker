import time
import redis
from flask import Flask, render_template
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io, base64
import os   # <- new
from dotenv import load_dotenv   # <- new

load_dotenv()  # <- new 
cache = redis.Redis(host=os.getenv('REDIS_HOST'), port=6379,  password=os.getenv('REDIS_PASSWORD')) # <- changed
app = Flask(__name__)

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

@app.route('/')
def hello():
    count = get_hit_count()
    return render_template('hello.html', name= "BIPM", count = count)

@app.route("/titanic")
def titanic():
    df = pd.read_csv("titanic.csv")
    table_html = df.head(5).to_html(classes="titanic-table", index=False)

    # Bar chart: survivors by sex
    survived = df[df["Survived"] == 1]["Sex"].value_counts()
    fig, ax = plt.subplots()
    survived.plot(kind="bar", ax=ax, color=["steelblue", "salmon"])
    ax.set_title("Titanic Survivors by Sex")
    ax.set_xlabel("Sex")
    ax.set_ylabel("Count")
    ax.set_xticklabels(survived.index, rotation=0)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    chart = base64.b64encode(buf.read()).decode("utf-8")
    plt.close()

    return render_template("titanic.html", table=table_html, chart=chart)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)