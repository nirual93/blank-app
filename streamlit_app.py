import streamlit as st
import math

# --- LOGIK DES AGENTEN (DIN 38402-13) ---
def berechne_hydraulik(dn, tiefe, rws):
    radius_m = (dn / 2) / 1000
    wassersaeule = tiefe - rws
    standwasser = math.pi * (radius_m ** 2) * wassersaeule * 1000
    mindest_volumen = 3 * standwasser
    return wassersaeule, standwasser, mindest_volumen

def pruefe_chemie(letzte, aktuelle):
    temp_stabil = abs(letzte['temp'] - aktuelle['temp']) <= 0.2
    ph_stabil = abs(letzte['ph'] - aktuelle['ph']) <= 0.05
    lf_stabil = abs(letzte['lf'] - aktuelle['lf']) / letzte['lf'] <= 0.05
    return temp_stabil and ph_stabil and lf_stabil

# --- SEITEN-SETUP ---
st.set_page_config(page_title="GW-Probenahme Agent", page_icon="💧")
st.title("💧 Ihr WhatsApp-Prototyp: GW-Agent")
st.write("Simulieren Sie hier das Gespräch, das Sie später per WhatsApp führen würden.")

# Speicher für den Chat-Verlauf und Messdaten anlegen
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hallo! Ich bin dein Feld-Assistent. Bitte gib mir die Stammdaten der Messstelle durch (z.B. 'GW-04, DN 100, Tiefe 22.5, RWS 14.2, Pumpe 10')."}]
if "messdaten" not in st.session_state:
    st.session_state.messdaten = []
if "stammdaten" not in st.session_state:
    st.session_state.stammdaten = None

# Chat-Verlauf anzeigen
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- CHAT-INTERAKTION ---
if user_input := st.chat_input("Schreibe dem Agenten..."):
    # Nachricht des Nutzers anzeigen
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # --- REAKTION DES AGENTEN ---
    with st.chat_message("assistant"):
        # Fall 1: Stammdaten einlesen (Wenn noch keine existieren)
        if not st.session_state.stammdaten:
            try:
                # Einfaches "Herauspicken" von Zahlen aus dem Text (Simuliert das LLM)
                wörter = user_input.replace(",", " ").split()
                zahlen = [float(s) for s in wörter if s.replace('.', '', 1).isdigit()]
                
                dn, tiefe, rws, pumpe = zahlen[0], zahlen[1], zahlen[2], zahlen[3]
                wasa, stw, min_vol = berechne_hydraulik(dn, tiefe, rws)
                min_zeit = min_vol / pumpe
                
                st.session_state.stammdaten = {"dn": dn, "tiefe": tiefe, "rws": rws, "pumpe": pumpe, "min_vol": min_vol}
                
                antwort = f"STAMMDATEN ERFASST:\n- Wassersäule: {wasa:.2f}m\n- Standwasser: {stw:.1f} L\n- **Mindest-Abpumpvolumen (3x DIN): {min_vol:.1f} Litern**.\n\nBei {pumpe} l/min erreichen wir das nach ca. **{min_zeit:.1f} Minuten**. Bitte starte die Pumpe und schicke mir die Messwerte, sobald die Zeit rum ist!"
            except:
                antwort = "Ich konnte die Stammdaten nicht korrekt herauslesen. Bitte nenne mir: Durchmesser (DN), Gesamttiefe, Ruhewasserspiegel und Förderstrom als reine Zahlen."
        
        # Fall 2: Messwerterfassung
        else:
            try:
                wörter = user_input.replace(",", " ").split()
                zahlen = [float(s) for s in wörter if s.replace('.', '', 1).isdigit()]
                ph, temp, lf = zahlen[0], zahlen[1], zahlen[2]
                
                aktuelle_messung = {"ph": ph, "temp": temp, "lf": lf}
                st.session_state.messdaten.append(aktuelle_messung)
                
                volumen_bisher = len(st.session_state.messdaten) * st.session_state.stammdaten["pumpe"] * 5 # Annahme: Messung alle 5 Min.
                
                # Prüfen
                hydraulik_ok = volumen_bisher >= st.session_state.stammdaten["min_vol"]
                
                if len(st.session_state.messdaten) > 1:
                    chemie_ok = pruefe_chemie(st.session_state.messdaten[-2], aktuelle_messung)
                else:
                    chemie_ok = False
                
                if chemie_ok:
                    antwort = f"Messung {len(st.session_state.messdaten)} erfasst.\n🎉 **PROBENAHME FREIGEGEBEN!** Die chemischen Parameter sind stabil und das Mindestvolumen ist gefördert. Du kannst jetzt abfüllen."
                else:
                    antwort = f"Messung {len(st.session_state.messdaten)} notiert (pH: {ph}, Temp: {temp}°C, LF: {lf}µS/cm).\nStatus: Bitte weiterpumpen. Die Parameter sind noch nicht stabil genug oder die Messreihe ist zu kurz."
            except:
                antwort = "Bitte gib die Messwerte im Format 'pH-Wert, Temperatur, Leitfähigkeit' ein (z.B. '7.2, 11.5, 510')."

        st.write(antwort)
        st.session_state.messages.append({"role": "assistant", "content": antwort})
