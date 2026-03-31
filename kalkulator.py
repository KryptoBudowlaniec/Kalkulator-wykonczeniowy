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
    branza = st.selectbox("Wybierz rodzaj prac:", 
        ["🎨 Malowanie", "🧱 Szpachlowanie", "📐 Podłogi (Panele/Deska)", "🚿 Łazienka"])
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
            
        margines = 0.10 # 10% widełek
        k_mat_sredni = (l_biala * baza_biale[f_biala]) + (l_kolor * baza_kolory[f_kolor]) + \
                       (l_grunt * baza_grunty[f_grunt]) + (szt_tasma * baza_tasmy[f_tasma]) + 150
        
        k_mat_min = k_mat_sredni * (1 - margines)
        k_mat_max = k_mat_sredni * (1 + margines)
        k_rob = m2_razem * stawka

        # --- WYŚWIETLANIE WYNIKÓW (Potem pokazujemy!) ---
        with col_f2:
            st.subheader("💰 Przewidywany budżet")
            total_min = k_mat_min + k_rob
            total_max = k_mat_max + k_rob
            
            st.success(f"### RAZEM: **{round(total_min)} - {round(total_max)} zł**")
            st.metric("Twoja Robocizna (Stała)", f"{round(k_rob)} zł")
            st.info(f"**Materiały (widełki):** {round(k_mat_min)} - {round(k_mat_max)} zł")
        
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
            stawka_szp = st.slider("Twoja stawka za m2 (robocizna):", 35, 85, 50)

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
    st.header("Kalkulator Układania Podłóg")
    
    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        m2_p = st.number_input("Metraż podłogi (m2):", min_value=0.1, value=20.0, step=0.1)
        typ_ukladania = st.selectbox("Sposób układania:", ["Zwykły panel (7% zapasu)", "Jodełka (20% zapasu)"])
        m2_w_paczce = st.number_input("M2 w paczce paneli:", min_value=0.1, value=2.22, step=0.01)
        
        st.markdown("---")
        typ_podkladu = st.selectbox("Rodzaj podkładu:", ["Premium (Rolka 8m2)", "Ecopor (Paczka 7m2)"])
        
        st.markdown("---")
        typ_listwy = st.selectbox("Rodzaj listew:", ["MDF (Cięcie 45°)", "PCV (Z akcesoriami)"])
        n_naroznikow = st.number_input("Liczba narożników/łączników (tylko dla PCV):", min_value=0, value=4)

    # --- LOGIKA PODŁOGI ---
    zapas = 0.07 if "Zwykły" in typ_ukladania else 0.20
    pow_z_zapasem = m2_p * (1 + zapas)
    paczki_szt = pow_z_zapasem / m2_w_paczce
    
    wyd_podkladu = 8 if "Premium" in typ_podkladu else 7
    podklad_szt = m2_p / wyd_podkladu
    
    # Obliczanie listew (obwód + zapas 10%)
    mb_listew = (4 * (m2_p**0.5)) * 1.1 
    szt_listew_25m = mb_listew / 2.5 # Listwy mają zazwyczaj 2.5m

    with col_p2:
        st.subheader("📦 Lista zakupów")
        st.write(f"• **Panele:** {int(paczki_szt + 0.99)} paczek ({round(pow_z_zapasem, 1)} m2)")
        st.write(f"• **Podkład ({typ_podkladu}):** {int(podklad_szt + 0.99)} szt.")
        st.write(f"• **Listwy (2.5m):** {int(szt_listew_25m + 0.99)} szt. ({round(mb_listew, 1)} mb)")
        
        if typ_listwy == "PCV (Z akcesoriami)":
            st.info(f"Pamiętaj o zakupie {n_naroznikow} szt. akcesoriów (narożniki/łączniki).")
        else:
            st.warning("Wybrano MDF: Pamiętaj o kleju montażowym i akrylu do wykończenia.")

        # --- WYCENA ROBOCIZNY ---
        cena_m = 25 if "Zwykły" in typ_ukladania else 65 # Jodełka droższa
        st.metric("Szacowana robocizna", f"{round(m2_p * cena_m + mb_listew * 15)} zł")
