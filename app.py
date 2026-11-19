
from flask import Flask, render_template, request, session
import random
import os

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "dev-only-change-this-before-deploying"
)
app.secret_key = "probability_world_3_secret_key"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/experiment/<name>", methods=["GET", "POST"])
def experiment(name):

    experiments = {
        "spinner": "🎡 Spinner Lab",
        "dice": "🎲 Dice Lab",
        "coin": "🪙 Coin Lab",
        "card": "🃏 Card Lab"
    }

    if name not in experiments:
        return "Experiment not found", 404

    
    if name == "spinner":    

        colors = ["RED", "BLUE", "GREEN", "YELLOW"]

        if "spinner_spins" not in session:
            session["spinner_spins"] = 0
            session["spinner_counts"] = {
                color: 0 for color in colors
            }

        

        result = None
        rotation = 0

        if request.method == "POST":
            result_index = random.randrange(len(colors))
            result = colors[result_index]

            rotation = 5 * 360 + (360 - (result_index * 90 + 45))

            session["spinner_spins"] += 1

            counts = session["spinner_counts"]
            counts[result] += 1

            session["spinner_counts"] = counts
            session.modified = True

        total = session["spinner_spins"]
        counts = session["spinner_counts"]

        return render_template(
            "experiment.html",
            title=experiments[name],
            colors=colors,
            result=result,
            rotation=rotation,
            total=total,
            counts=counts
        )

    return render_template(
        "experiment.html",
        title=experiments[name]
    )


if __name__ == "__main__":
    app.run(debug=True)
