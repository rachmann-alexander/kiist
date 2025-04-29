import csv
import re
from collections import defaultdict
from pyvis.network import Network

# === Farbcodierung je nach Gewicht ===
def gewicht_to_color(gewicht, min_w, max_w):
    # Normalisierung
    norm = (gewicht - min_w) / max(1, max_w - min_w)
    # Farbspektrum: Grün (viel) bis Rot (wenig)
    r = int(255 * norm)
    g = int(255 * (1 - norm))
    b = 0
    return f"rgb({r},{g},{b})"

# === Daten einlesen ===
def lese_csv(pfad):
    with open(pfad, newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        return [row for row in reader]
    print(f"{len(zeilen)} Zeilen aus Datei geladen.")

# === Pfade extrahieren ===
def baue_baumstrukturen(zeilen):
    root = "Künstliche Intelligenz ist"
    kanten = defaultdict(int)

    for row in zeilen:
        if len(row) < 2:
            continue
        text = row[1]
        words = re.findall(r'\b\w+\b', text)

        if words[:3] != ["Künstliche", "Intelligenz", "ist"]:
            continue

        path = [root] + words[3:]
        for i in range(len(path) - 1):
            kanten[(path[i], path[i + 1])] += 1

        print(f"Verarbeite Text: {text[:60]}...")

    return kanten

# === Netzwerk aufbauen & visualisieren ===
def visualisiere_baum(kanten, output_html="baum.html"):
    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", notebook=True, select_menu=True)

    net.barnes_hut()

    gewichte = list(kanten.values())
    if not gewichte:
        print("Keine gültigen Kanten gefunden. Überprüfe die Eingabedatei.")
        return
    min_w, max_w = min(gewichte), max(gewichte)

    knoten_set = set()
    for (src, tgt), weight in kanten.items():
        for k in (src, tgt):
            if k not in knoten_set:
                if k == "Künstliche Intelligenz ist":
                    net.add_node(k, label=k, title=k, font={"size": 66, "bold": True}, color="yellow")
                else:
                    net.add_node(k, label=k, title=k, font={"size": 22})
                knoten_set.add(k)

        color = gewicht_to_color(weight, min_w, max_w)
        # Berechne relatives Gewicht
        ausgehende_kanten = sum(w for (n, _), w in kanten.items() if n == src)
        relatives_gewicht = weight / ausgehende_kanten if ausgehende_kanten > 0 else 0
        relatives_gewicht = round(relatives_gewicht * 100, 2)
        net.add_edge(src, tgt, value=weight, title=f"{weight}x", label=f"{relatives_gewicht}%", color=color)

    
    net.show_buttons(filter_=['physics'])
    net.write_html(output_html)
    print(f"Interaktive Baumstruktur gespeichert unter: {output_html}")

# === Main ===
if __name__ == "__main__":
    dateipfad = "./responses.csv"  # <== Hier Datei-Pfad anpassen
    daten = lese_csv(dateipfad)
    kanten = baue_baumstrukturen(daten)
    visualisiere_baum(kanten)