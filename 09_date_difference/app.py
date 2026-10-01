"""Difference between two dates — Flask."""

from datetime import datetime

from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        start_raw = request.form.get("start", "")
        end_raw = request.form.get("end", "")
        try:
            start = datetime.strptime(start_raw, "%Y-%m-%d").date()
            end = datetime.strptime(end_raw, "%Y-%m-%d").date()
        except ValueError:
            result = {"error": "Use valid dates."}
        else:
            delta = abs((end - start).days)
            result = {
                "start": start.isoformat(),
                "end": end.isoformat(),
                "days": delta,
                "weeks": delta // 7,
                "extra_days": delta % 7,
            }
    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)
