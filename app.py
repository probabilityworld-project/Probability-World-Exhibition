
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

    # Bulk simulation input (kept separate from the existing single-trial action).
    bulk_trials = 0
    bulk_message = None
    prediction_trials = 0
    prediction_result = None
    prediction_error = None

    prediction_options_map = {
        "spinner": ["RED", "BLUE", "GREEN", "YELLOW"],
        "dice": [str(i) for i in range(1, 7)],
        "coin": ["HEADS", "TAILS"],
        "card": ["Hearts", "Diamonds", "Clubs", "Spades"]
    }
    prediction_options = prediction_options_map[name]

    if request.method == "POST" and request.form.get("action") == "bulk":
        try:
            bulk_trials = int(request.form.get("trials", "0"))
        except (TypeError, ValueError):
            bulk_trials = 0

        if not 1 <= bulk_trials <= 10000:
            bulk_message = "Please enter a number of trials between 1 and 10,000."
            bulk_trials = 0

    if request.method == "POST" and request.form.get("action") == "prediction":
        try:
            prediction_trials = int(request.form.get("prediction_trials", "0"))
        except (TypeError, ValueError):
            prediction_trials = 0

        prediction_choice = request.form.get("prediction", "")
        if not 1 <= prediction_trials <= 10000:
            prediction_error = "Please enter a number of trials between 1 and 10,000."
            prediction_trials = 0
        elif prediction_choice not in prediction_options:
            prediction_error = "Please select a valid predicted outcome."
            prediction_trials = 0


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

        if request.method == "POST" and request.form.get("action") == "bulk" and bulk_trials:
            counts = session["spinner_counts"]
            for _ in range(bulk_trials):
                outcome = random.choice(colors)
                counts[outcome] += 1
            session["spinner_spins"] += bulk_trials
            session["spinner_counts"] = counts
            bulk_message = f"Completed {bulk_trials:,} spinner trials!"

        elif request.method == "POST" and request.form.get("action") == "prediction" and prediction_trials:
            counts = session["spinner_counts"]
            prediction_choice = request.form.get("prediction")
            run_counts = {color: 0 for color in colors}
            for _ in range(prediction_trials):
                outcome = random.choice(colors)
                counts[outcome] += 1
                run_counts[outcome] += 1
            session["spinner_spins"] += prediction_trials
            session["spinner_counts"] = counts
            highest = max(run_counts.values())
            winners = [key for key, value in run_counts.items() if value == highest]
            prediction_result = {
                "predicted": prediction_choice, "winners": winners,
                "predicted_count": run_counts[prediction_choice],
                "max_count": highest, "trials": prediction_trials,
                "correct": prediction_choice in winners
            }

        elif request.method == "POST" and request.form.get("action") not in ("reset", "bulk", "prediction"):
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
            bulk_message=bulk_message,
            prediction_options=prediction_options,
            prediction_result=prediction_result,
            prediction_error=prediction_error,
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

        if request.method == "POST" and request.form.get("action") == "bulk" and bulk_trials:
            counts = session["dice_counts"]
            for _ in range(bulk_trials):
                outcome = random.randint(1, 6)
                counts[str(outcome)] += 1
            session["dice_total"] += bulk_trials
            session["dice_counts"] = counts
            bulk_message = f"Completed {bulk_trials:,} dice rolls!"

        elif request.method == "POST" and request.form.get("action") == "prediction" and prediction_trials:
            counts = session["dice_counts"]
            prediction_choice = request.form.get("prediction")
            run_counts = {str(i): 0 for i in range(1, 7)}
            for _ in range(prediction_trials):
                outcome = str(random.randint(1, 6))
                counts[outcome] += 1
                run_counts[outcome] += 1
            session["dice_total"] += prediction_trials
            session["dice_counts"] = counts
            highest = max(run_counts.values())
            winners = [key for key, value in run_counts.items() if value == highest]
            prediction_result = {
                "predicted": prediction_choice, "winners": winners,
                "predicted_count": run_counts[prediction_choice],
                "max_count": highest, "trials": prediction_trials,
                "correct": prediction_choice in winners
            }

        elif request.method == "POST" and request.form.get("action") not in ("reset", "bulk", "prediction"):
            result = random.randint(1, 6)

            session["dice_total"] += 1

            counts = session["dice_counts"]
            counts[str(result)] += 1

            session["dice_counts"] = counts

        return render_template(
            "experiment.html",
            title=title,
            bulk_message=bulk_message,
            prediction_options=prediction_options,
            prediction_result=prediction_result,
            prediction_error=prediction_error,
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

        if request.method == "POST" and request.form.get("action") == "bulk" and bulk_trials:
            counts = session["coin_counts"]
            for _ in range(bulk_trials):
                outcome = random.choice(["HEADS", "TAILS"])
                counts[outcome] += 1
            session["coin_total"] += bulk_trials
            session["coin_counts"] = counts
            bulk_message = f"Completed {bulk_trials:,} coin tosses!"

        elif request.method == "POST" and request.form.get("action") == "prediction" and prediction_trials:
            counts = session["coin_counts"]
            prediction_choice = request.form.get("prediction")
            run_counts = {"HEADS": 0, "TAILS": 0}
            for _ in range(prediction_trials):
                outcome = random.choice(["HEADS", "TAILS"])
                counts[outcome] += 1
                run_counts[outcome] += 1
            session["coin_total"] += prediction_trials
            session["coin_counts"] = counts
            highest = max(run_counts.values())
            winners = [key for key, value in run_counts.items() if value == highest]
            prediction_result = {
                "predicted": prediction_choice, "winners": winners,
                "predicted_count": run_counts[prediction_choice],
                "max_count": highest, "trials": prediction_trials,
                "correct": prediction_choice in winners
            }

        elif request.method == "POST" and request.form.get("action") not in ("reset", "bulk", "prediction"):
            result = random.choice(["HEADS", "TAILS"])

            session["coin_total"] += 1

            counts = session["coin_counts"]
            counts[result] += 1

            session["coin_counts"] = counts

        return render_template(
            "experiment.html",
            title=title,
            bulk_message=bulk_message,
            prediction_options=prediction_options,
            prediction_result=prediction_result,
            prediction_error=prediction_error,
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

        if request.method == "POST" and request.form.get("action") == "bulk" and bulk_trials:
            deck = session["card_deck"]
            counts = session["card_counts"]

            for _ in range(bulk_trials):
                # A standard deck is reshuffled only after all 52 cards are drawn.
                if not deck:
                    deck = [
                        {"rank": rank, "suit": suit}
                        for suit in suits
                        for rank in ranks
                    ]
                    random.shuffle(deck)

                drawn_card = deck.pop()
                counts[drawn_card["suit"]] += 1

            session["card_deck"] = deck
            session["card_total"] += bulk_trials
            session["card_counts"] = counts
            bulk_message = f"Completed {bulk_trials:,} card draws!"

        elif request.method == "POST" and request.form.get("action") == "prediction" and prediction_trials:
            deck = session["card_deck"]
            counts = session["card_counts"]
            prediction_choice = request.form.get("prediction")
            run_counts = {suit: 0 for suit in suits}

            for _ in range(prediction_trials):
                if not deck:
                    deck = [
                        {"rank": rank, "suit": suit}
                        for suit in suits
                        for rank in ranks
                    ]
                    random.shuffle(deck)
                drawn_card = deck.pop()
                counts[drawn_card["suit"]] += 1
                run_counts[drawn_card["suit"]] += 1

            session["card_deck"] = deck
            session["card_total"] += prediction_trials
            session["card_counts"] = counts
            highest = max(run_counts.values())
            winners = [key for key, value in run_counts.items() if value == highest]
            prediction_result = {
                "predicted": prediction_choice, "winners": winners,
                "predicted_count": run_counts[prediction_choice],
                "max_count": highest, "trials": prediction_trials,
                "correct": prediction_choice in winners
            }

        elif request.method == "POST" and request.form.get("action") not in ("reset", "bulk", "prediction"):
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
            bulk_message=bulk_message,
            prediction_options=prediction_options,
            prediction_result=prediction_result,
            prediction_error=prediction_error,
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
