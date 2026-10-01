"""Calculate the number of vowels in a given string — Flask."""

from flask import Flask, render_template, request

app = Flask(__name__)
VOWELS = set("aeiou")


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        text = request.form.get("text", "")
        counts = {v: 0 for v in "aeiou"}
        for ch in text.lower():
            if ch in VOWELS:
                counts[ch] += 1
        result = {
            "text": text,
            "total": sum(counts.values()),
            "counts": counts,
        }
    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)
