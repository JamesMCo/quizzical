from flask import Flask, render_template, request, session
import json
import uuid

app = Flask(__name__, static_folder="static")

@app.route("/")
def main():
    if "team_id" in session:
        if session["team_id"] == settings["admin_id"]:
            # Administrator, so show admin page
            return render_template("admin.html", **settings)
        elif session["team_id"] in [t["leader"] for t in teams]:
            # Team leader, so show entry page
            return render_template("index.html", **settings)
        elif session["team_id"] in [t["member"] for t in teams]:
            # Team member, so show submitted page
            return render_template("index.html", **settings)
    # Not yet part of a team or an admin, so show basic index page
    return render_template("index.html", **settings)

@app.route("/api/join", methods=["POST"])
def join():
    if "team_id" not in request.form:
        return "Team not specified", 400
    elif request.form["team_id"] == settings["admin_id"] or request.form["team_id"] in [t["leader"] for t in teams] or [t["member"] for t in teams]:
        session["team_id"] = request.form["team_id"]
        return "Team successfully joined", 200
    else:
        return "Team not found", 404

@app.route("/api/leave")
def leave():
    if "team_id" in session:
        session.pop("team_id")
        return "Team successfully left", 200
    else:
        return "Already not in a team", 400

if __name__ == "__main__":
    with open("quiz_settings.json") as f:
        settings = json.loads(f.read())
    if "" in settings.values():
        print("All settings require values: please check quiz_settings.json")
        exit(1)

    print(settings["secret_key"])
    app.secret_key = settings["secret_key"]
    teams = {}

    app.run(host="0.0.0.0", port=80)