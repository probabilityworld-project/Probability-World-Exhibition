
from flask import Flask, render_template, request, session, redirect, url_for
import random
import os

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "dev-only-change-this-before-deploying"
)


@app.route("/")
def index():

    dashboard_totals = {
        "spinner": session.get("spinner_spins", 0),
        "dice": session.get("dice_total", 0),
        "coin": session.get("coin_total", 0),
        "card": session.get("card_total", 0)
    }

    overall_total = sum(dashboard_totals.values())

    return render_template(
        "index.html",
        dashboard_totals=dashboard_totals,
        overall_total=overall_total
    )


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

    title = experiments[name]


    # =================================
    # EXPERIMENT RESET
    # =================================

    if request.method == "POST" and request.form.get("action") == "reset":

        reset_keys = {
            "spinner": ["spinner_spins", "spinner_counts"],
            "dice": ["dice_total", "dice_counts"],
            "coin": ["coin_total", "coin_counts"],
            "card": ["card_deck", "card_total", "card_counts"]
        }

        for key in reset_keys[name]:
            session.pop(key, None)

        return redirect(url_for("experiment", name=name))

    # =================================
    # SPINNER LAB
    # =================================

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

            rotation = 5 * 360 + (
                360 - (result_index * 90 + 45)
            )

            session["spinner_spins"] += 1

            counts = session["spinner_counts"]
            counts[result] += 1

            session["spinner_counts"] = counts

        return render_template(
            "experiment.html",
            title=title,
            graph_labels=colors,
graph_values=[session["spinner_counts"][color] for color in colors],
            theoretical_values=[25, 25, 25, 25],
            colors=colors,
            result=result,
            rotation=rotation,
            total=session["spinner_spins"],
            counts=session["spinner_counts"]
        )

    # =================================
    # DICE LAB
    # =================================

    elif name == "dice":

        if "dice_total" not in session:
            session["dice_total"] = 0
            session["dice_counts"] = {
                str(i): 0 for i in range(1, 7)
            }

        result = None

        if request.method == "POST":

            result = random.randint(1, 6)

            session["dice_total"] += 1

            counts = session["dice_counts"]
            counts[str(result)] += 1

            session["dice_counts"] = counts

        return render_template(
            "experiment.html",
            title=title,
            graph_labels=[str(i) for i in range(1, 7)],
graph_values=[session["dice_counts"][str(i)] for i in range(1, 7)],
           theoretical_values=[16.67, 16.67, 16.67, 16.67, 16.67, 16.67],
            result=result,
            total=session["dice_total"],
            counts=session["dice_counts"]
        )

    # =================================
    # COIN LAB
    # =================================

    elif name == "coin":

        if "coin_total" not in session:
            session["coin_total"] = 0
            session["coin_counts"] = {
                "HEADS": 0,
                "TAILS": 0
            }

        result = None

        if request.method == "POST":

            result = random.choice(["HEADS", "TAILS"])

            session["coin_total"] += 1

            counts = session["coin_counts"]
            counts[result] += 1

            session["coin_counts"] = counts

        return render_template(
            "experiment.html",
            title=title,
            graph_labels=["HEADS", "TAILS"],
graph_values=[session["coin_counts"][side] for side in ["HEADS", "TAILS"]],
            theoretical_values=[50, 50],
            result=result,
            total=session["coin_total"],
            counts=session["coin_counts"]
        )

    # =================================
    # CARD LAB
    # =================================

    elif name == "card":

        suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
        ranks = [
            "A", "2", "3", "4", "5", "6", "7",
            "8", "9", "10", "J", "Q", "K"
        ]

        if "card_deck" not in session:
            session["card_deck"] = []
            session["card_total"] = 0
            session["card_counts"] = {
                suit: 0 for suit in suits
            }

        card_result = None

        if request.method == "POST":

            deck = session["card_deck"]

            # Create and shuffle a fresh deck
            # when all 52 cards have been drawn.

            if not deck:
                deck = [
                    {"rank": rank, "suit": suit}
                    for suit in suits
                    for rank in ranks
                ]

                random.shuffle(deck)

            card_result = deck.pop()

            session["card_deck"] = deck
            session["card_total"] += 1

            counts = session["card_counts"]
            counts[card_result["suit"]] += 1

            session["card_counts"] = counts

        return render_template(
            "experiment.html",
            title=title,
            graph_labels=suits,
graph_values=[session["card_counts"][suit] for suit in suits],
            theoretical_values=[25, 25, 25, 25],
            card_result=card_result,
            total=session["card_total"],
            counts=session["card_counts"],
            remaining=len(session["card_deck"])
        )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
