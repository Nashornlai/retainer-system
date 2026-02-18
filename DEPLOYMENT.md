# 🚀 Deployment Guide: Retainer System

Dieses Dokument erklärt, wie du deine Streamlit-App online bringst, damit dein Team darauf zugreifen kann.

## ⚠️ Wichtig: "Normales Webhosting" (All-Inkl, Strato, IONOS Shared)
**Kurz:** Das reicht meistens nicht.
**Warum?** "All-Inkl" und Co. sind für PHP-Webseiten (Wordpress etc.) gemacht. Streamlit ist eine **Python-App**, die im Hintergrund dauerhaft laufen muss ("Server-Prozess"). Das erlauben normale Webhosting-Pakete oft nicht oder nur sehr umständlich (via CGI/Passenger, was oft langsam oder fehleranfällig ist).

**Empfehlung:** Nutze einen spezialisierten Python-Hoster oder einen eigenen kleinen Server (VPS).

---

## ✅ Option A: Streamlit Community Cloud (Der einfachste Weg)
Perfekt für den Start. Kostenlos.

1.  Lade deinen Code auf **GitHub** hoch (kostenloses Konto).
2.  Gehe auf [share.streamlit.io](https://share.streamlit.io).
3.  Verknüpfe dein GitHub-Konto und wähle dein Repository aus.
4.  Klicke "Deploy".
5.  **Fertig!** Deine App ist unter `https://dein-name-app.streamlit.app` erreichbar.

*   **Vorteil:** Extrem einfach, in 5 Minuten fertig.
*   **Nachteil:** Server stehen in den USA (Datenschutz?), "schläft" bei Inaktivität ein.

---

## 🏢 Option B: Hetzner Cloud / VPS (Die Profi-Lösung)
Eigener Server, totale Kontrolle, Server in Deutschland.

1.  Miete einen "Cloud Server" bei Hetzner (z.B. CX22 für ~5€/Monat).
2.  Installiere "Docker" auf dem Server (ein Befehl).
3.  Lade deine Dateien (inkl. `Dockerfile`) hoch.
4.  Starte den Container:
    ```bash
    docker build -t retainer-app .
    docker run -d -p 80:8501 --restart always retainer-app
    ```

*   **Vorteil:** Schnell, DSGVO-konform (DE Standort), professionell.
*   **Nachteil:** Erfordert etwas Linux-Kenntnisse (oder meine Hilfe beim Einrichten).

---

## ☁️ Option C: PaaS (Railway / Render / Piko)
Ein Mittelweg. Einfacher als Hetzner, mächtiger als Streamlit Cloud.

1.  Konto bei z.B. **Railway.app** erstellen.
2.  GitHub verknüpfen.
3.  Railway erkennt das `Dockerfile` und baut die App automatisch.
4.  Kosten: Wenige Euro pro Monat (nutzungsabhängig).

---

## 📂 Vorbereitete Dateien
Ich habe für dich bereits erstellt:
*   `requirements.txt`: Liste aller benötigten Python-Bibliotheken.
*   `Dockerfile`: "Bauplan" für den Server (für Option B und C).
