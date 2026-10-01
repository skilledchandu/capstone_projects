"""Water Intake Tracker — Introduction to Flask."""

from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        name = request.form.get("name", "").strip() or "Friend"
        try:
            goal = int(request.form.get("goal", "0"))
            glasses = int(request.form.get("glasses", "0"))
        except ValueError:
            result = {"error": "Enter whole numbers for the goal and glasses."}
            return render_template("index.html", result=result)
        if goal <= 0 or glasses < 0:
            result = {"error": "Goal must be at least 1, and glasses cannot be negative."}
        else:
            percent = min(100, round((glasses / goal) * 100))
            remaining = max(0, goal - glasses)
            result = {
                "name": name,
                "goal": goal,
                "glasses": glasses,
                "percent": percent,
                "remaining": remaining,
                "done": glasses >= goal,
            }
    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)
