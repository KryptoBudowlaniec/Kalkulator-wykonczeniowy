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
    
    with tab_fast:
        st.header("⚡ Szybki szacunek materiałów i robocizny")
    
    col_f1, col_f2 = st.columns([1, 2])
    
    with col_f1:
        m_uzytkowy = st.number_input("Metraż mieszkania (m2):", min_value=0.0, value=50.0, key="fast_m")
        stan_f = st.selectbox("Stan lokalu:", ["Deweloperski", "Zamieszkały (meble)"], key="fast_s")
        std_f = st.selectbox("Standard materiałów:", ["Ekonomiczny", "Premium"], key="fast_std")

    # --- LOGIKA SZYBKIEJ WYCENY ---
    m2_sufit = m_uzytkowy * 1.0
    m2_sciany = m_uzytkowy * 2.5
    m2_razem = m2_sufit + m2_sciany
    mnoznik = 1.0 if stan_f == "Deweloperski" else 1.3
    
    # Ceny jednostkowe dla szybkiej wyceny
    ceny_f = {
        "Ekonomiczny": {"sufit": 15, "sciany": 24, "grunt": 5, "tasma": 12, "robocizna": 18},
        "Premium": {"sufit": 35, "sciany": 58, "grunt": 14, "tasma": 28, "robocizna": 20}
    }
    cf = ceny_f[std_f]

    # Obliczenia ilości
    l_biala = (m2_sufit / 10) * 2
    l_kolor = (m2_sciany / 10) * 2
    l_grunt = m2_razem * 0.1
    szt_tasma = (m_uzytkowy / 15) * mnoznik
    opk_folia = (m_uzytkowy / 20) * mnoznik

    # Obliczenia kosztów
    koszt_mat = (l_biala * cf["sufit"]) + (l_kolor * cf["sciany"]) + (l_grunt * cf["grunt"]) + (szt_tasma * cf["tasma"]) + 100
    koszt_rob = m2_razem * cf["robocizna"]

    with col_f2:
        st.subheader("💰 Podsumowanie finansowe")
        c1, c2 = st.columns(2)
        c1.metric("Materiały", f"{round(koszt_mat)} zł")
        c2.metric("Robocizna", f"{round(koszt_rob)} zł")
        st.metric("RAZEM DO ZAPŁATY", f"{round(koszt_mat + koszt_rob)} zł")
        
        with st.expander("📦 Lista zakupów (Szacunkowa)"):
            st.write(f"• **Farba BIAŁA (sufity):** {round(l_biala)} L")
            st.write(f"• **Farba KOLOR (ściany):** {round(l_kolor)} L")
            st.write(f"• **Grunt:** {round(l_grunt)} L")
            st.write(f"• **Taśma malarska:** {round(szt_tasma + 0.4)} szt.")
            st.write(f"• **Folia ochronna:** {round(opk_folia + 0.4)} szt.")
            st.caption(f"Wyliczenia dla {round(m2_razem)} m2 powierzchni malowania.")
        st.write("Szybki szacunek malowania...")
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

# --- SEKCJA: SZPACHLOWANIE ---
elif branza == "🧱 Szpachlowanie":
    st.header("Kalkulator Gładzi i Przygotowania Ścian")
    tab_s1, tab_s2 = st.tabs(["⚡ Szybka Wycena", "💎 Detale PRO"])

    with tab_s1:
        m2_podl = st.number_input("Metraż podłogi (m2):", min_value=0.0, value=50.0, key="szp_m")
        warstwy = st.slider("Liczba warstw gładzi:", 1, 3, 2)
        typ_gladzi = st.selectbox("Rodzaj gładzi:", ["Sypka (do rozrobienia)", "Gotowa (w wiadrze)"])


        
        # --- LOGIKA SZPACHLOWANIA ---
        m2_scian = m2_podl * 3.5
        # Zużycie: ok 2kg/m2 na warstwę (gotowa) lub 1.5kg/m2 (sypka)
        norma = 1.2 if typ_gladzi == "Sypka (do rozrobienia)" else 2
        kg_razem = m2_scian * norma * warstwy
        
        # Opakowania
        waga_opk = 20 if typ_gladzi == "Sypka (do rozrobienia)" else 18
        szt_opk = kg_razem / waga_opk

