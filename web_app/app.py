from flask import Flask, render_template, jsonify
import os
import sys
import traceback


app = Flask(__name__)

# Make project root importable and initialize BarrierControl
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
try:
    from schrankensteuerung import create_barrier_control
    config_path = os.path.join(ROOT, 'config.yaml')
    try:
        bc = create_barrier_control(config_path)
        print(str(bc))
        print("Alles gut")
    except Exception:
        print("Fehler beim Erstellen von BarrierControl:")
        traceback.print_exc()
        bc = None
except Exception:
    print("Fehler beim Importieren von schrankensteuerung:")
    traceback.print_exc()
    bc = None

@app.route('/')
def index():
    return _render_index()


@app.route('/status', methods=['GET'])
def status():
    return jsonify({'barrier_status': _current_barrier_status()})


def _current_barrier_status():
    if bc and hasattr(bc, 'status'):
        return bc.status
    return 'down'


def _render_index(nachricht=None):
    return render_template(
        "index.html",
        nachricht=nachricht,
        barrier_status=_current_barrier_status()
    )

@app.route("/klick_barrier", methods=["POST"])
def button_barrier():
    print(str(bc))
    ergebnis_text = "Der Button Schranke wurde erfolgreich verarbeitet!"
    if bc:
        try:
            bc.move_barrier(None)
        except Exception as e:
            ergebnis_text = f"Fehler beim Auslösen der Schranke: {e}"
    else:
        ergebnis_text = "BarrierControl nicht initialisiert."
    return _render_index(nachricht=ergebnis_text)

@app.route("/klick_tor", methods=["POST"])
def button_tor():
    ergebnis_text = "Der Button Tor wurde erfolgreich verarbeitet!"
    if bc:
        try:
            bc.open_close_garage()
            ergebnis_text = "Garagentor: Aktion ausgelöst."
        except Exception as e:
            ergebnis_text = f"Fehler beim Garagentor: {e}"
    else:
        ergebnis_text = "BarrierControl nicht initialisiert."
    return _render_index(nachricht=ergebnis_text)

def start():
    # Startet den Server im lokalen Netzwerk auf Port 5000
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

if __name__ == '__main__':
    start()