from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    name = "marcus"
    hobby = ["running", "accordeon"]
    return render_template("index.html", name=name, hobby_liste=hobby)

@app.route("/klick_barrier", methods=["POST"])
def button_barrier():
    ergebnis_text = "Der Button Garage wurde erfolgreich verarbeitet!"
    return render_template("index.html", nachricht=ergebnis_text)

@app.route("/klick_tor", methods=["POST"])
def button_tor():
    ergebnis_text = "Der Button Tor wurde erfolgreich verarbeitet!"
    return render_template("index.html", nachricht=ergebnis_text)

def start():
    # Startet den Server im lokalen Netzwerk auf Port 5000
    app.run(host='192.168.178.43', port=5000, debug=True)

if __name__ == '__main__':
    start()