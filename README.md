# Quizzical :memo:

## About :information_source:

Quizzical is an answer submission system for quizzes. It was inspired by the website used for the Insomnia "[World Famous Pub Quiz](https://www.worldfamouspubquiz.com/)" remote events during 2020, but with a focus on allowing other members in a team to be able to see the answers that were submitted.

## Setup :hammer:

1. Ensure that [Python 3](https://python.org/downloads) is installed <sup id="a1">[1](#f1)</sup>, and that you can [run pip](https://packaging.python.org/tutorials/installing-packages/#ensure-you-can-run-pip-from-the-command-line).
2. Download or clone the repository to the computer or server that will be running Quizzical.
3. Navigate to the downloaded folder in a command prompt or terminal, and install the dependencies with either `python -m pip install -r requirements.txt` or `pip install -r requirements.txt`.
4. Fill out the desired settings in the [quiz_settings.json](quiz_settings.json) file (explained below).
5. Start the server by running the file [app.py](app.py).

<a name="f1">1</a>: Quizzical was developed using Python 3.9, but may still work on earlier versions. [↩](#a1)

## Settings :wrench:

All settings for Quizzical are specified in the [quiz_settings.json](quiz_settings.json) file. Where applicable, optional settings can be left blank by using the value `null`.

Setting          | Description                                                                                                                                             | Optional | Default Value
-----------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|----------|---------------
`quiz_name`      | The name of the quiz being hosted. Shown at the top of all users' pages.                                                                                | False    | None
`admin_id`       | The team id used to log into the admin page. May be anything, but usually the first 8 characters from a [UUID4 string](https://www.uuidgenerator.net/). | False    | None
`secret_key`     | A secret key used by Flask to sign the session cookies. Can be generated in a terminal using `python -c "import os; print(os.urandom(24).hex())"`.      | False    | None
`heartbeat_freq` | How often the clients will update their status, in milliseconds. Smaller values update pages more often, but use more bandwidth.                        | False    | 5000
`https_enabled`  | Whether or not to try to use HTTPS. Will still default to HTTP if either `ssl_fullchain` or `ssl_privkey` are not provided.                             | False    | True
`ssl_fullchain`  | The full chain component of an SSL certificate. Required if running with HTTPS enabled.                                                                 | True     | null
`ssl_privkey`    | The private key component of an SSL certificate. Required if running with HTTPS enabled.                                                                | True     | null

## Usage :computer:

There are three types of user: team members, team leaders, and administrators.

### Team members

Team members are users in a team, and are able to see the current state of the quiz alongside the answers that have been submitted by their team in the current round. Team members are not able to submit answers.

### Team leaders

Team leaders can see everything a team member can see, but are able to enter and submit answers during the answering state. It is recommended to only have one team leader per team.

### Administrators

Administrators control the quiz as a whole.

- During the pre-round state, they are able to add new teams, and can start a round with a specific number of questions.
- During the answering state, they are able to see which teams have submitted their answers, and can stop the round.
- During the post-round state, they are able to see the answers that were submitted by each team, download a copy of all answers submitted in this round, and complete the round (returning to the pre-round state).