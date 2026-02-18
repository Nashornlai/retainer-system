import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys
from streamlit_option_menu import option_menu

# Configure Streamlit page (Must be first Streamlit command)
st.set_page_config(page_title="Leads Generator 3000", page_icon="⚡", layout="wide")

# Ensure 'tools' package is importable
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from tools.orchestrator import main as run_orchestrator
import tools.database as db

# Initialize Database
db.init_db()

# Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None

# --- CUSTOM CSS (Polished Light Theme) ---
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #F3F4F6; /* Light Grey */
        color: #1F2937; /* Dark Grey Text */
    }
    
    /* Text Color Override */
    h1, h2, h3, h4, p, li, span, div {
        color: #1F2937 !important;
    }
    
    /* Headings specific color */
    h1, h2, h3, h4 {
        color: #111827 !important; /* Almost Black */
        font-weight: 700;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E5E7EB;
    }
    
    /* Cards / Containers */
    .stCard {
        background-color: #FFFFFF;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid #E5E7EB;
        margin-bottom: 24px;
    }
    
    /* Metrics Box */
    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        padding: 16px;
        border-radius: 8px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    [data-testid="stMetricLabel"] p {
        color: #6B7280 !important; /* Muted Grey */
        font-size: 0.875rem;
        font-weight: 500;
    }
    [data-testid="stMetricValue"] div {
        color: #1E4D2B !important; /* Brand Green */
        font-weight: 700;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #1E4D2B;
        color: white !important;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
    }
    .stButton > button:hover {
        background-color: #14532d;
        color: white !important;
    }
    
    /* Dataframes */
    [data-testid="stDataFrame"] {
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- LOGIN ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        # Card Wrapper
        with st.container():
            st.markdown("""
            <div style="background-color: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); text-align: center; border: 1px solid #E5E7EB;">
                <h2 style="color: #1E4D2B; margin-bottom: 0.5rem;">⚡ Login</h2>
                <p style="color: #6B7280; margin-bottom: 1.5rem;">Retainer System Access</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            username = st.text_input("Benutzername", label_visibility="collapsed", placeholder="User")
            password = st.text_input("Passwort", type="password", label_visibility="collapsed", placeholder="Password")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Anmelden", use_container_width=True):
                user_check = db.verify_user(username, password)
                if user_check:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_check[0]
                    st.session_state.username = user_check[1]
                    st.rerun()
                else:
                    st.error("Zugangsdaten falsch.")
                
        # Persistence Proof
        try:
            conn = db.get_connection()
            count = conn.cursor().execute("SELECT COUNT(*) FROM leads").fetchone()[0]
            conn.close()
            st.caption(f"💾 System Status: {count} Leads gesichert.")
        except:
            pass
    st.stop()

# --- APP NAVIGATION ---

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=40)
    st.markdown(f"**User:** {st.session_state.username}")
    st.markdown("---")
    
    # Navigation with Icons
    # Use key to allow programmatic navigation
    page = option_menu(
        "Startmenü",
        ["Dashboard", "Neue Suche", "CRM & Leads", "Wiedervorlage", "Kategorien", "Papierkorb"],
        icons=['speedometer2', 'search', 'people-fill', 'calendar-check', 'tags-fill', 'trash'],
        menu_icon="cast", 
        default_index=0,
        key='main_navigation',
        styles={
            "container": {"padding": "0!important", "background-color": "#FFFFFF"},
            "icon": {"color": "#1E4D2B", "font-size": "20px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#F3F4F6", "color": "#1F2937"},
            "nav-link-selected": {"background-color": "#1E4D2B", "color": "white !important"},
        }
    )
    
    st.markdown("---")
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.rerun()

# --- PAGE LOGIC ---

if page == "Dashboard":
    st.title("Dashboard")
    stats = db.get_dashboard_stats(st.session_state.user_id)
    
    # Metrics Row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Gesamt Leads", stats["total_leads"])
    c2.metric("E-Mails Raus", stats["emails_sent"])
    c3.metric("Antworten", stats["responses"])
    c4.metric("Wins", stats["conversions"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts & Tables
    col_chart, col_kpi = st.columns([2, 1])
    
    with col_chart:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.markdown("### 📈 Aktivität")
        if stats["total_leads"] > 0:
            chart_data = pd.DataFrame({
                "Phasen": ["Newsletter", "Warenkorb", "Waitlist", "Antwort", "Kunde"],
                "Anzahl": [
                    stats["newsletter_signups"], 
                    stats.get("cart_abandoned", 0),
                    stats["emails_sent"], 
                    stats["responses"],
                    stats["conversions"]
                ]
            })
            
            fig = px.bar(chart_data, x="Phasen", y="Anzahl", text="Anzahl",
                         color="Phasen", 
                         color_discrete_sequence=["#D1FAE5", "#A7F3D0", "#6EE7B7", "#34D399", "#10B981"])
            
            # Explicitly set layout colors for light theme
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)", 
                showlegend=False,
                font={'color': '#1F2937'},
                xaxis=dict(showgrid=False, color='#4B5563'),
                yaxis=dict(showgrid=True, gridcolor='#E5E7EB', color='#4B5563')
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Noch keine Daten verfügbar.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_kpi:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.markdown("### 🔥 Top Keywords")
        if stats["top_keywords"]:
            html = "<table style='width:100%; border-collapse: collapse;'>"
            for kw, count in stats["top_keywords"]:
                html += f"<tr style='border-bottom: 1px solid #E5E7EB;'><td style='padding: 8px; color: #1F2937;'>{kw}</td><td style='padding: 8px; text-align: right; color: #1E4D2B; font-weight: bold;'>{count}</td></tr>"
            html += "</table>"
            st.markdown(html, unsafe_allow_html=True)
        else:
            st.write("Keine Daten.")
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "Neue Suche":
    st.title("Neue Leads")
    
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([3, 1, 1])
    keyword = c1.text_input("Suchbegriff", placeholder="z.B. Marketing Agentur")
    country = c2.text_input("Land", value="DE")
    max_results = c3.number_input("Anzahl", min_value=5, max_value=50, value=10)
    
    if st.button("Suche Starten 🚀"):
        progress_text = "Starte Suche..."
        bar = st.progress(0, text=progress_text)
        
        try:
            bar.progress(10, "Verbinde mit API...")
            df, stats = run_orchestrator(keywords=[keyword], country=country, max_results=max_results)
            bar.progress(80, "Speichere Daten...")
            
            if not df.empty:
                if "Ad URL" in df.columns:
                     df["Ad URL"] = df["Ad URL"].apply(lambda x: f"{x}&country={country}" if "?" in str(x) else f"{x}?country={country}")
                
                db.save_search_results(st.session_state.user_id, keyword, country, df)
                bar.progress(100, "Fertig!")
                st.success(f"✅ {len(df)} Leads gefunden!")
                st.dataframe(df, use_container_width=True)
            else:
                bar.progress(100, "Fertig!")
                st.warning("Keine Ergebnisse gefunden.")
        except Exception as e:
            st.error(f"Fehler: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "CRM & Leads":
    st.title("CRM & Leads")
    
    df_leads = db.get_user_leads(st.session_state.user_id)
    
    if not df_leads.empty:
        # Determine default category index from Session State
        default_cat_index = 0
        categories = ["Alle"]
        available_cats = []
        if "Category" in df_leads.columns:
            available_cats = [x for x in df_leads["Category"].unique() if x]
            categories += available_cats
            
        if "target_category" in st.session_state and st.session_state.target_category in categories:
            default_cat_index = categories.index(st.session_state.target_category)
            # Clear it so it doesn't stick forever
            del st.session_state.target_category
            
        # Filter Bar
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 1, 2])
        
        # Category Filter
        sel_cat = c1.selectbox("Kategorie Filter", categories, index=default_cat_index)
        
        # Keyword Filter
        keywords = ["Alle"]
        if "Keyword" in df_leads.columns:
            # Sort unique keywords alphabetically, ignoring nulls
            unique_kws = sorted([x for x in df_leads["Keyword"].unique() if x and str(x).strip() != ""])
            keywords += unique_kws
            
        sel_kw = c2.selectbox("Keyword Filter", keywords)
        
        filtered_df = df_leads.copy()
        
        # Apply Category Filter
        if sel_cat != "Alle":
            filtered_df = filtered_df[filtered_df["Category"] == sel_cat]
            
        # Apply Keyword Filter
        if sel_kw != "Alle":
            filtered_df = filtered_df[filtered_df["Keyword"] == sel_kw]
            
        st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        edited_df = st.data_editor(
            filtered_df,
            key="crm_editor",
            use_container_width=True,
            column_config={
                "ID": None,
                "Website": st.column_config.LinkColumn("Link", display_text="🔗"),
                "Ad URL": st.column_config.LinkColumn("Ad", display_text="👀"),
                "Ad Image": st.column_config.ImageColumn("Img"),
                "Newsletter": st.column_config.CheckboxColumn("✉️ NL", width="small"),
                "Warenkorb": st.column_config.CheckboxColumn("🛒 Cart", width="small"),
                "Angeschrieben": st.column_config.CheckboxColumn("📤 Sent", width="small"),
                "Antwort": st.column_config.CheckboxColumn("🗣️ Reply", width="small"),
                "Kunde": st.column_config.CheckboxColumn("🤝 Win", width="small"),
                "Notizen": st.column_config.TextColumn("Notizen"),
                "Trash": st.column_config.CheckboxColumn("🗑️", width="small"),
                "Date": st.column_config.DatetimeColumn("Datum", format="D.M.Y")
            },
            hide_index=True,
            disabled=["Company", "Email", "Keyword", "Date", "Website", "Ad URL", "Ad Image", "Category"]
        )
        st.markdown('</div>', unsafe_allow_html=True)
        if "crm_editor" in st.session_state:
            changes = st.session_state.crm_editor.get("edited_rows", {})
            
            # Application of standard changes (excluding Trash for now)
            for idx, updates in changes.items():
                if "Trash" in updates: 
                    continue # Handle Trash separately
                try:
                    real_row = filtered_df.loc[int(idx)]
                    lead_id = real_row["ID"]
                    for col, val in updates.items():
                         db.update_lead(lead_id, col, val)
                except:
                    pass

        # Batch Delete Action
        trash_indices = [idx for idx, updates in st.session_state.get("crm_editor", {}).get("edited_rows", {}).items() if updates.get("Trash")]
        
        if trash_indices:
            st.warning(f"⚠️ Du hast {len(trash_indices)} Leads zum Löschen markiert.")
            if st.button(f"🗑️ {len(trash_indices)} Leads endgültig löschen", type="primary"):
                for idx in trash_indices:
                    try:
                        real_row = filtered_df.loc[int(idx)]
                        db.update_lead(real_row["ID"], "Trash", True)
                    except:
                        pass
                
                # Reset Editor State
                del st.session_state.crm_editor
                st.success("Leads gelöscht!")
                st.rerun()
    else:
        st.info("Keine Leads vorhanden.")

elif page == "Wiedervorlage":
    st.title("📅 Wiedervorlage & Aufgaben")
    st.info("Hier landen Leads, die du zur Prüfung markiert hast (z.B. nach Newsletter-Anmeldung).")
    
    # 1. Fetch Follow-ups
    df_all = db.get_user_leads(st.session_state.user_id)
    
    if not df_all.empty and "Wiedervorlage" in df_all.columns:
        # Filter for pending tasks
        # Ensure Status column exists (migration script added it)
        # We filter where 'Wiedervorlage' is set AND Status is NOT 'completed'
        # Note: SQLite might return None for Status if default missing, but we set default 'pending'.
        
        # Safe filtering
        mask_pending = (df_all["Wiedervorlage"].notna()) & (df_all["Wiedervorlage"] != "") & (df_all["Status"] != "completed")
        df_tasks = df_all[mask_pending].copy()
        
        # Sort by Date (oldest first = overdue)
        if not df_tasks.empty:
            df_tasks = df_tasks.sort_values(by="Wiedervorlage")
            
            # Metrics
            today_str = datetime.now().strftime('%Y-%m-%d')
            count_total = len(df_tasks)
            count_overdue = len(df_tasks[df_tasks["Wiedervorlage"] < today_str])
            
            m1, m2 = st.columns(2)
            m1.metric("Offene Aufgaben", count_total)
            m2.metric("Überfällig", count_overdue, delta_color="inverse")
            
            st.markdown("### Aufgaben Liste")
            st.markdown('<div class="stCard">', unsafe_allow_html=True)
            
            # Prepare for Editor
            # We add a "Done" column for interaction (default False)
            df_tasks.insert(0, "Erledigt", False)
            
            edited_tasks = st.data_editor(
                df_tasks,
                key="tasks_editor",
                use_container_width=True,
                column_config={
                    "ID": None,
                    "Erledigt": st.column_config.CheckboxColumn("✅ Fertig?", help="Markiere als erledigt, um aus der Liste zu entfernen."),
                    "Wiedervorlage": st.column_config.DateColumn("Fällig am", format="D.M.Y"),
                    "Aufgabe": st.column_config.TextColumn("Aufgabe"),
                    "Company": "Firma",
                    "Website": st.column_config.LinkColumn("Link"),
                    "Notizen": st.column_config.TextColumn("Notizen"),
                    # Hide others
                    "Ad URL": None, "Ad Image": None, "Newsletter": None, "Warenkorb": None, 
                    "Angeschrieben": None, "Antwort": None, "Kunde": None, "Trash": None, "Grund": None, 
                    "Keyword": None, "Category": None, "Date": None, "Status": None
                },
                hide_index=True,
                disabled=["Company", "Website", "Aufgabe"] 
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Save Logic
            if "tasks_editor" in st.session_state:
                changes = st.session_state.tasks_editor.get("edited_rows", {})
                
                dirty = False
                for idx, updates in changes.items():
                    try:
                        # Use .loc for safety as per previous fix
                        real_row = df_tasks.loc[int(idx)]
                        lead_id = real_row["ID"]
                        
                        if "Erledigt" in updates and updates["Erledigt"] is True:
                            # Mark as completed
                            # We can use update_lead generic logic or sql directly?
                            # update_lead maps 'Kunde' etc. but 'follow_up_status' is raw?
                            # We need to use update_lead but add handling for 'follow_up_status' in db tool?
                            # OR just use a specialized call?
                            # Let's add 'Status' handling to update_lead in database.py? 
                            # Wait, usually I prefer raw SQL updates for non-standard columns if update_lead is strict.
                            # But I can abuse update_lead if I pass the column name directly?
                            # database.py uses `db_col = ... .get(column, column)`. So existing names works!
                            db.update_lead(lead_id, "follow_up_status", "completed")
                            dirty = True
                            
                        # Handle date changes
                        if "Wiedervorlage" in updates:
                             db.update_lead(lead_id, "follow_up_date", updates["Wiedervorlage"])
                             
                        # Handle Note changes
                        if "Notizen" in updates:
                             db.update_lead(lead_id, "Notizen", updates["Notizen"])
                             
                    except Exception as e:
                        print(e)
                
                if dirty:
                    st.success("Aufgaben aktualisiert!")
                    st.rerun()

        else:
            st.success("🎉 Keine offenen Aufgaben. Alles erledigt!")
    else:
        st.info("Noch keine Aufgaben vorhanden. Markiere Newsletter oder Warenkorb in der Lead-Liste als erledigt, um hier Aufgaben zu erzeugen.")

elif page == "Kategorien":
    st.title("Such-Historie & Details")
    
    conn = db.get_connection()
    searches_df = pd.read_sql_query("SELECT id, keyword, country, num_leads, category, timestamp FROM searches WHERE user_id = ? ORDER BY timestamp DESC", conn, params=(st.session_state.user_id,))
    conn.close()
    
    if not searches_df.empty:
        st.info("💡 Klicke auf eine Suche in der Tabelle, um Details & Leads zu sehen.")
        
        # 1. Master Table (Selectable)
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        
        # Configure columns for display
        display_df = searches_df.copy()
        display_df["timestamp"] = pd.to_datetime(display_df["timestamp"]).dt.strftime('%d.%m.%Y %H:%M')
        
        event = st.dataframe(
            display_df,
            key="search_history_table",
            use_container_width=True,
            on_select="rerun",
            selection_mode="single-row",
            column_config={
                "id": None,
                "keyword": "Suchbegriff",
                "country": "Land",
                "num_leads": "Anzahl Leads",
                "category": st.column_config.TextColumn("Kategorie", help="Klicke zum Bearbeiten unten"),
                "timestamp": "Zeitpunkt"
            },
            hide_index=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 2. Detail View (If selected)
        if event.selection.rows:
            selected_index = event.selection.rows[0]
            selected_row = searches_df.iloc[selected_index]
            search_id = selected_row["id"]
            current_cat = selected_row["category"]
            keyword = selected_row["keyword"]
            
            st.markdown(f"### Details zu: **{keyword}**")
            
            # 2a. Edit Category
            st.markdown('<div class="stCard">', unsafe_allow_html=True)
            c1, c2 = st.columns([3, 1])
            new_cat = c1.selectbox(
                "Kategorie zuweisen:", 
                options=["Marketing", "E-Commerce", "Agentur", "Tierfutter", "Immobilien", "Sonstiges", "Neu..."],
                index=["Marketing", "E-Commerce", "Agentur", "Tierfutter", "Immobilien", "Sonstiges", "Neu..."].index(current_cat) if current_cat in ["Marketing", "E-Commerce", "Agentur", "Tierfutter", "Immobilien", "Sonstiges", "Neu..."] else 0,
                key=f"cat_select_{search_id}"
            )
            
            if c2.button("Speichern 💾", key=f"save_{search_id}"):
                db.update_search_category(search_id, new_cat)
                st.success(f"Kategorie '{new_cat}' gespeichert!")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 2b. Show Leads for this Search
            user_leads = db.get_user_leads(st.session_state.user_id)
            if not user_leads.empty:
                search_leads = user_leads[user_leads["Keyword"] == keyword]
                
                if not search_leads.empty:
                    st.markdown(f"#### Gefundene Leads ({len(search_leads)})")
                    st.markdown('<div class="stCard">', unsafe_allow_html=True)
                    
                    # Use DataEditor here as well to allow deletion
                    edited_sl = st.data_editor(
                        search_leads,
                        key=f"leads_editor_{search_id}",
                        use_container_width=True,
                        column_config={
                            "ID": None,
                            "Website": st.column_config.LinkColumn("Link"),
                            "Ad URL": st.column_config.LinkColumn("Ad"),
                            "Ad Image": st.column_config.ImageColumn("Img"),
                            "Newsletter": st.column_config.CheckboxColumn("✉️", disabled=True),
                            "Trash": st.column_config.CheckboxColumn("🗑️", width="small"),
                            "Date": st.column_config.DatetimeColumn("Datum", format="D.M.Y")
                        },
                        hide_index=True,
                        disabled=["Company", "Email", "Keyword", "Date", "Website", "Ad URL", "Ad Image", "Newsletter", "Category", "Notes", "Warenkorb", "Angeschrieben", "Antwort", "Kunde"]
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    if f"leads_editor_{search_id}" in st.session_state:
                         changes = st.session_state[f"leads_editor_{search_id}"].get("edited_rows", {})
                         
                         # Batch Delete for Detail View
                         trash_indices = [idx for idx, updates in changes.items() if updates.get("Trash")]
                         if trash_indices:
                             st.warning(f"⚠️ {len(trash_indices)} Leads markiert.")
                             if st.button(f"🗑️ Löschen", key=f"del_btn_detail_{search_id}", type="primary"):
                                 for idx in trash_indices:
                                     try:
                                         real_row = search_leads.loc[int(idx)]
                                         db.update_lead(real_row["ID"], "Trash", True)
                                     except:
                                         pass
                                 
                                 if f"leads_editor_{search_id}" in st.session_state:
                                     del st.session_state[f"leads_editor_{search_id}"]
                                 st.success("Gelöscht!")
                                 st.rerun()
                         
                         # Apply other changes immediately (excluding Trash for now)
                         for idx, updates in changes.items():
                            st.rerun()

                else:
                    st.warning("Keine Leads zu diesem Suchbegriff gespeichert.")
            else:
                st.info("Keine Leads in Datenbank.")
            
    else:
        st.info("Keine Suchen vorhanden.")

elif page == "Papierkorb":
    st.title("🗑️ Papierkorb (Aussortiert)")
    st.info("Hier landen alle Leads, die du aussortiert hast. Du kannst sie wiederherstellen oder einen Grund angeben.")
    
    # Fetch ONLY deleted leads
    df_deleted = db.get_user_leads(st.session_state.user_id, filter_status='deleted')
    
    if not df_deleted.empty:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        edited_trash = st.data_editor(
            df_deleted,
            key="trash_editor",
            use_container_width=True,
            column_config={
                "ID": None,
                "Website": st.column_config.LinkColumn("Link", display_text="🔗"),
                "Company": "Firma",
                "Trash": st.column_config.CheckboxColumn("Gelöscht?", default=True, help="Häkchen entfernen zum Wiederherstellen"),
                "Grund": st.column_config.TextColumn("Grund für Löschung", help="Warum aussortiert?"),
                "Date": st.column_config.DatetimeColumn("Datum", format="D.M.Y")
            },
            hide_index=True,
            disabled=["Company", "Email", "Keyword", "Date", "Website", "Ad URL", "Ad Image", "Newsletter", "Category", "Notizen", "Warenkorb", "Angeschrieben", "Antwort", "Kunde"]
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if "trash_editor" in st.session_state:
            changes = st.session_state.trash_editor.get("edited_rows", {})
            for idx, updates in changes.items():
                try:
                    real_row = df_deleted.loc[int(idx)]
                    lead_id = real_row["ID"]
                    for col, val in updates.items():
                        # Map friendly names if needed or rely on db logic
                        # 'Trash' -> 'deleted' handled in update_lead
                        # 'Grund' -> 'deletion_reason' handled in update_lead
                        db.update_lead(lead_id, col, val)
                        
                    # If Trash status changed (uncheck), rerun to move it back to active
                    if "Trash" in updates:
                        st.balloons() # Nice touch for restoring
                        st.rerun()
                except:
                    pass
    else:
        st.info("Der Papierkorb ist leer. Alles sauber! 🧹")
