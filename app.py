from flask import abort, escape, Flask, render_template, request, session
from functools import wraps
import json
import sys
import uuid

app = Flask(__name__, static_folder="static")


# Decorators

def requires_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "team_id" not in session or session["team_id"] != settings["admin_id"]:
            abort(404)
        return f(*args, **kwargs)
    return decorated_function

def requires_team_leader(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "team_id" not in session:
            abort(404)
        elif session["team_id"] not in [t["leader"] for t in teams]:
            abort(404)
        return f(*args, **kwargs)
    return decorated_function

def requires_team_member(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "team_id" not in session:
            abort(404)
        elif session["team_id"] not in [t["member"] for t in teams]:
            abort(404)
        return f(*args, **kwargs)
    return decorated_function

def requires_team_leader_or_member(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "team_id" not in session:
            abort(404)
        elif session["team_id"] not in [t["leader"] for t in teams]:
            abort(404)
        elif session["team_id"] not in [t["member"] for t in teams]:
            abort(404)
        return f(*args, **kwargs)
    return decorated_function

def requires_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "team_id" not in session:
            abort(404)
        elif session["team_id"] != settings["admin_id"] and session["team_id"] not in [t["leader"] for t in teams] and session["team_id"] not in [t["member"] for t in teams]:
            abort(404)
        return f(*args, **kwargs)
    return decorated_function

def requires_post(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == "GET":
            abort(405)
        return f(*args, **kwargs)
    return decorated_function

# Routes

@app.route("/")
def main():
    if "team_id" in session:
        if session["team_id"] == settings["admin_id"]:
            # Administrator, so show admin page
            return render_template("admin.html", **settings)
        elif session["team_id"] in [t["leader"] for t in teams]:
            # Team leader, so show entry page
            team_data = [t for t in teams if t["leader"] == session["team_id"]][0]
            return render_template("leader.html", **settings, team_data=team_data)
        elif session["team_id"] in [t["member"] for t in teams]:
            # Team member, so show submitted page
            team_data = [t for t in teams if t["member"] == session["team_id"]][0]
            return render_template("member.html", **settings, team_data=team_data)
    # Not yet part of a team or an admin, so show basic index page
    return render_template("index.html", **settings)

@app.route("/api/join", methods=["POST"])
def join():
    if "team_id" not in request.form:
        return "Team not specified", 400

    requested_id = request.form["team_id"].lower()
    if requested_id == settings["admin_id"] or requested_id in [t["leader"] for t in teams] or requested_id in [t["member"] for t in teams]:
        session["team_id"] = requested_id
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

@app.route("/api/round/start", methods=["GET", "POST"])
@requires_admin
@requires_post
def round_start():
    if quiz["state"] != "preround":
        return "Quiz not expecting to start a round", 403
    elif "question_count" not in request.form or request.form["question_count"] == "":
        return "Question count not specified", 400 
    else:
        try:
            question_count = int(request.form["question_count"])
        except:
            return "Question count not integer", 400

        quiz["question_count"] = question_count
        quiz["state"] = "answering"
        for i in range(len(teams)):
            teams[i]["submitted"] = False
            teams[i]["answers"] = [""] * question_count
        return f"Round started with {question_count} question{'s' if question_count != 1 else ''}", 200

@app.route("/api/round/stop", methods=["GET", "POST"])
@requires_admin
@requires_post
def round_stop():
    if quiz["state"] != "answering":
        return "Quiz not expecting to stop a round", 403
    else:
        quiz["state"] = "postround"
        return "Round stopped", 200

@app.route("/api/round/complete", methods=["GET", "POST"])
@requires_admin
@requires_post
def round_complete():
    if quiz["state"] != "postround":
        return "Quiz not expecting to complete a round", 403
    else:
        quiz["state"] = "preround"
        return "Round complete, waiting to start a new round", 200


@app.route("/api/status")
@requires_login
def status():
    if session["team_id"] == settings["admin_id"]:
        if quiz["state"] == "preround":
            return {"state": quiz["state"],
                    "teams": [{"name": t["name"], "leader": t["leader"], "member": t["member"]} for t in teams]}, 200
        elif quiz["state"] == "answering":
            return {"state": quiz["state"],
                    "question_count": quiz["question_count"],
                    "teams": [{"name": t["name"], "leader": t["leader"], "member": t["member"]} for t in teams],
                    "submitted": [t["name"] for t in teams if t["submitted"]]}, 200
        elif quiz["state"] == "postround":
            return {"state": quiz["state"],
                "question_count": quiz["question_count"],
                "teams": [{"name": t["name"], "leader": t["leader"], "member": t["member"]} for t in teams],
                "submissions": [{"name": t["name"], "answers": t["answers"]} for t in teams if t["submitted"]]}, 200
        else:
            return {"state": "invalid",
                    "teams": [{"name": t["name"], "leader": t["leader"], "member": t["member"]} for t in teams]}, 500
    else:
        if quiz["state"] == "preround":
            return {"state": "preround"}, 200
        elif quiz["state"] == "answering":
            team_data = [t for t in teams if t["leader"] == session["team_id"] or t["member"] == session["team_id"]][0]
            if team_data["submitted"]:
                return {"state": "answering",
                        "question_count": quiz["question_count"],
                        "submitted": team_data["submitted"],
                        "answers": team_data["answers"]}, 200
            else:
                return {"state": "answering",
                        "question_count": quiz["question_count"],
                        "submitted": team_data["submitted"]}, 200
        elif quiz["state"] == "postround":
            team_data = [t for t in teams if t["leader"] == session["team_id"] or t["member"] == session["team_id"]][0]
            return {"state": "postround",
                    "question_count": quiz["question_count"],
                    "answers": team_data["answers"]}, 200
        else:
            return {"state": "invalid"}, 500

@app.route("/api/answers.txt")
@requires_admin
def answers():
    if quiz["state"] != "postround":
        return "Quiz not expecting to return an answers file", 403
    else:
        return "\n\n".join(
            t['name'] + "\n" +
            "\n".join(f"{i+1}) {a}" for i, a in enumerate(t['answers']))
            for t in teams if t["submitted"]
        ), 200


@app.route("/api/create", methods=["GET", "POST"])
@requires_admin
@requires_post
def create():
    if "team_name" not in request.form or request.form["team_name"] == "":
        return "Team name not specified", 400
    else:
        existing_ids = [t["leader"] for t in teams] + [t["member"] for t in teams]

        leader_id = str(uuid.uuid4())[:8]
        while leader_id in existing_ids:
            leader_id = str(uuid.uuid4())[:8]

        member_id = str(uuid.uuid4())[:8]
        while member_id in existing_ids:
            member_id = str(uuid.uuid4())[:8]

        teams.append({"name": escape(request.form["team_name"]),
                      "leader": leader_id,
                      "member": member_id,
                      "submitted": False,
                      "answers": []})
        return {"leader": leader_id, "member": member_id}, 200

@app.route("/api/exportstate")
@requires_admin
def exportstate():
    try:
        with open("state_data.json", "w") as f:
            state = json.dumps([quiz, teams])
            f.write(state)
        return "State exported successfully", 200
    except Exception as e:
        return "State failed to export:\n" + str(e), 500


@app.route("/api/submit", methods=["POST"])
@requires_team_leader
def submit():
    if "answers" not in request.form:
        return "Answers not specified", 400

    t = [i for i, t in enumerate(teams) if t["leader"] == session["team_id"]][0]
    teams[t]["submitted"] = True
    teams[t]["answers"] = [escape(a) for a in json.loads(request.form["answers"])]
    return "Answers submitted successfully", 200


if __name__ == "__main__":
    with open("quiz_settings.json") as f:
        settings = json.loads(f.read())
    if "" in settings.values():
        print("All settings require values: please check quiz_settings.json")
        exit(1)

    if len(sys.argv) > 1:
        print("Using predefined state from " + sys.argv[1])
        with open(sys.argv[1]) as f:
            quiz, teams = json.loads(f.read())
    else:
        quiz = {"state": "preround", "question_count": 0}
        teams = []

    app.secret_key = settings["secret_key"]
    app.run(host="0.0.0.0", port=80)