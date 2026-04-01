import streamlit as st

# 1. KONFIGURACJA GŁÓWNA
st.set_page_config(page_title="Ekspert Wykończeń", layout="wide")

# Nagłówek z logo i tytułem
col_space1, col_logo, col_space2 = st.columns([1, 2, 1]) 

with col_logo:
    # TE LINIE MUSZĄ MIEĆ 4 SPACJE WCIĘCIA:
    try:
        st.image("logo2.png", use_container_width=True)
    except:
        st.error("Brak pliku logo2.png")

# Te linie wracają do lewej krawędzi (0 spacji):
st.markdown("<p style='text-align: center; color: gray;'>Profesjonalny system kosztorysowania remontów</p>", unsafe_allow_html=True)
   

# --- STYLE CSS (Twoje poprawione style) ---
st.markdown("""
<style>
    <style>
    /* 1. POWIĘKSZENIE TEKSTU DLA WSZYSTKICH PRZYCISKÓW PILLS */
    [data-testid="stPills"] button p {
        font-size: 26px !important; 
        font-weight: 800 !important;
        color: white !important;
        margin: 0 !important;
    }

    /* 2. POWIĘKSZENIE SAMEGO KONTENERA PRZYCISKU */
    [data-testid="stPills"] button {
        padding: 20px 40px !important;
        height: auto !important;
        min-height: 70px !important;
        background-color: #1A1C23 !important;
        border: 2px solid #2D2F39 !important;
        border-radius: 15px !important;
    }

    /* 3. STYL DLA AKTYWNEJ PIGUŁKI (WYMUSZENIE KOLORU) */
    [data-testid="stPills"] button[aria-checked="true"] {
        background-color: #00D395 !important;
        border-color: #00D395 !important;
    }
    
    /* 4. KOLOR TEKSTU DLA AKTYWNEJ PIGUŁKI (ŻEBY BYŁ CZARNY) */
    [data-testid="stPills"] button[aria-checked="true"] p {
        color: black !important;
    }

    /* 5. EFEKT HOVER */
    [data-testid="stPills"] button:hover {
        border-color: #00D395 !important;
</style>
""", unsafe_allow_html=True)

# --- STAN APLIKACJI ---
if 'pokoje_pro' not in st.session_state: st.session_state.pokoje_pro = []
if 'pokoje' not in st.session_state: st.session_state.pokoje = []

