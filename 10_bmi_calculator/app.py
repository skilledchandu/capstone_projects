"""BMI Calculator — Flask."""

from flask import Flask, render_template, request

app = Flask(__name__)


def category(bmi: float) -> str:
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Healthy weight"
    if bmi < 30:
        return "Overweight"
    return "Obese range"


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        try:
            weight = float(request.form.get("weight", ""))
            height_cm = float(request.form.get("height", ""))
        except ValueError:
            result = {"error": "Enter numbers for weight and height."}
        else:
            if weight <= 0 or height_cm <= 0:
                result = {"error": "Weight and height must be greater than 0."}
            else:
                height_m = height_cm / 100
                bmi = weight / (height_m ** 2)
                result = {
                    "weight": weight,
                    "height": height_cm,
                    "bmi": round(bmi, 1),
                    "category": category(bmi),
                }
    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)
