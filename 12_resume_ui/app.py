"""Create Resume Part 1 — Flask UI for a resume template."""

from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    resume = None
    if request.method == "POST":
        skills = [s.strip() for s in request.form.get("skills", "").split(",") if s.strip()]
        resume = {
            "name": request.form.get("name", "").strip() or "Your Name",
            "title": request.form.get("title", "").strip() or "Student",
            "email": request.form.get("email", "").strip(),
            "phone": request.form.get("phone", "").strip(),
            "summary": request.form.get("summary", "").strip(),
            "education": request.form.get("education", "").strip(),
            "project": request.form.get("project", "").strip(),
            "skills": skills,
        }
    return render_template("index.html", resume=resume)


if __name__ == "__main__":
    app.run(debug=True)