# --- 1. STYLE CSS (NAJPIERW STYL) ---
st.markdown("""
<style>
    /* AGRESYWNE POWIĘKSZENIE WSZYSTKICH PRZYCISKÓW W MENU PILLS */
    div[data-selection-mode="single"] button {
        padding: 15px 30px !important;
        min-height: 60px !important;
        border-radius: 12px !important;
        background-color: #1A1C23 !important;
        border: 2px solid #2D2F39 !important;
    }

    /* POWIĘKSZENIE TEKSTU */
    div[data-selection-mode="single"] button p {
        font-size: 22px !important;
        font-weight: bold !important;
        color: white !important;
    }

    /* KOLOR AKTYWNEGO ELEMENTU */
    div[data-selection-mode="single"] button[aria-checked="true"] {
        background-color: #00D395 !important;
        border-color: #00D395 !important;
    }

    div[data-selection-mode="single"] button[aria-checked="true"] p {
        color: black !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. NOWOCZESNE MENU POZIOME (POTEM MENU) ---
branza = st.pills(
    "Wybierz rodzaj prac:", 
    [
        "🎨 Malowanie", "🧱 Szpachlowanie", "📐 Podłogi", 
        "🏗️ Tynkowanie", "⚒️ Sucha Zabudowa", "⚡ Elektryka", 
        "🚿 Łazienka", "🚪 Drzwi", "🚀 PANEL INWESTORA (PREMIUM)"
    ],
    selection_mode="single",
    default="🎨 Malowanie"
)

st.markdown("---")

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
elif branza == "📐 Podłogi":
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
    st.header("🏗️ Kalkulator Tynków i Suchego Tynku")
    
    # 1. BAZA WIEDZY: MASY DO SPOINOWANIA
    baza_masy = {
        "Knauf Uniflot (Premium)": 115, # wiadro/worek 25kg
        "Knauf Vario (Bardzo elastyczna)": 95,
        "Dolina Nidy Start (Ekonomiczna)": 45,
        "Franspol (Standard)": 55
    }

    baza_tynkow = {
        "Knauf MP 75 (Maszynowy Gipsowy)": {"cena": 25, "waga": 30, "norma": 0.8, "typ": "mokry"},
        "Baumit MPI25 Cem-Wap ": {"cena": 27, "waga": 30, "norma": 1.4, "typ": "mokry"},
        "Wyklejanie Płytami GK (Suchy Tynk)": {"cena_plyta": 35, "cena_klej": 24, "typ": "drywall"}
    }
    
    baza_grunt_kwarc = {
        "Dolina Nidy Inter-Grunt (20kg)": 140, "Knauf Betokontakt (20kg)": 200, "Atlas Grunto-Plast (20kg)": 110
    }

    tab_t1, tab_t2 = st.tabs(["⚡ Szybka Wycena", "💎 Detale PRO"])

    with tab_t1:
        col_t1, col_t2 = st.columns([1, 1.2])
        
        with col_t1:
            m2_podl_t = st.number_input("Metraż mieszkania (podłoga m2):", min_value=1.0, value=50.0, key="tyn_m_fast")
            
            # LOGIKA POWIERZCHNI: Mokry (Sufit+Ściany=3.5) vs GK (Same ściany=2.5)
            wybrany_tynk = st.selectbox("Wybierz system:", list(baza_tynkow.keys()))
            dane_t = baza_tynkow[wybrany_tynk]
            
            mnoznik = 3.5 if dane_t["typ"] == "mokry" else 2.5
            m2_robocizny = m2_podl_t * mnoznik
            st.info(f"📐 Powierzchnia prac: **{round(m2_robocizny)} m²**")

            if dane_t["typ"] == "drywall":
                st.markdown("---")
                st.subheader("Opcje spoinowania GK")
                typ_tasmy = st.radio("Rodzaj zbrojenia łączy:", ["Wszystko Tuff-Tape (Pancerne)", "Tuff-Tape (Naroża) + Flizelina (Reszta)"])
                wybrana_masa = st.selectbox("Masa do spoinowania:", list(baza_masy.keys()))
            else:
                wybrany_grunt_t = st.selectbox("Wybierz grunt kwarcowy:", list(baza_grunt_kwarc.keys()))
                grubosc_t = st.slider("Średnia grubość tynku (mm):", 10, 30, 15)
            
            stawka_rob_t = st.slider("Stawka za robociznę (zł/m2):", 1, 120, 45)

        # --- 2. LOGIKA OBLICZEŃ ---
        if dane_t["typ"] == "mokry":
            kg_na_m2_t = dane_t["norma"] * grubosc_t
            kg_razem_t = m2_robocizny * kg_na_m2_t
            worki_t = int(kg_razem_t / dane_t["waga"] + 0.99)
            wiadra_gruntu = int((m2_robocizny * 0.3) / 20 + 0.99)
            koszt_mat_t = (worki_t * dane_t["cena"]) + (wiadra_gruntu * baza_grunt_kwarc[wybrany_grunt_t]) + (m2_robocizny * 5)
        else:
            # --- LOGIKA GK (WYKLEJANIE) ---
            liczba_plyt = int((m2_robocizny * 1.1) / 3.12 + 0.99)
            worki_kleju = int(liczba_plyt / 2.5 + 0.99)
            
            # Materiały do spoinowania
            # Norma masy: ok. 0.5kg/m2 płyty (na gotowo)
            worki_masy = int((m2_robocizny * 0.5) / 25 + 0.99)
            cena_tasmy = 120 if "Tuff-Tape" in typ_tasmy else 60 # koszt orientacyjny na całość
            
            koszt_mat_t = (liczba_plyt * dane_t["cena_plyta"]) + (worki_kleju * dane_t["cena_klej"]) + \
                          (worki_masy * baza_masy[wybrana_masa]) + cena_tasmy + (m2_robocizny * 2)
            
        koszt_rob_t = m2_robocizny * stawka_rob_t

        with col_t2:
            st.subheader("💰 Podsumowanie Etapu")
            st.success(f"### RAZEM: **{round(koszt_mat_t + koszt_rob_t)} zł**")
            
            c1, c2 = st.columns(2)
            c1.metric("Twoja Robocizna", f"{round(koszt_rob_t)} zł")
            c2.metric("Materiały (ok.)", f"{round(koszt_mat_t)} zł")

            with st.expander("📦 SZCZEGÓŁOWA LISTA ZAKUPÓW", expanded=True):
                if dane_t["typ"] == "mokry":
                    st.write(f"• **Tynk ({wybrany_tynk}):** {worki_t} worków")
                    st.write(f"• **Grunt ({wybrany_grunt_t}):** {wiadra_gruntu} wiader (20kg)")
                else:
                    st.write(f"• **Płyty GK (1.2x2.6m):** {liczba_plyt} szt.")
                    st.write(f"• **Klej Perlfix:** {worki_kleju} worków")
                    st.write(f"• **Masa ({wybrana_masa}):** {worki_masy} szt.")
                    st.write(f"• **Zbrojenie:** {typ_tasmy}")
                    st.caption("Pamiętaj: Sufity w tym systemie liczymy w zakładce 'Sucha Zabudowa'.")
                    
elif branza == "⚒️ Sucha Zabudowa":
    st.header("⚒️ Kompleksowe Systemy G-K")
    tab_gk1, tab_gk2 = st.tabs(["⚡ Szybka Wycena", "💎 Kosztorys PRO"])

    # --- BAZA CENOWA ---
    baza_mat_gk = {
        "Plyta GK 12.5mm (szt)": 35.0, "Profil CD60 (3mb)": 24.0, "Profil UD27 (3mb)": 15.0,
        "Profil CW50 (3mb)": 15.0, "Profil UW50 (3mb)": 12.0, "Profil UA50 (3mb)": 65.0,
        "Wieszak ES / Obrotowy (szt)": 2.5, "Wkrety TN25 (1000szt)": 45.0,
        "Wkrety TN35 (1000szt)": 55.0, "Kolki 8x60 (100szt)": 32.0, "Welna (m2)": 18.0
    }
    baza_masy_gk = {"Knauf Uniflot": 115, "Knauf Vario": 95, "Dolina Nidy Start": 45, "Franspol": 55}

    with tab_gk1:
        
        # --- WARTOŚCI DOMYŚLNE (Zapobiegają błędom NameError) ---
        m2_gk = 0
        robocizna = 0
        total_material = 0
        szer_profilu = 60
        laczniki_cd1 = 0    
        laczniki_cd2 = 0   
        laczniki_krzyzowe = 0
        szt_cd = 0          
        szt_ud = 0          
        szt_wieszaki = 0    
        
        col_g1, col_g2 = st.columns([1, 1.2])

        with col_g1:
            
            szer_profilu = 60 
            
            rodzaj_gk = st.radio("Co budujemy?", ["Sufit Podwieszany", "Ściana Działowa"], key="gk_type")
            dl_profilu_cd = 3.0
            
            if rodzaj_gk == "Sufit Podwieszany":
                c1, c2 = st.columns(2)
                dl_sufitu = c1.number_input("Długość sufitu (m):", min_value=0.1, value=5.0)
                sz_sufitu = c2.number_input("Szerokość sufitu (m):", min_value=0.1, value=4.0)
                m2_gk = dl_sufitu * sz_sufitu
                typ_stelaza = st.radio("Rodzaj stelaża:", ["Pojedynczy", "Krzyżowy"])
                
                # --- OBLICZENIA SUFIT ---
                rozstaw_cd1 = 0.40 if typ_stelaza == "Pojedynczy" else 1.10
                liczba_cd1 = int(sz_sufitu / rozstaw_cd1) + 1
                odcinki_cd1 = int(dl_sufitu / dl_profilu_cd)
                reszta_cd1 = dl_sufitu % dl_profilu_cd
                szt_cd1 = liczba_cd1 * (odcinki_cd1 + (1 if reszta_cd1 > 0 else 0))
                laczniki_cd1 = odcinki_cd1 * liczba_cd1

                if typ_stelaza == "Krzyżowy":
                    rozstaw_cd2 = 0.40
                    liczba_cd2 = int(dl_sufitu / rozstaw_cd2) + 1
                    odcinki_cd2 = int(sz_sufitu / dl_profilu_cd)
                    reszta_cd2 = sz_sufitu % dl_profilu_cd
                    szt_cd2 = liczba_cd2 * (odcinki_cd2 + (1 if reszta_cd2 > 0 else 0))
                    laczniki_cd2 = odcinki_cd2 * liczba_cd2
                    laczniki_krzyzowe = liczba_cd1 * liczba_cd2
                    szt_cd2 = laczniki_cd2 = laczniki_krzyzowe = 0
                else:
                    szt_cd2 = 0
                    laczniki_cd2 = 0
                    laczniki_krzyzowe = 0
                
                szt_cd = szt_cd1 + szt_cd2
                szt_ud = int(((dl_sufitu + sz_sufitu) * 2 * 1.1) / 3) + 1
                szt_wieszaki = int(m2_gk / 0.7) + 1 # Gęściej dla bezpieczeństwa
                szt_cw = szt_uw = szt_ua = 0

            else: # ŚCIANA DZIAŁOWA
                c1, c2 = st.columns(2)
                szer_sciany = c1.number_input("Długość ścianki (m):", min_value=0.1, value=4.0)
                wys_sciany = c2.number_input("Wysokość ścianki (m):", min_value=0.1, value=2.6)
                m2_gk = szer_sciany * wys_sciany
                szer_profilu = st.selectbox("Profil CW/UW:", [50, 75, 100], format_func=lambda x: f"{x} mm")
                plytowanie = st.radio("Płytowanie:", ["1xGK (Jednostronnie)", "2xGK (Dwustronnie)"])
                n_drzwi = st.number_input("Otwory drzwiowe (UA):", min_value=0, value=0)
                
                szt_uw = int((szer_sciany * 2 * 1.1) / 3) + 1
                szt_cw = int((szer_sciany / 0.6) * (wys_sciany / 3) + 1)
                szt_ua = n_drzwi * 2
                szt_cd = szt_ud = szt_wieszaki = laczniki_cd1 = laczniki_krzyzowe = 0

            izolacja_gk = st.checkbox("Wypełnienie wełną?")
            if izolacja_gk:
                # Ustawiamy domyślny indeks wełny na podstawie wybranego profilu
                opcje_welny = [50, 75, 100, 150]
                try:
                    domyslny_indeks = opcje_welny.index(szer_profilu)
                except ValueError:
                    domyslny_indeks = 0 # Jeśli profilu nie ma na liście (np. sufit), daj 50mm

                grubosc_welny = st.selectbox(
                    "Grubość wełny:",
                    opcje_welny,
                    index=domyslny_indeks,
                    format_func=lambda x: f"{x} mm"
                )
            else:
                grubosc_welny = None
            wybrana_masa = st.selectbox("Masa do spoinowania:", list(baza_masy_gk.keys()))
            stawka_gk = st.slider("Stawka za robociznę (zł/m2):", 1, 250, 110)

        # --- LOGIKA MATERIAŁOWA ---
        naddatek = 1.10 # 10% zapasu na wszystko
        szt_plyt = int((m2_gk * naddatek) / 2.88) + 1
        wkret_25 = int(m2_gk * 20)
        
        koszt_plyt = szt_plyt * baza_mat_gk["Plyta GK 12.5mm (szt)"]
        koszt_profile = (szt_cd * baza_mat_gk["Profil CD60 (3mb)"]) + (szt_ud * baza_mat_gk["Profil UD27 (3mb)"]) + \
                        (szt_cw * baza_mat_gk.get(f"Profil CW{szer_profilu} (3mb)", 0)) + \
                        (szt_uw * baza_mat_gk.get(f"Profil UW{szer_profilu} (3mb)", 0)) + \
                        (szt_ua * baza_mat_gk.get(f"Profil UA{szer_profilu} (3mb)", 0))
        
        koszt_akcesoria = (szt_wieszaki * baza_mat_gk["Wieszak ES / Obrotowy (szt)"]) + \
                          (int(wkret_25/1000+1) * baza_mat_gk["Wkrety TN25 (1000szt)"])
        
        koszt_welny = (m2_gk * baza_mat_gk["Welna (m2)"]) if izolacja_gk else 0
        koszt_masy = (int(m2_gk * 0.5 / 25) + 1) * baza_masy_gk[wybrana_masa]
        # Pchełki do skręcania stelaża (średnio 10 szt / m2)
        szt_pchelki = int(m2_gk * 10 / 1000 + 1) 
        koszt_pchelki = szt_pchelki * 40.0 # ok 40 zł za paczkę 1000szt

        # Łączniki wzdłużne (tylko jeśli profil CD jest łączony)
        koszt_laczniki = (laczniki_cd1 + laczniki_cd2) * 1.50 # ok 1.50 zł/szt
        
        total_material = koszt_plyt + koszt_profile + koszt_akcesoria + koszt_welny + koszt_masy + koszt_pchelki + koszt_laczniki

        # --- 1. LOGIKA SPOINOWANIA (TAŚMY I MASY) ---
        st.markdown("---")
        st.subheader("Wykończenie spoin")
        c_sp1, c_sp2 = st.columns(2)
        
        typ_tasmy = c_sp1.radio("Zbrojenie:", ["Tuff-Tape (Całość)", "Flizelina + Tuff-Tape (Narożniki)"])
        wybrana_masa = c_sp2.selectbox("Masa do spoinowania:", list(baza_masy_gk.keys()), key="masa_wybor")

        # --- 2. OBLICZENIA ILOŚCI I KOSZTÓW ---
        naddatek = 1.10 
        szt_plyt = int((m2_gk * naddatek) / 2.88) + 1
        
        # Wkręty: TN25 (20 szt/m2) + Pchełki LN (10 szt/m2 sufitu)
        wkret_25 = int(m2_gk * 20 * naddatek)
        szt_pchelki = int(m2_gk * 12) if rodzaj_gk == "Sufit Podwieszany" else int(m2_gk * 5)

        # Taśmy i masy
        if typ_tasmy == "Tuff-Tape (Całość)":
            mb_tuff = m2_gk * 1.5
            mb_fliz = 0
        else:
            mb_tuff = m2_gk * 0.4 # Tylko narożniki
            mb_fliz = m2_gk * 1.1 # Połączenia płaskie
        
        koszt_tasm = (int(mb_tuff/30)+1)*120 + (int(mb_fliz/25)+1)*15
        worki_masy = int((m2_gk * 0.5) / 25 + 0.99)
        
        # Sumowanie kosztów
        koszt_plyt = szt_plyt * baza_mat_gk["Plyta GK 12.5mm (szt)"]
        koszt_pchelki = (int(szt_pchelki/1000)+1) * 45.0
        koszt_wkrety = (int(wkret_25/1000)+1) * baza_mat_gk["Wkrety TN25 (1000szt)"]
        koszt_masy = worki_masy * baza_masy_gk[wybrana_masa]
        
        total_material = koszt_plyt + koszt_profile + koszt_akcesoria + koszt_welny + koszt_masy + koszt_pchelki + koszt_wkrety + koszt_tasm
        robocizna = m2_gk * stawka_gk

        
            # --- 3. WYŚWIETLANIE (PRAWA KOLUMNA) ---
        with col_g2:
            st.subheader("💰 Podsumowanie")
            st.success(f"### RAZEM: **{round(total_material + robocizna)} zł**")
            
            with st.expander("📦 LISTA ZAKUPÓW", expanded=True):
                if rodzaj_gk == "Sufit Podwieszany":
                    st.write(f"• Profile CD60: {szt_cd} szt.")
                    st.write(f"• Profile UD27: {szt_ud} szt.")
                    st.write(f"• Wieszaki: {szt_wieszaki} szt.")
                    if laczniki_krzyzowe > 0: st.write(f"• Łączniki krzyżowe: {laczniki_krzyzowe} szt.")
                else:
                    st.write(f"• Profile CW{szer_profilu}: {szt_cw} szt.")
                    st.write(f"• Profile UW{szer_profilu}: {szt_uw} szt.")
                
                st.write(f"• Płyty GK (120x240): {szt_plyt} szt.")
                st.write(f"• Wkręty TN25: {int(wkret_25/1000)+1} op. (1000szt)")
                st.write(f"• Wkręty Pchełki LN: {int(szt_pchelki/1000)+1} op. (1000szt)")
                
                if mb_tuff > 0: st.write(f"• Taśma Tuff-Tape: {int(mb_tuff/30)+1} rolka (30mb)")
                if mb_fliz > 0: st.write(f"• Flizelina: {int(mb_fliz/25)+1} rolka (25mb)")
                
                st.write(f"• Masa ({wybrana_masa}): {worki_masy} worki/wiadra")
                if izolacja_gk: st.write(f"• Wełna ({grubosc_welny}mm): {round(m2_gk, 1)} m²")
            
# --- SEKCJA: ELEKTRYKA ---
elif branza == "⚡ Elektryka":
    st.header("⚡ Instalacja Elektryczna (Mieszkanie)")
    
    # Przeniesienie definicji kolumn do środka elif
    col_e1, col_e2 = st.columns([1, 1.2])

    # --- KONFIGURACJA MAREK OSPRZĘTU ---
    opcje_osprzetu = {
        "Ekonomiczny (np. Simon 10, Adelid)": 12,
        "Standard (np. Simon 54, Legrand Niloe)": 38,
        "Premium (np. Berker R.1, Jung, Gira)": 95
    }

    with col_e1:
        st.subheader("Parametry instalacji")
        m2_mieszkania = st.number_input("Metraż mieszkania (m²):", min_value=10, value=60)
        mnoznik_m2 = m2_mieszkania / 60
        st.markdown("---")
        sugerowane_punkty = int(m2_mieszkania * 0.75)
        n_punktow = st.slider("Liczba punktów (gniazda/włączniki):", 10, 150, sugerowane_punkty) 
        typ_scian = st.radio("Materiał ścian:", ["Gazobeton/Cegła", "Żelbet (Wielka Płyta)"])
        n_punkty_tele = 2
        wybrany_standard = st.selectbox("Marka osprzętu:", list(opcje_osprzetu.keys()), index=1)
        stawka_punkt = st.slider("Stawka montażu osprzętu (zł/szt):", 20, 60, 35)

    # --- OBLICZENIA (Te linie MUSZĄ być idealnie pod 'with') ---
    kabel_25 = 150 * mnoznik_m2
    kabel_15 = 100 * mnoznik_m2
    kabel_4x15 = 30 * mnoznik_m2
    kabel_tv = 30 * mnoznik_m2
    kabel_lan = 50 * mnoznik_m2
    
    szt_mocowania = int((kabel_25 + kabel_15 + kabel_4x15 + kabel_tv + kabel_lan) * 3)
    paczki_mocowania = int(szt_mocowania / 100) + 1
    
    srednia_cena_szt = opcje_osprzetu[wybrany_standard]
    koszt_rozdzielnicy_mat = 1500 

    mat_kable = (kabel_25 * 4.50) + (kabel_15 * 3.20) + (kabel_4x15 * 5.50) + (kabel_tv * 2.80) + (kabel_lan * 3.50)
    mat_osprzet = n_punktow * srednia_cena_szt
    mat_mocowania = paczki_mocowania * 22.0
    
    total_material_e = mat_kable + mat_osprzet + koszt_rozdzielnicy_mat + mat_mocowania

    # ROBOCIZNA (zgodnie z wytycznymi elektryka na 7-10 tys.)
    mnoznik_trudnosci = 1.4 if typ_scian == "Żelbet (Wielka Płyta)" else 1.0
    robocizna_baza = (m2_mieszkania * 90) # Podstawa za mb i bruzdy
    robocizna_osprzet = (n_punktow + n_punkty_tele) * stawka_punkt
    robocizna_rozdzielnica = 1200
    
    total_robocizna_e = (robocizna_baza + robocizna_osprzet + robocizna_rozdzielnica) * mnoznik_trudnosci

    with col_e2:
        st.subheader("💰 Kosztorys Elektryki")
        total_e = total_material_e + total_robocizna_e
        st.success(f"### RAZEM: **{round(total_e)} zł**")
        
        c1, c2 = st.columns(2)
        c1.metric("Materiały", f"{round(total_material_e)} zł")
        c2.metric("Robocizna", f"{round(total_robocizna_e)} zł")

        with st.expander("📦 WYKAZ MATERIAŁÓW DO KUPNA", expanded=True):
            st.write(f"• Kabel 3x2.5 (Gniazda): **{round(kabel_25)} mb**")
            st.write(f"• Kabel 3x1.5 (Światło): **{round(kabel_15)} mb**")
            st.write(f"• Kabel 4x1.5 (Schodowe/Siła): **{round(kabel_4x15)} mb**")
            st.write(f"• Rozdzielnica + 10 bezpieczników (Eaton/Hager): **1 kpl**")
            st.write(f"• Osprzęt: **{n_punktow} szt.** ({wybrany_standard})")
            st.write(f"• Uchwyty mocujące (paczki 100 szt.): **{paczki_mocowania} op.**")
            st.write(f"• Kabel antenowy RG6 (TV): **{round(kabel_tv)} mb**")
            st.write(f"• Kabel LAN kat. 6 (Internet): **{round(kabel_lan)} mb**")
            st.write(f"• Dodatkowe puszki/gniazda LAN/RTV: **{n_punkty_tele} szt.**")
            
            st.warning("⚠️ **UWAGA:** Wycena nie uwzględnia zakupu lamp (oprawy oświetleniowe).")
            st.info("Ilość kabla liczona szacunkowo dla instalacji prowadzonej w tynku/podłogach.")

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

elif branza == "🚀 PANEL INWESTORA (PREMIUM)":
    st.title("🚀 Szybki Kosztorys Inwestorski (All-in-One)")
    st.info("Opcja dla firm i flipperów: Pełna wycena całego remontu na jednym ekranie.")

    # --- 1. DANE WEJŚCIOWE ---
    col_inv1, col_inv2 = st.columns([1, 1.5])
    
    with col_inv1:
        m2_total = st.number_input("Metraż mieszkania (m2):", min_value=1.0, value=50.0)
        standard = st.select_slider("Standard wykończenia:", options=["Ekonomiczny", "Standard", "Premium"])
        stan_lokalu = st.radio("Stan lokalu:", ["Deweloperski", "Do remontu (Rynek wtórny)"])
        
        st.markdown("---")
        st.subheader("Wybierz zakres prac:")
        do_elektryka = st.checkbox("Instalacja elektryczna", value=True)
        do_tynki = st.checkbox("Tynkowanie ścian", value=False)
        do_gladzie = st.checkbox("Gładzie i szlifowanie", value=True)
        do_podlogi = st.checkbox("Podłogi (panele/listwy)", value=True)
        do_lazienka = st.checkbox("Łazienka (płytki/biały montaż)", value=True)
        do_drzwi = st.checkbox("Drzwi wewnętrzne", value=True)
        do_malowanie = st.checkbox("Malowanie końcowe", value=True)

    # --- 2. LOGIKA MATEMATYCZNA (Uśredniona na m2) ---
    # Ceny za m2 robocizna + materiał zależnie od standardu
    mnoznik = 1.0 if standard == "Standard" else (0.75 if standard == "Ekonomiczny" else 1.5)
    dodatek_wtórny = 1.2 if stan_lokalu == "Do remontu (Rynek wtórny)" else 1.0

    koszty = {}
    if do_elektryka: koszty["Elektryka"] = m2_total * 120 * mnoznik
    if do_tynki: koszty["Tynki"] = (m2_total * 3.5) * 65 * mnoznik
    if do_gladzie: koszty["Gładzie"] = (m2_total * 3.5) * 55 * mnoznik
    if do_podlogi: koszty["Podłogi"] = m2_total * 160 * mnoznik
    if do_lazienka: koszty["Łazienka"] = 15000 * mnoznik * dodatek_wtórny # stała na 1 łazienkę
    if do_drzwi: koszty["Drzwi"] = (m2_total // 12 + 1) * 1200 * mnoznik # średnio 1 para na 12m2
    if do_malowanie: koszty["Malowanie"] = (m2_total * 3.5) * 45 * mnoznik

    # --- 3. WYNIKI I LOGISTYKA ---
    with col_inv2:
        st.subheader(f"📊 Budżet Remontowy: {standard}")
        total_sum = sum(koszty.values())
        
        st.success(f"### SZACOWANY KOSZT CAŁOŚCI: **{round(total_sum)} zł**")
        
        # ZBIORCZA LISTA ZAKUPÓW (Zsumowana z wybranych etapów)
        with st.expander("📦 ZBIORCZA LISTA MATERIAŁÓW (Całe mieszkanie)", expanded=True):
            col_z1, col_z2 = st.columns(2)
            
            with col_z1:
                if do_tynki:
                    st.write("🏗️ **Tynki:**")
                    st.write(f"- Tynk maszynowy: {int((m2_total*3.5*15/30)+1)} worków")
                    st.write(f"- Grunt kwarcowy: {int((m2_total*3.5*0.3/20)+1)} wiadra")
                
                if do_gladzie:
                    st.write("🧱 **Gładzie:**")
                    st.write(f"- Masa gotowa: {int((m2_total*3.5*2/20)+1)} wiader 20kg")
                    st.write(f"- Narożniki: {round(m2_total*0.8)} szt.")

                if do_podlogi:
                    st.write("📐 **Podłogi:**")
                    st.write(f"- Panele (+7%): {int((m2_total*1.07/2.22)+1)} paczek")
                    st.write(f"- Listwy (2.5m): {int((m2_total*0.8/2.5)+1)} szt.")

            with col_z2:
                if do_malowanie:
                    st.write("🎨 **Malowanie:**")
                    st.write(f"- Farba biała: {int((m2_total*1.0/10*2)/10+1)} wiadra 10L")
                    st.write(f"- Farba kolor: {int((m2_total*2.5/10*2)/5+1)} puszek 5L")
                
                if do_drzwi:
                    st.write("🚪 **Stolarka:**")
                    st.write(f"- Komplety drzwiowe: {int(m2_total//12 + 1)} szt.")
                    st.write(f"- Pianka montażowa: {int((m2_total//12 + 1)/2 + 1)} szt.")

                if do_lazienka:
                    st.write("🚿 **Łazienka:**")
                    st.write("- Płytki (podłoga+ściany): ok. 25 m2")
                    st.write("- Zestaw hydroizolacji: 1 kpl.")

        st.markdown("---")
        # --- RAPORT OPŁACALNOŚCI (Twoja propozycja ROI) ---
        st.subheader("💼 Kalkulator ROI (Zwrot z Inwestycji)")
        c_inv_a, c_inv_b = st.columns(2)
        cena_zakupu = c_inv_a.number_input("Cena zakupu nieruchomości:", value=350000, step=5000)
        cena_sprzedazy = c_inv_b.number_input("Przewidywana cena sprzedaży:", value=520000, step=5000)
        
        podatek = (cena_sprzedazy - cena_zakupu - total_sum) * 0.19
        zysk_netto = cena_sprzedazy - cena_zakupu - total_sum - (podatek if podatek > 0 else 0)
        
        st.metric("ZYSK NETTO (po remoncie i podatku)", f"{round(zysk_netto)} zł", 
                  delta=f"{round((zysk_netto/cena_zakupu)*100, 1)}% ROI")

# --- 1. DEFINICJA FUNKCJI (Przepis) ---
        from fpdf import FPDF
        import base64

        def create_pdf(koszty_dict, total, metraz, std, lista_tekst):
            def pl_to_en(text):
                pl = "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ"
                en = "acelnoszzACELNOSZZ"
                for p, e in zip(pl, en):
                    text = text.replace(p, e)
                return text

            pdf = FPDF()
            pdf.add_page()
            
            # Nagłówek
            pdf.set_font("Arial", "B", 16)
            pdf.cell(200, 10, pl_to_en("KOSZTORYS INWESTORSKI - RAPORT"), ln=True, align='C')
            pdf.set_font("Arial", "", 12)
            pdf.cell(200, 10, pl_to_en(f"Metraz: {metraz} m2 | Standard: {std}"), ln=True, align='C')
            pdf.ln(10)
            
            # Tabela kosztów robocizny/etapów
            pdf.set_font("Arial", "B", 12)
            pdf.cell(200, 10, pl_to_en("1. PODSUMOWANIE ETAPOW (Robocizna + Material):"), ln=True)
            pdf.set_font("Arial", "", 11)
            for k, v in koszty_dict.items():
                pdf.cell(100, 10, pl_to_en(f"- {k}:"), border=1)
                pdf.cell(90, 10, f"{round(v)} zl", border=1, ln=True)
            
            pdf.set_font("Arial", "B", 11)
            pdf.cell(100, 10, pl_to_en("SUMA CALKOWITA:"), border=1)
            pdf.cell(90, 10, f"{round(total)} zl", border=1, ln=True)
            
            # --- NOWA SEKCJA: LISTA ZAKUPÓW ---
            pdf.ln(10)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(200, 10, pl_to_en("2. SZCZEGOLOWA LISTA ZAKUPOW:"), ln=True)
            pdf.set_font("Arial", "", 10)
            
            # Rozbijamy tekst listy na linie i dodajemy do PDF
            for linia in lista_tekst.split('\n'):
                if linia.strip():
                    pdf.multi_cell(190, 7, pl_to_en(linia))
            
            return pdf.output(dest="S").encode("latin-1")

        # Przygotowanie tekstu listy zakupów do PDF
        tekst_listy = ""
        if do_tynki: tekst_listy += f"Tynki: {int((m2_total*3.5*15/30)+1)} workow, {int((m2_total*3.5*0.3/20)+1)} wiadra gruntu\n"
        if do_gladzie: tekst_listy += f"Gladzie: {int((m2_total*3.5*2/20)+1)} wiader, {round(m2_total*0.8)} szt. naroznikow\n"
        if do_podlogi: tekst_listy += f"Podlogi: {int((m2_total*1.07/2.22)+1)} paczek paneli, {int((m2_total*0.8/2.5)+1)} szt. listew\n"
        if do_malowanie: tekst_listy += f"Malowanie: {int((m2_total*1.0/10*2)/10+1)} wiader bialej, {int((m2_total*2.5/10*2)/5+1)} puszek koloru\n"

        # Przycisk generowania
        if st.button("📄 Generuj Raport z Lista Zakupow"):
            pdf_data = create_pdf(koszty, total_sum, m2_total, standard, tekst_listy)
            b64 = base64.b64encode(pdf_data).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="kosztorys_pelny.pdf" style="text-decoration:none; background-color:#4CAF50; color:white; padding:10px; border-radius:5px;">📥 POBIERZ PELNY KOSZTORYS PDF</a>'
            st.markdown(href, unsafe_allow_html=True)
