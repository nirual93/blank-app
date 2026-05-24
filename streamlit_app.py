import math

print("=== GRUNDWASSER-VOLUMEN RECHNER (DIN 38402-13) ===")

try:
    # 1. Daten vom Nutzer abfragen
    durchmesser_mm = float(input("Rohr-Durchmesser in mm (z.B. 100): "))
    tiefe_m = float(input("Gesamttiefe in m (z.B. 22.5): "))
    ruhewasser_m = float(input("Ruhewasserstand in m (z.B. 14.2): "))

    # 2. Mathematische Berechnung
    radius_m = (durchmesser_mm / 2) / 1000
    wassersaeule_m = tiefe_m - ruhewasser_m
    
    # Kurzer Check, ob die Eingaben Sinn machen
    if wassersaeule_m < 0:
        print("\nFehler: Der Ruhewasserstand kann nicht tiefer sein als die Gesamttiefe!")
    else:
        standwasser_volumen = math.pi * (radius_m ** 2) * wassersaeule_m * 1000
        abpump_volumen = 3 * standwasser_volumen

        # 3. Ergebnis übersichtlich ausgeben
        print("\n--- ERGEBNIS ---")
        print(f"Höhe der Wassersäule: {wassersaeule_m:.2f} m")
        print(f"Einfaches Rohrvolumen: {standwasser_volumen:.1f} Liter")
        print(f"-> Abzupumpendes Volumen (3-fach): {abpump_volumen:.1f} Liter")

except ValueError:
    print("\nFehler: Bitte geben Sie nur Zahlen ein (bei Kommazahlen einen Punkt nutzen, z.B. 14.2).")