# --- CENNIK MATERIAŁÓW SZPACHLARSKICH ---
        ceny_mat = {
            "Sypka (do rozrobienia)": 65,  # cena za worek 20kg (np. Cekol/Knauf)
            "Gotowa (w wiadrze)": 95       # cena za wiadro 18-20kg (np. Śmig/Sheetrock)
        }
        cena_opk = ceny_mat[typ_gladzi]
        
        # Koszty dodatków
        koszt_naroznikow = (m2_podl * 0.8 / 2.5) * 12  # ok. 12 zł za narożnik z osadzeniem
        koszt_tasmy = (m2_podl * 1.0) * 3               # ok. 3 zł za mb taśmy (rolka 30m ok. 90-100 zł)
        koszt_gruntu = (m2_scian * 0.15) * 6            # ok. 6 zł za litr gruntu
        
        suma_material_szp = (szt_opk * cena_opk) + koszt_naroznikow + koszt_tasmy + koszt_gruntu

        # --- WYŚWIETLANIE FINANSÓW ---
        st.markdown("---")
        st.subheader("💰 Kosztorys Szpachlowania")
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            st.metric("Koszt materiałów", f"{round(suma_material_szp)} zł")
            st.caption(f"W tym gładź ({typ_gladzi}): {round(szt_opk * cena_opk)} zł")
            
        with col_f2:
            # Zakładamy 45 zł/m2 za robociznę (grunt + 2x gładź + szlifowanie)
            koszt_rob_szp = m2_scian * 45
            st.metric("Robocizna (45 zł/m2)", f"{round(koszt_rob_szp)} zł")
            
        st.success(f"**ŁĄCZNY KOSZT ETAPU: {round(suma_material_szp + koszt_rob_szp)} zł**")
        
        # Finanse
        cena_rob_szp = 45 # zł/m2 za kompleks (grunt + 2x gładź + szlif)

        # --- ZAKRES PRAC (Co płaci klient) ---
        with st.expander("🛠️ Zobacz co wchodzi w cenę robocizny:"):
            # Możemy rozbić stawkę 45 zł na etapy (szacunkowo)
            st.write(f"1. **Gruntowanie wstępne:** przygotowanie podłoża")
            st.write(f"2. **Szpachlowanie ({warstwy} warstwy):** nałożenie masy")
            st.write(f"3. **Szlifowanie mechaniczne:** wyrównanie powierzchni")
            st.write(f"4. **Odpylanie:** przygotowanie pod malowanie")
            st.write(f"5. **Gruntowanie końcowe:** stabilizacja gładzi")
            st.info(f"Łączna powierzchnia prac: {round(m2_scian)} m²")

        # --- DODATKOWY SMACZEK: CZAS PRACY ---
        # Zakładamy, że jeden fachowiec robi ok. 50 m2 "na gotowo" dziennie (ze schnięciem)
        dni_pracy = m2_scian / 50
        st.warning(f"⏳ Przewidywany czas realizacji: ok. **{round(dni_pracy + 0.5)} dni** roboczych.")
        
        c_s1, c_s2 = st.columns(2)
        with c_s1:
            st.metric("Powierzchnia szpachlowania", f"{round(m2_scian)} m2")
            st.metric("Potrzebna gładź (łącznie)", f"{round(kg_razem)} kg")
        
        with c_s2:
            st.metric("Liczba opakowań", f"{round(szt_opk + 0.4)} szt.")
            st.metric("Robocizna szacowana", f"{round(m2_scian * cena_rob_szp)} zł")

        with st.expander("📦 Co musisz kupić?"):
            st.write(f"• **Gładź {typ_gladzi}:** {round(szt_opk + 0.4)} opk. po {waga_opk}kg")
            st.write(f"• **Grunt głęboki:** {round(m2_scian * 0.15)} L")
            st.write(f"• **Narożniki aluminiowe:** ok. {round(m2_podl * 0.8 / 2.5)} szt. (2.5mb)")
            st.write(f"• **Papier ścierny (rolka/opk):** {round(m2_scian / 40 + 0.4)} szt.")

    with tab_s2:
        st.info("Tutaj możesz połączyć dane z modułu malarskiego, aby precyzyjnie wyliczyć gładź na każdą ścianę z osobna.")
        # Tutaj w przyszłości dodamy listę konkretnych ścian



# --- SEKCJA: PODŁOGI ---
elif branza == "📐 Podłogi (Panele/Deska)":
    st.header("Kalkulator Podłóg")
    col1, col2 = st.columns(2)
    with col1:
        m2_podlogi = st.number_input("Powierzchnia podłogi (m2):", min_value=0.0)
        zapas = st.slider("Zapas na dylatacje/docinki (%)", 5, 20, 10)
    
    suma_podloga = m2_podlogi * (1 + zapas/100)
    st.metric("Potrzebny materiał (z zapasem)", f"{round(suma_podloga, 2)} m2")
