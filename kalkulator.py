import streamlit as st

# 1. KONFIGURACJA GŁÓWNA
st.set_page_config(page_title="Ekspert Wykończeń", layout="wide")

if 'pokoje_pro' not in st.session_state:
    st.session_state.pokoje_pro = []

if 'pokoje' not in st.session_state:
    st.session_state.pokoje = []

# Menu boczne do wyboru branży
with st.sidebar:
    st.title("🛠️ Menu Wykonawcy")
    branza = st.sidebar.selectbox("Wybierz rodzaj prac:", 
    ["🎨 Malowanie", "🧱 Szpachlowanie", "📐 Podłogi (Panele/Deska)", 
     "🏗️ Tynkowanie", "⚒️ Sucha Zabudowa", "⚡ Elektryka", "🚿 Łazienka", "🚪 Drzwi"])
    st.info(f"Aktualnie edytujesz: {branza}")

# --- SEKCJA: MALOWANIE ---
if branza == "🎨 Malowanie":
    st.subheader("Kalkulator Malarski")
    tab_fast, tab_pro = st.tabs(["⚡ Szybka Wycena", "💎 Kosztorys PRO"])

    # --- BAZA WIEDZY ---
    baza_biale = {
        "Śnieżka Eko (Akryl)": 14, "Dekoral Polinak": 19, "Tikkurila Anti-Reflex 2": 38,
        "Bondex Super White": 28, "Magnat Ultra Matt": 34, "Greinplast Comfort": 24
    }
    baza_kolory = {
        "Dekoral Akrylit W": 24, "Beckers It's Simple": 38, "Tikkurila Optiva 5": 52,
        "Magnat Ceramic": 62, "Dulux Kolory Świata": 28, "Bondex Smart Paint": 44
    }
    baza_grunty = {
        "Unigrunt Atlas (Standard)": 7, "Mapei Primer G (Premium)": 15,
        "Knauf Tiefengrund (Specjalistyczny)": 19, "Grunt Marketowy (Eko)": 4
    }
    baza_tasmy = {
        "Żółta Papierowa (Market)": 12, "Solid (Niebieska)": 24,
        "Blue Dolphin (Profesjonalna)": 34, "Tesa Precision (Premium)": 52, "3M / Scotch": 58
    }
    
    with tab_fast:
        st.header("⚡ Szybki szacunek materiałów i robocizny")
        col_f1, col_f2 = st.columns([1, 1.2])

        with col_f1:
            m_uzytkowy = st.number_input("Metraż mieszkania (podłoga m2):", min_value=1.0, value=50.0, key="fast_m")
            stan_f = st.selectbox("Stan lokalu:", ["Deweloperski", "Zamieszkały (meble)"], key="fast_s")
            
            st.subheader("Wybór Produktów")
            f_biala = st.selectbox("Farba BIAŁA (Sufity):", list(baza_biale.keys()))
            f_kolor = st.selectbox("Farba KOLOR (Ściany):", list(baza_kolory.keys()))
            f_grunt = st.selectbox("Marka Gruntu:", list(baza_grunty.keys()))
            f_tasma = st.selectbox("Rodzaj Taśmy:", list(baza_tasmy.keys()))
            
            stawka = st.slider("Twoja stawka za m2 robocizny:", 1, 70, 35)

            st.markdown("---")
            st.subheader("⚜️ Sztukateria (Listwy ścienne/sufitowe)")
            mb_sztukaterii = st.number_input("Łączna długość listew (mb):", min_value=0.0, value=0.0, step=1.0)
            typ_sztukaterii = st.selectbox("Rodzaj listew:", ["Styropianowe (Eko)", "Poliuretanowe (Twarde)", "Gipsowe (Premium)"])

        # --- LOGIKA OBLICZEŃ (Najpierw liczymy...) ---
        m2_sufit = m_uzytkowy * 1.0
        m2_sciany = m_uzytkowy * 2.5
        m2_razem = m2_sufit + m2_sciany
        mnoznik = 1.0 if stan_f == "Deweloperski" else 1.3

        l_biala = (m2_sufit / 10) * 2
        l_kolor = (m2_sciany / 10) * 2
        l_grunt = m2_razem * 0.15
        szt_akryl = m_uzytkowy / 12
        koszt_akrylu = (szt_akryl + 0.4) * 15 # przyjmijmy średnio 15 zł za tubkę
        szt_tasma = (m_uzytkowy / 15) * mnoznik
        opk_folia = (m_uzytkowy / 20) * mnoznik
        # SZTUKATERIA (Logika)
        szt_klej_sztukateria = mb_sztukaterii / 8
        stawki_szt = {"Styropianowe (Eko)": 25, "Poliuretanowe (Twarde)": 45, "Gipsowe (Premium)": 65}
        koszt_rob_sztukateria = mb_sztukaterii * stawki_szt[typ_sztukaterii]
        koszt_mat_sztukateria = (szt_klej_sztukateria + 0.4) * 25

            
        margines = 0.10
        k_mat_sredni = (l_biala * baza_biale[f_biala]) + (l_kolor * baza_kolory[f_kolor]) + \
                       (l_grunt * baza_grunty[f_grunt]) + (szt_tasma * baza_tasmy[f_tasma]) + \
                       koszt_mat_sztukateria + 150 # 150zł na drobnicę (folie/wałki)
        
        k_mat_min, k_mat_max = k_mat_sredni * (1 - margines), k_mat_sredni * (1 + margines)
        k_rob_total = (m2_razem * stawka) + koszt_rob_sztukateria

        # Stawka za montaż mb (cięcie, klejenie, akrylowanie łączeń)
        stawki_szt = {"Styropianowe (Eko)": 25, "Poliuretanowe (Twarde)": 45, "Gipsowe (Premium)": 65}
        koszt_rob_sztukateria = mb_sztukaterii * stawki_szt[typ_sztukaterii]


        # --- WYŚWIETLANIE WYNIKÓW (Potem pokazujemy!) ---
        with col_f2:
            st.subheader("💰 Przewidywany budżet")
            total_min = k_mat_min + k_rob_total
            total_max = k_mat_max + k_rob_total
            
            st.success(f"### RAZEM: **{round(total_min)} - {round(total_max)} zł**")
            st.metric("Twoja Robocizna (Stała)", f"{round(k_rob_total)} zł")
            st.info(f"**Materiały (widełki):** {round(k_mat_min)} - {round(k_mat_max)} zł")
            total_z_sztukateria = total_max + koszt_rob_sztukateria + koszt_mat_sztukateria
            st.success(f"### RAZEM Z SZTUKATERIĄ: **{round(total_z_sztukateria)} zł**")
        
        with st.expander("📦 Twoja lista zakupów"):
                # --- LOGIKA PAKOWANIA BIAŁEJ (Wiadra 10L / 5L / 2.5L) ---
            ile_biala = round(l_biala, 1)
            w10 = int(ile_biala // 10)
            reszta_b = ile_biala % 10
            w5 = 1 if 0 < reszta_b <= 5 else 0
            w25 = 1 if reszta_b > 5 else 0 # jeśli zostanie >5L, weź 10L lub 5+2.5
            # Uproszczona logika dla przejrzystości:
            koszt_b = ile_biala * baza_biale[f_biala]
            
            st.write(f"### ⚪ FARBA BIAŁA: {f_biala}")
            if w10 > 0: st.write(f"- Kup: **{w10} x wiadro 10L**")
            if reszta_b > 0: 
                pucha = "5L" if reszta_b > 2.5 else "2.5L"
                st.write(f"- Kup dodatkowo: **1 x puszka {pucha}**")
            st.write(f"Szacowany koszt bieli: **{round(koszt_b)} zł**")
            if mb_sztukaterii > 0:
                    st.write("### ⚜️ SZTUKATERIA")
                    st.write(f"- Klej: {int(szt_klej_sztukateria + 0.99)} szt.")
                    st.write(f"- Akryl do łączeń: {int(mb_sztukaterii/15 + 1)} szt.")
            st.markdown("---")

            # --- LOGIKA PAKOWANIA KOLORU (Puszki 5L / 2.5L) ---
            ile_kolor = round(l_kolor, 1)
            p5 = int(ile_kolor // 5)
            reszta_k = ile_kolor % 5
            p25 = 1 if reszta_k > 0 else 0
            koszt_k = ile_kolor * baza_kolory[f_kolor]

            st.write(f"### 🎨 FARBA KOLOR: {f_kolor}")
            if p5 > 0: st.write(f"- Kup: **{p5} x puszka 5L**")
            if p25 > 0: st.write(f"- Kup dodatkowo: **{p25} x puszka 2.5L**")
            st.write(f"Szacowany koszt koloru: **{round(koszt_k)} zł**")

            st.markdown("---")

            # --- GRUNT I TAŚMY ---
            st.write(f"### 🛠️ AKCESORIA")
            st.write(f"- Grunt **{f_grunt}**: {round(l_grunt)} L (ok. {int(l_grunt/5 + 0.99)} bańki 5L) — **{round(l_grunt * baza_grunty[f_grunt])} zł**")
            st.write(f"- Taśma **{f_tasma}**: {round(szt_tasma + 0.4)} szt. — **{round((szt_tasma + 0.4) * baza_tasmy[f_tasma])} zł**")
            st.write(f"- **Akryl szpachlowy (300ml):** {round(szt_akryl + 0.4)} szt. — **{round((szt_akryl + 0.4) * 15)} zł**")
            koszt_mat_sztukateria = (szt_klej_sztukateria + 0.4) * 25 # ok. 25 zł za dobry klej hybrydowy
            
            st.info("💡 Podpowiedzi opakowań są orientacyjne. Wybieraj największe dostępne puszki, aby zaoszczędzić.")
    with tab_pro:
        st.write("Tu wkleisz swoją logikę PRO z dodawaniem pojedynczych ścian.")
     # --- 2. ZAKŁADKA: KOSZTORYS PRO ---   
    with tab_pro:
        st.subheader("Precyzyjne planowanie ścian i kolorów")
    
    # Formularz dodawania ścian 
    with st.expander("➕ DODAJ ŚCIANĘ DO PROJEKTU", expanded=True):
        c1, c2, c3 = st.columns(3)
        nazwa_p = c1.text_input("Nazwa pokoju:", "Salon", key="pro_room")
        szer = c2.number_input("Szerokość ściany (m):", min_value=0.1, value=4.0, step=0.1)
        wys = c3.number_input("Wysokość ściany (m):", min_value=0.1, value=2.6, step=0.1)
        
        kolor_hex = st.color_picker("Wybierz kolor tej ściany:", "#D3D3D3")
        
        if st.button("Zatwierdź i dodaj ścianę"):
            # Dodajemy nową ścianę do listy w pamięci (session_state)
            st.session_state.pokoje_pro.append({
                "pokoj": nazwa_p, 
                "szer": szer, 
                "wys": wys, 
                "kolor": kolor_hex
            })
            st.success(f"Dodano ścianę do pokoju: {nazwa_p}")
            st.rerun()

    st.markdown("---")
            

    # Wyświetlanie i podliczanie PRO
    if not st.session_state.pokoje_pro:
        # Stan domyślny, gdy lista jest pusta
        st.info("💡 Twój kosztorys PRO jest pusty. Wypełnij powyższy formularz i kliknij 'Zatwierdź', aby zacząć.")
    else:
        # Jeśli są dane, to je podliczamy
        total_m2_pro = 0
        zestawienie_kolorow = {}

        st.subheader("📋 Twoje zestawienie ścian:")
        
        # Wyświetlamy listę dodanych ścian (żebyś wiedział co już dodałeś)
        for i, s in enumerate(st.session_state.pokoje_pro):
            pow = s['szer'] * s['wys']
            total_m2_pro += pow
            
            # Grupowanie kolorów
            zestawienie_kolorow[s['kolor']] = zestawienie_kolorow.get(s['kolor'], 0) + pow
            
            # Mały pasek z opisem każdej ściany
            st.write(f"{i+1}. **{s['pokoj']}**: {s['szer']}m x {s['wys']}m = **{round(pow, 2)} m²** (Kolor: {s['kolor']})")

        st.markdown("---")
        st.subheader(f"📊 Razem do pomalowania: {round(total_m2_pro, 1)} m² ścian")
        # Wyniki PRO
        st.subheader(f"📊 Wyniki precyzyjne: {round(total_m2_pro, 1)} m2 ścian")
        
        # Wyświetlanie kółek z kolorami
        cols_palette = st.columns(len(zestawienie_kolorow) if len(zestawienie_kolorow) > 0 else 1)
        for idx, (k, m) in enumerate(zestawienie_kolorow.items()):
            litry = (m / 10) * 2
            st.markdown(f"""
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div style="width: 25px; height: 25px; background-color: {k}; border-radius: 50%; border: 1px solid #ddd; margin-right: 10px;"></div>
                    <b>{round(litry, 1)} L</b> (Kolor: {k})
                </div>
            """, unsafe_allow_html=True)

        # PRZYCISK CZYSZCZENIA
        st.write("##")
        if st.button("🗑️ Wyczyść wszystkie dane PRO"):
            st.session_state.pokoje_pro = []
            st.rerun()

elif branza == "🧱 Szpachlowanie":
    st.header("Kalkulator Gładzi i Przygotowania Ścian")

    # 1. TWOJA BAZA WIEDZY
    baza_sypkie = {
        "Cekol C-45 (20kg)": {"cena": 58, "waga": 20},
        "FransPol GS-2 (20kg)": {"cena": 50, "waga": 20},
        "Dolina Nidy Omega (20kg)": {"cena": 37, "waga": 20},
        "Atlas Gipsar Uni (20kg)": {"cena": 52, "waga": 20}
    }
    
    baza_gotowe = {
        "Śmig A-2 (Wiadro 17kg)": {"cena": 63, "waga": 17},
        "Knauf Goldband Finish (18kg)": {"cena": 50, "waga": 18},
        "Knauf Goldband Finish (28kg)": {"cena": 72, "waga": 28},
        "Knauf Fill & Finish (20kg)": {"cena": 115, "waga": 20},
        "Sheetrock Blue (28kg)": {"cena": 145, "waga": 28},
        "Atlas GTA (20kg)": {"cena": 94, "waga": 20}
    }
    
    baza_grunty_szp = {
        "Atlas Unigrunt (Standard)": 7,
        "Knauf Tiefengrund (Premium)": 18,
        "Mapei Primer G": 15,
        "Ceresit CT 17": 11
    }

    tab_s1, tab_s2 = st.tabs(["⚡ Szybka Wycena", "💎 Detale PRO"])

    with tab_s1:
        col_s1, col_s2 = st.columns([1, 1.2])
        
        with col_s1:
            m2_podl = st.number_input("Metraż podłogi (m2):", min_value=1.0, value=50.0, key="szp_m")
            warstwy = st.slider("Liczba warstw gładzi:", 1, 3, 2, key="szp_w")
            typ_g = st.radio("Rodzaj gładzi:", ["Sypka (Worek)", "Gotowa (Wiadro)"])

            if typ_g == "Sypka (Worek)":
                marka = st.selectbox("Wybierz gładź:", list(baza_sypkie.keys()))
                dane_g = baza_sypkie[marka]
                norma = 1.2
            else:
                marka = st.selectbox("Wybierz gładź:", list(baza_gotowe.keys()))
                dane_g = baza_gotowe[marka]
                norma = 2.0
            
            marka_gruntu = st.selectbox("Wybierz Grunt:", list(baza_grunty_szp.keys()))
            stawka_szp = st.slider("Twoja stawka za m2 (robocizna):", 1, 150, 50)

        # --- LOGIKA OBLICZEŃ ---
        m2_scian = m2_podl * 3.5
        kg_razem = m2_scian * norma * warstwy
        szt_opk = kg_razem / dane_g["waga"]
        
        # Gruntowanie (przed i po - ok. 0.2L na m2)
        l_gruntu = m2_scian * 0.2
        koszt_gruntu = l_gruntu * baza_grunty_szp[marka_gruntu]
        
        # Suma materiałów (gładź + grunt + narożniki/taśmy stałe 15zł/m2 podłogi)
        k_mat_base = (szt_opk * dane_g["cena"]) + koszt_gruntu + (m2_podl * 15)
        k_rob_szp = m2_scian * stawka_szp

        # --- LOGIKA CZASU PRACY ---
        # Baza: 50m2 ścian dziennie + 1 dzień na każdą warstwę (schnięcie)
        dni_robocze = (m2_scian / 50) + (warstwy * 1) 

        with col_s2:
            st.subheader("💰 Kosztorys Szpachlowania")
            st.success(f"### RAZEM: **{round((k_mat_base * 0.9) + k_rob_szp)} - {round((k_mat_base * 1.1) + k_rob_szp)} zł**")
            
            c1, c2 = st.columns(2)
            c1.metric("Twoja Robocizna", f"{round(k_rob_szp)} zł")
            c2.metric("Materiały (ok.)", f"{round(k_mat_base)} zł")

            st.warning(f"⏳ Przewidywany czas: **ok. {round(dni_robocze + 0.5)} dni**")
            st.caption("⚠️ Czas uzależniony od temperatury i wilgotności (schnięcie gładzi).")

            with st.expander("📦 Twoja lista zakupów"):
                st.write(f"• **Gładź ({marka}):** {int(szt_opk + 0.99)} szt.")
                st.write(f"• **Grunt ({marka_gruntu}):** {int((l_gruntu/5)+0.99)} bańki (5L)")
                st.write(f"• **Narożniki aluminiowe:** {round(m2_podl * 0.8 / 2.5)} szt.")
                st.write(f"• **Taśma zbrojąca:** {round(m2_podl)} mb")

            with st.expander("🛠️ Zakres prac:"):
                st.write(f"1. Gruntowanie ({marka_gruntu})")
                st.write(f"2. Nałożenie {warstwy} warstw gładzi ({marka})")
                st.write("3. Szlifowanie mechaniczne i odpylanie")
                st.write("4. Gruntowanie końcowe pod malowanie")

    with tab_s2:
        st.info("Sekcja PRO: Precyzyjne odliczanie otworów okiennych.")


# --- SEKCJA: PODŁOGI ---
elif branza == "📐 Podłogi (Panele/Deska)":
    st.header("📐 Kalkulator Podłóg: Pływające vs Klejone")
    tab_p1, tab_p2 = st.tabs(["⚡ Szybka Wycena", "💎 Szczegóły Montażu"])

    with tab_p1:
        col_p1, col_p2 = st.columns([1, 1.2])
        
        with col_p1:
            m2_p = st.number_input("Metraż podłogi (m2):", min_value=0.1, value=20.0, step=0.1, key="pod_m")
            
            # NOWOŚĆ: SYSTEM MONTAŻU
            system_montazu = st.radio("System montażu:", ["Pływający (Na podkładzie)", "Klejony (Na gruncie i kleju)"])
            
            typ_ukladania = st.selectbox("Sposób układania:", ["Zwykły panel (7% zapasu)", "Jodełka (20% zapasu)"])
            m2_paczka = st.number_input("M2 w paczce paneli/desek:", min_value=0.1, value=2.22, step=0.01)
            
            st.markdown("---")
            if system_montazu == "Pływający (Na podkładzie)":
                wybrany_mat = st.selectbox("Rodzaj podkładu:", ["Premium (Rolka 8m2)", "Ecopor (Paczka 7m2)", "Standard (Pianka 10m2)"])
            else:
                wybrany_mat = st.selectbox("Marka chemii (Klej + Grunt):", ["Mapei (Profesjonalna)", "Wakol (Premium)", "Bona (Standard)"])
            
            st.markdown("---")
            stawka_podl = st.slider("Twoja stawka za m2 montażu (zł):", 1, 160, 45 if "Zwykły" in typ_ukladania else 120)

        # --- LOGIKA OBLICZEŃ ---
        zapas = 0.07 if "Zwykły" in typ_ukladania else 0.20
        m2_z_zapasem = m2_p * (1 + zapas)
        paczki_szt = int(m2_z_zapasem / m2_paczka + 0.99)
        
        # Koszty chemii / podkładu
        if system_montazu == "Pływający (Na podkładzie)":
            wydajnosci = {"Premium (Rolka 8m2)": 8, "Ecopor (Paczka 7m2)": 7, "Standard (Pianka 10m2)": 10}
            ceny_p = {"Premium (Rolka 8m2)": 160, "Ecopor (Paczka 7m2)": 45, "Standard (Pianka 10m2)": 30}
            szt_podkladu = int(m2_p / wydajnosci[wybrany_mat] + 0.99)
            koszt_akc = szt_podkladu * ceny_p[wybrany_mat]
            info_zakup = f"{szt_podkladu} szt. podkładu {wybrany_mat}"
        else:
            # System klejony: Grunt (0.15kg/m2) + Klej (1.2kg/m2)
            kg_kleju = m2_p * 1.2
            l_gruntu = m2_p * 0.15
            # Średnie ceny chemii klejonej (zestaw na m2 ok. 45-60 zł)
            koszt_akc = m2_p * 55 
            info_zakup = f"{int(kg_kleju/15 + 0.99)} wiader kleju (15kg) + {int(l_gruntu/5 + 0.99)} bańki gruntu (5L)"

        # Finanse
        k_robocizna = m2_p * stawka_podl
        total_mat = (paczki_szt * m2_paczka * 100) + koszt_akc # przyjąłem średnią cenę deski 100zł/m2

        with col_p2:
            st.subheader("💰 Kosztorys Podłogi")
            st.success(f"### RAZEM: **{round((total_mat + k_robocizna) * 0.95)} - {round((total_mat + k_robocizna) * 1.05)} zł**")
            
            c1, c2 = st.columns(2)
            c1.metric("Twoja Robocizna", f"{round(k_robocizna)} zł")
            c2.metric("Chemia / Podkład", f"{round(koszt_akc)} zł")

            with st.expander("📦 Twoja lista zakupów"):
                st.write(f"• **Panele/Deska:** {paczki_szt} paczek")
                st.write(f"• **System:** {info_zakup}")
                if system_montazu == "Klejony (Na gruncie i kleju)":
                    st.warning("⚠️ System klejony: Pamiętaj o odpowiednim czasie schnięcia gruntu przed klejeniem!")
                st.caption(f"Przyjęto zapas materiału: {int(zapas*100)}%")

            # Czas pracy (klejenie trwa dłużej)
            tempo = 25 if system_montazu == "Pływający (Na podkładzie)" else 12
            st.warning(f"⏳ Czas realizacji: ok. **{round(m2_p/tempo + 1)} dni**")

# --- SEKCJA: TYNKOWANIE ---
elif branza == "🏗️ Tynkowanie":
    st.header("🏗️ Kalkulator Tynków Maszynowych i Ręcznych")
    
    # --- BAZA WIEDZY: TYNKI I GRUNTY ---
    baza_tynkow = {
        "Knauf MP 75 (Maszynowy Gipsowy)": {"cena": 25, "waga": 30, "norma": 0.8}, # 0.8kg na 1mm/m2
        "Knauf Goldband (Ręczny Gipsowy)": {"cena": 38, "waga": 30, "norma": 0.85},
        "Baumit MPI25 Cem-Wap ": {"cena": 27, "waga": 30, "norma": 1.4},
        "Kreisel 561L Cem-Wap": {"cena": 28, "waga": 25, "norma": 1.6}
    }
    
    baza_grunt_kwarc = {
        "Dolina Nidy Inter-Grunt": 140, # cena za wiadro 20kg
        "Knauf Betokontakt": 200, # cena za wiadro 20kg
        "Atlas Grunto-Plast": 110
    }

    tab_t1, tab_t2 = st.tabs(["⚡ Szybka Wycena", "💎 Detale PRO"])

    with tab_t1:
        col_t1, col_t2 = st.columns([1, 1.2])
        
        with col_t1:
            m2_podl_t = st.number_input("Metraż mieszkania (podłoga m2):", min_value=1.0, value=50.0, key="tyn_m_fast")
            wybrany_tynk = st.selectbox("Wybierz rodzaj tynku:", list(baza_tynkow.keys()))
            wybrany_grunt_t = st.selectbox("Wybierz grunt kwarcowy:", list(baza_grunt_kwarc.keys()))
            
            st.markdown("---")
            grubosc_t = st.slider("Średnia grubość tynku (mm):", 10, 30, 15)
            stawka_rob_t = st.slider("Stawka za robociznę (zł/m2):", 1, 100, 45)

        # --- LOGIKA OBLICZEŃ (Twoje m2 ścian) ---
        m2_scian_t = m2_podl_t * 3.5
        dane_t = baza_tynkow[wybrany_tynk]
        
        # Zużycie tynku
        kg_na_m2_t = dane_t["norma"] * grubosc_t
        kg_razem_t = m2_scian_t * kg_na_m2_t
        worki_t = kg_razem_t / dane_t["waga"]
        
        # Zużycie gruntu (ok. 0.3kg / m2)
        kg_gruntu_t = m2_scian_t * 0.3
        wiadra_gruntu = kg_gruntu_t / 15 # wiadra 15kg
        
        # Finanse
        koszt_mat_t = (worki_t * dane_t["cena"]) + (wiadra_gruntu * baza_grunt_kwarc[wybrany_grunt_t]) + (m2_scian_t * 5) # +5zł na narożniki
        koszt_rob_t = m2_scian_t * stawka_rob_t

        with col_t2:
            st.subheader("📊 Wyniki Tynkowania")
            # Widełki 10% na materiał
            st.success(f"### RAZEM: **{round((koszt_mat_t * 0.9) + koszt_rob_t)} - {round((koszt_mat_t * 1.1) + koszt_rob_t)} zł**")
            
            c1, c2 = st.columns(2)
            c1.metric("Twoja Robocizna", f"{round(koszt_rob_t)} zł")
            c2.metric("Waga materiału", f"{round(kg_razem_t/1000, 1)} Tony")

            with st.expander("📦 Lista zakupów (Szczegółowa)"):
                st.write(f"### 🧱 TYNK: {wybrany_tynk}")
                st.write(f"- Kup: **{int(worki_t + 0.99)} worków** (opakowanie {dane_t['waga']}kg)")
                st.write(f"- Szacowany koszt tynku: **{round(worki_t * dane_t['cena'])} zł**")
                
                st.markdown("---")
                st.write(f"### 🧪 GRUNT: {wybrany_grunt_t}")
                st.write(f"- Kup: **{int(wiadra_gruntu + 0.99)} wiader** (opakowanie 15kg)")
                
                st.markdown("---")
                st.write(f"• Narożniki tynkarskie: ok. {round(m2_podl_t * 0.5)} szt.")
                st.caption(f"Przyjęto grubość {grubosc_t} mm na {round(m2_scian_t)} m² ścian.")

    with tab_t2:
        st.info("💎 Wersja PRO: Tutaj odliczymy otwory okienne, co przy tynkach maszynowych jest kluczowe dla precyzyjnej wyceny.")

# --- SEKCJA: SUCHA ZABUDOWA ---
elif branza == "⚒️ Sucha Zabudowa":
    st.header("⚒️ Systemy Suchej Zabudowy (G-K)")
    typ_gk = st.selectbox("Co budujemy?", ["Ściana działowa (dwustronna)", "Sufit podwieszany", "Zabudowa poddasza"])
    m2_gk = st.number_input("Metraż zabudowy (m2):", min_value=1.0, value=20.0)
    
    # Logika: Średnio 2.1 m2 płyty na 1 m2 ściany (odpady + 2 strony)
    m2_plyt = m2_gk * (2.1 if "Ściana" in typ_gk else 1.1)
    
    st.metric("Potrzebne płyty G-K", f"{round(m2_plyt, 1)} m2", f"ok. {int(m2_plyt/3 + 0.99)} szt. (1.2x2.5m)")
    st.info("Logika PRO doliczy tu profile (CD/UD/CW/UW), wkręty i wełnę.")

# --- SEKCJA: ELEKTRYKA ---
elif branza == "⚡ Elektryka":
    st.header("⚡ Kalkulator Instalacji Elektrycznej")
    punkty = st.number_input("Liczba punktów elektrycznych (gniazdka, wypusty):", min_value=1, value=40)
    typ_inst = st.selectbox("Standard instalacji:", ["Podstawowy (Mieszkanie)", "Rozbudowany (Smart Home)"])
    
    stawka_pkt = 80 if "Podstawowy" in typ_inst else 150
    st.metric("Szacowany koszt robocizny", f"{punkty * stawka_pkt} zł", f"{stawka_pkt} zł/pkt")
    st.warning("⚠️ Cena nie zawiera osprzętu (gniazdek) i rozdzielni.")

elif branza == "🚪 Drzwi":
    st.header("🚪 Kalkulator Montażu Drzwi Wewnętrznych")
    
    col_d1, col_p2 = st.columns(2)
    
    with col_d1:
        szt_drzwi = st.number_input("Liczba kompletów (skrzydło + ościeżnica):", min_value=1, value=5)
        typ_drzwi = st.selectbox("Rodzaj drzwi:", ["Przylgowe (Standard)", "Bezprzylgowe (Ukryte zawiasy)", "Przesuwne"])
        szerokosc_opaski = st.radio("Szerokość muru (zakres):", ["80-100mm", "100-140mm", "140mm+ (Dopłata)"])
        
        st.markdown("---")
        podciecie = st.checkbox("Podcięcie wentylacyjne (łazienkowe)?")
        demontaz = st.checkbox("Demontaż starych drzwi/ościeżnic?")

    # --- LOGIKA DRZWI ---
    stawka_base = 250 if "Standard" in typ_drzwi else 350
    if "Ukryte" in typ_drzwi: stawka_base = 450
    
    dodatki = 0
    if podciecie: dodatki += (szt_drzwi * 30)
    if demontaz: dodatki += (szt_drzwi * 100)
    
    robocizna_drzwi = (szt_drzwi * stawka_base) + dodatki
    
    with col_p2:
        st.subheader("💰 Wycena Montażu")
        st.metric("Łączna robocizna", f"{round(robocizna_drzwi)} zł")
        st.write(f"• Stawka za sztukę: {stawka_base} zł")
        
        with st.expander("📦 Co musisz kupić (Materiały):"):
            st.write(f"• **Pianka montażowa (niskoprężna):** {int(szt_drzwi/2 + 0.99)} szt. (wydajna)")
            st.write(f"• **Klej do listew/opasek:** 1-2 tubki")
            st.write(f"• **Kliny montażowe:** zestaw 1 opk.")
        
        st.warning(f"⏳ Czas montażu: ok. **{int(szt_drzwi/2 + 1)} dni** (średnio 2-3 pary dziennie)")
