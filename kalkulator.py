import streamlit as st
import math
import os
from supabase import create_client, Client
import time
import streamlit.components.v1 as components

# 1. KONFIGURACJA GŁÓWNA (SEO i Favicon)
st.set_page_config(
    page_title="ProCalc | Profesjonalny Kalkulator Budowlany",
    page_icon="logo2.png",  # To ustawi ikonkę na karcie przeglądarki
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://procalc.pl/kontakt',
        'Report a bug': "mailto:biuro@procalc.pl",
        'About': "# ProCalc\nTwój cyfrowy kosztorysant wykończeniowy. Oblicz materiały z precyzją fachowca."
    }
)
# --- ZAAWANSOWANE SEO (Meta Tagi) ---
st.markdown(
    """
<meta name="description" content="ProCalc - Profesjonalny kalkulator remontowy dla Inwestorów i Ekip. Precyzyjne listy materiałowe, kosztorysy PDF i analiza ROI flippów.">
<meta name="keywords" content="kalkulator remontowy, kosztorys wykończenia, wycena remontu, kalkulator malowania, kalkulator szpachlowania, ROI flip, budowa, wykończenia">
<meta property="og:title" content="ProCalc | Profesjonalny Kalkulator Budowlany">
<meta property="og:description" content="Oblicz materiały i robociznę z dokładnością do jednego worka. Pobieraj raporty PDF i zarządzaj budżetem.">
<meta property="og:image" content="https://raw.githubusercontent.com/KryptoBudowlaniec/Kalkulator-wykonczeniowy/main/logo2.png">
<meta property="og:url" content="https://procalc.pl">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="ProCalc | Twój Cyfrowy Kosztorysant">
<meta name="twitter:description" content="Koniec z błędami w zamówieniach materiałów. Precyzyjne obliczenia w 30 sekund.">
    """,
    unsafe_allow_html=True
)

# ==========================================
# 🟢 BANER COOKIES I PRYWATNOŚCI (PRZYWRÓCONY)
# ==========================================
if "cookies_accepted" not in st.session_state:
    st.session_state.cookies_accepted = False

if not st.session_state.cookies_accepted:
    with st.container(border=True):
        st.markdown("### 🍪 Szanujemy Twoją prywatność")
        st.write("""
        Serwis ProCalc wykorzystuje pliki cookies niezbędne do prawidłowego działania aplikacji (utrzymywanie sesji logowania, zapisywanie projektów) oraz w celach analitycznych. 
        Dalsze korzystanie z serwisu oznacza akceptację naszej Polityki Prywatności.
        """)
        col_btn, _ = st.columns([1, 3])
        with col_btn:
            if st.button("Zrozumiałem i Akceptuję ✅", type="primary", use_container_width=True, key="btn_cookies"):
                st.session_state.cookies_accepted = True
                st.rerun() 
    st.markdown("---")

# ==========================================
# 2. POŁĄCZENIE Z BAZĄ DANYCH (SECURE)
# ==========================================
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
except KeyError:
    st.error("⚠️ Brak kluczy bazy danych! Skonfiguruj zakładkę 'Secrets' w ustawieniach Streamlit Cloud.")
    st.stop()

supabase: Client = None
try:
    supabase = create_client(url, key)
except Exception as e:
    st.error(f"Błąd inicjalizacji Supabase: {e}")
    st.stop()

# ========================================================
# PODTRZYMANIE AUTORYZACJI SUPABASE (Naprawa błędu RLS)
# ========================================================
if supabase and "access_token" in st.session_state and "refresh_token" in st.session_state:
    try:
        supabase.auth.set_session(st.session_state.access_token, st.session_state.refresh_token)
    except Exception:
        pass

# ==========================================
# 3. STAN APLIKACJI (INICJALIZACJA)
# ==========================================
if 'zalogowany' not in st.session_state:
    st.session_state.zalogowany = False # <--- ZMIENIONE NA FALSE (Prawdziwe zabezpieczenie)
if 'pakiet' not in st.session_state:
    st.session_state.pakiet = "Podstawowy"
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
if 'refresh_token' not in st.session_state:
    st.session_state.refresh_token = None
if 'przekierowanie' not in st.session_state:
    st.session_state.przekierowanie = False

# =======================================================
# 4. KULOODPORNY ŁAPACZ SESJI (BEZ WYLOGOWYWANIA)
# =======================================================
st.components.v1.html("""
    <script>
        const h = window.parent.location.hash;
        if (h.includes("access_token=")) {
            const newUrl = window.parent.location.href.split('#')[0] + "?" + h.substring(1);
            window.parent.location.replace(newUrl);
        }
    </script>
""", height=0)

# Jeśli mamy tokeny w URL (Właśnie wracamy z Google)
try:
    q = st.query_params
    acc_token = q.get("access_token")
    ref_token = q.get("refresh_token")
except:
    q = st.experimental_get_query_params()
    acc_token = q.get("access_token", [None])[0]
    ref_token = q.get("refresh_token", [None])[0]

# SYTUACJA A: Logowanie z Google
if acc_token and ref_token:
    try:
        if supabase:
            supabase.auth.set_session(acc_token, ref_token)
            user_res = supabase.auth.get_user()
            if user_res and user_res.user:
                st.session_state.user_email = user_res.user.email
                st.session_state.user_id = user_res.user.id  
                st.session_state.access_token = acc_token
                st.session_state.refresh_token = ref_token
                
        st.session_state.zalogowany = True
        st.session_state.pakiet = "PRO"
        
        st.query_params.clear()
        st.success("Autoryzacja udana! Wczytuję panel PRO...")
        time.sleep(1)
        st.rerun()
        st.stop()
    except Exception:
        pass

# SYTUACJA B: PODTRZYMANIE SESJI
elif st.session_state.get("zalogowany") == True:
    st.session_state.pakiet = "PRO"
    # Dodajemy zabezpieczenie: jeśli user_id zniknął, a mamy sesję w Supabase, spróbuj go odzyskać
    if not st.session_state.get("user_id") and supabase:
        try:
            user_res = supabase.auth.get_user()
            if user_res and user_res.user:
                st.session_state.user_id = user_res.user.id
        except:
            pass



# =======================================================
# --- HEADER: LOGO LEWA | MENU PRAWA ---
col_logo, col_nav = st.columns([1.5, 2.5]) 

with col_logo:
    try:
        st.image("logo2.png", use_container_width=True)
    except:
        st.error("Brak logo2.png")

with col_nav:
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    

    nawigacja = st.pills(
        "", 
        ["Start", "Kalkulatory", "Panel Inwestora", "Harmonogram", "Kontakt", "Logowanie"],
        selection_mode="single",
        default="Start", 
        key="main_nav"
    )
    st.markdown('</div>', unsafe_allow_html=True)
# --- LOGIKA NAWIGACJI ---
if st.session_state.przekierowanie:
    branza = "Logowanie"
else:
    branza = nawigacja

# --- OBSŁUGA PODMENU KALKULATORY ---
if nawigacja == "Kalkulatory":
    st.markdown("<br>", unsafe_allow_html=True)
    # Wyświetlamy pillsy tylko w sekcji kalkulatorów
    wybor_kalkulatora = st.pills(
        "Wybierz branżę:", 
        ["Malowanie", "Szpachlowanie", "Tynkowanie", "Sucha Zabudowa", "Elektryka", "Łazienka", "Podłogi", "Drzwi", "Efekty Dekoracyjne","Tapetowanie"],
        selection_mode="single",
        default="Malowanie",
        key="sub_nav"
    )
    branza = wybor_kalkulatora


# --- STYLE CSS (Twoje, nietknięte!) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif !important; }
    .stApp { background-color: #FFFFFF !important; color: #1E1E1E !important; }
    li::before { content: none !important; display: none !important; }
    [data-testid="stMarkdownContainer"] ul, [data-testid="stMarkdownContainer"] li { list-style-type: none !important; padding-left: 0px !important; margin-left: 0px !important; }
    .custom-card { background-color: #FFFFFF !important; border: 1px solid #E9ECEF !important; border-radius: 12px !important; padding: 20px !important; margin-bottom: 15px !important; display: flex !important; flex-direction: column !important; align-items: center !important; justify-content: flex-start !important; text-align: center !important; gap: 12px !important; height: 100% !important; min-height: 240px !important; transition: 0.3s; }
    .custom-card:hover { transform: translateY(-5px) !important; border-color: #00D395 !important; box-shadow: 0px 8px 20px rgba(0, 211, 149, 0.1) !important; }
    .card-title { color: #00D395 !important; font-size: 18px !important; font-weight: 800 !important; text-transform: uppercase !important; margin: 0 !important; padding: 0 !important; }
    .card-text { color: #6C757D !important; font-size: 14px !important; margin: 0 !important; padding: 0 !important; line-height: 1.4 !important; }
    .card-list { display: block !important; text-align: center !important; padding: 0 !important; margin: 0 auto !important; border: none !important; width: 100% !important; }
    .card-list li { font-size: 13px !important; color: #495057 !important; margin-bottom: 6px !important; display: block !important; font-weight: 600 !important; text-align: center !important; }
    .card-list li::before { content: "✔ " !important; color: #00D395 !important; font-weight: bold !important; margin-right: 5px !important; }
    .pricing-card { background-color: #FFFFFF; border: 2px solid #E9ECEF; border-radius: 15px; padding: 30px 20px; text-align: center; height: 100%; transition: 0.3s; position: relative; }
    .pricing-pro { border-color: #00D395; background-color: #F0FFF4; box-shadow: 0px 10px 30px rgba(0, 211, 149, 0.15); }
    .pricing-badge { position: absolute; top: -15px; left: 50%; transform: translateX(-50%); background-color: #00D395; color: white; padding: 5px 15px; border-radius: 20px; font-size: 12px; font-weight: bold; text-transform: uppercase; white-space: nowrap; }
    .pricing-price { font-size: 42px; font-weight: 800; color: #1E1E1E; margin: 15px 0 5px 0; }
    .pricing-sub { font-size: 13px; color: #6C757D; margin-bottom: 20px; min-height: 35px; }
    .faq-card-question { background: #FFF; border: 2px solid #00D395; border-radius: 15px 15px 0 0; padding: 20px; font-weight: 800; text-align: center; margin-top: 20px;}
    .faq-card-answer, .faq-card-answer-blue { background: #00D395; border-radius: 0 0 15px 15px; padding: 20px; color: #FFF !important; text-align: center; margin-bottom: 20px;}
    .faq-card-answer-blue { background: #0E172B; }
    div.stButton > button { background-color: #00D395 !important; color: white !important; font-weight: 800 !important; height: 60px !important; border-radius: 15px !important; width: 100%; }
       
    /* 1. Globalna czcionka */
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; }
    
    /* 2. NAPRAWA IKON: Przywracamy czcionkę dla ikon Streamlita */
    span.material-symbols-rounded, 
    [data-testid="stIconMaterial"], 
    i {
        font-family: 'Material Symbols Rounded' !important;
    }
    
    /* 3. CAŁKOWITE UKRYCIE STRZAŁKI W EXPANDERZE */
    [data-testid="stExpander"] summary span.material-symbols-rounded,
    [data-testid="stExpander"] summary [data-testid="stIconMaterial"] {
        display: none !important;
        font-size: 0px !important;
        color: transparent !important;
    }
    [data-testid="stExpander"] summary {
        list-style: none !important; 
        display: flex !important;
    }
    [data-testid="stExpander"] summary::-webkit-details-marker {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# GLOBALNY PANEL BOCZNY (Dla zalogowanych)
# ==========================================
opcja_boczna = "Nawigacja Główna" # Domyślnie
if st.session_state.zalogowany:
    with st.sidebar:
        st.title("Panel Zarządzania")
        st.markdown(f"Konto: **{st.session_state.user_email}**")
        
        # Rozbudowane menu SaaS
        opcja_boczna = st.radio(
            "Menu Konta",
            ["Nawigacja Główna", "Mój Profil", "Moja Subskrypcja", "Bezpieczeństwo", "Język i Region"],
            key="globalny_sidebar"
        )
        
        st.markdown("---")
        if st.button("Wyloguj się", key="btn_wyloguj_global"):
            st.session_state.zalogowany = False
            st.session_state.pakiet = "Podstawowy"
            if supabase: supabase.auth.sign_out()
            st.rerun()

# ==========================================
# NADPISYWANIE WIDOKU PRZEZ PANEL BOCZNY
# ==========================================
if st.session_state.zalogowany and opcja_boczna == "Mój Profil":
    st.header("Mój Profil i Dane Firmy")
    st.write("Uzupełnij dane, które będą używane do wystawiania faktur oraz na nagłówkach Twoich kosztorysów PDF.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Imię i Nazwisko / Nazwa Firmy")
        st.text_input("NIP (Opcjonalnie)")
        st.text_input("Adres kontaktowy")
    with c2:
        st.number_input("Domyślny narzut na materiały (%)", value=10)
        st.number_input("Twoja bazowa stawka za roboczogodzinę (PLN/h)", value=60)
        st.text_input("Numer telefonu (do kosztorysów)")
        
    if st.button("Zapisz ustawienia profilu", type="primary"):
        st.success("Zapisano zmiany w profilu!")

elif st.session_state.zalogowany and opcja_boczna == "Moja Subskrypcja":
    st.header("Zarządzanie Subskrypcją ")
    
    col_sub1, col_sub2 = st.columns([2, 1])
    with col_sub1:
        st.info(f"Twój obecny pakiet: **Premium {st.session_state.pakiet}**")
        st.write("Konto aktywne i opłacone.")
        st.write("Twoja subskrypcja odnawia się automatycznie: **12.11.2024**")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("Zarządzaj kartą płatniczą (Stripe)")
        st.button("Pobierz ostatnie faktury")
        
    with col_sub2:
        st.markdown("""
        <div style="border: 1px solid #E9ECEF; border-radius: 10px; padding: 20px; text-align: center;">
            <p style="margin-bottom: 5px; color: #6C757D;">Chcesz zrezygnować?</p>
            <button style="background: transparent; border: 1px solid #FF4B4B; color: #FF4B4B; padding: 8px 15px; border-radius: 5px; cursor: pointer; width: 100%;">Anuluj Subskrypcję</button>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.zalogowany and opcja_boczna == "Bezpieczeństwo":
    st.header("Bezpieczeństwo i Logowanie 🔒")
    
    st.subheader("Zmiana hasła")
    st.write("Zalecamy używanie silnego hasła składającego się z minimum 8 znaków.")
    
    col_pw1, col_pw2 = st.columns(2)
    with col_pw1:
        st.text_input("Obecne hasło", type="password")
        nowe_haslo = st.text_input("Nowe hasło", type="password")
        powtorz_haslo = st.text_input("Powtórz nowe hasło", type="password")
        
        if st.button("Zaktualizuj hasło", type="primary"):
            if nowe_haslo and nowe_haslo == powtorz_haslo:
                st.success("Hasło zostało pomyślnie zmienione! (Symulacja)")
                # Docelowo tutaj wejdzie logika: supabase.auth.update_user({"password": nowe_haslo})
            else:
                st.error("Nowe hasła nie są identyczne lub pole jest puste.")

    st.markdown("---")
    st.subheader("Strefa Niebezpieczna")
    with st.expander("Usuwanie konta"):
        st.warning("Usunięcie konta jest nieodwracalne. Utracisz dostęp do wszystkich zapisanych projektów, kosztorysów oraz aktywnej subskrypcji.")
        st.text_input("Aby potwierdzić, wpisz słowo: USUŃ", key="del_confirm")
        st.button("Trwale usuń moje konto", type="secondary")

elif st.session_state.zalogowany and opcja_boczna == "Język i Region":
    st.header("Ustawienia Regionalne 🌍")
    st.selectbox("Wybierz język interfejsu", ["Polski", "English"])
    st.selectbox("Domyślna waluta systemu", ["PLN", "EUR", "USD", "GBP"])
    if st.button("Zapisz ustawienia regionalne"):
        st.success("Zapisano zmiany!")


# ==========================================
# GŁÓWNA LOGIKA WYŚWIETLANIA (IF / ELIF)
# ==========================================
# --- SYSTEM RATUNKOWY DLA ZMIENNEJ NAWIGACJI ---
try:
    _ = branza
except NameError:
    branza = "Logowanie"
    
if branza == "Start":
    # ---------------- EKRAN STARTOWY (Nietknięty!) ----------------
    st.markdown("<h1 style='text-align: center; color: #00D395; font-size: 50px; margin-top: 0; font-weight: 800;'>Witaj w ProCalc</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; font-size: 26px; margin-bottom: 50px; color: #495057;'>Twój Cyfrowy Kosztorysant Wykończeniowy</h3>", unsafe_allow_html=True)
    
    col_c1, col_center, col_c2 = st.columns([1, 4, 1])
    with col_center:
        st.markdown("<h2 style='text-align: center; color: #000000; margin-bottom: 40px; font-weight: 800;'>Dla kogo jest ProCalc?</h2>", unsafe_allow_html=True)
        
        benefity = [
            ["Inwestorzy", "Błyskawiczna analiza ROI i rentowności flipa. Podejmuj decyzje zakupowe w oparciu o twarde dane, a nie intuicję."],
            ["Ekipy Wykonawcze", "Precyzyjne listy materiałowe z dokładnością do jednego worka. Koniec z przestojami, błędami i zbędnymi kursami."],
            ["Klienci Prywatni", "Pełna kontrola nad budżetem remontowym. Wiesz dokładnie, ile zapłacisz za materiał i robociznę."]
        ]

        cols_ben = st.columns(3)
        for i, (tytul, tekst) in enumerate(benefity):
            with cols_ben[i]:
                st.markdown(f'<div class="custom-card"><div class="card-title">{tytul}</div><div class="card-text">{tekst}</div></div>', unsafe_allow_html=True)
        
        st.markdown("<div style='text-align: center; margin-top: 20px;'>", unsafe_allow_html=True)
        _, col_btn_top, _ = st.columns([1, 2, 1])
        with col_btn_top:
            if st.button("ZAŁÓŻ DARMOWE KONTO I ZAPISUJ KOSZTORYSY", use_container_width=True):
                st.info("👆 Aby założyć konto, wybierz zakładkę 'Logowanie' z menu na samej górze strony!")

        st.markdown("<div style='text-align: center; width: 100%; margin-top: 15px;'><p style='font-size: 15px; color: #6c757d; font-weight: 600;'>✅ Rejestracja zajmie Ci 30 sekund. Nie wymaga podpięcia karty płatniczej.</p></div>", unsafe_allow_html=True)

    # ==========================================
    # SEKCJA: JAK TO DZIAŁA (KOLOROWE KAFELKI - KULOODPORNE)
    # ==========================================
    st.markdown("<br><br><h2 style='text-align: center; font-weight: 800;'>Jak to działa? (3 proste kroki)</h2><br>", unsafe_allow_html=True)
    
    col_krok1, col_krok2, col_krok3 = st.columns(3)
    
    with col_krok1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #00D395, #00A876); border-radius: 15px; padding: 30px; text-align: center; color: white; box-shadow: 0 10px 20px rgba(0, 211, 149, 0.2); min-height: 260px; display: flex; flex-direction: column; justify-content: center;">
            <h1 style="color: rgba(255, 255, 255, 0.4); font-size: 70px; margin: 0; line-height: 1;">1</h1>
            <h3 style="color: white; margin: 15px 0 10px 0; font-weight: 800; text-transform: uppercase;">Wybierz zakres</h3>
            <p style="color: white; font-size: 15px; line-height: 1.5; margin: 0;">Wybierz kalkulator z menu (np. Szpachlowanie) i określ parametry startowe oraz rodzaj podłoża.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_krok2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #0E172B, #1A2540); border-radius: 15px; padding: 30px; text-align: center; color: white; box-shadow: 0 10px 20px rgba(14, 23, 43, 0.2); min-height: 260px; display: flex; flex-direction: column; justify-content: center;">
            <h1 style="color: rgba(255, 255, 255, 0.2); font-size: 70px; margin: 0; line-height: 1;">2</h1>
            <h3 style="color: white; margin: 15px 0 10px 0; font-weight: 800; text-transform: uppercase;">Wpisz wymiary</h3>
            <p style="color: white; font-size: 15px; line-height: 1.5; margin: 0;">Podaj metraż podłogi lub dodaj konkretne pomieszczenia. Wybierz materiały z naszej bazy.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_krok3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #00D395, #00A876); border-radius: 15px; padding: 30px; text-align: center; color: white; box-shadow: 0 10px 20px rgba(0, 211, 149, 0.2); min-height: 260px; display: flex; flex-direction: column; justify-content: center;">
            <h1 style="color: rgba(255, 255, 255, 0.4); font-size: 70px; margin: 0; line-height: 1;">3</h1>
            <h3 style="color: white; margin: 15px 0 10px 0; font-weight: 800; text-transform: uppercase;">Gotowe!</h3>
            <p style="color: white; font-size: 15px; line-height: 1.5; margin: 0;">Odbierz kosztorys z wyliczoną robocizną i wygeneruj listę zakupów PDF co do jednego worka.</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("<br><br><h2 style='text-align: center; font-weight: 800;'>Co oferują nasze kalkulatory?</h2>", unsafe_allow_html=True)
    
    oferta = [
        ["Malowanie", "Finalne wykończenie powierzchni.", ["Wydajność farb z bazy", "Obliczanie m2 i zapasów", "Dobór gruntów", "Wycena drobnego sprzętu"]], 
        ["Szpachlowanie", "Przygotowanie gładzi.", ["Masy sypkie i gotowe", "Zbrojenie narożników", "Taśmy flizelinowe", "Oszacowanie dniówek"]],
        ["Tynkowanie", "Prace tynkarskie.", ["Tynki maszynowe i GK", "Listwy i narożniki", "Dokładne zużycie kleju", "Grunty kwarcowe"]],
        ["Sucha Zabudowa", "Konstrukcje GK.", ["Systemy profili CD/UD", "Wyliczanie sztuk płyt", "Zbrojenie łączy (Tuff-Tape)", "Wełna izolacyjna"]],
        ["Elektryka", "Instalacja prądowa.", ["Szacowanie mb przewodów", "Osprzęt i rozdzielnica", "Uchwyty montażowe", "Puszki rtv/lan"]],
        ["Łazienka", "Kompleksowy remont.", ["Płytki (format i zapas)", "Hydroizolacja i taśmy", "Biały montaż (ryczałt)", "Fugi i sylikony"]],
        ["Podłogi", "Panele i winyle.", ["Metraż i odpad (jodełka)", "Listwy i podkłady", "Systemy poziomujące", "Chemia posadzkowa"]],
        ["Drzwi", "Stolarka wewnętrzna.", ["Drzwi bezprzylgowe", "Ościeżnice regulowane", "Pianki montażowe", "Opaski maskujące"]],
        ["Premium PRO", "Dla profesjonalistów.", ["Zapisywanie projektów", "Eksport PDF do hurtowni", "Zarządzanie stawkami", "Analiza ROI (flipy)"]]
    ]

    cols_oferta = st.columns(3)
    for i, item in enumerate(oferta):
        with cols_oferta[i % 3]:
            style_extra = "border: 2px solid #00D395; background-color: #F0FFF4 !important;" if item[0] == "Premium PRO" else ""
            lista_html = "".join([f"<li>{punkt}</li>" for punkt in item[2]])
            st.markdown(f'<div class="custom-card" style="{style_extra}"><div class="card-title">{item[0]}</div><div class="card-text" style="margin-bottom: 10px !important;">{item[1]}</div><ul class="card-list">{lista_html}</ul></div>', unsafe_allow_html=True)

    st.markdown("<div style='text-align: center; width: 100%; padding: 20px;'><p style='font-size: 26px; font-weight: 800; color: #1E1E1E; margin-bottom: 10px;'>GOTOWY DO WYCENY?</p><p style='font-size: 20px; color: #00D395; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;'>Wybierz sekcję z menu bocznego i zacznij liczyć!</p></div>", unsafe_allow_html=True)

    st.markdown("<br><br><h2 style='text-align: center; font-weight: 800;'>Dlaczego warto nam zaufać?</h2><br>", unsafe_allow_html=True)
    zalety = [
        ["NORMY", "Algorytmy oparte na realnych normach zużycia materiałów z kart technicznych."],
        ["DOŚWIADCZENIE", "Aplikacja stworzona przy współpracy z wieloletnimi wykonawcami."],
        ["CENY", "Bazy cenowe aktualizowane na bieżąco według największych hurtowni."],
        ["PRECYZJA", "Zminimalizujesz ryzyko przestojów z powodu braku 1 worka kleju."],
        ["LISTY ZAKUPÓW", "Gotowe raporty dla sklepów oszczędzają Twój czas."],
        ["NIEZALEŻNOŚĆ", "Nie jesteśmy sponsorowani - dobierasz producenta sam."]
    ]
    _, col_main, _ = st.columns([1, 4, 1])
    with col_main:
        sub_l, sub_m, sub_r = st.columns(3) 
        kolumny = [sub_l, sub_m, sub_r, sub_l, sub_m, sub_r]
        for i, (tytul, opis) in enumerate(zalety):
            with kolumny[i]:
                st.markdown(f'<div style="display: flex; flex-direction: column; align-items: center; text-align: center; margin-bottom: 30px; padding: 0 10px;"><div style="color: #00D395; font-size: 28px; margin-bottom: 10px; font-weight: bold; line-height: 1;">✔</div><div style="font-size: 15px; color: #495057; line-height: 1.4;"><b style="color: #1E1E1E; font-size: 16px; display: block; margin-bottom: 5px; text-transform: uppercase;">{tytul}</b><span style="display: block; opacity: 0.8;">{opis}</span></div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
        
    _, col_demo, _ = st.columns([1, 1.5, 1])
    with col_demo:
        if st.button("SPRAWDŹ DARMOWE DEMO (MALOWANIE)", use_container_width=True, key="btn_demo_main"):
            st.info("👆 Wybierz zakładkę 'Kalkulatory' na górze, a następnie 'Malowanie'!")

    st.markdown("<p style='text-align: center; font-size: 14px; color: gray; margin-top: 5px;'>Nie wymaga logowania. Sprawdź jak to działa w 15 sekund.</p>", unsafe_allow_html=True)

    st.markdown("<br><br><h2 style='text-align: center; font-weight: 800;'>Wybierz pakiet dla siebie</h2>", unsafe_allow_html=True)
    _, col_p1, col_p2, col_p3, _ = st.columns([0.5, 3, 3, 3, 0.5])
    with col_p1:
        st.markdown('<div class="pricing-card"><h3 style="color: #1E1E1E; font-weight: 800; margin-bottom: 0;">Podstawowy</h3><div class="pricing-price">0 zł</div><div class="pricing-sub">Zawsze za darmo</div><ul class="card-list" style="margin-top: 10px !important;"><li>Dostęp do Szybkich Wycen</li><li>Podstawowe algorytmy zużycia</li><li>Brak możliwości zapisu projektów</li><li>Brak generatora ofert PDF</li></ul></div>', unsafe_allow_html=True)
    with col_p2:
        st.markdown('<div class="pricing-card"><h3 style="color: #1E1E1E; font-weight: 800; margin-bottom: 0;">PRO (Miesiąc)</h3><div class="pricing-price">19 zł <span style="font-size: 20px; color: #6C757D;">/ mc</span></div><div class="pricing-sub">Elastyczna subskrypcja z możliwością rezygnacji</div><ul class="card-list" style="margin-top: 10px !important;"><li><b>Wszystko z wersji Podstawowej</b></li><li>Precyzyjne listy zakupowe PRO</li><li>Nielimitowane generowanie PDF</li><li>Zapisywanie i edycja kosztorysów</li><li>Zaawansowany kalkulator (ROI)</li></ul></div>', unsafe_allow_html=True)
    with col_p3:
        st.markdown('<div class="pricing-card pricing-pro"><div class="pricing-badge">NAJLEPSZY WYBÓR</div><h3 style="color: #00D395; font-weight: 800; margin-bottom: 0;">PRO (Rok)</h3><div class="pricing-price">190 zł <span style="font-size: 20px; color: #6C757D;">/ rok</span></div><div class="pricing-sub"><b>Oszczędzasz 38 zł</b><br>(2 miesiące całkowicie GRATIS!)</div><ul class="card-list" style="margin-top: 10px !important;"><li><b>Wszystko to, co w pakiecie Miesiąc</b></li><li>Gwarancja stałej, niższej ceny</li><li>Priorytetowe wsparcie mailowe</li><li>Wcześniejszy dostęp do nowości</li></ul></div>', unsafe_allow_html=True)

    st.markdown("<br><br><h2 style='text-align: center;'>Często Zadawane Pytania</h2>", unsafe_allow_html=True)
    col_f1, col_faq, col_f2 = st.columns([1, 2.5, 1])
    with col_faq:
        st.markdown('<div class="faq-card-question">Czy wyceny materiałów są aktualne?</div><div class="faq-card-answer">Tak. Nasze bazy cenowe są aktualizowane raz w miesiącu na podstawie średnich cen rynkowych z największych marketów i hurtowni.</div>', unsafe_allow_html=True)
        st.markdown('<div class="faq-card-question">Czy mogę zapisać swój kosztorys?</div><div class="faq-card-answer-blue">Funkcja zapisywania i edycji wielu projektów jest dostępna dla zalogowanych użytkowników w wersji <b>Premium PRO</b>.</div>', unsafe_allow_html=True)
        st.markdown('<div class="faq-card-question">Jak dokładne są listy zakupowe?</div><div class="faq-card-answer">Algorytmy uwzględniają oficjalne normy zużycia producentów oraz standardowy naddatek 10% na odpady i docięcia.</div>', unsafe_allow_html=True)
        st.markdown('<div class="faq-card-question">Czy format płytek wpływa na wycenę?</div><div class="faq-card-answer-blue">Oczywiście. W sekcji Łazienka możesz wybrać format (np. 120x60), a system automatycznie podniesie stawkę za robociznę i zużycie kleju.</div>', unsafe_allow_html=True)

        st.markdown("---")

# ==========================================
    # SEKCJA: OPINIE (SOCIAL PROOF)
    # ==========================================
    st.markdown("<br><br><h2 style='text-align: center; font-weight: 800;'>Co mówią fachowcy?</h2><br>", unsafe_allow_html=True)
    
    col_op1, col_op2, col_op3 = st.columns(3)
    
    with col_op1:
        st.markdown(
            """
<div style="background-color: white; border-radius: 15px; padding: 25px; border-left: 5px solid #00D395; box-shadow: 0 4px 10px rgba(0,0,0,0.05); min-height: 220px; display: flex; flex-direction: column;">
    <div style="color: #F5B041; font-size: 20px; margin-bottom: 10px;">⭐⭐⭐⭐⭐</div>
    <p style="font-style: italic; color: #555; font-size: 14px; flex-grow: 1;">"Koniec z liczeniem worków gładzi na brudnym kartonie. ProCalc na telefonie robi mi listę do hurtowni w 2 minuty. Klient widzi PDF-a i od razu wie, za co płaci. Pełna profeska."</p>
    <div style="margin-top: 15px;">
        <strong style="color: #1E1E1E; display: block;">Marcin</strong>
        <span style="color: #777; font-size: 12px;">Właściciel ekipy wykończeniowej</span>
    </div>
</div>
            """, unsafe_allow_html=True)
        
    with col_op2:
        st.markdown(
            """
<div style="background-color: white; border-radius: 15px; padding: 25px; border-left: 5px solid #0E172B; box-shadow: 0 4px 10px rgba(0,0,0,0.05); min-height: 220px; display: flex; flex-direction: column;">
    <div style="color: #F5B041; font-size: 20px; margin-bottom: 10px;">⭐⭐⭐⭐⭐</div>
    <p style="font-style: italic; color: #555; font-size: 14px; flex-grow: 1;">"Przelicznik flizeliny uratował mi tyłek przy ostatnim zleceniu z płytami GK. Zawsze kupowałem za dużo albo mi brakowało. Tu wpisuję metry narożników i mam wynik rolek."</p>
    <div style="margin-top: 15px;">
        <strong style="color: #1E1E1E; display: block;">Kamil</strong>
        <span style="color: #777; font-size: 12px;">Majster (Zabudowy GK)</span>
    </div>
</div>
            """, unsafe_allow_html=True)

    with col_op3:
        st.markdown(
            """
<div style="background-color: white; border-radius: 15px; padding: 25px; border-left: 5px solid #00D395; box-shadow: 0 4px 10px rgba(0,0,0,0.05); min-height: 220px; display: flex; flex-direction: column;">
    <div style="color: #F5B041; font-size: 20px; margin-bottom: 10px;">⭐⭐⭐⭐⭐</div>
    <p style="font-style: italic; color: #555; font-size: 14px; flex-grow: 1;">"Robię flippy i ten kalkulator z kosztorysem materiałowym to dla mnie gamechanger. Wiem, jaki mam budżet na remont mieszkania, zanim w ogóle pojadę do notariusza."</p>
    <div style="margin-top: 15px;">
        <strong style="color: #1E1E1E; display: block;">Piotr</strong>
        <span style="color: #777; font-size: 12px;">Inwestor / Flipper</span>
    </div>
</div>
            """, unsafe_allow_html=True)
        
    st.markdown("<br><br>", unsafe_allow_html=True)
        
    st.header("Plan Rozwoju Aplikacji (Roadmap)")
    col_dev1, col_dev2 = st.columns(2)
    
    with col_dev1:
        st.markdown("#### W TRAKCIE (Koncept/Dev)")
        st.info("**Live Progress (CRM)**\n\nInteraktywna checklista etapów prac.")
        st.info("**Dokumentacja Foto**\n\nMożliwość wgrywania zdjęć z budowy.")
        
    with col_dev2:
        st.markdown("#### DO ZROBIENIA (Plany)")
        st.success("**Efekty Dekoracyjne** – Beton architektoniczny, stiuk.")
        st.success("**Baza Danych (Cloud)** – Integracja z Firebase (zapisywanie projektów).")


# ==========================================
# TUTAJ WCHODZI NASZ NOWY PANEL INWESTORA!
# ==========================================
elif branza == "Panel Inwestora":
    st.markdown("<br>", unsafe_allow_html=True)
    if not st.session_state.zalogowany:
        st.warning("Ta sekcja dostępna jest wyłącznie dla zalogowanych użytkowników.")
        st.info("Przejdź do zakładki 'Logowanie' w górnym menu, aby założyć darmowe konto.")
    

        # Odpalamy Zawartość w zależności od wyboru w boczku
        if opcja_boczna == "Nawigacja Główna":
            st.header("Twoje Kosztorysy i Projekty")
            st.info("Tutaj docelowo wyświetlą się Twoje wyceny i analiza ROI.")
            
        elif opcja_boczna == "Mój Profil":
            st.header("Mój Profil Inwestora")
            c1, c2 = st.columns(2)
            with c1:
                st.text_input("Imię i Nazwisko / Nazwa Firmy")
            with c2:
                st.number_input("Domyślny narzut na materiały (%)", value=10)
                st.number_input("Twoja stawka za roboczogodzinę (PLN/h)", value=60)
            if st.button("Zapisz ustawienia profilu"):
                st.success("Zapisano zmiany!")
                
        elif opcja_boczna == "Język i Region":
            st.header("Ustawienia Regionalne")
            st.selectbox("Wybierz język", ["Polski", "English"])
            st.selectbox("Domyślna waluta", ["PLN", "EUR", "USD"])
            if st.button("Zapisz region"):
                st.success("Zapisano zmiany!")

elif branza == "Kontakt":
    # ---------------- EKRAN KONTAKTU (Nietknięty!) ----------------
    st.markdown("<h1 style='text-align: center; color: #00D395;'>Kontakt</h1>", unsafe_allow_html=True)
    _, col_k, _ = st.columns([1, 2, 1])
    with col_k:
        st.markdown("""
        <div class="custom-card" style="text-align: center;">
            <p class="card-text">Masz pytania lub propozycję współpracy? Napisz do nas!</p>
            <h3 style="color: #0E172B; font-weight: 800; margin: 20px 0;">biuro@procalc.pl</h3>
            <p class="card-text">Infolinia (Pn-Pt 8:00-16:00): <b>+48 123 456 789</b></p>
        </div>
        """, unsafe_allow_html=True)

elif branza == "Logowanie":
    st.session_state.przekierowanie = False
    
    if not st.session_state.zalogowany:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.subheader("Witaj w ProCalc")
        st.write("Zaloguj się, aby odblokować pakiet PRO, zapisywać projekty i pobierać raporty PDF.")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- ZAKŁADKI LOGOWANIA I REJESTRACJI ---
        tab_log, tab_rej = st.tabs(["🔐 Logowanie", "📝 Rejestracja"])
        
        with tab_log:
            st.markdown("#### Zaloguj się adresem E-mail")
            email_log = st.text_input("Adres E-mail", key="log_email")
            pass_log = st.text_input("Hasło", type="password", key="log_pass")
            
            if st.button("Zaloguj się", type="primary", use_container_width=True):
                if supabase:
                    try:
                        res = supabase.auth.sign_in_with_password({"email": email_log, "password": pass_log})
                        if res.user:
                            st.session_state.zalogowany = True
                            st.session_state.user_email = res.user.email
                            st.session_state.user_id = str(res.user.id)
                            # --- TE DWIE LINIJKI TO LEKARSTWO NA AMNEZJĘ ---
                            st.session_state.access_token = res.session.access_token
                            st.session_state.refresh_token = res.session.refresh_token
                            # -----------------------------------------------
                            st.session_state.pakiet = "PRO"
                            st.success("Zalogowano pomyślnie! Zaraz odświeżę...")
                            time.sleep(1)
                            st.rerun()
                    except Exception as e:
                        st.error("Błąd logowania. Sprawdź e-mail i hasło.")
            
            st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
            st.markdown("#### Lub użyj konta Google")
            
            # Używamy zmiennej 'url', którą zdefiniowaliśmy na samej górze z secrets
            login_url = f"{url}/auth/v1/authorize?provider=google&redirect_to=https://kalkulator-wykonczeniowy-buwyvwvkgmc7qdxit7ipst.streamlit.app/"

            przycisk_html = f"""
            <a href="{login_url}" target="_self" style="text-decoration: none;">
                <div style="background-color: #00D395; color: white; padding: 15px; text-align: center; border-radius: 12px; font-weight: 800; cursor: pointer; transition: 0.3s; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    🌐 Zaloguj przez Google
                </div>
            </a>
            """
            st.markdown(przycisk_html, unsafe_allow_html=True)
            
        with tab_rej:
            st.markdown("#### Utwórz darmowe konto")
            email_rej = st.text_input("Twój adres E-mail", key="rej_email")
            pass_rej = st.text_input("Utwórz Hasło (min. 6 znaków)", type="password", key="rej_pass")
            pass_rej2 = st.text_input("Powtórz Hasło", type="password", key="rej_pass2")
            
            if st.button("Zarejestruj się", type="primary", use_container_width=True):
                if pass_rej != pass_rej2:
                    st.error("Hasła nie są identyczne!")
                elif len(pass_rej) < 6:
                    st.error("Hasło musi mieć minimum 6 znaków.")
                elif supabase:
                    try:
                        res = supabase.auth.sign_up({"email": email_rej, "password": pass_rej})
                        st.success("Konto utworzone! Możesz się teraz zalogować w zakładce obok.")
                    except Exception as e:
                        st.error(f"Błąd rejestracji. Upewnij się, że mail jest poprawny.")

    else:
        # WIDOK PO ZALOGOWANIU
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.success("✅ Witaj z powrotem! Jesteś zalogowany.")
        st.info(f"Zalogowano jako: **{st.session_state.get('user_email', '')}**")
        st.write("Twój aktywny pakiet: **Premium PRO 💎**")
        st.markdown("<br>", unsafe_allow_html=True)
        
        _, col_logout, _ = st.columns([1, 1, 1])
        with col_logout:
            if st.button("WYLOGUJ SIĘ", use_container_width=True, type="secondary"):
                st.session_state.zalogowany = False
                st.session_state.pakiet = "Podstawowy"
                st.session_state.user_email = ""
                st.session_state.pop("user_id", None)
                if supabase: supabase.auth.sign_out()
                st.rerun()
                
# --- INICJALIZACJA STANU ---
if 'pokoje_pro' not in st.session_state:
    st.session_state.pokoje_pro = []

# --- INICJALIZACJA HARMONOGRAMU ---
if 'etapy_projektu' not in st.session_state:
    st.session_state.etapy_projektu = [
        {"Zadanie": "Demontaże i Przygotowanie", "Dni": 4, "Postęp": 100},
        {"Zadanie": "Instalacje WOD-KAN i ELE", "Dni": 7, "Postęp": 0},
        {"Zadanie": "Tynki i Wylewki", "Dni": 10, "Postęp": 0},
        {"Zadanie": "Gładzie i Malowanie", "Dni": 12, "Postęp": 0},
        {"Zadanie": "Łazienka (Płytki)", "Dni": 14, "Postęp": 0},
        {"Zadanie": "Montaże końcowe", "Dni": 5, "Postęp": 0}
    ]
            



# --- SEKCJA: MALOWANIE ---
if branza == "Malowanie":
    st.subheader("Kalkulator Malarski")
    tab_fast, tab_pro = st.tabs([" Szybka Wycena", " Kosztorys PRO"])

    # --- BAZA WIEDZY (Ceny rynkowe zaktualizowane: za 1 Litr / 1 Sztukę) ---
    baza_biale = {
        "Śnieżka Eko (Ekonomiczna)": 7,          # ok. 70 zł / 10L
        "Dekoral Polinak (Standard)": 10,        # ok. 100 zł / 10L
        "Beckers Designer White (Standard+)": 14,# ok. 140 zł / 10L
        "Magnat Ultra Matt (Premium)": 18,       # ok. 180 zł / 10L
        "Tikkurila Anti-Reflex 2 (Premium+)": 28,# ok. 280 zł / 10L
        "Flugger Flutex Pro 5 (Top Premium)": 35 # ok. 350 zł / 10L
    }
    
    baza_kolory = {
        "Śnieżka Barwy Natury (Eko)": 17,        # ok. 85 zł / 5L
        "Dekoral Akrylit W (Standard)": 20,      # ok. 100 zł / 5L
        "Magnat Ceramic (Standard+)": 30,        # ok. 150 zł / 5L
        "Beckers Designer Colour (Premium)": 32, # ok. 160 zł / 5L
        "Tikkurila Optiva 5 (Premium+)": 50,     # ok. 250 zł / 5L
        "Flugger Dekso (Top Premium)": 70        # ok. 350 zł / 5L (z barwieniem)
    }
    
    baza_grunty = {
        "Grunt Marketowy (Eko)": 5,              # ok. 25 zł / 5L
        "Unigrunt Atlas (Standard)": 8,          # ok. 40 zł / 5L
        "Ceresit CT 17 (Klasyk)": 12,            # ok. 60 zł / 5L
        "Mapei Primer G Pro (Premium)": 17       # ok. 85 zł / 5L
    }
    
    baza_tasmy = {
        "Żółta Papierowa (Market)": 8,
        "Solid (Niebieska)": 14,
        "Blue Dolphin (Profesjonalna)": 18,
        "Tesa Precision (Premium)": 25,
        "3M / Scotch (Top)": 30
    }
    
    with tab_fast:
        st.header(" Błyskawiczny szacunek kosztów")
        st.info("Pełne możliwości, dokładne pomiary i wybór konkretnych marek farb znajdziesz w zakładce Kosztorys PRO.")
        
        col_input, col_spacer = st.columns([1, 1])
        with col_input:
            st.write("Podaj metraż podłogi, aby otrzymać orientacyjne koszty malowania całego pomieszczenia (ściany + sufity).")
            
            # Suwak z metrażem i input dla stawki
            m2_podloga_fast = st.slider("Metraż mieszkania / pokoju (m2 podłogi):", 1, 1000, 50)
            stawka_rob_fast = st.number_input("Twoja stawka za m2 robocizny (malowanie):", value=35)
        
            # Logika uproszczona: 
            # Zakładamy, że powierzchnia malowania (ściany + sufit) to ok. 3.5x pow. podłogi
            pow_malowania_fast = m2_podloga_fast * 3.5
            estymacja_robocizny = pow_malowania_fast * stawka_rob_fast
            
            # Estymacja materiałów: średnio 12 zł za m2 powierzchni malowania (farba, grunt, folia, akcesoria) 
            # (obniżone z 14 zł po aktualizacji rynkowej dla standardu)
            estymacja_materialow = pow_malowania_fast * 12 
            
            # Wyświetlanie wyników w kolumnach
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                st.metric("Szacowana Robocizna", f"{round(estymacja_robocizny)} zł")
            with c_f2:
                st.metric("Szacowane Materiały", f"{round(estymacja_materialow)} zł")
                
            st.success(f"### Przybliżony koszt całkowity: **{round(estymacja_robocizny + estymacja_materialow)} zł**")
            
            # Adnotacja o wersji PRO
            st.markdown("""
            ---
            ###  Chcesz większej precyzji?
            Przejdź do zakładki **Kosztorys PRO**, aby uzyskać dostęp do:
            * **Pełnej bazy materiałów:** Wybór konkretnych marek farb (kolor/biała), gruntów i taśm.
            * **Precyzyjnego planowania:** Możliwość dodawania każdej ściany z osobna (szerokość x wysokość).
            * **Sztukaterii:** Kalkulator listew ściennych i sufitowych wraz z klejami.
            * **Listy zakupowej:** Gotowe zestawienie ile dokładnie litrów farby i sztuk akcesoriów musisz kupić.
            """)

    # ==========================================
    # TAB 2: KOSZTORYS PRO
    # ==========================================
    with tab_pro:
        # --- BLOKADA PRO ---
        if not st.session_state.zalogowany or st.session_state.pakiet != "PRO":
            st.error("🔒 **Dostęp zablokowany**")
            st.warning("Ta sekcja dostępna jest wyłącznie dla użytkowników z pakietem Premium PRO.")
            
            _, col_k, _ = st.columns([1, 2, 1])
            with col_k:
                if st.button("Odblokuj dostęp (Przejdź do logowania)", use_container_width=True, key="btn_odblokuj_malowanie"):
                    st.session_state.przekierowanie = True  
                    st.rerun()  
        else:
            # --- TYLKO DLA ZALOGOWANYCH PRO ---
            st.header("Profesjonalny Arkusz Kalkulacyjny")
            
            # --- SEKCJA 1: SZYBKI SZACUNEK (Otwarty wewnątrz PRO) ---
            st.subheader(" Szybki szacunek materiałów i robocizny")
            col_f1, col_f2 = st.columns([1, 1.2])

            with col_f1:
                m_uzytkowy = st.number_input("Metraż mieszkania (podłoga m2):", min_value=1.0, value=50.0, key="pro_m_fast")
                stan_f = st.selectbox("Stan lokalu:", ["Deweloperski", "Zamieszkały (meble)"], key="pro_s_fast")
                
                st.markdown("**Wybór Produktów**")
                f_biala = st.selectbox("Farba BIAŁA (Sufity):", list(baza_biale.keys()), key="pro_fb")
                f_kolor = st.selectbox("Farba KOLOR (Ściany):", list(baza_kolory.keys()), key="pro_fk")
                f_grunt = st.selectbox("Marka Gruntu:", list(baza_grunty.keys()), key="pro_fg")
                f_tasma = st.selectbox("Rodzaj Taśmy:", list(baza_tasmy.keys()), key="pro_ft")
                
                stawka = st.slider("Twoja stawka za m2 robocizny:", 1, 100, 35, key="pro_r_fast")

                st.markdown("---")
                st.subheader("Sztukateria")
                mb_sztukaterii = st.number_input("Łączna długość listew (mb):", min_value=0.0, value=0.0, step=1.0, key="pro_sz_fast")
                typ_sztukaterii = st.selectbox("Rodzaj listew:", ["Styropianowe (Eko)", "Poliuretanowe (Twarde)", "Gipsowe (Premium)"], key="pro_tsz_fast")

            # --- LOGIKA OBLICZEŃ (Stała) ---
            m2_sufit = m_uzytkowy * 1.0
            m2_sciany = m_uzytkowy * 2.5
            m2_razem = m2_sufit + m2_sciany
            mnoznik = 1.0 if stan_f == "Deweloperski" else 1.3

            l_biala = (m2_sufit / 10) * 2
            l_kolor = (m2_sciany / 10) * 2
            l_grunt = m2_razem * 0.15
            szt_akryl = m_uzytkowy / 12
            szt_tasma = (m_uzytkowy / 15) * mnoznik
            
            stawki_szt = {"Styropianowe (Eko)": 25, "Poliuretanowe (Twarde)": 45, "Gipsowe (Premium)": 65}
            koszt_rob_sztukateria = mb_sztukaterii * stawki_szt[typ_sztukaterii]
            koszt_mat_sztukateria = (mb_sztukaterii / 8 + 0.4) * 25
                
            k_mat_sredni = (l_biala * baza_biale[f_biala]) + (l_kolor * baza_kolory[f_kolor]) + \
                           (l_grunt * baza_grunty[f_grunt]) + (szt_tasma * baza_tasmy[f_tasma]) + \
                           koszt_mat_sztukateria + 150 
            
            k_rob_total = (m2_razem * stawka) + koszt_rob_sztukateria

            with col_f2:
                st.subheader("Wyniki i Lista zakupów")
                
                # Obliczenia końcowe
                total_pro = k_mat_sredni + k_rob_total
                
                # --- PANEL FINANSOWY ---
                st.success(f"### RAZEM: **{round(total_pro)} zł**")
                
                c_money1, c_money2 = st.columns(2)
                with c_money1:
                    st.metric("Twoja Robocizna", f"{round(k_rob_total)} zł")
                with c_money2: 
                    st.metric("Materiały (ok.)", f"{round(k_mat_sredni)} zł")
                
                st.markdown("---")

                # --- LISTA ZAKUPÓW (Widoczna na wierzchu) ---
                st.markdown("### Twoja lista zakupów")
                
                st.write(f"**Farby i Grunt:**")
                st.write(f"- Biała ({f_biala}): **{round(l_biala, 1)}L**")
                st.write(f"- Kolor ({f_kolor}): **{round(l_kolor, 1)}L**")
                st.write(f"- Grunt ({f_grunt}): **{round(l_grunt, 1)}L**")
                
                st.write(f"**Akcesoria:**")
                st.write(f"- Taśma ({f_tasma}): **{round(szt_tasma + 0.5)} szt.**")
                st.write(f"- Akryl szpachlowy: **{round(szt_akryl + 0.5)} szt.**")
                
                if mb_sztukaterii > 0:
                    st.write(f"**Sztukateria:**")
                    st.write(f"- Robocizna (montaż): **{round(koszt_rob_sztukateria)} zł**")
                    st.write(f"- Klej: **Bostik Mamut** ({int(mb_sztukaterii/8 + 1)} szt.)")
                
                st.info("Kwoty materiałów zawierają doliczony margines bezpieczeństwa (10%) oraz 150 zł na folie i wałki.")

            st.markdown("---")

            # --- SEKCJA 2: DODAWANIE ŚCIAN (Na wierzchu, bez expandera) ---
            st.subheader("➕ Dodaj konkretną ścianę do projektu")
            c1, c2, c3 = st.columns([2, 1, 1])
            nazwa_p = c1.text_input("Nazwa / Pomieszczenie:", "Salon - Ściana TV", key="wall_name")
            szer = c2.number_input("Szerokość (m):", min_value=0.1, value=4.0, step=0.1, key="wall_w")
            wys = c3.number_input("Wysokość (m):", min_value=0.1, value=2.6, step=0.1, key="wall_h")
            
            kolor_hex = st.color_picker("Kolor tej ściany:", "#D3D3D3", key="wall_c")
            
            if st.button("ZATWIERDŹ I DODAJ ŚCIANĘ", use_container_width=True):
                st.session_state.pokoje_pro.append({
                    "pokoj": nazwa_p, "szer": szer, "wys": wys, "kolor": kolor_hex
                })
                st.rerun()

            # --- WYKAZ DODANYCH ELEMENTÓW ---
            if st.session_state.pokoje_pro:
                st.markdown("### Zestawienie szczegółowe")
                total_m2_walls = 0
                for i, s in enumerate(st.session_state.pokoje_pro):
                    p_m2 = s['szer'] * s['wys']
                    total_m2_walls += p_m2
                    st.write(f"{i+1}. **{s['pokoj']}**: {s['szer']}m x {s['wys']}m = **{round(p_m2, 2)} m²**")
                
                st.info(f"Łączna powierzchnia dodanych ścian: **{round(total_m2_walls, 1)} m²**")
                
                if st.button("WYCZYŚĆ LISTĘ ŚCIAN"):
                    st.session_state.pokoje_pro = []
                    st.rerun()
                    
            st.markdown("---")
            
            st.subheader("Zarządzanie Projektem")
            
            c_btn1, c_btn2 = st.columns(2)

            with c_btn1:
                if st.button("Wyczyść projekt PRO", use_container_width=True):
                    st.session_state.pokoje_pro = []
                    st.rerun()

            with c_btn2:
                try:
                    from fpdf import FPDF
                    import os
                    from datetime import datetime

                    # 1. Inicjalizacja PDF
                    pdf = FPDF()
                    pdf.add_page()

                    # 2. KONFIGURACJA CZCIONKI INTER
                    font_path = "Inter-Regular.ttf"
                    if os.path.exists(font_path):
                        pdf.add_font("Inter", "", font_path)
                        pdf.set_font("Inter", size=12)
                        font_exists = True
                    else:
                        pdf.set_font("Arial", size=12)
                        font_exists = False

                    # --- NAGŁÓWEK ---
                    if os.path.exists("logo.png"):
                        pdf.image("logo.png", x=10, y=8, w=35)
                    
                    pdf.set_font("Inter" if font_exists else "Arial", size=18)
                    pdf.cell(0, 15, "PROCALC - RAPORT KOSZTORYSOWY", ln=True, align='C')
                    pdf.ln(10)

                    # --- LINIA SEPARATORA ---
                    pdf.set_draw_color(0, 0, 0)
                    pdf.line(10, 35, 200, 35)
                    pdf.ln(5)

                    # --- DANE PROJEKTU ---
                    pdf.set_font("Inter" if font_exists else "Arial", size=10)
                    data_str = datetime.now().strftime("%d.%m.%Y %H:%M")
                    pdf.cell(0, 8, f"Data: {data_str} | Metraz: {m_uzytkowy} m2", ln=True)
                    pdf.ln(5)

                    # --- SEKCJA 1: FINANSE (Tabela) ---
                    pdf.set_fill_color(230, 230, 230)
                    pdf.set_font("Inter" if font_exists else "Arial", size=12)
                    pdf.cell(0, 10, " 1. PODSUMOWANIE KOSZTOW", ln=True, fill=True)
                    
                    pdf.set_font("Inter" if font_exists else "Arial", size=11)
                    pdf.cell(95, 10, " Twoja Robocizna:", 1)
                    pdf.cell(95, 10, f" {round(k_rob_total)} PLN", 1, ln=True)
                    
                    pdf.cell(95, 10, " Szacowane Materialy:", 1)
                    pdf.cell(95, 10, f" {round(k_mat_sredni)} PLN", 1, ln=True)
                    
                    pdf.set_font("Inter" if font_exists else "Arial", size=13)
                    pdf.cell(95, 12, " SUMA CALKOWITA:", 1)
                    pdf.cell(95, 12, f" {round(total_pro)} PLN", 1, ln=True)
                    pdf.ln(10)

                    # --- SEKCJA 2: LISTA ZAKUPOWA ---
                    pdf.set_font("Inter" if font_exists else "Arial", size=12)
                    pdf.cell(0, 10, " 2. SZCZEGOLOWA LISTA ZAKUPOW", ln=True, fill=True)
                    pdf.set_font("Inter" if font_exists else "Arial", size=10)
                    pdf.ln(2)

                    lista_pdf = {
                        "Farba Biała (Sufity)": f"{round(l_biala, 1)}L ({f_biala})",
                        "Farba Kolor (Ściany)": f"{round(l_kolor, 1)}L ({f_kolor})",
                        "Grunt głęboko penetrujący": f"{round(l_grunt, 1)}L ({f_grunt})",
                        "Taśma malarska": f"{round(szt_tasma + 0.5)} szt. ({f_tasma})",
                        "Akryl szpachlowy": f"{round(szt_akryl + 0.5)} szt."
                    }
                    
                    if mb_sztukaterii > 0:
                        lista_pdf["Klej do listew"] = f"Bostik Mamut ({int(mb_sztukaterii/8 + 1)} szt.)"

                    def czysc_tekst(tekst):
                        pl_znaki = {'ą':'a','ć':'c','ę':'e','ł':'l','ń':'n','ó':'o','ś':'s','ź':'z','ż':'z','Ą':'A','Ć':'C','Ę':'E','Ł':'L','Ń':'N','Ó':'O','Ś':'S','Ź':'Z','Ż':'Z'}
                        for pl, ang in pl_znaki.items(): tekst = tekst.replace(pl, ang)
                        return tekst.encode('latin-1', 'replace').decode('latin-1')

                    for produkt, opis in lista_pdf.items():
                        pdf.cell(0, 8, f"- {czysc_tekst(produkt)}: {czysc_tekst(opis)}", ln=True)

                    # --- STOPKA ---
                    pdf.set_y(-25)
                    pdf.set_font("Inter" if font_exists else "Arial", size=8)
                    pdf.set_text_color(100, 100, 100)
                    pdf.cell(0, 10, "Wygenerowano automatycznie przez proCalc. Kosztorys nie stanowi oferty handlowej.", 0, 0, 'C')

                    pdf_output = pdf.output(dest="S")
                    
                    if isinstance(pdf_output, str):
                        safe_bytes = pdf_output.encode('latin-1', 'replace')
                    else:
                        safe_bytes = bytes(pdf_output)
                    
                    st.download_button(
                        label="Pobierz Raport PDF",
                        data=safe_bytes,
                        file_name=f"Kosztorys_Malowanie_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Błąd PDF: {e}")





elif branza == "Szpachlowanie":
    st.header("Kalkulator Gładzi i Przygotowania Ścian")

    # ==========================================
    # WIDGET: SZYBKI PRZELICZNIK (KG <-> LITRY)
    # ==========================================
    with st.expander("Przelicznik: KG ↔ Litry &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;", expanded=False):
        
        # Słownik gęstości (waga 1 litra w kg)
        gestosc = {
            "Gładź gotowa (wiadro)": 1.7,
            "Farba lateksowa / gruntująca": 1.4,
            "Grunt wodny (np. Unigrunt)": 1.05,
            "Gips startowy (rozrobiony)": 1.1
        }
        
        kol_prz1, kol_prz2 = st.columns(2)
        with kol_prz1:
            typ_materialu = st.selectbox("Wybierz rodzaj materiału:", list(gestosc.keys()), key="prz_mat")
            kierunek = st.radio("Kierunek przeliczenia:", ["Litry ➡️ Kilogramy", "Kilogramy ➡️ Litry"], key="prz_kier")
            
        with kol_prz2:
            wartosc_we = st.number_input("Wpisz wartość:", min_value=0.0, value=15.0, step=1.0, key="prz_wart")
            wspolczynnik = gestosc[typ_materialu]
            
            st.markdown("<br>", unsafe_allow_html=True) # Mały odstęp dla wyrównania
            
            if "Litry" in kierunek.split(" ➡️ ")[0]: # Liczymy Litry na KG
                wynik = wartosc_we * wspolczynnik
                st.success(f"**{wartosc_we} Litrów** to ok. **{round(wynik, 1)} kg**")
            else: # Liczymy KG na Litry
                wynik = wartosc_we / wspolczynnik
                st.info(f"**{wartosc_we} Kilogramów** to ok. **{round(wynik, 1)} Litrów**")
                
            st.caption(f"*Przyjęta gęstość rynkowa: ~{wspolczynnik} kg/L*")

    # 1. BAZA DANYCH
    baza_sypkie = {
        "Cekol C-45 (20kg)": {"cena": 65, "waga": 20},
        "FransPol GS-2 (20kg)": {"cena": 45, "waga": 20},
        "Dolina Nidy Omega (20kg)": {"cena": 38, "waga": 20},
        "Atlas Gipsar Uni (20kg)": {"cena": 45, "waga": 20}
    }
    
    baza_gotowe = {
        "Śmig A-2 (Wiadro 20kg)": {"cena": 55, "waga": 20},
        "Knauf Goldband Finish (18kg)": {"cena": 60, "waga": 18},
        "Knauf Goldband Finish (28kg)": {"cena": 80, "waga": 28},
        "Knauf Fill & Finish Light (20kg)": {"cena": 120, "waga": 20},
        "Sheetrock Super Finish (28kg)": {"cena": 135, "waga": 28},
        "Atlas GTA (18kg)": {"cena": 70, "waga": 18},
        "Atlas GTA (25kg)": {"cena": 90, "waga": 25}
    }

    baza_gipsow = {
        "FransPol GS-100 (20kg)": {"cena": 45, "waga": 20},
        "Nida Start (20kg)": {"cena": 40, "waga": 20},
        "Knauf Fugenfuller (25kg)": {"cena": 55, "waga": 25}
    }
    
    baza_grunty_szp = {
        "Atlas Unigrunt (Standard)": 8, 
        "Ceresit CT 17 (Klasyk)": 12,
        "Knauf Tiefengrund (Premium)": 14,
        "Mapei Primer G Pro (Koncentrat)": 17
    }

    if 'pokoje_szp' not in st.session_state:
        st.session_state.pokoje_szp = []

    tab_s1, tab_s2 = st.tabs([" Szybka Wycena", " Detale PRO"])

    # ==========================================
    # ZAKŁADKA 1: SZYBKA WYCENA
    # ==========================================
    with tab_s1:
        st.subheader("Błyskawiczny szacunek kosztów")
        c_fast1, c_fast2 = st.columns(2)
        with c_fast1:
            m2_podl_fast = st.number_input("Podaj metraż podłogi mieszkania (m2):", min_value=1.0, value=50.0, key="fast_podl")
            czy_gk_fast = st.checkbox("Powierzchnie z płyt GK? (Mniejsze zużycie)", key="fast_gk")
        with c_fast2:
            l_warstw_fast = st.slider("Liczba warstw gładzi:", 1, 3, 1 if czy_gk_fast else 2, key="fast_warstwy")
        
        m2_scian_fast = m2_podl_fast * 3.5
        # Redukcja ceny materiału/robocizny przy GK (mniej szlifowania/nakładania)
        mnoznik_gk = 0.7 if czy_gk_fast else 1.0
        cena_za_m2_fast = (20 + (l_warstw_fast * 30)) * mnoznik_gk
        szacunek_total = m2_scian_fast * cena_za_m2_fast 
        
        st.success(f"### Szacowany koszt całkowity: **ok. {round(szacunek_total):,} PLN**".replace(",", " "))
        st.info(f"Przyjęto {m2_scian_fast} m² ścian. Stawka: {round(cena_za_m2_fast, 2)} zł/m².")

   # ==========================================
    # ZAKŁADKA 2: DETALE PRO
    # ==========================================
    with tab_s2:
        # Pancerne sprawdzenie uprawnień
        ma_dostep = st.session_state.get("zalogowany", False) and st.session_state.get("pakiet") == "PRO"
        
        if not ma_dostep:
            st.error("🔒 Sekcja dostępna dla pakietu PRO")
        else:
            st.subheader("Konfiguracja Wykonania (PRO)")
            
            c_konf1, c_konf2 = st.columns(2)
            with c_konf1:
                system_szpachlowania = st.radio("Wariant wykonania:", ["Standardowy", "Mocny start (Gips + Gładź)"], horizontal=True)
                czy_gk = st.checkbox("Podłoże z płyt GK? (Zmniejsza zużycie gładzi o 40%)")
            
            with c_konf2:
                uzyj_flizeliny = st.checkbox("Zbrojenie narożników/łączeń flizeliną?")
                if uzyj_flizeliny:
                    metry_flizeliny_in = st.number_input("Ile mb narożników/łączeń do uzbrojenia?", min_value=0.0, value=20.0)
                    st.caption("Przelicznik: 2mb taśmy na 1mb narożnika")

            col_c1, col_c2 = st.columns(2)
            with col_c1:
                typ_g_pro = st.radio("Gładź finiszowa:", ["Gotowa (Wiadro)", "Sypka (Worek)"], horizontal=True)
                wybrana_g = st.selectbox("Wybierz gładź:", list(baza_sypkie.keys()) if typ_g_pro == "Sypka (Worek)" else list(baza_gotowe.keys()))
                dane_g = baza_sypkie[wybrana_g] if typ_g_pro == "Sypka (Worek)" else baza_gotowe[wybrana_g]

                # --- WYBÓR METODY NAKŁADANIA ---
                metoda_nakladania = st.radio(
                    "Metoda nakładania:",
                    ["Ręczna (Paca)", "Wałek", "Natrysk (Agregat)"],
                    horizontal=True
                )
                
                if system_szpachlowania == "Mocny start (Gips + Gładź)":
                    wybrany_gips = st.selectbox("Wybierz gips startowy:", list(baza_gipsow.keys()))
                    dane_gips = baza_gipsow[wybrany_gips]
                
                wybrany_grunt = st.selectbox("Wybierz Grunt:", list(baza_grunty_szp.keys()))

            with col_c2:
                # Jeśli GK, sugerujemy 1 warstwę, jeśli tynk - 2.
                l_warstw = st.slider("Łączna liczba warstw:", 1, 4, 1 if czy_gk else 2)
                
                # --- LOGIKA CENOWA ZALEŻNA OD METODY ---
                stawka_bazowa = 45 if czy_gk else 55
                if metoda_nakladania == "Wałek":
                    stawka_bazowa -= 2
                elif metoda_nakladania == "Natrysk (Agregat)":
                    stawka_bazowa -= 7
                    
                stawka_szp = st.number_input("Stawka robocizny (zł/m2):", 1, 300, stawka_bazowa)

            # --- LOGIKA MNOŻNIKA ZUŻYCIA ---
            mnoznik_zuzycia = 1.0
            if metoda_nakladania == "Wałek":
                mnoznik_zuzycia = 1.15
            elif metoda_nakladania == "Natrysk (Agregat)":
                mnoznik_zuzycia = 1.25

            st.markdown("---")
            st.subheader("Metraż prac")
            metoda_pomiaru = st.radio("Sposób podania metrażu:", ["Podaj metraż podłogi pokoju", "Dodaj konkretne pomieszczenia"], horizontal=True)

            m2_total = 0.0
            if metoda_pomiaru == "Podaj metraż podłogi pokoju":
                p_m2 = st.number_input("Metraż podłogi (m2):", 1.0, 500.0, 20.0)
                m2_total = p_m2 * 3.5
                st.info(f"Przeliczono na **{round(m2_total, 1)} m²** ścian/sufitów.")
            else:
                cp1, cp2 = st.columns(2)
                with cp1:
                    naz_p = st.text_input("Nazwa:", key="p_naz")
                    dl_p = st.number_input("Długość:", value=4.0, key="p_dl")
                    sz_p = st.number_input("Szerokość:", value=3.0, key="p_sz")
                with cp2:
                    wy_p = st.number_input("Wysokość:", value=2.6, key="p_wy")
                    suf_p = st.checkbox("Sufit?", value=True)
                    ok_drz = st.number_input("Odliczenia (m2):", value=3.5)
                
                if st.button("Dodaj pokój"):
                    netto = (((dl_p + sz_p) * 2 * wy_p) + (dl_p * sz_p if suf_p else 0)) - ok_drz
                    st.session_state.pokoje_szp.append({"nazwa": naz_p, "netto": netto})
                    st.rerun()
                
                for i, p in enumerate(st.session_state.pokoje_szp):
                    c_l, c_b = st.columns([5, 1])
                    c_l.info(f"{p['nazwa']}: {round(p['netto'],1)} m2")
                    if c_b.button("Usuń", key=f"del_p_{i}"):
                        st.session_state.pokoje_szp.pop(i)
                        st.rerun()
                m2_total = sum(p["netto"] for p in st.session_state.pokoje_szp)

            # ==========================================
            # WYNIKI I LISTA ZAKUPÓW
            # ==========================================
            if m2_total > 0:
                # LOGIKA ZUŻYCIA Z MNOŻNIKIEM METODY NAKŁADANIA
                norma_g = (0.5 if czy_gk else 1.2) * mnoznik_zuzycia 
                szt_gipsu = 0
                
                if system_szpachlowania == "Mocny start (Gips + Gładź)":
                    kg_gips = (m2_total * 0.8 if czy_gk else m2_total * 1.2) * mnoznik_zuzycia
                    szt_gipsu = int((kg_gips / dane_gips["waga"]) + 0.99)
                    warstwy_finisz = l_warstw - 1
                else:
                    warstwy_finisz = l_warstw

                kg_gladzi = m2_total * norma_g * warstwy_finisz
                szt_gladzi = int((kg_gladzi / dane_g["waga"]) + 0.99)
                
                szt_gruntu = int(m2_total * 0.2 / 5 + 0.99)
                szt_krazkow = int((m2_total / 50) + 0.99) if czy_gk else int((m2_total / 35) + 0.99)
                
                # Logika Flizeliny
                mb_flizeliny = 0
                szt_flizeliny = 0
                koszt_flizeliny = 0
                if uzyj_flizeliny:
                    mb_flizeliny = metry_flizeliny_in * 2
                    szt_flizeliny = int((mb_flizeliny / 25) + 0.99)
                    koszt_flizeliny = szt_flizeliny * 15

                koszt_m_dodatki = (m2_total * 3.5) + koszt_flizeliny
                koszt_m = (szt_gladzi * dane_g["cena"]) + (szt_gipsu * (dane_gips["cena"] if szt_gipsu > 0 else 0)) + (szt_gruntu * baza_grunty_szp[wybrany_grunt] * 5) + koszt_m_dodatki
                robocizna = m2_total * stawka_szp
                
                st.markdown("---")
                st.success(f"### WARTOŚĆ CAŁKOWITA: **{round(koszt_m + robocizna)} PLN**")
                
                res1, res2 = st.columns(2)
                res1.metric("Twoja Robocizna", f"{round(robocizna)} PLN")
                res2.metric("Materiały", f"{round(koszt_m)} PLN")
                
                st.markdown("---")
                st.subheader("Lista Zakupów")
                c_zak1, c_zak2 = st.columns(2)
                
                with c_zak1:
                    st.info("**MATERIAŁY GŁÓWNE**")
                    if system_szpachlowania == "Mocny start (Gips + Gładź)":
                        st.write(f"🔹 **Gips startowy ({wybrany_gips}):** {szt_gipsu} szt.")
                    st.write(f"🔹 **Gładź finiszowa ({wybrana_g}):** {szt_gladzi} szt.")
                    st.write(f"🔹 **Grunt ({wybrany_grunt}):** {szt_gruntu} baniek (5L)")
                    if uzyj_flizeliny:
                        st.write(f"🔹 **Flizelina (Zbrojenie):** {szt_flizeliny} rolek (25m)")
                with c_zak2:
                    st.warning("**MATERIAŁY ZUŻYWALNE**")
                    st.write(f"🔸 **Krążki ścierne P180/220:** {szt_krazkow} szt.")
                    st.write(f"🔸 **Narożniki, folie, akcesoria:** ~{round(koszt_m_dodatki - koszt_flizeliny)} zł")
                    
                # ==========================================
                # PDF GENERATION
                # ==========================================
                st.markdown("---")
                c_pdf1, c_pdf2 = st.columns(2)
                
                with c_pdf1:
                    if st.button("Wyczyść wszystko", use_container_width=True, key="btn_wyczysc_szp"):
                        st.session_state.pokoje_szp = []
                        st.rerun()

                with c_pdf2:
                    try:
                        from fpdf import FPDF
                        from datetime import datetime
                        import os

                        pdf = FPDF()
                        pdf.add_page()
                        
                        if os.path.exists("logo.png"):
                            pdf.image("logo.png", x=10, y=8, w=35)
                            
                        pdf.set_font("Arial", "B", 16)
                        pdf.cell(0, 15, "PROCALC - KOSZTORYS SZPACHLOWANIA", ln=True, align='C')
                        pdf.ln(5)
                        pdf.line(10, 35, 200, 35)
                        
                        pdf.ln(10)
                        pdf.set_font("Arial", "B", 12)
                        pdf.set_fill_color(240, 240, 240)
                        pdf.cell(0, 10, " 1. PODSUMOWANIE FINANSOWE", ln=True, fill=True)
                        pdf.set_font("Arial", "", 10)
                        pdf.cell(0, 8, f" Suma calkowita: {round(koszt_m + robocizna)} PLN", ln=True)
                        pdf.cell(0, 8, f" W tym robocizna: {round(robocizna)} PLN | Materialy: {round(koszt_m)} PLN", ln=True)

                        pdf.ln(5)
                        pdf.set_font("Arial", "B", 12)
                        pdf.cell(0, 10, " 2. SZCZEGOLY WYKONANIA", ln=True, fill=True)
                        pdf.set_font("Arial", "", 10)
                        
                        def czysc_tekst(tekst):
                            pl_znaki = {'ą':'a','ć':'c','ę':'e','ł':'l','ń':'n','ó':'o','ś':'s','ź':'z','ż':'z','Ą':'A','Ć':'C','Ę':'E','Ł':'L','Ń':'N','Ó':'O','Ś':'S','Ź':'Z','Ż':'Z'}
                            for pl, ang in pl_znaki.items(): tekst = tekst.replace(pl, ang)
                            return tekst.encode('latin-1', 'replace').decode('latin-1')

                        pdf.cell(0, 8, f" - Calkowity metraz prac: {round(m2_total, 1)} m2", ln=True)
                        pdf.cell(0, 8, f" - Liczba warstw: {l_warstw}", ln=True)
                        pdf.cell(0, 8, f" - Podloze: {'Plyty GK' if czy_gk else 'Tynki/Beton'}", ln=True)
                        if uzyj_flizeliny:
                            pdf.cell(0, 8, f" - Zbrojenie flizelina: TAK ({mb_flizeliny} mb tasmy)", ln=True)

                        pdf.ln(5)
                        pdf.set_font("Arial", "B", 12)
                        pdf.cell(0, 10, " 3. LISTA MATERIALOW", ln=True, fill=True)
                        
                        pdf.set_font("Arial", "B", 10)
                        pdf.cell(15, 10, " OK", 1, 0, 'C')
                        pdf.cell(135, 10, " Nazwa materialu", 1, 0)
                        pdf.cell(40, 10, " Ilosc", 1, 1, 'C')
                        
                        pdf.set_font("Arial", "", 10)
                        materialy_lista = [
                            (f"Gladz: {czysc_tekst(wybrana_g)}", f"{szt_gladzi} szt."),
                            (f"Grunt: {czysc_tekst(wybrany_grunt)}", f"{szt_gruntu} szt. (5L)"),
                            (f"Krazki scierne P180/220", f"{szt_krazkow} szt."),
                        ]
                        if szt_gipsu > 0:
                            materialy_lista.insert(0, (f"Gips start: {czysc_tekst(wybrany_gips)}", f"{szt_gipsu} szt."))
                        if uzyj_flizeliny:
                            materialy_lista.append(("Flizelina / Tasma zbrojaca", f"{szt_flizeliny} rolek"))
                        
                        for mat, ilosc in materialy_lista:
                            pdf.cell(15, 10, "[   ]", 1, 0, 'C')
                            pdf.cell(135, 10, f" {mat}", 1, 0)
                            pdf.cell(40, 10, f" {ilosc}", 1, 1, 'C')

                        pdf.ln(10)
                        pdf.set_font("Arial", "I", 8)
                        pdf.cell(0, 10, f"Wygenerowano: {datetime.now().strftime('%Y-%m-%d %H:%M')} | ProCalc", align='R')
                        
                        pdf_bytes = pdf.output(dest="S")
                        safe_bytes = pdf_bytes.encode('latin-1', 'replace') if isinstance(pdf_bytes, str) else bytes(pdf_bytes)

                        st.download_button(
                            label="Pobierz Raport PDF",
                            data=safe_bytes,
                            file_name=f"Szpachlowanie_Raport_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Błąd PDF: {e}")


# --- SEKCJA: PODŁOGI ---
elif branza == "Podłogi":
    st.header("Kalkulator Podłóg: Panele, Deska i Płytki")
    
    # --- BAZA CENOWA CHEMII GLAZURNICZEJ ---
    baza_kleje_plytki = {
        "Atlas Geoflex (Żelowy S1) - 25kg": 75.0,
        "Mapei Keraflex Extra S1 - 25kg": 80.0,
        "Kerakoll Bioflex (Żelowy S1) - 25kg": 85.0,
        "Atlas Plus (Wysokoelastyczny S1) - 25kg": 105.0,
        "Kerakoll H40 No Limits (Top Żel) - 25kg": 125.0
    }

    tab_p1, tab_p2 = st.tabs(["Szybka Wycena", "Kosztorys PRO"])

    # ==========================================
    # TAB 1: SZYBKA WYCENA
    # ==========================================
    with tab_p1:
        st.subheader("Błyskawiczny szacunek kosztów")
        m2_fast_p = st.number_input("Metraż podłogi (m2):", min_value=1.0, value=20.0, step=1.0, key="pod_m_fast")
        typ_fast = st.radio("Typ posadzki:", ["Panele (Pływające)", "Płytki / Gres"])
        
        if typ_fast == "Panele (Pływające)":
            k_rob_fast = m2_fast_p * 45
            k_mat_fast = m2_fast_p * 15
        else:
            k_rob_fast = m2_fast_p * 120
            k_mat_fast = m2_fast_p * 45
            
        total_fast = k_rob_fast + k_mat_fast
        
        st.success(f"### Szacowany koszt realizacji: ok. {round(total_fast)} PLN")
        st.caption("Cena nie zawiera zakupu samych paneli/płytek.")
        
        c_f1, c_f2 = st.columns(2)
        c_f1.metric("Szacowana Robocizna", f"{round(k_rob_fast)} PLN")
        c_f2.metric("Szacowana Chemia/Dodatki", f"{round(k_mat_fast)} PLN")
        
        st.info("Przejdź do zakładki Kosztorys PRO, aby wyliczyć zapasy, wybrać konkretny klej i wygenerować raport PDF.")

    # ==========================================
    # TAB 2: KOSZTORYS PRO
    # ==========================================
    with tab_p2:
        # --- BLOKADA PRO ---
        if not st.session_state.zalogowany or st.session_state.pakiet != "PRO":
            st.error("🔒 **Dostęp zablokowany**")
            st.warning("Zaawansowane wyliczenia zużycia klejów, systemów poziomujących oraz generowanie PDF dostępne są w wersji PRO.")
            
            _, col_k, _ = st.columns([1, 2, 1])
            with col_k:
                if st.button("Odblokuj dostęp (Logowanie)", use_container_width=True, key="btn_odblokuj_podlogi"):
                    st.session_state.przekierowanie = True  
                    st.rerun()  
        else:
            # --- TYLKO DLA ZALOGOWANYCH PRO ---
            col_p1, col_p2 = st.columns([1, 1.2])
            
            with col_p1:
                st.subheader("Konfiguracja posadzki")
                m2_p = st.number_input("Dokładny metraż podłogi (m2):", min_value=0.1, value=20.0, step=0.1, key="pod_m_pro")
                
                system_montazu = st.radio("System montażu:", 
                                         ["Pływający (Na podkładzie)", 
                                          "Klejony (Deska na kleju)", 
                                          "Płytki / Gres (System poziomujący)"])
                
                if system_montazu == "Płytki / Gres (System poziomujący)":
                    st.markdown("---")
                    st.write("**Parametry płytek i chemia**")
                    c_pl1, c_pl2 = st.columns(2)
                    dl_p = c_pl1.number_input("Długość płytki (cm):", 10, 200, 60)
                    sz_p = c_pl2.number_input("Szerokość płytki (cm):", 10, 200, 60)
                    typ_ukladania = "Płytki (10% zapasu)"
                    m2_paczka = st.number_input("M2 w paczce płytek:", min_value=0.1, value=1.44, step=0.01)
                    wybrany_klej_plytki = st.selectbox("Wybierz klej do gresu:", list(baza_kleje_plytki.keys()))
                else:
                    st.markdown("---")
                    st.write("**Parametry deski/paneli**")
                    typ_ukladania = st.selectbox("Sposób układania:", ["Zwykły panel (7% zapasu)", "Jodełka (20% zapasu)"])
                    m2_paczka = st.number_input("M2 w paczce paneli/desek:", min_value=0.1, value=2.22, step=0.01)
                
                st.markdown("---")
                domyslna_stawka = 120 if "Płytki" in system_montazu else (45 if "Zwykły" in typ_ukladania else 100)
                stawka_podl = st.number_input("Stawka za m2 montażu (zł):", 1, 300, domyslna_stawka)

            # --- LOGIKA OBLICZEŃ ---
            if "Płytki" in system_montazu:
                zapas = 0.10
            else:
                zapas = 0.07 if "Zwykły" in typ_ukladania else 0.20
                
            m2_z_zapasem = m2_p * (1 + zapas)
            paczki_szt = int(m2_z_zapasem / m2_paczka + 0.99)
            
            info_zakup = [] 
            koszt_akc = 0

            if system_montazu == "Pływający (Na podkładzie)":
                wybrany_mat = st.selectbox("Rodzaj podkładu:", ["Premium (Rolka 8m2)", "Ecopor (Paczka 7m2)", "Standard (Pianka 10m2)"])
                wydajnosci = {"Premium (Rolka 8m2)": 8, "Ecopor (Paczka 7m2)": 7, "Standard (Pianka 10m2)": 10}
                ceny_p = {"Premium (Rolka 8m2)": 180, "Ecopor (Paczka 7m2)": 55, "Standard (Pianka 10m2)": 35}
                szt_podkladu = int(m2_p / wydajnosci[wybrany_mat] + 0.99)
                koszt_akc = szt_podkladu * ceny_p[wybrany_mat]
                info_zakup.append((f"Podkład {wybrany_mat}", f"{szt_podkladu} szt."))

            elif system_montazu == "Klejony (Deska na kleju)":
                wiader_kleju = int(m2_p / 12 + 0.99) 
                baniek_gruntu = int(m2_p / 30 + 0.99) 
                koszt_akc = (wiader_kleju * 280) + (baniek_gruntu * 60) 
                info_zakup.append(("Klej poliuretanowy do podłóg (15kg)", f"{wiader_kleju} wiader"))
                info_zakup.append(("Grunt podkładowy (5L)", f"{baniek_gruntu} baniek"))

            else: # Płytki / Gres
                zuzycie_m2 = (1 / ((dl_p/100) * (sz_p/100))) * 4
                suma_klipsow = int(zuzycie_m2 * m2_p * 1.1)
                op_klipsy = int(suma_klipsow / 100 + 0.99)
                
                kg_kleju_gres = m2_p * 5.0
                worki_kleju = int(kg_kleju_gres / 25 + 0.99)
                
                cena_wybranego_kleju = baza_kleje_plytki[wybrany_klej_plytki]
                koszt_akc = (op_klipsy * 40) + (worki_kleju * cena_wybranego_kleju)
                info_zakup.append(("System poziomujący (klipsy)", f"{op_klipsy} op. (po 100 szt.)"))
                info_zakup.append((f"{wybrany_klej_plytki}", f"{worki_kleju} worków"))

            k_robocizna = m2_p * stawka_podl
            usluga_plus_chemia = k_robocizna + koszt_akc 

            with col_p2:
                st.subheader("Podsumowanie Kosztorysu")
                
                st.success(f"### KOSZT REALIZACJI: **{round(usluga_plus_chemia)} PLN**")
                st.caption("Cena obejmuje robociznę oraz niezbędną chemię. Nie zawiera ceny okładziny.")

                c1, c2 = st.columns(2)
                c1.metric("Robocizna", f"{round(k_robocizna)} PLN")
                c2.metric("Chemia / Podkłady", f"{round(koszt_akc)} PLN")

                st.markdown("---")
                st.subheader("Lista materiałowa")
                
                st.write(f"• **Okładzina główna:** {paczki_szt} paczek")
                st.caption(f"Powierzchnia z uwzględnieniem {int(zapas*100)}% zapasu: {round(m2_z_zapasem, 2)} m2")
                
                for nazwa, ilosc in info_zakup:
                    st.write(f"• **{nazwa}:** {ilosc}")
                
                if "Płytki" in system_montazu:
                    st.info(f"Wyliczono system poziomujący dla formatu {dl_p}x{sz_p} cm.")
                
                st.markdown("---")

                # --- GENERATOR PDF (PODŁOGI) ---
                try:
                    from fpdf import FPDF
                    from datetime import datetime
                    import os
                    import base64

                    def czysc_tekst(tekst):
                        pl_znaki = {'ą':'a','ć':'c','ę':'e','ł':'l','ń':'n','ó':'o','ś':'s','ź':'z','ż':'z','Ą':'A','Ć':'C','Ę':'E','Ł':'L','Ń':'N','Ó':'O','Ś':'S','Ź':'Z','Ż':'Z'}
                        for pl, ang in pl_znaki.items(): tekst = tekst.replace(pl, ang)
                        return tekst.encode('latin-1', 'replace').decode('latin-1')

                    if st.button("Generuj Kosztorys PDF", use_container_width=True, key="pod_pdf_btn"):
                        pdf = FPDF()
                        pdf.add_page()
                        
                        f_path = "Inter-Regular.ttf"
                        if os.path.exists(f_path):
                            pdf.add_font("Inter", "", f_path)
                            pdf.set_font("Inter", size=12)
                        else:
                            pdf.set_font("Arial", size=12)
                        
                        pdf.set_font(pdf.font_family, size=16)
                        pdf.cell(0, 15, "KOSZTORYS: PRACE POSADZKOWE", ln=True, align='C')
                        pdf.ln(5)

                        pdf.set_fill_color(245, 245, 245)
                        pdf.set_font(pdf.font_family, size=12)
                        
                        pdf.cell(95, 10, " Metraz calkowity:", 1)
                        pdf.cell(95, 10, f" {m2_p} m2", 1, 1)
                        pdf.cell(95, 10, " System montazu:", 1)
                        pdf.cell(95, 10, f" {czysc_tekst(system_montazu)}", 1, 1)
                        
                        if "Płytki" in system_montazu:
                            pdf.cell(95, 10, " Format plytki:", 1)
                            pdf.cell(95, 10, f" {dl_p}x{sz_p} cm", 1, 1)

                        pdf.ln(10)
                        pdf.cell(95, 10, " Robocizna (Montaz):", 1)
                        pdf.cell(95, 10, f" {round(k_robocizna)} PLN", 1, 1)
                        pdf.cell(95, 10, " Chemia i materialy:", 1)
                        pdf.cell(95, 10, f" {round(koszt_akc)} PLN", 1, 1)
                        
                        pdf.set_font(pdf.font_family, size=13)
                        pdf.cell(95, 12, " LACZNIE REALIZACJA:", 1, 0, 'L', True)
                        pdf.cell(95, 12, f" {round(usluga_plus_chemia)} PLN", 1, 1, 'L', True)
                        
                        pdf.ln(10)
                        pdf.set_font(pdf.font_family, size=12)
                        pdf.cell(0, 10, "LISTA MATERIALOWA DO ZAMOWIENIA:", ln=True)
                        pdf.set_font(pdf.font_family, size=10)
                        
                        pdf.cell(0, 7, f"- Okladzina: {paczki_szt} paczek (zawiera {int(zapas*100)}% zapasu)", ln=True)
                        for nazwa, ilosc in info_zakup:
                            pdf.cell(0, 7, f"- {czysc_tekst(nazwa)}: {czysc_tekst(ilosc)}", ln=True)

                        pdf_bytes = pdf.output(dest="S").encode('latin-1')
                        pdf_b64 = base64.b64encode(pdf_bytes).decode()
                        href = f'<a href="data:application/pdf;base64,{pdf_b64}" download="Kosztorys_Podloga.pdf" style="display: block; text-align: center; padding: 15px; background-color: #00D395; color: white; text-decoration: none; border-radius: 10px; font-weight: bold; font-size: 18px; margin-top: 10px;">Pobierz Raport PDF</a>'
                        st.markdown(href, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Błąd PDF: {e}")
                      
# --- SEKCJA: TYNKOWANIE ---
elif branza == "Tynkowanie":
    st.header("Kalkulator Tynków i Suchego Tynku")
    
    # --- BAZA DANYCH (Zaktualizowane ceny rynkowe) ---
    baza_masy = {
        "Knauf Uniflott (25kg)": 140, 
        "Knauf Vario (5kg)": 45,
        "Dolina Nidy Start (20kg)": 50,
        "Franspol (20kg)": 60
    }

    baza_tynkow = {
        "Knauf MP 75 (Maszynowy Gipsowy)": {"cena": 34, "waga": 30, "norma": 0.8, "typ": "mokry"},
        "Baumit MPI25 Cem-Wap": {"cena": 32, "waga": 30, "norma": 1.4, "typ": "mokry"},
        "Wyklejanie Płytami GK (Suchy Tynk)": {"cena_plyta": 35, "cena_klej": 28, "typ": "drywall"}
    }
    
    baza_grunt_kwarc = {
        "Dolina Nidy Inter-Grunt (20kg)": 130, 
        "Knauf Betokontakt (20kg)": 220, 
        "Atlas Grunto-Plast (20kg)": 145
    }

    tab_t1, tab_t2 = st.tabs(["Szybka Wycena", "Detale PRO"])

    # --- TAB 1: SZYBKA WYCENA ---
    with tab_t1:
        st.subheader("Błyskawiczny szacunek")
        m2_podl_fast = st.number_input("Metraż mieszkania (podłoga m2):", 1.0, 500.0, 50.0, key="tyn_m_fast")
        
        # Uproszczona logika: Średnio 3x metraż podłogi, średnia cena 85 zł/m2 (robocizna + mat)
        szacunkowy_metraz = m2_podl_fast * 3.0
        szacunkowy_koszt = szacunkowy_metraz * 85
        
        st.metric("Przybliżony koszt całkowity", f"{round(szacunkowy_koszt)} PLN")
        st.caption(f"Szacowany metraż ścian i sufitów: ok. {round(szacunkowy_metraz)} m²")
        
        st.markdown("---")
        st.info("""
        **Co zyskujesz w wersji PRO?**
        * Wybór konkretnych systemów (Gipsowe, Cem-Wap, GK).
        * Precyzyjne obliczenia stolarki (okna, narożniki, folie).
        * Pełna lista zakupów (liczba worków, płyt, rolek taśm).
        * Profesjonalny raport PDF z normami zużycia.
        """)

    # --- TAB 2: DETALE PRO ---
    with tab_t2:
        # --- BLOKADA PRO ---
        if not st.session_state.zalogowany or st.session_state.pakiet != "PRO":
            st.error("🔒 **Dostęp zablokowany**")
            st.warning("Precyzyjne zestawienie materiałów dla tynków mokrych i suchych dostępne jest tylko dla użytkowników PRO.")
            
            _, col_k, _ = st.columns([1, 2, 1])
            with col_k:
                if st.button("Odblokuj dostęp (Logowanie)", use_container_width=True, key="btn_odblokuj_tynki"):
                    st.session_state.przekierowanie = True  
                    st.rerun()  
        else:
            # --- TYLKO DLA ZALOGOWANYCH PRO ---
            col_t1, col_t2 = st.columns([1, 1.2])
            
            with col_t1:
                st.subheader("Konfiguracja")
                m2_podl_pro = st.number_input("Metraż podłogi (m2):", 1.0, 500.0, 50.0, key="tyn_m_pro")
                wybrany_tynk = st.selectbox("Wybierz system:", list(baza_tynkow.keys()))
                dane_t = baza_tynkow[wybrany_tynk]
                
                # Logika powierzchni PRO
                mnoznik = 3.5 if dane_t["typ"] == "mokry" else 2.5
                m2_rob_pro = m2_podl_pro * mnoznik
                st.warning(f"Powierzchnia obliczeniowa: **{round(m2_rob_pro, 1)} m²**")

                if dane_t["typ"] == "drywall":
                    typ_tasmy = st.radio("Rodzaj zbrojenia łączy:", ["Wszystko Tuff-Tape (Pancerne)", "Tuff-Tape + Flizelina"])
                    wybrana_masa = st.selectbox("Masa do spoinowania:", list(baza_masy.keys()))
                    grubosc_t = 0 
                else:
                    wybrany_grunt_t = st.selectbox("Wybierz grunt kwarcowy:", list(baza_grunt_kwarc.keys()))
                    grubosc_t = st.slider("Średnia grubość tynku (mm):", 10, 40, 15)
                
                stawka_rob_t = st.number_input("Stawka robocizny (zł/m2):", 10, 200, 50)

                st.markdown("---")
                st.subheader("Stolarka (Okna i Drzwi)")
                
                std_okna = {
                    "Własny wymiar": None,
                    "60x60 (Łazienkowe)": (60, 60),
                    "90x120 (Standard 1)": (90, 120),
                    "120x120 (Standard 2)": (120, 120),
                    "150x150 (Duże)": (150, 150),
                    "90x210 (Balkonowe)": (90, 210),
                    "240x210 (Tarasowe HS)": (240, 210),
                    "100x210 (Drzwi wejściowe)": (100, 210)
                }

                wybor_okna = st.selectbox("Wybierz typ okna:", list(std_okna.keys()))
                
                col_o1, col_o2 = st.columns(2)
                if wybor_okna == "Własny wymiar":
                    w_szer = col_o1.number_input("Szerokość (cm):", 10, 600, 100, key="w_szer_tyn")
                    w_wys = col_o2.number_input("Wysokość (cm):", 10, 600, 120, key="w_wys_tyn")
                else:
                    w_szer, w_wys = std_okna[wybor_okna]
                    col_o1.info(f"Szer: {w_szer} cm")
                    col_o2.info(f"Wys: {w_wys} cm")

                ile_okien = st.number_input("Liczba takich okien (szt.):", 1, 50, 1, key="ile_okien_tyn")

                if "lista_okien_tyn" not in st.session_state:
                    st.session_state.lista_okien_tyn = []

                if st.button("Dodaj okna do zestawienia", use_container_width=True, key="btn_add_okno_tyn"):
                    st.session_state.lista_okien_tyn.append({
                        "nazwa": wybor_okna,
                        "szer": w_szer,
                        "wys": w_wys,
                        "szt": ile_okien
                    })
                    st.rerun()

                if st.session_state.lista_okien_tyn:
                    for i, o in enumerate(st.session_state.lista_okien_tyn):
                        c_ok1, c_ok2 = st.columns([4, 1])
                        c_ok1.caption(f"{o['szt']}x {o['nazwa']} ({o['szer']}x{o['wys']})")
                        if c_ok2.button("Usuń", key=f"del_o_tyn_{i}"):
                            st.session_state.lista_okien_tyn.pop(i)
                            st.rerun()

            # --- OBLICZENIA PRO ---
            lista_zakupow = []
            if dane_t["typ"] == "mokry":
                kg_na_m2_t = dane_t["norma"] * grubosc_t
                kg_razem_t = m2_rob_pro * kg_na_m2_t
                worki_t = int(kg_razem_t / dane_t["waga"] + 0.99)
                wiadra_gruntu = int((m2_rob_pro * 0.3) / 20 + 0.99)
                koszt_mat_t = (worki_t * dane_t["cena"]) + (wiadra_gruntu * baza_grunt_kwarc[wybrany_grunt_t]) + (m2_rob_pro * 5)
                lista_zakupow = [
                    (f"Tynk {wybrany_tynk}", f"{worki_t} worków"),
                    (f"Grunt kwarcowy {wybrany_grunt_t}", f"{wiadra_gruntu} wiader 20kg")
                ]
            else:
                liczba_plyt = int((m2_rob_pro * 1.1) / 3.12 + 0.99)
                worki_kleju = int(liczba_plyt / 2.5 + 0.99)
                worki_masy = int((m2_rob_pro * 0.5) / 25 + 0.99)
                
                mb_laczen = m2_rob_pro * 1.5
                if typ_tasmy == "Wszystko Tuff-Tape (Pancerne)":
                    rolki_tuff = int(mb_laczen / 30 + 0.99)
                    cena_tasmy = rolki_tuff * 150
                    zbrojenie_lista = [("Taśma Tuff-Tape (30m)", f"{rolki_tuff} rolka/i")]
                else:
                    rolki_tuff = int((m2_rob_pro * 0.4) / 30 + 0.99)
                    rolki_fliz = int((m2_rob_pro * 1.1) / 25 + 0.99)
                    cena_tasmy = (rolki_tuff * 150) + (rolki_fliz * 20)
                    zbrojenie_lista = [
                        ("Taśma Tuff-Tape (30m)", f"{rolki_tuff} rolka/i"),
                        ("Taśma flizelina (25m)", f"{rolki_fliz} rolka/i")
                    ]

                koszt_mat_t = (liczba_plyt * dane_t["cena_plyta"]) + (worki_kleju * dane_t["cena_klej"]) + \
                              (worki_masy * baza_masy[wybrana_masa]) + cena_tasmy + (m2_rob_pro * 2)
                
                lista_zakupow = [
                    ("Płyty GK (1.2x2.6m)", f"{liczba_plyt} szt."),
                    ("Klej gipsowy do płyt", f"{worki_kleju} worków"),
                    (f"Masa spoinowa {wybrana_masa}", f"{worki_masy} szt.")
                ]
                lista_zakupow.extend(zbrojenie_lista)

            # --- LOGIKA STOLARKI ---
            total_mb_naroznikow = 0.0
            total_m2_folii = 0.0
            total_mb_tasmy = 0.0

            for o in st.session_state.get("lista_okien_tyn", []):
                s = o["szer"] / 100 
                w = o["wys"] / 100
                szt = o["szt"]
                mb_na_okno = (2 * w) + s
                total_mb_naroznikow += (mb_na_okno * 1.30) * szt
                total_m2_folii += (s * w * szt) * 1.15
                total_mb_tasmy += ((2 * s + 2 * w) * 1.10) * szt

            szt_naroznik_3m = int(total_mb_naroznikow / 3 + 0.99)
            rolki_tasmy_50m = int(total_mb_tasmy / 50 + 0.99)
            szt_folii_op = int(total_m2_folii / 20 + 0.99)

            koszt_stolarki = (szt_naroznik_3m * 8) + (rolki_tasmy_50m * 25) + (szt_folii_op * 15)

            if total_mb_naroznikow > 0:
                lista_zakupow.append(("Narożniki aluminiowe (3m)", f"{szt_naroznik_3m} szt."))
                lista_zakupow.append(("Taśma malarska (50m)", f"{rolki_tasmy_50m} rolka/i"))
                lista_zakupow.append(("Folia ochronna okienna", f"{szt_folii_op} op."))

            koszt_mat_t += koszt_stolarki
            koszt_rob_t = m2_rob_pro * stawka_rob_t
            suma_tynki = koszt_mat_t + koszt_rob_t

            with col_t2:
                st.subheader("Wynik PRO")
                st.success(f"### RAZEM: **{round(suma_tynki)} PLN**")
                
                c1, c2 = st.columns(2)
                c1.metric("Robocizna", f"{round(koszt_rob_t)} zł")
                c2.metric("Materiały", f"{round(koszt_mat_t)} zł")

                st.markdown("---")
                st.subheader("Zestawienie materiałowe")
                for przedmiot, ilosc in lista_zakupow:
                    st.write(f"• **{przedmiot}:** {ilosc}")

                # --- GENERATOR PDF ---
                try:
                    from fpdf import FPDF
                    from datetime import datetime
                    import base64
                    import os

                    def czysc_tekst(tekst):
                        pl_znaki = {'ą':'a','ć':'c','ę':'e','ł':'l','ń':'n','ó':'o','ś':'s','ź':'z','ż':'z','Ą':'A','Ć':'C','Ę':'E','Ł':'L','Ń':'N','Ó':'O','Ś':'S','Ź':'Z','Ż':'Z'}
                        for pl, ang in pl_znaki.items(): tekst = tekst.replace(pl, ang)
                        return tekst.encode('latin-1', 'replace').decode('latin-1')

                    if st.button("Generuj Raport PDF", use_container_width=True, key="btn_pdf_tyn"):
                        pdf = FPDF()
                        pdf.add_page()
                        
                        f_path = "Inter-Regular.ttf"
                        if os.path.exists(f_path):
                            pdf.add_font("Inter", "", f_path)
                            pdf.set_font("Inter", size=12)
                        else:
                            pdf.set_font("Arial", size=12)

                        pdf.set_font(pdf.font_family, size=16)
                        pdf.cell(0, 15, "OFERTA: TYNKOWANIE / SUCHY TYNK", ln=True, align='C')
                        pdf.ln(5)

                        pdf.set_fill_color(245, 245, 245)
                        pdf.set_font(pdf.font_family, size=12)
                        
                        pdf.cell(95, 10, " Powierzchnia prac:", 1)
                        pdf.cell(95, 10, f" {round(m2_rob_pro, 1)} m2", 1, 1)
                        pdf.cell(95, 10, " Robocizna:", 1)
                        pdf.cell(95, 10, f" {round(koszt_rob_t)} PLN", 1, 1)
                        pdf.cell(95, 10, " Materialy:", 1)
                        pdf.cell(95, 10, f" {round(koszt_mat_t)} PLN", 1, 1)
                        pdf.set_font(pdf.font_family, size=13)
                        pdf.cell(95, 12, " SUMA CALKOWITA:", 1, 0, 'L', True)
                        pdf.cell(95, 12, f" {round(suma_tynki)} PLN", 1, 1, 'L', True)

                        pdf.ln(10)
                        pdf.set_font(pdf.font_family, size=12)
                        pdf.cell(0, 10, "LISTA MATERIALOW:", ln=True)
                        pdf.set_font(pdf.font_family, size=10)
                        for przedmiot, ilosc in lista_zakupow:
                            pdf.cell(0, 7, f"- {czysc_tekst(przedmiot)}: {czysc_tekst(ilosc)}", ln=True)

                        pdf_bytes = pdf.output(dest="S").encode('latin-1')
                        pdf_b64 = base64.b64encode(pdf_bytes).decode()
                        href = f'<a href="data:application/pdf;base64,{pdf_b64}" download="Oferta_Tynki.pdf" style="display: block; text-align: center; padding: 15px; background-color: #00D395; color: white; text-decoration: none; border-radius: 10px; font-weight: bold; font-size: 18px; margin-top: 10px;">Pobierz Raport PDF</a>'
                        st.markdown(href, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Problem z PDF: {e}")
                    
# --- SEKCJA: SUCHA ZABUDOWA ---
elif branza == "Sucha Zabudowa":
    st.header("Kompleksowe Systemy G-K")
    
    # --- BAZA CENOWA ---
    baza_mat_gk = {
        "Plyta GK 12.5mm (szt)": 32.0, 
        "Profil CD60 (3mb)": 16.0, 
        "Profil UD27 (3mb)": 11.0,
        "Profil CW50 (3mb)": 19.0, 
        "Profil UW50 (3mb)": 15.0, 
        "Profil CW75 (3mb)": 23.0, 
        "Profil UW75 (3mb)": 18.0, 
        "Profil CW100 (3mb)": 28.0, 
        "Profil UW100 (3mb)": 22.0, 
        "Profil UA50 (3mb)": 75.0,
        "Profil UA75 (3mb)": 85.0,
        "Profil UA100 (3mb)": 95.0,
        "Wieszak ES / Obrotowy (szt)": 1.5, 
        "Wkrety TN25 (1000szt)": 40.0,
        "Wkrety TN35 (1000szt)": 50.0, 
        "Kolki 8x60 (100szt)": 35.0, 
        "Welna (m2)": 16.0
    }
    
    baza_masy_gk = {
        "Knauf Uniflott (25kg)": 140, 
        "Rigips Vario (25kg)": 145, 
        "Dolina Nidy Start (20kg)": 60, 
        "Franspol GS-6(20kg)": 96
    }

    if "pokoje_sufit" not in st.session_state:
        st.session_state.pokoje_sufit = []

    tab_gk1, tab_gk2 = st.tabs(["Szybka Wycena", "Kosztorys PRO"])

    # ==========================================
    # TAB 1: SZYBKA WYCENA
    # ==========================================
    with tab_gk1:
        st.subheader("Blyskawiczny szacunek kosztow")
        m2_fast = st.number_input("Przyblizony metraz zabudowy (m2):", min_value=1.0, value=20.0, key="gk_fast_m2")
        
        # Uśrednione stawki: robota 120, materiał 75
        k_rob_fast = m2_fast * 120
        k_mat_fast = m2_fast * 75
        total_fast = k_rob_fast + k_mat_fast
        
        st.success(f"### Szacowany koszt calkowity: ok. {round(total_fast)} PLN")
        
        c_f1, c_f2 = st.columns(2)
        c_f1.metric("Szacowana Robocizna", f"{round(k_rob_fast)} PLN")
        c_f2.metric("Szacowane Materialy", f"{round(k_mat_fast)} PLN")
        
        st.info("Powyzsza wycena jest usredniona. Przejdz do zakladki Kosztorys PRO, aby wyliczyc systemy CD/UD lub CW/UW i pobrac liste zakupow.")

    # ==========================================
    # TAB 2: KOSZTORYS PRO
    # ==========================================
    with tab_gk2:
        # --- BLOKADA PRO ---
        if not st.session_state.zalogowany or st.session_state.pakiet != "PRO":
            st.error("🔒 **Dostęp zablokowany**")
            st.warning("Zaawansowane wyliczenia konstrukcji szkieletowych, wieszaków i izolacji dostępne są w wersji PRO.")
            
            _, col_k, _ = st.columns([1, 2, 1])
            with col_k:
                if st.button("Odblokuj dostęp (Logowanie)", use_container_width=True, key="btn_odblokuj_gk"):
                    st.session_state.przekierowanie = True  
                    st.rerun()  
        else:
            # --- TYLKO DLA ZALOGOWANYCH PRO ---
            m2_gk = 0.0
            robocizna = 0
            total_material = 0
            szer_profilu = 60
            laczniki_cd1 = laczniki_cd2 = laczniki_krzyzowe = 0
            szt_cd = szt_ud = szt_wieszaki = 0
            szt_cw = szt_uw = szt_ua = 0
            grubosc_welny = None
            izolacja_gk = False
            plytowanie = "1xGK (Jednostronnie)"
            lista_z = []
            
            col_g1, col_g2 = st.columns([1, 1.2])

            with col_g1:
                st.subheader("Konfiguracja konstrukcji")
                rodzaj_gk = st.radio("Co budujemy?", ["Sufit Podwieszany", "Sciana Dzialowa"], key="gk_type_pro")
                dl_profilu_cd = 3.0
                
                if rodzaj_gk == "Sufit Podwieszany":
                    st.markdown("---")
                    st.write("**Dodaj pomieszczenia do zabudowy sufitu:**")
                    c1, c2, c3 = st.columns([2,1,1])
                    nazwa_suf = c1.text_input("Pomieszczenie:", placeholder="np. Salon", key="suf_n_pro")
                    dl_suf = c2.number_input("Dl. (m):", min_value=0.1, value=5.0, key="suf_d_pro")
                    sz_suf = c3.number_input("Szer. (m):", min_value=0.1, value=4.0, key="suf_s_pro")
                    typ_stelaza_suf = st.radio("Rodzaj stelaza dla tego pokoju:", ["Pojedynczy", "Krzyzowy"], horizontal=True, key="suf_typ_pro")

                    if st.button("Dodaj sufit do listy", use_container_width=True, key="btn_add_suf_pro"):
                        st.session_state.pokoje_sufit.append({
                            "nazwa": nazwa_suf if nazwa_suf else f"Pokoj {len(st.session_state.pokoje_sufit)+1}",
                            "dl": dl_suf,
                            "sz": sz_suf,
                            "typ": typ_stelaza_suf
                        })
                        st.rerun()

                    if st.session_state.pokoje_sufit:
                        for i, p in enumerate(st.session_state.pokoje_sufit):
                            cc1, cc2 = st.columns([4, 1])
                            pow_p = p['dl'] * p['sz']
                            cc1.caption(f"{p['nazwa']} ({p['dl']}x{p['sz']}m) - {round(pow_p, 1)} m2 [{p['typ']}]")
                            if cc2.button("Usun", key=f"del_suf_pro_{i}"):
                                st.session_state.pokoje_sufit.pop(i)
                                st.rerun()
                        
                        # Sumowanie
                        for p in st.session_state.pokoje_sufit:
                            p_dl, p_sz = p['dl'], p['sz']
                            p_m2 = p_dl * p_sz
                            m2_gk += p_m2
                            szt_ud += int(((p_dl + p_sz) * 2 * 1.1) / 3) + 1
                            szt_wieszaki += int(p_m2 / 0.7) + 1
                            rozstaw_cd1 = 0.40 if p['typ'] == "Pojedynczy" else 1.10
                            liczba_cd1 = int(p_sz / rozstaw_cd1) + 1
                            odcinki_cd1 = int(p_dl / dl_profilu_cd)
                            szt_cd += liczba_cd1 * (odcinki_cd1 + (1 if p_dl % dl_profilu_cd > 0 else 0))
                            laczniki_cd1 += odcinki_cd1 * liczba_cd1

                            if p['typ'] == "Krzyzowy":
                                liczba_cd2 = int(p_dl / 0.40) + 1
                                odcinki_cd2 = int(p_sz / dl_profilu_cd)
                                szt_cd += liczba_cd2 * (odcinki_cd2 + (1 if p_sz % dl_profilu_cd > 0 else 0))
                                laczniki_cd2 += odcinki_cd2 * liczba_cd2
                                laczniki_krzyzowe += (liczba_cd1 * liczba_cd2)
                else:
                    # Ściana Działowa
                    c1, c2 = st.columns(2)
                    szer_sciany = c1.number_input("Dlugosc scianki (m):", min_value=0.1, value=4.0, key="wall_l_gk")
                    wys_sciany = c2.number_input("Wysokosc scianki (m):", min_value=0.1, value=2.6, key="wall_h_gk")
                    m2_gk = szer_sciany * wys_sciany
                    szer_profilu = st.selectbox("Profil scianki (CW/UW):", [50, 75, 100], format_func=lambda x: f"{x} mm", key="wall_prof_gk")
                    plytowanie = st.radio("Plytowanie:", ["1xGK (Jednostronnie)", "2xGK (Dwustronnie)", "2xGK (Z obu stron - 4 warstwy)"], key="wall_ply_gk")
                    n_drzwi = st.number_input("Otwory drzwiowe (Profil UA):", min_value=0, value=0, key="wall_d_gk")
                    szt_uw = int((szer_sciany * 2 * 1.1) / 3) + 1
                    szt_cw = int((szer_sciany / 0.6) * (wys_sciany / 3) + 1)
                    szt_ua = n_drzwi * 2

                st.markdown("---")
                st.subheader("Izolacja i Wykonczenie")
                izolacja_gk = st.checkbox("Wypelnienie welna akustyczna", key="gk_izol_pro")
                if izolacja_gk:
                    opcje_welny = [50, 75, 100, 150]
                    idx = opcje_welny.index(szer_profilu) if szer_profilu in opcje_welny else 0
                    grubosc_welny = st.selectbox("Grubosc welny:", opcje_welny, index=idx, format_func=lambda x: f"{x} mm")

                typ_tasmy = st.radio("Zbrojenie laczy:", ["Tuff-Tape (Calosc)", "Flizelina + Tuff-Tape"], key="gk_tasma_pro")
                wybrana_masa = st.selectbox("Masa do spoinowania:", list(baza_masy_gk.keys()), key="gk_masa_pro")
                stawka_gk = st.number_input("Stawka robocizny (zl/m2):", 1, 300, 110, key="gk_rob_pro")

            # --- LOGIKA MATERIAŁOWA ---
            if m2_gk > 0:
                nad = 1.10
                mnoz_p = 2 if "Dwustronnie" in plytowanie else (4 if "4 warstwy" in plytowanie else 1)
                szt_plyt = int(((m2_gk * mnoz_p) * nad) / 3.12) + 1
                wkret_25 = int(m2_gk * 20 * mnoz_p * nad)
                szt_pchelki = int(m2_gk * 12) if rodzaj_gk == "Sufit Podwieszany" else int(m2_gk * 5)

                if "Calosc" in typ_tasmy:
                    mb_tuff, mb_fliz = (m2_gk * mnoz_p * 1.5), 0
                else:
                    mb_tuff, mb_fliz = (m2_gk * mnoz_p * 0.4), (m2_gk * mnoz_p * 1.1)
                
                rolki_tuff = int(mb_tuff / 30) + (1 if mb_tuff > 0 else 0)
                rolki_fliz = int(mb_fliz / 25) + (1 if mb_fliz > 0 else 0)
                worki_masy = int((m2_gk * 0.5 * mnoz_p) / 25 + 0.99)

                koszt_plyt = szt_plyt * baza_mat_gk["Plyta GK 12.5mm (szt)"]
                koszt_profile = (szt_cd * baza_mat_gk["Profil CD60 (3mb)"]) + (szt_ud * baza_mat_gk["Profil UD27 (3mb)"]) + \
                                (szt_cw * baza_mat_gk.get(f"Profil CW{szer_profilu} (3mb)", 0)) + \
                                (szt_uw * baza_mat_gk.get(f"Profil UW{szer_profilu} (3mb)", 0)) + \
                                (szt_ua * baza_mat_gk.get(f"Profil UA{szer_profilu} (3mb)", 0))
                
                total_material = koszt_plyt + koszt_profile + (szt_wieszaki * 1.5) + (m2_gk * 16 if izolacja_gk else 0) + \
                                 (worki_masy * baza_masy_gk[wybrana_masa]) + (rolki_tuff * 150) + (rolki_fliz * 20) + (m2_gk * 15)
                robocizna = m2_gk * stawka_gk

                # Lista zakupów
                if rodzaj_gk == "Sufit Podwieszany":
                    lista_z.append(("Profile CD60 (3m)", f"{szt_cd} szt."))
                    lista_z.append(("Profile UD27 (3m)", f"{szt_ud} szt."))
                    lista_z.append(("Wieszaki ES/Obrotowe", f"{szt_wieszaki} szt."))
                else:
                    lista_z.append((f"Profile CW{szer_profilu} (3m)", f"{szt_cw} szt."))
                    lista_z.append((f"Profile UW{szer_profilu} (3m)", f"{szt_uw} szt."))
                
                lista_z.append(("Plyty G-K 12.5mm", f"{szt_plyt} szt."))
                lista_z.append(("Wkrety TN25", f"{int(wkret_25/1000)+1} op."))
                lista_z.append((f"Masa ({wybrana_masa})", f"{worki_masy} szt."))

            with col_g2:
                st.subheader("Podsumowanie")
                st.success(f"### RAZEM: **{round(total_material + robocizna)} PLN**")
                c_r1, c_r2 = st.columns(2)
                c_r1.metric("Robocizna", f"{round(robocizna)} PLN")
                c_r2.metric("Materialy", f"{round(total_material)} PLN")
                
                st.markdown("---")
                st.subheader("Lista zakupow")
                if m2_gk > 0:
                    for poz, ilosc in lista_z:
                        st.write(f"• **{poz}:** {ilosc}")
                else:
                    st.info("Dodaj metraz, aby wygenerowac zestawienie.")
                
                # --- GENERATOR PDF ---
                try:
                    from fpdf import FPDF
                    from datetime import datetime
                    import base64
                    import os

                    def czysc_tekst(tekst):
                        pl_znaki = {'ą':'a','ć':'c','ę':'e','ł':'l','ń':'n','ó':'o','ś':'s','ź':'z','ż':'z','Ą':'A','Ć':'C','Ę':'E','Ł':'L','Ń':'N','Ó':'O','Ś':'S','Ź':'Z','Ż':'Z'}
                        for pl, ang in pl_znaki.items(): tekst = tekst.replace(pl, ang)
                        return tekst.encode('latin-1', 'replace').decode('latin-1')

                    if st.button("Generuj Kosztorys PDF", use_container_width=True, key="gk_pdf_btn_pro"):
                        if m2_gk > 0:
                            pdf = FPDF()
                            pdf.add_page()
                            f_path = "Inter-Regular.ttf"
                            if os.path.exists(f_path):
                                pdf.add_font("Inter", "", f_path)
                                pdf.set_font("Inter", size=12)
                            else:
                                pdf.set_font("Arial", size=12)
                            
                            pdf.set_font(pdf.font_family, size=16)
                            pdf.cell(0, 15, "OFERTA: SYSTEMY G-K (PRO)", ln=True, align='C')
                            pdf.ln(5)
                            pdf.set_fill_color(245, 245, 245)
                            pdf.cell(95, 10, " Metraz calkowity:", 1)
                            pdf.cell(95, 10, f" {round(m2_gk, 1)} m2", 1, 1)
                            pdf.cell(95, 12, " SUMA CALKOWITA:", 1, 0, 'L', True)
                            pdf.cell(95, 12, f" {round(total_material + robocizna)} PLN", 1, 1, 'L', True)
                            pdf.ln(10)
                            pdf.set_font(pdf.font_family, size=12)
                            pdf.cell(0, 10, "LISTA MATERIALOWA:", ln=True)
                            pdf.set_font(pdf.font_family, size=10)
                            for poz, ilosc in lista_z:
                                pdf.cell(0, 7, f"- {czysc_tekst(poz)}: {czysc_tekst(ilosc)}", ln=True)

                            pdf_bytes = pdf.output(dest="S").encode('latin-1')
                            pdf_b64 = base64.b64encode(pdf_bytes).decode()
                            href = f'<a href="data:application/pdf;base64,{pdf_b64}" download="Oferta_GK.pdf" style="display: block; text-align: center; padding: 15px; background-color: #00D395; color: white; text-decoration: none; border-radius: 10px; font-weight: bold; font-size: 18px; margin-top: 10px;">Pobierz Raport PDF</a>'
                            st.markdown(href, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Problem z PDF: {e}")
            
# --- SEKCJA: ELEKTRYKA ---
elif branza == "Elektryka":
    st.header("Instalacja Elektryczna (Mieszkanie)")
    
    col_e1, col_e2 = st.columns([1, 1.2])

    # --- KONFIGURACJA MAREK OSPRZĘTU (Zaktualizowane) ---
    opcje_osprzetu = {
        "Ekonomiczny (np. Simon 10, Adelid)": 15,
        "Standard (np. Simon 54, Legrand Niloe)": 45,
        "Premium (np. Berker R.1, Jung, Gira)": 110
    }

    with col_e1:
        st.subheader("Parametry instalacji")
        m2_mieszkania = st.number_input("Metraz mieszkania (m2):", min_value=10, value=60)
        mnoznik_m2 = m2_mieszkania / 60
        st.markdown("---")
        sugerowane_punkty = int(m2_mieszkania * 0.75)
        n_punktow = st.slider("Liczba punktow (gniazda/wlaczniki):", 10, 150, sugerowane_punkty) 
        typ_scian = st.radio("Material scian:", ["Gazobeton/Cegla", "Zelbet (Wielka Plyta)"])
        n_punkty_tele = 2
        wybrany_standard = st.selectbox("Marka osprzetu:", list(opcje_osprzetu.keys()), index=1)
        stawka_punkt = st.slider("Stawka montazu osprzetu (zl/szt):", 1, 100, 45)

    # --- OBLICZENIA ---
    kabel_25 = 150 * mnoznik_m2
    kabel_15 = 100 * mnoznik_m2
    kabel_4x15 = 30 * mnoznik_m2
    kabel_tv = 30 * mnoznik_m2
    kabel_lan = 50 * mnoznik_m2
    
    szt_mocowania = int((kabel_25 + kabel_15 + kabel_4x15 + kabel_tv + kabel_lan) * 3)
    paczki_mocowania = int(szt_mocowania / 100) + 1
    
    srednia_cena_szt = opcje_osprzetu[wybrany_standard]
    koszt_rozdzielnicy_mat = 1800 

    mat_kable = (kabel_25 * 5.20) + (kabel_15 * 3.80) + (kabel_4x15 * 6.50) + (kabel_tv * 2.50) + (kabel_lan * 3.00)
    mat_osprzet = n_punktow * srednia_cena_szt
    mat_mocowania = paczki_mocowania * 25.0
    
    total_material_e = mat_kable + mat_osprzet + koszt_rozdzielnicy_mat + mat_mocowania

    # ROBOCIZNA
    mnoznik_trudnosci = 1.4 if typ_scian == "Zelbet (Wielka Plyta)" else 1.0
    robocizna_baza = (m2_mieszkania * 90) # Podstawa za mb i bruzdy
    robocizna_osprzet = (n_punktow + n_punkty_tele) * stawka_punkt
    robocizna_rozdzielnica = 1500
    
    total_robocizna_e = (robocizna_baza + robocizna_osprzet + robocizna_rozdzielnica) * mnoznik_trudnosci

    # PRZYGOTOWANIE LISTY ZAKUPÓW
    lista_zakupow_ele = [
        ("Kabel 3x2.5 (Gniazda)", f"{round(kabel_25)} mb"),
        ("Kabel 3x1.5 (Swiatlo)", f"{round(kabel_15)} mb"),
        ("Kabel 4x1.5 (Schodowe/Sila)", f"{round(kabel_4x15)} mb"),
        ("Kabel antenowy RG6 (TV)", f"{round(kabel_tv)} mb"),
        ("Kabel LAN kat. 6 (Internet)", f"{round(kabel_lan)} mb"),
        ("Rozdzielnica + 10-15 bezpiecznikow (Eaton/Hager)", "1 kpl"),
        (f"Osprzet ({wybrany_standard})", f"{n_punktow} szt."),
        ("Uchwyty mocujace (paczki 100 szt.)", f"{paczki_mocowania} op."),
        ("Dodatkowe puszki/gniazda LAN/RTV", f"{n_punkty_tele} szt.")
    ]

    with col_e2:
        st.subheader("Kosztorys Elektryki")
        total_e = total_material_e + total_robocizna_e
        st.success(f"### RAZEM: **{round(total_e)} PLN**")
        
        c1, c2 = st.columns(2)
        c1.metric("Materialy", f"{round(total_material_e)} PLN")
        c2.metric("Robocizna", f"{round(total_robocizna_e)} PLN")

        st.markdown("---")
        st.subheader("Wykaz materialow do kupna")
        
        for przedmiot, ilosc in lista_zakupow_ele:
            st.write(f"• **{przedmiot}:** {ilosc}")
            
        st.markdown("---")
        st.info("UWAGA: Wycena nie uwzglednia zakupu opraw oswietleniowych (lamp). Ilosc kabla liczona szacunkowo dla instalacji prowadzonej w tynku/podlogach.")

        # --- GENERATOR PDF ELEKTRYKA ---
        try:
            from fpdf import FPDF
            from datetime import datetime
            import os

            if st.button("Generuj Kosztorys PDF", use_container_width=True, key="ele_pdf_btn"):
                pdf = FPDF()
                pdf.add_page()
                
                f_path = "Inter-Regular.ttf"
                if os.path.exists(f_path):
                    pdf.add_font("Inter", "", f_path)
                    pdf.set_font("Inter", size=12)
                else:
                    pdf.set_font("Arial", size=12)

                pdf.set_font(pdf.font_family, size=16)
                pdf.cell(0, 15, "KOSZTORYS: INSTALACJA ELEKTRYCZNA", ln=True, align='C')
                pdf.ln(5)

                pdf.set_fill_color(245, 245, 245)
                pdf.set_font(pdf.font_family, size=12)
                pdf.cell(95, 10, " Kategoria", 1, 0, 'L', True)
                pdf.cell(95, 10, " Koszt", 1, 1, 'L', True)
                
                pdf.cell(95, 10, " Robocizna:", 1)
                pdf.cell(95, 10, f" {round(total_robocizna_e)} PLN", 1, 1)
                pdf.cell(95, 10, " Materialy:", 1)
                pdf.cell(95, 10, f" {round(total_material_e)} PLN", 1, 1)
                pdf.set_font(pdf.font_family, size=13)
                pdf.cell(95, 12, " SUMA CALKOWITA:", 1, 0, 'L', True)
                pdf.cell(95, 12, f" {round(total_e)} PLN", 1, 1, 'L', True)

                pdf.ln(10)
                pdf.set_font(pdf.font_family, size=12)
                pdf.cell(0, 10, "SZCZEGOLY PROJEKTU:", ln=True)
                pdf.set_font(pdf.font_family, size=10)
                pdf.cell(0, 7, f"- Metraz lokalu: {m2_mieszkania} m2", ln=True)
                pdf.cell(0, 7, f"- Typ scian: {typ_scian}", ln=True)
                pdf.cell(0, 7, f"- Liczba punktow do osadzenia: {n_punktow}", ln=True)

                pdf.ln(5)
                pdf.set_font(pdf.font_family, size=12)
                pdf.cell(0, 10, "LISTA MATERIALOW DO ZAKUPU:", ln=True)
                pdf.set_font(pdf.font_family, size=10)
                for przedmiot, ilosc in lista_zakupow_ele:
                    pdf.cell(0, 7, f"- {przedmiot}: {ilosc}", ln=True)
                
                pdf.ln(5)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 7, "* Wycena nie uwzglednia zakupu lamp i opraw oswietleniowych.", ln=True)

                pdf_bytes = pdf.output()
                
                if isinstance(pdf_bytes, (bytearray, bytes)):
                    safe_bytes = bytes(pdf_bytes)
                else:
                    safe_bytes = pdf_bytes.encode('latin-1', 'replace')

                st.download_button(
                    label="Pobierz gotowy PDF",
                    data=safe_bytes,
                    file_name=f"Kosztorys_Elektryka_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        except Exception as e:
            st.error(f"Problem z generowaniem PDF: {e}")

elif branza == "Łazienka":
    # --- 1. BAZY MATERIAŁOWE (ŁAZIENKA) ---
    baza_kleje = {
        "Atlas Geoflex (Żelowy, C2TE) - 25kg": 65,
        "Atlas Plus (Wysokoelastyczny S1) - 25kg": 85,
        "Kerakoll Bioflex (Żelowy) - 25kg": 75,
        "Kerakoll H40 (Premium) - 25kg": 125,
        "Mapei Keraflex Extra S1 - 25kg": 80,
        "Sopro No.1 (400) - 22.5kg": 115,
        "Klej Standardowy C2T - 25kg": 50
    }
    
    baza_folie = {
        "Standardowa folia w płynie - 5kg": {"cena": 80, "waga": 5},
        "Sopro FDF 525 - 5kg": {"cena": 165, "waga": 5},
        "Sopro FDF 525 - 15kg": {"cena": 440, "waga": 15},
        "Ceresit CL 51 - 5kg": {"cena": 110, "waga": 5},
        "Ceresit CL 51 - 15kg": {"cena": 275, "waga": 15},
        "Atlas Woder E - 5kg": {"cena": 95, "waga": 5},
        "Atlas Woder E - 15kg": {"cena": 255, "waga": 15}
    }
    
    baza_maty = {
        "Mata uszczelniająca Standard (zł/m2)": 45,
        "Mata Sopro AEB 640 (zł/m2)": 85,
        "Mata Knauf (zł/m2)": 75,
        "Mata Ceresit CL 152 (zł/m2)": 70,
        "Mata Kerakoll Aquastop (zł/m2)": 65,
        "Mata Mapei Mapeguard (zł/m2)": 80
    }

    baza_masy_2k = {
        "Masa uszczelniająca 1K/2K Standard - 15kg": {"cena": 180, "waga": 15},
        "Sopro DSF 523 - 10kg": {"cena": 230, "waga": 10},
        "Sopro DSF 523 - 20kg": {"cena": 395, "waga": 20},
        "Kerakoll Aquastop Nanoflex - 20kg": {"cena": 260, "waga": 20},
        "Atlas Woder Duo (Masa 2K) - 15kg": {"cena": 240, "waga": 15},
        "Mapei Mapelastic (Masa 2K) - 16kg": {"cena": 290, "waga": 16}
    }

    # --- 2. INICJALIZACJA ZMIENNYCH ---
    m2_tynku = 0.0
    m2_scian_total = 0.0
    m2_podlogi = 0.0
    obwod = 0.0
    mb_tasma_hydro = 0.0
    m2_hydro_sciany = 0.0
    m2_maty = 0.0
    format_plytki = "Standardowe (np. 60x60, 30x60)"
    typ_hydro = "Standard (Folia w płynie)"
    
    st.header("Kompleksowy Kalkulator: Łazienka PRO")
    st.write("Profesjonalna wycena prac łazienkowych uwzględniająca hydroizolację, markową chemię, demontaże i biały montaż.")

    # --- ZAKŁADKI KROKOWE ---
    tab_wym, tab_plytki, tab_inst, tab_wynik = st.tabs([
        "1. Wymiary & Stan", "2. Płytki i Hydro", "3. Instalacje", "4. Podsumowanie"
    ])

    with tab_wym:
        st.subheader("Wymiary pomieszczenia")
        c_w1, c_w2 = st.columns(2)
        m2_podlogi = c_w1.number_input("Powierzchnia podłogi (m2):", 1.0, 100.0, 5.0, step=0.5)
        wysokosc = c_w2.number_input("Wysokość łazienki (m):", 2.0, 4.0, 2.5, step=0.1)
        
        import math
        bok_a = math.sqrt(m2_podlogi / 1.5)
        bok_b = bok_a * 1.5
        sugerowany_obwod = round(2 * (bok_a + bok_b), 1)
        
        obwod = st.number_input("Suma długości ścian (Obwód w metrach):", 2.0, 100.0, sugerowany_obwod)
        okna_drzwi = st.number_input("Otwory do odjęcia (drzwi/okna w m2):", 0.0, 10.0, 1.6, step=0.1)
        
        m2_scian_total = (obwod * wysokosc) - okna_drzwi
        st.info(f"Całkowita powierzchnia ścian do obróbki: **{round(m2_scian_total, 1)} m²**")
        
        st.markdown("---")
        st.subheader("Stan i Konstrukcje")
        stan_pomieszczenia = st.radio("Stan pomieszczenia:", ["Stan Deweloperski (Puste)", "Rynek Wtórny (Remont / Demontaże)"], horizontal=True)
        
        m2_skuwania = 0.0
        szt_kontener = 0
        if stan_pomieszczenia == "Rynek Wtórny (Remont / Demontaże)":
            c_d1, c_d2 = st.columns(2)
            m2_skuwania = c_d1.number_input("Metraż płytek do skucia (m2):", 0.0, 150.0, (m2_scian_total + m2_podlogi), step=1.0)
            szt_kontener = c_d2.number_input("Kontener na gruz (szt):", 0, 5, 1)
            
        robimy_sufit = st.checkbox("Sufit podwieszany GK (Płyta zielona H2, stelaż, szpachlowanie)", value=True)
                
    with tab_plytki:
        st.subheader("Hydroizolacja (Strefy mokre)")
        wybrana_folia = st.selectbox("Podstawowa folia w płynie (dla podłogi i ścian):", list(baza_folie.keys()))
        
        typ_hydro = st.radio("System hydroizolacji pod prysznicem:", ["Standard (Folia w płynie)", "Premium (Maty uszczelniające)"], horizontal=True)
        
        wybrana_mata = list(baza_maty.keys())[0]
        wybrana_masa = list(baza_masy_2k.keys())[0]
        
        if typ_hydro == "Premium (Maty uszczelniające)":
            st.markdown("##### Dobór systemu Mat")
            wybrana_mata = st.selectbox("Wybierz rodzaj maty:", list(baza_maty.keys()))
            wybrana_masa = st.selectbox("Wybierz masę do wklejenia maty:", list(baza_masy_2k.keys()))
            
            st.markdown("##### Wymiary strefy prysznicowej")
            ch3, ch4 = st.columns(2)
            szer_prysznic = ch3.number_input("Szerokość prysznica (m):", 0.5, 3.0, 0.9, step=0.1)
            dl_prysznic = ch4.number_input("Długość prysznica (m):", 0.5, 3.0, 1.2, step=0.1)
            m2_maty = (szer_prysznic + 0.5) * (dl_prysznic + 0.5)
            st.caption(f"Wyliczona powierzchnia maty (+50cm marginesu): **{round(m2_maty, 1)} m²**")

        c_h1, c_h2 = st.columns(2)
        m2_hydro_sciany = c_h1.number_input("Ściany pod prysznicem/wanną do hydroizolacji (m2):", 0.0, 50.0, 5.0, step=0.5)
        mb_tasma_hydro = c_h2.number_input("Długość taśm narożnikowych (mb):", 0.0, 100.0, 12.0, step=1.0)
        
        st.markdown("---")
        st.subheader("Płytki i Fuga")
        wybrany_klej = st.selectbox("Klej do płytek:", list(baza_kleje.keys()))
        
        c_f1, c_f2 = st.columns(2)
        format_plytki = c_f1.selectbox("Format płytek ściennych:", ["Standardowe (np. 60x60, 30x60)", "Wielki Format (np. 120x60, 120x120)", "Mozaika / Małe płyki"])
        rodzaj_fugi = c_f2.radio("Rodzaj fugi:", ["Cementowa (Elastyczna)", "Epoksydowa (Premium)"])
        
        szerokosc_fugi = st.slider("Zakładana szerokość fugi (mm):", 1.0, 5.0, 2.0, step=0.5)
        
        c_p1, c_p2 = st.columns(2)
        mb_zacinania = c_p1.number_input("Zacinanie płytek 45° (mb):", 0.0, 100.0, 5.0, step=0.5)
        mb_listwy = c_p2.number_input("Listwy narożne ozdobne (mb):", 0.0, 100.0, 0.0, step=0.5)

    with tab_inst:
        st.subheader("Prace instalacyjne i Biały Montaż")
        c_i1, c_i2 = st.columns(2)
        szt_wc = c_i1.number_input("Zabudowa stelaża WC (szt.):", 0, 5, 1)
        szt_odplyw = c_i2.number_input("Odpływ liniowy z kopertą (szt.):", 0, 5, 1)
        
        szt_podejscia = c_i1.number_input("Punkty wodne (mankiety uszczelniające):", 0, 20, 6)
        szt_wneki = c_i2.number_input("Półki / wnęki podświetlane (szt.):", 0, 10, 1)
        
        st.markdown("##### Montaże Specjalne")
        c_i3, c_i4 = st.columns(2)
        szt_wanna_wolno = c_i3.number_input("Wanna wolnostojąca + bateria podłogowa (szt):", 0, 2, 0)
        m2_lustra = c_i4.number_input("Wklejanie lustra na wymiar (m2):", 0.0, 10.0, 0.0, step=0.5)
        
        mb_led = st.number_input("Montaż profili LED w płytkach (mb):", 0.0, 50.0, 0.0, step=1.0)

    with tab_wynik:
        st.subheader("Cennik Wykonawcy (Dostosuj stawki)")
        c_c1, c_c2 = st.columns(2)
        stawka_mb_45 = c_c1.number_input("Zacinanie 45° (zł/mb):", 50, 300, 120)
        stawka_wc = c_c2.number_input("Zabudowa WC (zł/szt):", 100, 1500, 450)
        
        # --- 1. DEFINICJA WYMIARÓW PŁYTEK DO WZORU ---
        if "Wielki Format" in format_plytki:
            dl_p, szer_p, grub_p = 1200, 600, 10
        elif "Standardowe" in format_plytki:
            dl_p, szer_p, grub_p = 600, 600, 9
        else:
            dl_p, szer_p, grub_p = 600, 170, 8

        # --- 2. OBLICZENIA MATERIAŁOWE ---
        m2_plytek_total = m2_scian_total + m2_podlogi
        m2_hydro_total = m2_podlogi + m2_hydro_sciany
        
        procent_zapasu = 1.15 if "Wielki" in format_plytki or "Mozaika" in format_plytki else 1.10
        m2_plytek_z_zapasem = round(m2_plytek_total * procent_zapasu, 1)

        # Hydroizolacja
        m2_pod_folie = max(0, m2_hydro_total - m2_maty) if typ_hydro == "Premium (Maty uszczelniające)" else m2_hydro_total
        dane_folii = baza_folie[wybrana_folia]
        kg_folii_potrzebne = m2_pod_folie * 1.2
        op_folii = int(kg_folii_potrzebne / dane_folii["waga"] + 0.99)
        
        mb_tasmy = int(mb_tasma_hydro * 1.1)
        szt_mankiety = szt_podejscia 
        
        op_gruntu_5l = int((m2_scian_total * 0.2) / 5 + 0.99)
        zuzycie_kleju = 5.5 if "Wielki" in format_plytki else 4.0
        worki_kleju_25kg = int((m2_plytek_total * zuzycie_kleju) / 25 + 0.99)
        
        wspolczynnik_fugi = ((dl_p + szer_p) / (dl_p * szer_p)) * grub_p * szerokosc_fugi * 1.6
        kg_fugi = m2_plytek_total * wspolczynnik_fugi * 1.1 
        op_fugi_2kg = int(kg_fugi / 2 + 0.99)
        if op_fugi_2kg == 0: op_fugi_2kg = 1

        szt_silikon = int((mb_tasma_hydro + obwod) / 10 + 0.99)

        # --- 3. OBLICZENIA FINANSOWE (ROBOCIZNA) ---
        stawka_bazowa_m2 = 2000 
        robocizna_baza = m2_podlogi * stawka_bazowa_m2
        
        koszt_zacinania = mb_zacinania * stawka_mb_45
        koszt_listwy = mb_listwy * 100  
        koszt_odplywu = szt_odplyw * 800
        koszt_wneki = szt_wneki * 500
        koszt_led = mb_led * 120
        koszt_wc = szt_wc * stawka_wc
        koszt_demontazu = m2_skuwania * 60
        koszt_sufitu_rob = m2_podlogi * 180 if robimy_sufit else 0
        koszt_epoksydu_rob = m2_plytek_total * 50 if rodzaj_fugi == "Epoksydowa (Premium)" else 0
        koszt_lustro_rob = m2_lustra * 250
        koszt_wanna_rob = szt_wanna_wolno * 1000
        
        robocizna_suma = (robocizna_baza + koszt_zacinania + koszt_listwy + 
                          koszt_odplywu + koszt_wneki + koszt_led + koszt_wc + 
                          koszt_demontazu + koszt_sufitu_rob + koszt_epoksydu_rob + 
                          koszt_lustro_rob + koszt_wanna_rob)

        # --- 4. OBLICZENIA FINANSOWE (MATERIAŁY) ---
        mat_folia = op_folii * dane_folii["cena"]
        mat_tasma = mb_tasmy * 6
        
        if typ_hydro == "Premium (Maty uszczelniające)":
            mat_mata = m2_maty * baza_maty[wybrana_mata]
            dane_masy = baza_masy_2k[wybrana_masa]
            ile_op_masy = int((m2_maty * 1.5) / dane_masy["waga"] + 0.99)
            mat_klej_maty = ile_op_masy * dane_masy["cena"]
        else:
            mat_mata = 0
            mat_klej_maty = 0
            ile_op_masy = 0

        mat_klej = worki_kleju_25kg * baza_kleje[wybrany_klej]
        
        cena_fugi = 140 if rodzaj_fugi == "Epoksydowa (Premium)" else 45
        mat_fuga_sil = (op_fugi_2kg * cena_fugi) + (szt_silikon * 35)
        
        mat_sufit = m2_podlogi * 65 if robimy_sufit else 0 # Stelaże, GK, akcesoria
        mat_kontener = szt_kontener * 800
        mat_lustro_klej = math.ceil(m2_lustra) * 45 if m2_lustra > 0 else 0
        
        materialy_suma = mat_folia + mat_tasma + mat_mata + mat_klej_maty + mat_klej + mat_fuga_sil + mat_sufit + mat_kontener + mat_lustro_klej + 250

        # --- 5. WYŚWIETLANIE WYNIKÓW ---
        st.markdown("---")
        st.success(f"### ŁĄCZNA KWOTA ROBOCIZNY: **{round(robocizna_suma)} PLN**")
        
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Pakiet Bazowy (Łazienka)", f"{round(robocizna_baza)} zł", help="Obejmuje standardowe układanie płytek, hydroizolację i biały montaż.")
        with c2:
            suma_dodatkow = robocizna_suma - robocizna_baza
            st.metric("Suma dodatków (Detale i Ekstra)", f"{round(suma_dodatkow)} zł", delta="Trudność / Opcje Premium")

        st.markdown("---")
        st.subheader("Wycena detali (Poza pakietem bazowym)")
        detale = []
        if m2_skuwania > 0: detale.append({"Zadanie": "Skuwanie starych płytek/kucie", "Ilość": f"{round(m2_skuwania, 1)} m2", "Koszt": f"{round(koszt_demontazu)} zł"})
        if robimy_sufit: detale.append({"Zadanie": "Sufit podwieszany GK (Robocizna)", "Ilość": f"{round(m2_podlogi, 1)} m2", "Koszt": f"{round(koszt_sufitu_rob)} zł"})
        if rodzaj_fugi == "Epoksydowa (Premium)": detale.append({"Zadanie": "Aplikacja fugi epoksydowej", "Ilość": f"{round(m2_plytek_total, 1)} m2", "Koszt": f"{round(koszt_epoksydu_rob)} zł"})
        if mb_zacinania > 0: detale.append({"Zadanie": "Szlifowanie narożników 45°", "Ilość": f"{mb_zacinania} mb", "Koszt": f"{round(koszt_zacinania)} zł"})
        if mb_listwy > 0: detale.append({"Zadanie": "Montaż listew ozdobnych", "Ilość": f"{mb_listwy} mb", "Koszt": f"{round(koszt_listwy)} zł"})
        if szt_wneki > 0: detale.append({"Zadanie": "Wykonanie wnęk/półek", "Ilość": f"{szt_wneki} szt", "Koszt": f"{round(koszt_wneki)} zł"})
        if mb_led > 0: detale.append({"Zadanie": "Montaż profili LED", "Ilość": f"{mb_led} mb", "Koszt": f"{round(koszt_led)} zł"})
        if szt_odplyw > 0: detale.append({"Zadanie": "Odpływ liniowy (koperta)", "Ilość": f"{szt_odplyw} szt", "Koszt": f"{round(koszt_odplywu)} zł"})
        if szt_wc > 0: detale.append({"Zadanie": "Zabudowa stelaża WC", "Ilość": f"{szt_wc} szt", "Koszt": f"{round(koszt_wc)} zł"})
        if szt_wanna_wolno > 0: detale.append({"Zadanie": "Montaż wanny wolnostojącej", "Ilość": f"{szt_wanna_wolno} szt", "Koszt": f"{round(koszt_wanna_rob)} zł"})
        if m2_lustra > 0: detale.append({"Zadanie": "Wklejanie lustra licowanego", "Ilość": f"{m2_lustra} m2", "Koszt": f"{round(koszt_lustro_rob)} zł"})
        
        if detale:
            st.table(detale)
        else:
            st.info("Brak dodatkowych detali - łazienka w standardzie prostym.")

        # --- DEFINICJA LISTY ZAKUPÓW ---
        nazwa_fugi = "Fuga Epoksydowa (Premium 2kg)" if rodzaj_fugi == "Epoksydowa (Premium)" else "Fuga elastyczna cementowa (2kg)"
        
        lista_zakupow_lazienka = [
            ("PŁYTKI (łącznie z zapasem)", f"{m2_plytek_z_zapasem} m²"),
            (wybrany_klej, f"{worki_kleju_25kg} worków"),
            ("Taśma uszczelniająca", f"{mb_tasmy} mb"),
            ("Mankiety ścienne", f"{szt_mankiety} szt."),
            (nazwa_fugi, f"{op_fugi_2kg} op."),
            ("Silikon sanitarny", f"{szt_silikon} szt."),
            ("Grunt głęboko penetrujący", f"{op_gruntu_5l} wiader 5L"),
        ]
        
        if op_folii > 0:
            lista_zakupow_lazienka.append((wybrana_folia, f"{op_folii} op."))
        if m2_maty > 0 and typ_hydro == "Premium (Maty uszczelniające)":
            lista_zakupow_lazienka.append((wybrana_mata, f"{round(m2_maty, 1)} m²"))
            lista_zakupow_lazienka.append((wybrana_masa, f"{ile_op_masy} op."))
            
        if robimy_sufit:
            lista_zakupow_lazienka.append(("System Sufit GK (płyty H2, profile, uniflott)", f"Na ok. {round(m2_podlogi, 1)} m²"))
        if szt_kontener > 0:
            lista_zakupow_lazienka.append(("Kontener na gruz", f"{szt_kontener} szt."))
        if m2_lustra > 0:
            lista_zakupow_lazienka.append(("Klej do luster", f"{math.ceil(m2_lustra)} kartuszy"))

        # --- WYŚWIETLANIE WYNIKÓW I ANALIZA ---
        st.markdown("---")
        cena_za_m2_podlogi = robocizna_suma / m2_podlogi
        
        c_res1, c_res2 = st.columns(2)
        with c_res1:
            st.success(f"### RAZEM ROBOCIZNA\n**{round(robocizna_suma)} PLN**")
        with c_res2:
            st.info(f"### CHEMIA BUDOWLANA\n**~{round(materialy_suma)} PLN**")

        st.subheader("Analiza rynkowa wyceny")
        col_metric1, col_metric2 = st.columns([2, 1])
        
        with col_metric1:
            if 2000 <= cena_za_m2_podlogi <= 3500:
                st.write(f"Twoja wycena to **{round(cena_za_m2_podlogi)} zł/m²** podłogi. Mieścisz się w standardowym przedziale rynkowym.")
            elif cena_za_m2_podlogi < 2000:
                st.error(f"Uwaga: Wycena wynosi **{round(cena_za_m2_podlogi)} zł/m²** podłogi. To może być za mało przy wysokim standardzie!")
            else:
                st.warning(f"Standard Premium: Wycena wynosi **{round(cena_za_m2_podlogi)} zł/m²** podłogi. Upewnij się, że Inwestor akceptuje te stawki.")

        with col_metric2:
            st.metric("Cena / m² podłogi", f"{round(cena_za_m2_podlogi)} zł")

        st.markdown("---")
        st.subheader("Wykaz Chemii Budowlanej (Lista Zakupów)")
        col_list1, col_list2 = st.columns(2)
        half = len(lista_zakupow_lazienka) // 2 + 1
        
        with col_list1:
            for przedmiot, ilosc in lista_zakupow_lazienka[:half]:
                st.write(f"• **{przedmiot}:** {ilosc}")
        with col_list2:
            for przedmiot, ilosc in lista_zakupow_lazienka[half:]:
                st.write(f"• **{przedmiot}:** {ilosc}")
                  
        # --- 6. GENERATOR PDF ---
        st.markdown("---")
        if st.button("Generuj Pełny Kosztorys PDF (Łazienka PRO)"):
            try:
                from fpdf import FPDF
                from datetime import datetime
        
                pdf = FPDF()
                pdf.add_page()
                pdf.add_font('Inter', '', 'Inter-Regular.ttf', uni=True)
                
                pdf.set_font('Inter', '', 16)
                pdf.cell(190, 10, txt="KOSZTORYS WYKONAWCZY: LAZIENKA PRO", ln=True, align='C')
                pdf.set_font('Inter', '', 10)
                pdf.cell(190, 10, txt=f"Data wystawienia: {datetime.now().strftime('%d.%m.%Y')}", ln=True, align='C')
                pdf.ln(10)
        
                pdf.set_font('Inter', '', 12)
                pdf.set_fill_color(230, 230, 230)
                pdf.cell(190, 10, txt="1. PODSUMOWANIE KOSZTOW", ln=True, align='L', fill=True)
                pdf.ln(2)
                
                pdf.set_font('Inter', '', 10)
                pdf.cell(140, 8, txt="Pakiet Bazowy (Robocizna + przygotowanie)", border=1)
                pdf.cell(50, 8, txt=f"{round(robocizna_baza)} zl", border=1, ln=True, align='R')
                
                pdf.cell(140, 8, txt="Suma dodatkow i detali (W tym ew. demontaze)", border=1)
                pdf.cell(50, 8, txt=f"{round(suma_dodatkow)} zl", border=1, ln=True, align='R')
                
                pdf.cell(140, 8, txt="Szacowany koszt chemii budowlanej", border=1)
                pdf.cell(50, 8, txt=f"{round(materialy_suma)} zl", border=1, ln=True, align='R')
                
                pdf.set_font('Inter', '', 11)
                pdf.cell(140, 10, txt="RAZEM DO ZAPLATY (Usluga + Chemia):", border=1, fill=True)
                pdf.cell(50, 10, txt=f"{round(robocizna_suma + materialy_suma)} zl", border=1, ln=True, align='R', fill=True)
                pdf.ln(5)
        
                if detale:
                    pdf.set_font('Inter', '', 12)
                    pdf.cell(190, 10, txt="2. WYCENA ELEMENTOW DODATKOWYCH", ln=True, align='L', fill=True)
                    pdf.set_font('Inter', '', 9)
                    pdf.cell(100, 8, "Zadanie / Detal", 1, 0, 'C')
                    pdf.cell(40, 8, "Ilosc", 1, 0, 'C')
                    pdf.cell(50, 8, "Koszt", 1, 1, 'C')
                    for d in detale:
                        zadanie_pdf = d["Zadanie"].replace("ś", "s").replace("ó", "o").replace("ł", "l").replace("ń", "n").replace("ę", "e").replace("ą", "a").replace("ż", "z").replace("ź", "z")
                        pdf.cell(100, 8, zadanie_pdf, 1)
                        pdf.cell(40, 8, d["Ilość"], 1, 0, 'C')
                        pdf.cell(50, 8, d["Koszt"].replace("ł", "l"), 1, 1, 'R')
                    pdf.ln(5)
        
                pdf.set_font('Inter', '', 12)
                pdf.cell(190, 10, txt="3. WYKAZ MATERIALOW (Do dostarczenia)", ln=True, align='L', fill=True)
                pdf.set_font('Inter', '', 10)
                pdf.ln(2)
                for przedmiot, ilosc in lista_zakupow_lazienka:
                    prz_pdf = przedmiot.replace("ś", "s").replace("ó", "o").replace("ł", "l").replace("ń", "n").replace("ę", "e").replace("ą", "a").replace("ż", "z").replace("ź", "z").replace("Ś", "S")
                    pdf.cell(190, 7, txt=f"- {prz_pdf}: {ilosc.replace('ł', 'l').replace('²','2')}", ln=True)
        
                pdf_output = pdf.output()

                if isinstance(pdf_output, (bytearray, bytes)):
                    pdf_bytes = bytes(pdf_output)
                elif isinstance(pdf_output, str):
                    pdf_bytes = pdf_output.encode('latin-1', 'replace')
                else:
                    pdf_bytes = pdf_output
        
                st.download_button(
                    label="Pobierz Kosztorys PDF",
                    data=pdf_bytes,
                    file_name=f"Kosztorys_Lazienka_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Błąd PDF: {e}")
               
# --- SEKCJA: DRZWI ---
elif branza == "Drzwi":
    st.header("Kalkulator Montażu Drzwi Wewnętrznych")
    
    # Baza cenowa skrzydeł (średnia rynkowa: skrzydło + ościeżnica + klamka)
    baza_drzwi = {
        "Standardowe (Przylgowe)": 1200.0,
        "Bezprzylgowe (Ukryte zawiasy)": 1900.0,
        "Rewersyjne (Otwierane do wewnątrz)": 2300.0,
        "Ukryte (System zlicowany ze ścianą)": 1600.0
    }

    tab_d1, tab_d2 = st.tabs(["Szybka Wycena", "Kosztorys PRO"])

    # ==========================================
    # TAB 1: SZYBKA WYCENA
    # ==========================================
    with tab_d1:
        st.subheader("Błyskawiczny szacunek kosztów")
        szt_fast = st.number_input("Liczba drzwi (kompletów):", min_value=1, value=5, step=1, key="drzwi_fast")
        typ_fast = st.radio("Standard wykończenia:", ["Zwykłe (Przylgowe)", "Premium (Bezprzylgowe/Ukryte)"])
        
        # Uproszczone stawki
        if typ_fast == "Zwykłe (Przylgowe)":
            k_drzwi_fast = szt_fast * 1200
            k_rob_fast = szt_fast * 250
            k_chem_fast = szt_fast * 50
        else:
            k_drzwi_fast = szt_fast * 1800
            k_rob_fast = szt_fast * 350
            k_chem_fast = szt_fast * 60
            
        total_fast = k_drzwi_fast + k_rob_fast + k_chem_fast
        
        st.success(f"### Szacowany całkowity koszt inwestycji: ok. {round(total_fast)} PLN")
        st.caption("Cena zawiera szacunkowy koszt zakupu drzwi, chemię montażową oraz robociznę.")
        
        c_f1, c_f2 = st.columns(2)
        c_f1.metric("Szacowany zakup drzwi z chemią", f"{round(k_drzwi_fast + k_chem_fast)} PLN")
        c_f2.metric("Szacowana Robocizna", f"{round(k_rob_fast)} PLN")
        
        st.info("Przejdź do zakładki Kosztorys PRO, aby doliczyć podcięcia wentylacyjne, dopłaty za szeroki mur i wygenerować PDF.")

    # ==========================================
    # ==========================================
    # TAB 2: KOSZTORYS PRO
    # ==========================================
    with tab_d2:
        if not st.session_state.zalogowany or st.session_state.pakiet != "PRO":
            st.error("🔒 **Dostęp zablokowany**")
            
            _, col_k, _ = st.columns([1, 2, 1])
            with col_k:
                if st.button("Odblokuj dostęp (Przejdź do logowania)", use_container_width=True):
                    st.session_state.przekierowanie = True  # Ustawiamy flagę
                    st.rerun()  # Wymuszamy przeładowanie kodu od góry
        
        else:
            # --- TUTAJKOD WYKONUJE SIĘ TYLKO DLA ZALOGOWANYCH ---
            col_d1, col_d2 = st.columns([1, 1.2])

            with col_d1:
                st.subheader("Parametry zamówienia")
                szt_drzwi = st.number_input("Liczba kompletów (skrzydło + ościeżnica):", min_value=1, value=5, key="drzwi_pro")
                
                wybrany_model = st.selectbox(
                    "Model i standard drzwi:", 
                    options=list(baza_drzwi.keys())
                )
                
                szerokosc_muru = st.radio("Szerokość muru (zakres):", ["Standard (do 140mm)", "Szeroki (powyżej 140mm)"])
                
                st.markdown("---")
                st.write("**Usługi dodatkowe**")
                podciecie = st.checkbox("Podcięcie wentylacyjne (np. do łazienki/pralni)")
                demontaz = st.checkbox("Demontaż starych ościeżnic")
                
                st.markdown("---")
                # Dynamiczna stawka domyślna w zależności od stopnia skomplikowania
                if "Ukryte" in wybrany_model or "Rewersyjne" in wybrany_model:
                    domyslna_stawka = 380
                elif "Bezprzylgowe" in wybrany_model:
                    domyslna_stawka = 320
                else:
                    domyslna_stawka = 250
                    
                stawka_montazu = st.number_input("Bazowa stawka za montaż 1 kpl. (zł):", 100, 1000, domyslna_stawka)

            # --- LOGIKA OBLICZEŃ (WCIĘTA!) ---
            cena_jednostkowa = baza_drzwi[wybrany_model]
            koszt_samych_drzwi = szt_drzwi * cena_jednostkowa
            
            ilosc_pianki = szt_drzwi 
            ilosc_akrylu = int(szt_drzwi / 2 + 0.99)
            ilosc_klinow = int(szt_drzwi / 3 + 0.99)
            
            koszt_chemii = (ilosc_pianki * 45) + (ilosc_akrylu * 20) + (ilosc_klinow * 35)
            
            info_zakup = [
                (f"Drzwi wewnętrzne ({wybrany_model})", f"{szt_drzwi} kpl."),
                ("Pianka montażowa niskoprężna", f"{ilosc_pianki} szt."),
                ("Akryl malarski (do opasek)", f"{ilosc_akrylu} szt."),
                ("Kliny montażowe tworzywowe", f"{ilosc_klinow} opk.")
            ]
            
            total_materialy = koszt_samych_drzwi + koszt_chemii
            
            doplata_szeroki = 50 if szerokosc_muru == "Szeroki (powyżej 140mm)" else 0
            doplata_podciecie = 35 if podciecie else 0
            doplata_demontaz = 120 if demontaz else 0
            
            robocizna_jednostkowa = stawka_montazu + doplata_szeroki + doplata_podciecie + doplata_demontaz
            total_robocizna = szt_drzwi * robocizna_jednostkowa

            with col_d2:
                st.subheader("Podsumowanie Kosztorysu")
                suma_calkowita = total_materialy + total_robocizna
                
                st.success(f"### KOSZT CAŁKOWITY: **{round(suma_calkowita)} PLN**")
                st.caption("Cena obejmuje zakup drzwi, chemię montażową oraz robociznę.")

                c1, c2 = st.columns(2)
                c1.metric("Materiał (Drzwi + Chemia)", f"{round(total_materialy)} PLN")
                c2.metric("Robocizna", f"{round(total_robocizna)} PLN")

                st.markdown("---")
                st.subheader("Lista materiałowa do zamówienia")
                
                for nazwa, ilosc in info_zakup:
                    st.write(f"• **{nazwa}:** {ilosc}")
                
                st.markdown("---")
                st.write("**Szczegóły robocizny (za 1 komplet):**")
                st.write(f"- Montaż bazowy: {stawka_montazu} PLN")
                if doplata_szeroki > 0: st.write(f"- Dopłata za szeroki mur: {doplata_szeroki} PLN")
                if doplata_podciecie > 0: st.write(f"- Podcięcie wentylacyjne: {doplata_podciecie} PLN")
                if doplata_demontaz > 0: st.write(f"- Demontaż starych drzwi: {doplata_demontaz} PLN")
                st.write(f"**Łącznie za 1 sztukę: {robocizna_jednostkowa} PLN**")

                # --- GENERATOR PDF ---
                try:
                    from fpdf import FPDF
                    from datetime import datetime
                    import os

                    if st.button("Generuj Kosztorys PDF", use_container_width=True, key="drzwi_pdf_btn"):
                        pdf = FPDF()
                        pdf.add_page()
                        
                        f_path = "Inter-Regular.ttf"
                        if os.path.exists(f_path):
                            pdf.add_font("Inter", "", f_path)
                            pdf.set_font("Inter", size=12)
                        else:
                            pdf.set_font("Arial", size=12)
                        
                        pdf.set_font(pdf.font_family, size=16)
                        pdf.cell(0, 15, "KOSZTORYS: STOLARKA DRZWIOWA", ln=True, align='C')
                        pdf.ln(5)

                        pdf.set_fill_color(245, 245, 245)
                        pdf.set_font(pdf.font_family, size=12)
                        
                        pdf.cell(95, 10, " Liczba kompletów:", 1)
                        pdf.cell(95, 10, f" {szt_drzwi} szt.", 1, 1)
                        pdf.cell(95, 10, " Model drzwi:", 1)
                        pdf.cell(95, 10, f" {wybrany_model.split(' (')[0]}", 1, 1)
                        pdf.cell(95, 10, " Szerokość muru:", 1)
                        pdf.cell(95, 10, f" {szerokosc_muru}", 1, 1)

                        pdf.ln(10)
                        
                        pdf.cell(95, 10, " Robocizna (Montaż całości):", 1)
                        pdf.cell(95, 10, f" {round(total_robocizna)} PLN", 1, 1)
                        pdf.cell(95, 10, " Koszt zakupu drzwi (szacunek):", 1)
                        pdf.cell(95, 10, f" {round(koszt_samych_drzwi)} PLN", 1, 1)
                        pdf.cell(95, 10, " Chemia i akcesoria:", 1)
                        pdf.cell(95, 10, f" {round(koszt_chemii)} PLN", 1, 1)
                        
                        pdf.set_font(pdf.font_family, size=13)
                        pdf.cell(95, 12, " ŁĄCZNY KOSZT INWESTYCJI:", 1, 0, 'L', True)
                        pdf.cell(95, 12, f" {round(suma_calkowita)} PLN", 1, 1, 'L', True)
                        
                        pdf.ln(10)
                        pdf.set_font(pdf.font_family, size=12)
                        pdf.cell(0, 10, "LISTA ZAKUPÓW:", ln=True)
                        pdf.set_font(pdf.font_family, size=10)
                        for nazwa, ilosc in info_zakup:
                            pdf.cell(0, 7, f"- {nazwa}: {ilosc}", ln=True)

                        pdf_bytes = pdf.output()
                        safe_bytes = bytes(pdf_bytes) if isinstance(pdf_bytes, (bytearray, bytes)) else pdf_bytes.encode('latin-1', 'replace')

                        st.download_button(
                            label="Pobierz gotowy PDF",
                            data=safe_bytes,
                            file_name=f"Kosztorys_Drzwi_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"Błąd podczas generowania PDF: {e}")

                st.markdown("---")
                st.subheader("💾 Zapisz Kosztorys w Chmurze")
                st.caption("Zapisz ten projekt, aby mieć do niego dostęp z dowolnego urządzenia.")
                
                nazwa_projektu = st.text_input("Nazwa projektu (np. Mieszkanie na Złotej 44):", key="nazwa_proj_drzwi")
                
                if st.button("Zapisz Projekt", use_container_width=True, type="primary"):
                    if not nazwa_projektu:
                        st.warning("⚠️ Podaj nazwę projektu przed zapisaniem.")
                    # --- DODANE ZABEZPIECZENIE ---
                    elif 'user_id' not in st.session_state or not st.session_state.user_id:
                        st.error("❌ Błąd krytyczny: Zgubiłeś sesję! Wyloguj się i zaloguj ponownie.")
                    # ---------------------------
                    else:
                        try:
                            # 1. Pakujemy wszystkie ważne dane
                            dane_do_zapisu = {
                                "szt_drzwi": szt_drzwi,
                                "wybrany_model": wybrany_model,
                                "szerokosc_muru": szerokosc_muru,
                                "podciecie": podciecie,
                                "demontaz": demontaz,
                                "koszt_materialow": total_materialy,
                                "koszt_robocizny": total_robocizna,
                                "suma_calkowita": suma_calkowita
                            }
                            
                            # 2. Wysyłamy paczkę do bazy Supabase
                            response = supabase.table("projekty").insert({
                                "user_id": st.session_state.user_id, 
                                "nazwa_projektu": nazwa_projektu,
                                "branza": "Drzwi",
                                "dane_json": dane_do_zapisu
                            }).execute()
                            
                            st.success(f"✅ Projekt '{nazwa_projektu}' został bezpiecznie zapisany w chmurze!")
                        except Exception as e:
                            st.error(f"❌ Wystąpił błąd podczas zapisywania: {e}")


elif branza == "Tapetowanie":
    # --- 1. BAZY MATERIAŁOWE (TAPETY) ---
    baza_kleje_tapety = {
        "Metylan Direct (Do tapet na flizelinie) - 200g": {"cena": 45, "wydajnosc_rolek": 4},
        "Metylan Special (Do tapet winylowych) - 200g": {"cena": 40, "wydajnosc_rolek": 4},
        "Metylan Normal (Do tapet papierowych) - 200g": {"cena": 35, "wydajnosc_rolek": 4},
        "Klej gotowy w wiadrze (Fototapety/Ciężkie) - 5kg": {"cena": 85, "wydajnosc_rolek": 5}
    }
    
    # --- 2. INICJALIZACJA ZMIENNYCH ---
    m2_scian = 0.0
    obwod = 0.0
    
    st.header("Kalkulator: Tapetowanie PRO ")
    st.write("Precyzyjne wyliczanie zapotrzebowania na rolki tapety z uwzględnieniem raportu (pasowania wzoru) i odpadów.")

    # --- ZAKŁADKI KROKOWE ---
    tab_wym, tab_rolka, tab_wynik = st.tabs([
        "1. Pomiary Ścian", "2. Parametry Rolki", "3. Wycena i Zakupy"
    ])

    with tab_wym:
        st.subheader("Wymiary i Przygotowanie Podłoża")
        c_w1, c_w2 = st.columns(2)
        obwod = c_w1.number_input("Obwód ścian do tapetowania (m):", 1.0, 200.0, 12.0, step=0.5)
        wysokosc = c_w2.number_input("Wysokość pomieszczenia (m):", 2.0, 5.0, 2.6, step=0.05)
        
        odliczenia = st.number_input("Otwory do odjęcia (okna, drzwi w m2):", 0.0, 50.0, 2.0, step=0.5)
        m2_scian = (obwod * wysokosc) - odliczenia
        
        st.info(f"Powierzchnia robocza ścian: **{round(m2_scian, 1)} m²**")
        
        st.markdown("---")
        st.subheader("Prace przygotowawcze")
        zrywanie_starej = st.checkbox("Zrywanie starej tapety")
        gruntowanie = st.checkbox("Gruntowanie podłoża przed tapetowaniem", value=True)

    with tab_rolka:
        st.subheader("Właściwości Tapety")
        
        c_r1, c_r2 = st.columns(2)
        rodzaj_tapety = c_r1.selectbox("Rodzaj tapety:", ["Na flizelinie (najczęstsza)", "Winylowa", "Papierowa", "Fototapeta (na wymiar)"])
        
        szer_rolki = c_r2.number_input("Szerokość rolki (m):", 0.1, 1.5, 0.53, step=0.01)
        dl_rolki = c_r1.number_input("Długość rolki (m):", 1.0, 50.0, 10.05, step=0.1)
        
        raport = c_r2.number_input("Przesunięcie wzoru / Raport (cm):", 0, 100, 64, step=1, 
                                   help="Wpisz 0, jeśli tapeta jest gładka lub wzór nie wymaga pasowania.")
        
        # Dobór domyślnego kleju na podstawie wybranej tapety
        domyslny_klej = list(baza_kleje_tapety.keys())[0]
        if "Winylowa" in rodzaj_tapety: domyslny_klej = list(baza_kleje_tapety.keys())[1]
        elif "Papierowa" in rodzaj_tapety: domyslny_klej = list(baza_kleje_tapety.keys())[2]
        elif "Fototapeta" in rodzaj_tapety: domyslny_klej = list(baza_kleje_tapety.keys())[3]
        
        wybrany_klej = st.selectbox("Zalecany Klej:", list(baza_kleje_tapety.keys()), index=list(baza_kleje_tapety.keys()).index(domyslny_klej))

    with tab_wynik:
        st.subheader("Stawki i Obliczenia")
        import math
        
        c_c1, c_c2 = st.columns(2)
        
        # Baza cenowa dla robocizny
        stawka_baza = 50
        if "Fototapeta" in rodzaj_tapety: stawka_baza = 80
        elif "Papierowa" in rodzaj_tapety: stawka_baza = 60 # Papierowe kładzie się trudniej
        
        stawka_tapetowanie = c_c1.number_input("Stawka za kładzenie tapety (zł/m2):", 10, 200, stawka_baza)
        stawka_zrywanie = c_c2.number_input("Stawka za zrywanie (zł/m2):", 10, 100, 25) if zrywanie_starej else 0
        
        # ==========================================
        # LOGIKA PRO - OBLICZANIE PASÓW I ROLEK
        # ==========================================
        if "Fototapeta" not in rodzaj_tapety:
            # 1. Ile pasów wejdzie na ścianę?
            szerokosc_odliczen = odliczenia / wysokosc if wysokosc > 0 else 0
            obwod_netto = max(0, obwod - szerokosc_odliczen)
            liczba_pasow = math.ceil(obwod_netto / szer_rolki)
            
            # 2. Jak długi musi być jeden pas? (Wysokość + raport + 10 cm na docięcia góra/dół)
            zapas_techniczny = 0.10
            wysokosc_efektywna = wysokosc + (raport / 100) + zapas_techniczny
            
            # 3. Ile pasów wytniemy z 1 rolki?
            pasy_z_rolki = math.floor(dl_rolki / wysokosc_efektywna) if wysokosc_efektywna > 0 else 0
            
            # 4. Suma rolek
            if pasy_z_rolki > 0:
                potrzebne_rolki = math.ceil(liczba_pasow / pasy_z_rolki)
            else:
                potrzebne_rolki = 0
                
            # Wyliczenie kleju
            dane_kleju = baza_kleje_tapety[wybrany_klej]
            szt_kleju = math.ceil(potrzebne_rolki / dane_kleju["wydajnosc_rolek"])
        else:
            # Fototapeta na wymiar
            liczba_pasow = 0
            pasy_z_rolki = 0
            potrzebne_rolki = 1 # Jako komplet
            dane_kleju = baza_kleje_tapety[wybrany_klej]
            szt_kleju = math.ceil(m2_scian / 15) # Założenie: 1 opakowanie na 15 m2

        # ==========================================
        # OBLICZENIA FINANSOWE
        # ==========================================
        robocizna_tapetowanie = m2_scian * stawka_tapetowanie
        robocizna_zrywanie = m2_scian * stawka_zrywanie if zrywanie_starej else 0
        robocizna_grunt = m2_scian * 5 if gruntowanie else 0
        
        suma_robocizna = robocizna_tapetowanie + robocizna_zrywanie + robocizna_grunt
        
        koszt_kleju = szt_kleju * dane_kleju["cena"]
        szt_gruntu = math.ceil((m2_scian * 0.15) / 5) if gruntowanie else 0
        koszt_gruntu = szt_gruntu * 40
        
        suma_materialy = koszt_kleju + koszt_gruntu

        # ==========================================
        # WYŚWIETLANIE WYNIKÓW
        # ==========================================
        st.markdown("---")
        st.success(f"### RAZEM ROBOCIZNA: **{round(suma_robocizna)} PLN**")
        
        if "Fototapeta" not in rodzaj_tapety:
            st.markdown("### Analiza zużycia tapety")
            col_a1, col_a2, col_a3 = st.columns(3)
            col_a1.metric("Potrzebne rolki", f"{potrzebne_rolki} szt.")
            col_a2.metric("Łączna liczba pasów", f"{liczba_pasow} pasów")
            col_a3.metric("Pasów z 1 rolki", f"{pasy_z_rolki} pasy", 
                          delta=f"Odpad: {round(dl_rolki - (pasy_z_rolki * wysokosc_efektywna), 2)}m / rolkę", delta_color="off")
            
            if pasy_z_rolki == 3 and raport > 0:
                st.warning(f"💡 **Dlaczego tylko 3 pasy z rolki?** Przy wysokości ścian {wysokosc}m i raporcie {raport}cm, po docięciu wzoru potrzebujesz pasów o długości ok. {round(wysokosc_efektywna,2)}m. Z rolki (10.05m) wytniesz 3 takie pasy (ok. {round(wysokosc_efektywna * 3, 2)}m). Reszta to odpad techniczny.")
        else:
            st.info("💡 **Fototapeta na wymiar:** Tapeta przychodzi w gotowych brytach dociętych pod wymiar ściany.")

        st.markdown("---")
        st.subheader("Lista Zakupów (Chemia Markowa)")
        col_z1, col_z2 = st.columns(2)
        
        with col_z1:
            if "Fototapeta" not in rodzaj_tapety:
                st.write(f"🔹 **Tapeta {rodzaj_tapety}:** {potrzebne_rolki} rolek")
                st.caption("Pamiętaj o sprawdzeniu zgodności numeru partii (Batch/Lot number) na każdej rolce!")
            else:
                st.write(f"🔹 **Fototapeta:** 1 komplet pod wymiar ({round(m2_scian, 1)} m²)")
                
        with col_z2:
            st.write(f"🔸 **Klej:** {wybrany_klej.split(' - ')[0]} - {szt_kleju} op.")
            if gruntowanie:
                st.write(f"🔸 **Grunt głęboko penetrujący (5L):** {szt_gruntu} szt.")
            
        st.markdown(f"*Szacowany koszt chemii roboczej (klej, grunt): ~{round(suma_materialy)} zł*")

        # --- GENERATOR PDF (TAPETOWANIE) ---
        st.markdown("---")
        if st.button("Generuj Pełny Kosztorys PDF (Tapetowanie)"):
            try:
                from fpdf import FPDF
                from datetime import datetime
        
                pdf = FPDF()
                pdf.add_page()
                pdf.add_font('Inter', '', 'Inter-Regular.ttf', uni=True)
                
                pdf.set_font('Inter', '', 16)
                pdf.cell(190, 10, txt="KOSZTORYS WYKONAWCZY: TAPETOWANIE", ln=True, align='C')
                pdf.set_font('Inter', '', 10)
                pdf.cell(190, 10, txt=f"Data wystawienia: {datetime.now().strftime('%d.%m.%Y')}", ln=True, align='C')
                pdf.ln(10)
        
                pdf.set_font('Inter', '', 12)
                pdf.set_fill_color(230, 230, 230)
                pdf.cell(190, 10, txt="1. PODSUMOWANIE KOSZTOW ROBOCIZNY", ln=True, align='L', fill=True)
                pdf.ln(2)
                
                pdf.set_font('Inter', '', 10)
                pdf.cell(140, 8, txt=f"Tapetowanie ({round(m2_scian,1)} m2)", border=1)
                pdf.cell(50, 8, txt=f"{round(robocizna_tapetowanie)} zl", border=1, ln=True, align='R')
                
                if zrywanie_starej:
                    pdf.cell(140, 8, txt="Zrywanie starej tapety i przygotowanie", border=1)
                    pdf.cell(50, 8, txt=f"{round(robocizna_zrywanie)} zl", border=1, ln=True, align='R')
                
                if gruntowanie:
                    pdf.cell(140, 8, txt="Gruntowanie podloza", border=1)
                    pdf.cell(50, 8, txt=f"{round(robocizna_grunt)} zl", border=1, ln=True, align='R')
                
                pdf.set_font('Inter', '', 11)
                pdf.cell(140, 10, txt="RAZEM ROBOCIZNA:", border=1, fill=True)
                pdf.cell(50, 10, txt=f"{round(suma_robocizna)} zl", border=1, ln=True, align='R', fill=True)
                pdf.ln(10)
        
                pdf.set_font('Inter', '', 12)
                pdf.cell(190, 10, txt="2. LISTA ZAKUPOWA DLA INWESTORA", ln=True, align='L', fill=True)
                pdf.set_font('Inter', '', 10)
                pdf.ln(2)
                
                rodzaj_tapety_pdf = rodzaj_tapety.replace("ś", "s").replace("ł", "l").replace("ó", "o")
                
                if "Fototapeta" not in rodzaj_tapety:
                    pdf.cell(190, 7, txt=f"- Tapeta ({rodzaj_tapety_pdf}): {potrzebne_rolki} rolek", ln=True)
                    pdf.cell(190, 7, txt=f"  *Zalozenia: Pasowanie wzoru {raport}cm, co daje {pasy_z_rolki} pasy z 1 rolki.", ln=True)
                else:
                    pdf.cell(190, 7, txt=f"- Fototapeta na wymiar: Komplet ok. {round(m2_scian, 1)} m2", ln=True)
                
                klej_czysty = wybrany_klej.split(" - ")[0].replace("ż", "z").replace("ł", "l")
                pdf.cell(190, 7, txt=f"- Klej dedykowany ({klej_czysty}): {szt_kleju} op.", ln=True)
                
                if gruntowanie:
                    pdf.cell(190, 7, txt=f"- Grunt gleboko penetrujacy (5L): {szt_gruntu} opakowan", ln=True)
        
                pdf_output = pdf.output()

                if isinstance(pdf_output, (bytearray, bytes)):
                    pdf_bytes = bytes(pdf_output)
                elif isinstance(pdf_output, str):
                    pdf_bytes = pdf_output.encode('latin-1', 'replace')
                else:
                    pdf_bytes = pdf_output
        
                st.download_button(
                    label="Pobierz Kosztorys PDF",
                    data=pdf_bytes,
                    file_name=f"Kosztorys_Tapetowanie_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Błąd PDF: {e}")

# --- SEKCJA: EFEKTY DEKORACYJNE ---
elif branza == "Efekty Dekoracyjne":
    st.header("Kalkulator Efektów Dekoracyjnych")
    
    # Baza cenowa PRO (Podział na Efekt -> Marka/Półka cenowa)
    baza_dekoracji_pro = {
        "Beton architektoniczny": {
            "Jeger (Market - 1 warstwa)": {"mat": 50.0, "rob": 130.0},
            "Fox Dekorator (Profesjonalny - 2 warstwy)": {"mat": 85.0, "rob": 160.0},
            "Oikos (Premium Włoski)": {"mat": 140.0, "rob": 200.0}
        },
        "Stiuk wenecki": {
            "Magnat Style (Akrylowy)": {"mat": 60.0, "rob": 160.0},
            "Fox Dekorator (Wapienny Klasyczny)": {"mat": 95.0, "rob": 200.0},
            "San Marco (Premium - Prawdziwy marmur)": {"mat": 160.0, "rob": 250.0}
        },
        "Trawertyn": {
            "Primacol (Ekonomiczny)": {"mat": 55.0, "rob": 150.0},
            "Fox Dekorator (Profesjonalny)": {"mat": 80.0, "rob": 180.0},
            "Novacolor (Premium Włoski)": {"mat": 130.0, "rob": 220.0}
        },
        "Efekt rdzy": {
            "Jeger (Szybka rdza akrylowa)": {"mat": 70.0, "rob": 140.0},
            "Fox Dekorator (Prawdziwa rdza z aktywatorem)": {"mat": 110.0, "rob": 180.0}
        },
        "Farba strukturalna": {
            "Dekoral / Śnieżka (Market)": {"mat": 30.0, "rob": 80.0},
            "Fox Dekorator (Relief z piaskiem)": {"mat": 50.0, "rob": 120.0}
        }
    }

    tab_deko1, tab_deko2 = st.tabs(["Szybka Wycena", "Kosztorys PRO"])

    # ==========================================
    # TAB 1: SZYBKA WYCENA
    # ==========================================
    with tab_deko1:
        st.subheader("Błyskawiczny szacunek kosztów")
        
        c_fast1, c_fast2 = st.columns(2)
        with c_fast1:
            typ_fast = st.selectbox("Rodzaj efektu (Szybka wycena):", list(baza_dekoracji_pro.keys()), key="deko_typ_fast")
            m2_fast = st.number_input("Powierzchnia ściany (m2):", min_value=1.0, value=12.0, step=0.5, key="deko_m2_fast")
            
        # Szybka wycena bierze ŚREDNIĄ z dostępnych systemów dla danego efektu
        dostepne_systemy = baza_dekoracji_pro[typ_fast]
        srednia_mat = sum(sys["mat"] for sys in dostepne_systemy.values()) / len(dostepne_systemy)
        srednia_rob = sum(sys["rob"] for sys in dostepne_systemy.values()) / len(dostepne_systemy)
        
        k_mat_fast = m2_fast * srednia_mat
        k_rob_fast = m2_fast * srednia_rob
        total_fast = k_mat_fast + k_rob_fast
        
        st.success(f"### Szacowany całkowity koszt inwestycji: ok. {round(total_fast)} PLN")
        st.caption("Cena wyliczona na podstawie średniej rynkowej dla wybranego efektu (zawiera materiał i robociznę).")
        
        c_f1, c_f2 = st.columns(2)
        c_f1.metric("Szacowany Materiał (Średnia)", f"{round(k_mat_fast)} PLN")
        c_f2.metric("Szacowana Robocizna (Średnia)", f"{round(k_rob_fast)} PLN")
        
        st.info("Przejdź do zakładki Kosztorys PRO, aby wybrać konkretnego producenta (np. Fox, Oikos) i wygenerować PDF.")

    # ==========================================
    # TAB 2: KOSZTORYS PRO
    # ==========================================
    with tab_deko2:
        if not st.session_state.zalogowany or st.session_state.pakiet != "PRO":
            st.error("🔒 **Dostęp zablokowany**")
            _, col_k, _ = st.columns([1, 2, 1])
            with col_k:
                if st.button("Odblokuj dostęp (Przejdź do logowania)", use_container_width=True, key="btn_odblokuj_deko"):
                    st.session_state.przekierowanie = True  
                    st.rerun()  
        else:
            # --- TYLKO DLA ZALOGOWANYCH ---
            col_d1, col_d2 = st.columns([1, 1.2])

            with col_d1:
                st.subheader("Parametry zlecenia")
                m2_pro = st.number_input("Dokładna powierzchnia (m2):", min_value=1.0, value=12.0, step=0.1, key="deko_m2_pro")
                
                wybrany_efekt = st.selectbox(
                    "1. Wybierz rodzaj efektu:", 
                    options=list(baza_dekoracji_pro.keys()),
                    key="deko_typ_pro"
                )
                
                # Zależny dropdown - pokazuje marki tylko dla wybranego efektu
                wybrana_marka = st.selectbox(
                    "2. System / Producent:", 
                    options=list(baza_dekoracji_pro[wybrany_efekt].keys()),
                    key="deko_marka_pro"
                )
                
                st.markdown("---")
                st.write("**Stawki (PLN/m2)**")
                # Zaciągamy stawki dla KONKRETNEJ marki
                cena_mat_m2 = st.number_input("Koszt materiału za m2 (zł):", min_value=10.0, value=baza_dekoracji_pro[wybrany_efekt][wybrana_marka]["mat"])
                cena_rob_m2 = st.number_input("Stawka za wykonanie 1 m2 (zł):", min_value=50.0, value=baza_dekoracji_pro[wybrany_efekt][wybrana_marka]["rob"])

                st.markdown("---")
                st.write("**Usługi dodatkowe**")
                przygotowanie = st.checkbox("Wzmocnienie ściany (siatka + klej)")
                zabezpieczenie = st.checkbox("Dodatkowa warstwa wosku/lakieru (strefy mokre)")

            # --- LOGIKA OBLICZEŃ ---
            koszt_bazowy_mat = m2_pro * cena_mat_m2
            koszt_bazowy_rob = m2_pro * cena_rob_m2
            
            doplata_mat_dodatki = 0
            doplata_rob_dodatki = 0
            
            if przygotowanie:
                doplata_mat_dodatki += (m2_pro * 15) 
                doplata_rob_dodatki += (m2_pro * 30)
                
            if zabezpieczenie:
                doplata_mat_dodatki += (m2_pro * 10) 
                doplata_rob_dodatki += (m2_pro * 20)

            total_materialy = koszt_bazowy_mat + doplata_mat_dodatki
            total_robocizna = koszt_bazowy_rob + doplata_rob_dodatki
            suma_calkowita = total_materialy + total_robocizna

            # Wyciągamy samą nazwę producenta do wydruku (np. z "Fox Dekorator (Profesjonalny)" robi "Fox Dekorator")
            krotka_nazwa_systemu = wybrana_marka.split(" (")[0]

            # --- GENEROWANIE LISTY ZAKUPÓW NA PODSTAWIE NORM ---
            lista_zakupow = []
            if wybrany_efekt == "Beton architektoniczny":
                lista_zakupow = [
                    (f"Tynk mineralny beton ({krotka_nazwa_systemu})", f"{round(m2_pro * 2.0, 1)} kg"),
                    (f"Grunt kwarcowy podkładowy", f"{round(m2_pro * 0.2, 1)} L"),
                    (f"Lakier zabezpieczający matowy", f"{round(m2_pro * 0.15, 1)} L")
                ]
            elif wybrany_efekt == "Stiuk wenecki":
                lista_zakupow = [
                    (f"Masa stiukowa ({krotka_nazwa_systemu})", f"{round(m2_pro * 1.0, 1)} kg"),
                    (f"Grunt sczepny / podkład", f"{round(m2_pro * 0.15, 1)} L"),
                    (f"Wosk polerski impregnujący", f"{round(m2_pro * 0.05, 1)} kg")
                ]
            elif wybrany_efekt == "Trawertyn":
                lista_zakupow = [
                    (f"Tynk trawertyn w proszku ({krotka_nazwa_systemu})", f"{round(m2_pro * 1.5, 1)} kg"),
                    (f"Grunt z piaskiem kwarcowym", f"{round(m2_pro * 0.2, 1)} L"),
                    (f"Przecierka koloryzująca / Lakier", f"{round(m2_pro * 0.15, 1)} L")
                ]
            elif wybrany_efekt == "Efekt rdzy":
                lista_zakupow = [
                    (f"Farba podkładowa z opiłkami żelaza ({krotka_nazwa_systemu})", f"{round(m2_pro * 0.3, 1)} L"),
                    (f"Aktywator rdzy (spray/pędzel)", f"{round(m2_pro * 0.2, 1)} L"),
                    (f"Lakier odcinający reakcję", f"{round(m2_pro * 0.15, 1)} L")
                ]
            else:
                lista_zakupow = [
                    (f"Farba strukturalna ({krotka_nazwa_systemu})", f"{round(m2_pro * 0.4, 1)} L"),
                    (f"Grunt szczepny pod kolor", f"{round(m2_pro * 0.2, 1)} L")
                ]
                
            if przygotowanie: lista_zakupow.append(("Klej elastyczny + siatka z włókna", f"{round(m2_pro)} m2"))
            if zabezpieczenie: lista_zakupow.append(("Dodatkowa warstwa ochronna (wosk/lakier)", f"{round(m2_pro * 0.1, 1)} L"))

            with col_d2:
                st.subheader("Podsumowanie Kosztorysu")
                
                st.success(f"### KOSZT CAŁKOWITY: **{round(suma_calkowita)} PLN**")
                st.caption(f"Wycena dla systemu: **{wybrana_marka}**")

                c1, c2 = st.columns(2)
                c1.metric("Materiał (System + Grunt)", f"{round(total_materialy)} PLN")
                c2.metric("Robocizna", f"{round(total_robocizna)} PLN")

                st.markdown("---")
                st.subheader("Wymagane materiały (Normy zużycia)")
                for nazwa, ilosc in lista_zakupow:
                    st.write(f"• **{nazwa}:** {ilosc}")

                # --- GENERATOR PDF ---
                try:
                    from fpdf import FPDF
                    from datetime import datetime
                    import os
                    import base64

                    if st.button("Generuj Kosztorys PDF", use_container_width=True, key="deko_pdf_btn"):
                        pdf = FPDF()
                        pdf.add_page()
                        
                        f_path = "Inter-Regular.ttf"
                        if os.path.exists(f_path):
                            pdf.add_font("Inter", "", f_path)
                            pdf.set_font("Inter", size=12)
                        else:
                            pdf.set_font("Arial", size=12)
                        
                        pdf.set_font(pdf.font_family, size=16)
                        pdf.cell(0, 15, "KOSZTORYS: EFEKTY DEKORACYJNE", ln=True, align='C')
                        pdf.ln(5)

                        pdf.set_fill_color(245, 245, 245)
                        pdf.set_font(pdf.font_family, size=12)
                        
                        def czysc_tekst(tekst):
                            pl_znaki = {'ą':'a','ć':'c','ę':'e','ł':'l','ń':'n','ó':'o','ś':'s','ź':'z','ż':'z','Ą':'A','Ć':'C','Ę':'E','Ł':'L','Ń':'N','Ó':'O','Ś':'S','Ź':'Z','Ż':'Z'}
                            for pl, ang in pl_znaki.items(): tekst = tekst.replace(pl, ang)
                            return tekst.encode('latin-1', 'replace').decode('latin-1')

                        pdf.cell(95, 10, " Wybrany system:", 1)
                        pdf.cell(95, 10, f" {czysc_tekst(wybrany_efekt)}", 1, 1)
                        pdf.cell(95, 10, " Producent / Klasa:", 1)
                        pdf.cell(95, 10, f" {czysc_tekst(wybrana_marka)}", 1, 1)
                        pdf.cell(95, 10, " Powierzchnia sciany:", 1)
                        pdf.cell(95, 10, f" {m2_pro} m2", 1, 1)

                        pdf.ln(10)
                        pdf.cell(95, 10, " Wycena Robocizny:", 1)
                        pdf.cell(95, 10, f" {round(total_robocizna)} PLN", 1, 1)
                        pdf.cell(95, 10, " Koszt materialow (System):", 1)
                        pdf.cell(95, 10, f" {round(total_materialy)} PLN", 1, 1)
                        
                        pdf.set_font(pdf.font_family, size=13)
                        pdf.cell(95, 12, " LACZNY KOSZT INWESTYCJI:", 1, 0, 'L', True)
                        pdf.cell(95, 12, f" {round(suma_calkowita)} PLN", 1, 1, 'L', True)
                        
                        pdf.ln(10)
                        pdf.set_font(pdf.font_family, size=12)
                        pdf.cell(0, 10, "LISTA ZAKUPOW (Normy producenta):", ln=True)
                        pdf.set_font(pdf.font_family, size=10)
                        
                        for nazwa, ilosc in lista_zakupow:
                            pdf.cell(0, 7, f"- {czysc_tekst(nazwa)}: {czysc_tekst(ilosc)}", ln=True)

                        pdf_bytes = pdf.output(dest="S").encode('latin-1')
                        pdf_b64 = base64.b64encode(pdf_bytes).decode()
                        href = f'<a href="data:application/pdf;base64,{pdf_b64}" download="Kosztorys_Dekoracje_{datetime.now().strftime("%Y%m%d")}.pdf" style="display: block; text-align: center; padding: 15px; background-color: #00D395; color: white; text-decoration: none; border-radius: 10px; font-weight: bold; font-size: 18px; margin-top: 10px;">Pobierz gotowy PDF</a>'
                        st.markdown(href, unsafe_allow_html=True)
                        
                except Exception as e:
                    st.error(f"Błąd podczas generowania PDF: {e}")

                st.markdown("---")
                st.subheader("💾 Zapisz Kosztorys w Chmurze")
                st.caption("Zapisz ten projekt, aby pobrać go później w Panelu Inwestora.")
                
                nazwa_projektu = st.text_input("Nazwa projektu (np. Ściana TV - Beton Fox):", key="nazwa_proj_deko")
                
                if st.button("Zapisz Projekt", use_container_width=True, type="primary", key="btn_zapisz_deko"):
                    if not nazwa_projektu:
                        st.warning("⚠️ Podaj nazwę projektu przed zapisaniem.")
                    elif 'user_id' not in st.session_state or not st.session_state.user_id:
                        st.error("❌ Błąd krytyczny: Zgubiłeś sesję! Wyloguj się i zaloguj ponownie.")
                    else:
                        try:
                            zakupy_do_bazy = [f"{n}: {i}" for n, i in lista_zakupow]
                            
                            dane_do_zapisu = {
                                "typ_efektu": wybrany_efekt,
                                "producent": wybrana_marka,
                                "powierzchnia_m2": m2_pro,
                                "koszt_materialow": total_materialy,
                                "koszt_robocizny": total_robocizna,
                                "suma_calkowita": suma_calkowita,
                                "lista_zakupow": {"MATERIAŁY (SYSTEM)": zakupy_do_bazy}
                            }
                            
                            supabase.table("projekty").insert({
                                "user_id": st.session_state.user_id, 
                                "nazwa_projektu": nazwa_projektu,
                                "branza": "Efekty Dekoracyjne",
                                "dane_json": dane_do_zapisu
                            }).execute()
                            
                            st.success(f"✅ Projekt '{nazwa_projektu}' został bezpiecznie zapisany w chmurze!")
                        except Exception as e:
                            st.error(f"❌ Wystąpił błąd podczas zapisywania: {e}")
                            


# ==========================================
# TUTAJ WCHODZI NASZ NOWY PANEL INWESTORA!
# ==========================================
elif branza == "Panel Inwestora":
    st.markdown("<br>", unsafe_allow_html=True)
    if not st.session_state.zalogowany:
        st.warning("Ta sekcja dostępna jest wyłącznie dla zalogowanych użytkowników.")
        st.info("Przejdź do zakładki 'Logowanie' w górnym menu, aby założyć darmowe konto.")
    else:
        st.header("Pulpit Inwestora: Projekt Kompleksowy 🏢")
        
        # --- START: SEKCJA TWOJE PROJEKTY ---
        st.markdown("---")
        st.subheader("Twoje Zapisane Kosztorysy")
        
        u_id = st.session_state.get("user_id")
        
        if supabase and u_id:
            try:
                # Szukamy projektów tylko dla zalogowanego ID
                response = supabase.table("projekty").select("*").eq("user_id", u_id).order("data_stworzenia", desc=True).execute()
                zapisane_projekty = response.data
                
                if not zapisane_projekty:
                    st.info("Nie masz jeszcze żadnych zapisanych projektów w chmurze. Skonfiguruj projekt poniżej i zapisz go na ostatniej zakładce!")
                else:
                    col_h1, col_h2, col_h3, col_h4 = st.columns([3, 2, 1, 1])
                    col_h1.caption("Nazwa projektu")
                    col_h2.caption("Data")
                    
                    for proj in zapisane_projekty:
                        c1, c2, c3, c4 = st.columns([3, 2, 1, 1])
                        c1.write(f"**{proj['nazwa_projektu']}**")
                        c2.write(proj['data_stworzenia'][:10])
                        
                        if c3.button("Podgląd", key=f"view_{proj['id']}"):
                            st.json(proj['dane_json'])
                            
                        if c4.button("Usuń", key=f"del_{proj['id']}"):
                            supabase.table("projekty").delete().eq("id", proj['id']).execute()
                            st.rerun()
            except Exception as e:
                st.error(f"Błąd wczytywania projektów: {e}")
        else:
            st.warning("⚠️ Nie wykryto technicznego ID użytkownika. Wyloguj się i zaloguj ponownie.")
        
        st.markdown("---")
        st.write("### Skonfiguruj nowy kosztorys:")
        # --- KONIEC: SEKCJA TWOJE PROJEKTY ---

        tab_roi, tab_suche, tab_mokre, tab_ele, tab_podl, tab_meble, tab_podsumowanie = st.tabs([
            "1. ROI & Koszty", 
            "2. Prace Suche", 
            "3. Łazienka", 
            "4. Elektryka",
            "5. Podłogi & Drzwi", 
            "6. Stolarka & Meble",
            "7. Podsumowanie & Lista Zakupów"
        ])

        import math

        # --- ZAKŁADKA 1: PARAMETRY, KOSZTY STAŁE I ROI ---
        with tab_roi:
            st.subheader("Parametry Lokalu i Koszty Stałe")
            col_params, col_check = st.columns([1.2, 1])
            with col_params:
                nazwa_inwestycji = st.text_input("Nazwa Inwestycji:", value="Kawalerka na Start", key="inv_nazwa")
                m2_total = st.number_input("Metraż całkowity (m2):", min_value=1.0, value=50.0, key="inv_m2_total")
                cena_zakupu = st.number_input("Cena zakupu (PLN):", value=350000, step=5000, key="inv_cena_zakupu")
                cena_sprzedazy = st.number_input("Cena sprzedaży (PLN):", value=550000, step=5000, key="inv_cena_sprzedazy")
                stan_lokalu = st.radio("Stan lokalu:", ["Deweloperski", "Rynek Wtórny (Do remontu)"], key="inv_stan")

                st.markdown("##### Koszty Utrzymania (W trakcie flipa)")
                c_utr1, c_utr2, c_utr3 = st.columns(3)
                czynsz_mc = c_utr1.number_input("Czynsz do adm. (zł/mc):", 0, 3000, 500, step=50, key="inv_czynsz")
                media_mc = c_utr2.number_input("Prąd/Woda (zł/mc):", 0, 2000, 150, step=50, key="inv_media")
                czas_operacji = c_utr3.number_input("Czas trwania (mc):", 1, 36, 4, step=1, help="Czas remontu + szukanie kupca", key="inv_czas_mc")

            with col_check:
                st.markdown("##### Checklista Przedzakupowa")
                st.checkbox("Piony wod-kan (stan żeliwa/plastiku)", key="inv_ch_piony")
                st.checkbox("Okna (szczelność/wiek/pakiet szyb)", key="inv_ch_okna")
                st.checkbox("Instalacja elek. (miedź vs alu)", key="inv_ch_elek")
                st.checkbox("KW czysta (Dział III i IV)", key="inv_ch_kw")
                
                st.markdown("---")
                st.markdown("##### Budżet na robociznę (Szacunek)")
                standard = st.select_slider("Standard wykończenia:", options=["Ekonomiczny", "Standard", "Premium"], key="inv_standard")
                mnoznik_std = 0.8 if standard == "Ekonomiczny" else (1.3 if standard == "Premium" else 1.0)
                bazowy_remont_szacunek = (m2_total * 1200 * mnoznik_std) 
                if stan_lokalu == "Rynek Wtórny (Do remontu)": bazowy_remont_szacunek *= 1.25
                st.info(f"Szacowany koszt prac: **~{round(bazowy_remont_szacunek):,} zł**".replace(",", " "))

        
        # --- ZAKŁADKA 2: PRACE SUCHE ---
        with tab_suche:
            st.subheader("Gładzie, Malowanie i Zabudowy")
            
            # --- SEKCJA 1: GK ---
            st.markdown("#### 1. Konstrukcje GK")
            do_gk_inv = st.checkbox("Wlicz Sufity Podwieszane GK", value=False, key="inv_do_gk")
            if do_gk_inv:
                c_gk1, c_gk2 = st.columns(2)
                rodzaj_stelaza = c_gk1.radio("Konstrukcja stelaża:", ["Pojedynczy (Standard)", "Krzyżowy (Mniej spękań)"], key="inv_gk_stelaz")
                system_laczen = c_gk2.selectbox("System łączeń płyt:", ["Taśma z włókna", "Taśma TUFF-TAPE (Premium)", "Flizelina"], key="inv_gk_laczenia")
                c_gk3, c_gk4 = st.columns(2)
                rodzaj_plyty = c_gk3.selectbox("Rodzaj płyty:", ["Zwykła GKB", "Impregnowana GKBI (Zielona)"], key="inv_gk_plyta")
                welna_izolacja = c_gk4.checkbox("Dodaj wełnę mineralną", key="inv_gk_welna")
            
            st.markdown("---")
            
            # --- SEKCJA 2: GŁADZIE ---
            st.markdown("#### 2. Szpachlowanie i Gładzie")
            do_szpach_inv = st.checkbox("Wlicz Szpachlowanie", value=True, key="inv_do_szpach")
            
            if do_szpach_inv:
                # Bazy danych materiałów
                baza_sypka = {
                    "Cekol C-45 (20kg)": {"cena": 65, "waga": 20},
                    "FransPol GS-2 (20kg)": {"cena": 45, "waga": 20},
                    "Dolina Nidy Omega (20kg)": {"cena": 38, "waga": 20},
                    "Atlas Gipsar Uni (20kg)": {"cena": 45, "waga": 20}
                }
                baza_gotowa = {
                    "Śmig A-2 (20kg)": {"cena": 55, "waga": 20},
                    "Knauf Goldband Finish (18kg)": {"cena": 60, "waga": 18},
                    "Knauf Goldband Finish (28kg)": {"cena": 80, "waga": 28},
                    "Knauf Fill & Finish Light (20kg)": {"cena": 120, "waga": 20},
                    "Sheetrock Super Finish (28kg)": {"cena": 135, "waga": 28},
                    "Atlas GTA (18kg)": {"cena": 70, "waga": 18},
                    "Atlas GTA (25kg)": {"cena": 90, "waga": 25}
                }
                baza_start = {
                    "FransPol GS-100 (20kg)": {"cena": 45, "waga": 20},
                    "Nida Start (20kg)": {"cena": 40, "waga": 20},
                    "Knauf Fugenfuller (25kg)": {"cena": 55, "waga": 25}
                }

                c_sz1, c_sz2 = st.columns(2)
                typ_gl_radio = c_sz1.radio("Typ gładzi:", ["Sypka (Worki)", "Gotowa (Wiadra)"], horizontal=True, key="inv_szpach_typ_radio")
                
                # Wybór konkretnego produktu na podstawie typu
                if "Sypka" in typ_gl_radio:
                    produkt_gl = c_sz2.selectbox("Wybierz gładź sypką:", list(baza_sypka.keys()), key="inv_gl_produkt_sypka")
                    dane_materialu = baza_sypka[produkt_gl]
                else:
                    produkt_gl = c_sz2.selectbox("Wybierz gładź gotową:", list(baza_gotowa.keys()), key="inv_gl_produkt_gotowa")
                    dane_materialu = baza_gotowa[produkt_gl]

                c_sz3, c_sz4 = st.columns(2)
                liczba_warstw_gl = c_sz3.slider("Liczba warstw gładzi:", 1, 3, 2, key="inv_szpach_warstwy")
                
                # Opcjonalny gips startowy
                mocny_start = c_sz4.checkbox("Wlicz gips startowy (równanie)", key="inv_szpach_start")
                if mocny_start:
                    produkt_start = st.selectbox("Wybierz gips startowy:", list(baza_start.keys()), key="inv_gl_start_produkt")
                    dane_startu = baza_start[produkt_start]
                
            st.markdown("---")
            
            # --- SEKCJA 3: MALOWANIE ---
            st.markdown("#### 3. Gruntowanie i Malowanie")
            do_mal_inv = st.checkbox("Wlicz Gruntowanie i Malowanie", value=True, key="inv_do_mal")
            
            if do_mal_inv:
                baza_grunty = {
                    "Atlas Unigrunt (Standard)": 8, 
                    "Ceresit CT 17 (Klasyk)": 12,
                    "Knauf Tiefengrund (Premium)": 14,
                    "Mapei Primer G Pro (Koncentrat)": 17
                }
                baza_biale = {
                    "Śnieżka Eko (Ekonomiczna)": 7,
                    "Dekoral Polinak (Standard)": 10,
                    "Beckers Designer White (Standard+)": 14,
                    "Magnat Ultra Matt (Premium)": 18,
                    "Tikkurila Anti-Reflex 2 (Premium+)": 28,
                    "Flugger Flutex Pro 5 (Top Premium)": 35
                }
                baza_kolory = {
                    "Śnieżka Barwy Natury (Eko)": 17,
                    "Dekoral Akrylit W (Standard)": 20,
                    "Magnat Ceramic (Standard+)": 30,
                    "Beckers Designer Colour (Premium)": 32,
                    "Tikkurila Optiva 5 (Premium+)": 50,
                    "Flugger Dekso (Top Premium)": 70
                }

                st.markdown("##### Gruntowanie")
                wybrany_grunt = st.selectbox("Wybierz grunt:", list(baza_grunty.keys()), key="inv_grunt_wybor")
                
                st.markdown("##### Farby")
                c_m1, c_m2 = st.columns(2)
                
                with c_m1:
                    st.write("**Sufity (Biała)**")
                    produkt_biala = st.selectbox("Farba na sufit:", list(baza_biale.keys()), key="inv_paint_white")
                
                with c_m2:
                    st.write("**Ściany (Kolor)**")
                    produkt_kolor = st.selectbox("Farba na ściany:", list(baza_kolory.keys()), key="inv_paint_color")

                liczba_warstw_mal = st.slider("Liczba warstw farby (łącznie):", 1, 3, 2, key="inv_mal_warstwy")
                
        # --- ZAKŁADKA 3: ŁAZIENKA ---
        # --- ZAKŁADKA 3: KONFIGURACJA ŁAZIENKI ---
        with tab_mokre:
            st.subheader("Konfiguracja Łazienki 🚿")
            do_laz_inv = st.checkbox("Wlicz Remont Łazienki", value=True, key="inv_do_laz")
            
            if do_laz_inv:
                # --- BAZY DANYCH MATERIAŁÓW ---
                baza_kleje = {
                    "Atlas Geoflex (Żelowy, C2TE) - 25kg": 65,
                    "Atlas Plus (Wysokoelastyczny S1) - 25kg": 85,
                    "Kerakoll Bioflex (Żelowy) - 25kg": 75,
                    "Kerakoll H40 (Premium) - 25kg": 125,
                    "Mapei Keraflex Extra S1 - 25kg": 80,
                    "Sopro No.1 (400) - 22.5kg": 115,
                    "Klej Standardowy C2T - 25kg": 50
                }
                baza_folie = {
                    "Standardowa folia w płynie - 5kg": {"cena": 80, "waga": 5},
                    "Sopro FDF 525 - 5kg": {"cena": 165, "waga": 5},
                    "Sopro FDF 525 - 15kg": {"cena": 440, "waga": 15},
                    "Ceresit CL 51 - 5kg": {"cena": 110, "waga": 5},
                    "Ceresit CL 51 - 15kg": {"cena": 275, "waga": 15},
                    "Atlas Woder E - 5kg": {"cena": 95, "waga": 5},
                    "Atlas Woder E - 15kg": {"cena": 255, "waga": 15}
                }
                baza_maty = {
                    "Mata uszczelniająca Standard (m2)": 45,
                    "Mata Sopro AEB 640 (m2)": 85,
                    "Mata Knauf (m2)": 75,
                    "Mata Ceresit CL 152 (m2)": 70,
                    "Mata Kerakoll Aquastop (m2)": 65,
                    "Mata Mapei Mapeguard (m2)": 80
                }
                baza_masy_2k = {
                    "Masa 1K/2K Standard - 15kg": {"cena": 180, "waga": 15},
                    "Sopro DSF 523 - 10kg": {"cena": 230, "waga": 10},
                    "Sopro DSF 523 - 20kg": {"cena": 395, "waga": 20},
                    "Kerakoll Aquastop Nanoflex - 20kg": {"cena": 260, "waga": 20},
                    "Atlas Woder Duo (Masa 2K) - 15kg": {"cena": 240, "waga": 15},
                    "Mapei Mapelastic (Masa 2K) - 16kg": {"cena": 290, "waga": 16}
                }

                # --- INTERFEJS ---
                st.markdown("#### 1. Wymiary i Płytki")
                c_l1, c_l2 = st.columns(2)
                m2_laz = c_l1.number_input("Powierzchnia łazienki (m2 podłogi):", 1.0, 30.0, 5.0, key="inv_laz_m2")
                format_plytek_laz = c_l2.selectbox("Format płytek:", ["Standard (do 60x60)", "Wielki Format (120x60)", "Spiek / Mega Format"], key="inv_laz_format")
                
                st.markdown("---")
                st.markdown("#### 2. Hydroizolacja (Strefa Mokra)")
                c_l3, c_l4 = st.columns([1, 2])
                
                # Wybór technologii
                typ_hydro = c_l3.radio("System ochrony:", ["Folia w płynie", "Mata Uszczelniająca", "Masa 2K (Szlam)"], key="inv_laz_hydro_tech")
                m2_hydro = c_l4.number_input("Metraż hydroizolacji (m2 ścian i podłóg):", 2.0, 50.0, 8.0, key="inv_laz_hydro_m2")
                
                # Wybór konkretnego produktu na podstawie technologii
                if "Folia" in typ_hydro:
                    produkt_hydro = st.selectbox("Wybierz folię w płynie:", list(baza_folie.keys()), key="inv_laz_prod_folia")
                elif "Mata" in typ_hydro:
                    produkt_hydro = st.selectbox("Wybierz matę uszczelniającą:", list(baza_maty.keys()), key="inv_laz_prod_mata")
                else:
                    produkt_hydro = st.selectbox("Wybierz masę 2K:", list(baza_masy_2k.keys()), key="inv_laz_prod_2k")

                st.markdown("---")
                st.markdown("#### 3. Klejenie i Fugowanie")
                c_l5, c_l6 = st.columns(2)
                
                # Inteligentna podpowiedź kleju
                rekomendacja_kleju = list(baza_kleje.keys())[1] if "Wielki" in format_plytek_laz else list(baza_kleje.keys())[0]
                wybrany_klej = c_l5.selectbox("Wybierz klej:", list(baza_kleje.keys()), index=list(baza_kleje.keys()).index(rekomendacja_kleju), key="inv_laz_klej_wybor")
                
                rodzaj_fugi_laz = c_l6.radio("Rodzaj fugi:", ["Cementowa", "Epoksydowa (Szczelna/Premium)"], key="inv_laz_fuga")
                
                st.markdown("#### 4. Dodatki")
                odplyw_liniowy = st.checkbox("Odpływ liniowy (wymaga spadków/koperty)", value=True, key="inv_laz_odplyw")
                if odplyw_liniowy:
                    st.info("💡 Pamiętaj: Odpływ liniowy wymaga użycia masy 2K lub maty wokół rynny dla pełnej szczelności.")

        # --- ZAKŁADKA 4: ELEKTRYKA ---
        with tab_ele:
            st.subheader("Instalacja Elektryczna ⚡")
            do_elek_inv = st.checkbox("Wymiana całej instalacji elektrycznej", value=True, key="inv_do_ele")
            if do_elek_inv:
                c_e1, c_e2 = st.columns(2)
                szt_punktow = c_e1.number_input("Szacowana ilość punktów (gniazda/włączniki):", 10, 150, 45, key="inv_ele_punkty")
                std_osprzet = c_e2.selectbox("Standard osprzętu:", ["Ekonomiczny (np. Simon 10)", "Standard (np. Sedna, As)", "Premium (np. Simon 54, Legrand)"], key="inv_ele_std")
                
                rob_ele = szt_punktow * 110 
                mat_ele = szt_punktow * 45 
                koszt_ele_total = rob_ele + mat_ele
                st.info(f"Szacowany koszt elektryki (Robocizna + Materiał): **{koszt_ele_total:,} zł**".replace(",", " "))
            else:
                koszt_ele_total = 0

        # --- ZAKŁADKA 5: PODŁOGI, WYLEWKI I DRZWI ---
        with tab_podl:
            st.subheader("Podłogi i Stolarka Otworowa 🪵")
            
            st.markdown("##### 1. Przygotowanie podłoża i Wylewki")
            c_p1, c_p2 = st.columns(2)
            zrywanie_podlogi = c_p1.checkbox("Zrywanie starego parkietu / płytek", key="inv_zrywanie")
            wylewka_samopoz = c_p2.checkbox("Wylewka samopoziomująca", key="inv_wylewka")
            
            koszt_podloze_total = 0
            if zrywanie_podlogi:
                koszt_podloze_total += (m2_total * 35) 
            
            if wylewka_samopoz:
                grubosc_wyl = st.slider("Średnia grubość wylewki (mm):", 3, 20, 5, key="inv_wyl_grub")
                kg_wylewki = 1.6 * grubosc_wyl * m2_total
                worki_wylewki = math.ceil(kg_wylewki / 25)
                koszt_mat_wyl = worki_wylewki * 55 
                koszt_rob_wyl = m2_total * 25
                koszt_podloze_total += (koszt_mat_wyl + koszt_rob_wyl)
                st.caption(f"Potrzeba ok. **{worki_wylewki} worków** samopoziomu. Koszt wylewek: {round(koszt_mat_wyl + koszt_rob_wyl):,} zł.")
            else:
                worki_wylewki = 0

            st.markdown("---")
            st.markdown("##### 2. Wykończenie Podłóg")
            do_podl_fin = st.checkbox("Układanie nowej podłogi", value=True, key="inv_podl_fin")
            if do_podl_fin:
                typ_p = st.selectbox("Materiał:", ["Panele Laminowane", "Winyle (SPC/LVT)", "Deska/Parkiet"], key="inv_p_typ")
            
            st.markdown("---")
            st.markdown("##### 3. Drzwi")
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.markdown("**Drzwi Wewnętrzne**")
                do_drzwi = st.checkbox("Montaż nowych drzwi", value=True, key="inv_do_drzwi_wew_ch")
                if do_drzwi:
                    szt_d_wew = st.number_input("Ilość (szt):", 1, 10, 3, key="inv_d_wew_szt")
                    typ_d_wew = st.selectbox("Rodzaj:", ["Przylgowe (Budżet)", "Bezprzylgowe (Standard)", "Ukryta ościeżnica (Premium)"], key="inv_d_wew_typ")
                    koszt_drzwi_wew = szt_d_wew * (1000 if "Przylgowe" in typ_d_wew else (2500 if "Ukryta" in typ_d_wew else 1600))
                else:
                    koszt_drzwi_wew = 0
            
            with col_d2:
                st.markdown("**Drzwi Wejściowe**")
                wymiana_wej = st.checkbox("Wymień drzwi wejściowe", key="inv_d_wej_do")
                if wymiana_wej:
                    typ_d_wej = st.selectbox("Standard:", ["Marketowe (ok. 1200 zł)", "Standard (Porta/KrCenter)", "Premium (Gerda)"], key="inv_d_wej_typ")
                    koszt_drzwi_wej = 1200 if "Marketowe" in typ_d_wej else (4500 if "Premium" in typ_d_wej else 2800)
                else:
                    koszt_drzwi_wej = 0
                    
            koszt_drzwi_total = koszt_drzwi_wew + koszt_drzwi_wej

        # --- ZAKŁADKA 6: STOLARKA (Meble na wymiar) ---
        with tab_meble:
            st.subheader("Meble na wymiar i zabudowy 🪚")
            c_m1, c_m2 = st.columns(2)
            kuchnia_inv = c_m1.number_input("Budżet na kuchnię (PLN):", 0, 100000, 20000, step=1000, key="inv_k_budzet")
            szafy_inv = c_m2.number_input("Budżet na szafy/wnęki (PLN):", 0, 50000, 4500, step=500, key="inv_s_budzet")
            laz_stolarz = st.number_input("Szafka umywalkowa / Zabudowa pralki (PLN):", 0, 15000, 1500, step=100, key="inv_l_budzet")
            
            koszt_mebli_total = kuchnia_inv + szafy_inv + laz_stolarz

# --- ZAKŁADKA 7: PODSUMOWANIE & LISTA ZAKUPÓW ---
        with tab_podsumowanie:
            st.subheader("Analiza Rentowności i Kosztorys Materiałowy 📊")

            # --- 1. RE-KALKULACJA KOSZTÓW MATERIAŁÓW (MÓZG SYSTEMU) ---
            koszt_materialow_detal = 0
            zakupy = {"ELEKTRYKA": [], "ŁAZIENKA": [], "SUCHY MONTAŻ (G-K)": [], "ŚCIANY (GŁADZIE I MALOWANIE)": [], "PODŁOGI I DRZWI": [], "ZABUDOWY MEBLOWE": []}

            # ELEKTRYKA
            if do_elek_inv:
                zakupy["ELEKTRYKA"].extend([
                    f"Przewód 3x2.5 (Gniazda): ~{int(m2_total*2.5)} mb",
                    f"Przewód 3x1.5 (Światło): ~{int(m2_total*1.5)} mb",
                    "Rozdzielnica + Bezpieczniki",
                    f"Osprzęt ({std_osprzet}): {szt_punktow} szt."
                ])

            # ŁAZIENKA
            if do_laz_inv:
                m2_plytek_laz = m2_laz * 3.5 
                cena_kleju = baza_kleje[wybrany_klej]
                worki_kleju = math.ceil((m2_plytek_laz * 5) / 25) 
                koszt_materialow_detal += (worki_kleju * cena_kleju)
                
                zakupy["ŁAZIENKA"].extend([
                    f"Płytki ({format_plytek_laz}): ok. {math.ceil(m2_plytek_laz * 1.15)} m2",
                    f"Klej ({wybrany_klej}): {worki_kleju} worków",
                    f"Fuga ({rodzaj_fugi_laz}): 2-3 op."
                ])
                if odplyw_liniowy: zakupy["ŁAZIENKA"].append("Odpływ liniowy (koperta) - 1 szt.")
                
                # Hydroizolacja
                if "Folia" in typ_hydro:
                    dane_h = baza_folie[produkt_hydro]
                    op_h = math.ceil((m2_hydro * 1.5) / dane_h['waga'])
                    koszt_materialow_detal += (op_h * dane_h['cena'])
                    zakupy["ŁAZIENKA"].append(f"Hydroizolacja ({produkt_hydro}): {op_h} szt.")
                elif "Mata" in typ_hydro:
                    cena_m = baza_maty[produkt_hydro]
                    koszt_materialow_detal += (m2_hydro * cena_m)
                    zakupy["ŁAZIENKA"].append(f"Mata uszczelniająca ({produkt_hydro}): {math.ceil(m2_hydro)} m2")
                else: 
                    dane_m2k = baza_masy_2k[produkt_hydro]
                    op_m2k = math.ceil((m2_hydro * 2.5) / dane_m2k['waga'])
                    koszt_materialow_detal += (op_m2k * dane_m2k['cena'])
                    zakupy["ŁAZIENKA"].append(f"Masa 2K ({produkt_hydro}): {op_m2k} szt.")
                koszt_materialow_detal += (m2_plytek_laz * 1.15 * 100) # szacunek za same płytki

            # G-K
            if do_gk_inv:
                zakupy["SUCHY MONTAŻ (G-K)"].extend([
                    f"Płyty GK ({rodzaj_plyty}): {math.ceil((m2_total*1.1)/3)} szt.",
                    f"Stelaż ({rodzaj_stelaza}) - profile CD/UD i wieszaki",
                    f"Łączenia: {system_laczen}"
                ])
                if welna_izolacja: zakupy["SUCHY MONTAŻ (G-K)"].append(f"Wełna mineralna: {math.ceil(m2_total)} m2")

            # GŁADZIE I MALOWANIE
            pow_scian_total = m2_total * 3.5
            if do_szpach_inv:
                d_gl = baza_sypka[produkt_gl] if "Sypka" in typ_gl_radio else baza_gotowa[produkt_gl]
                worki_gl = math.ceil((pow_scian_total * liczba_warstw_gl * 1.0) / d_gl['waga'])
                koszt_materialow_detal += (worki_gl * d_gl['cena'])
                zakupy["ŚCIANY (GŁADZIE I MALOWANIE)"].append(f"Gładź ({produkt_gl}): {worki_gl} op.")
                if mocny_start: zakupy["ŚCIANY (GŁADZIE I MALOWANIE)"].append(f"Gips szpachlowy (Start): {math.ceil(pow_scian_total/20)} worków")

            if do_mal_inv:
                cena_gruntu = baza_grunty[wybrany_grunt]
                op_gruntu = math.ceil(pow_scian_total / 50)
                koszt_materialow_detal += (op_gruntu * cena_gruntu * 5)
                zakupy["ŚCIANY (GŁADZIE I MALOWANIE)"].append(f"Grunt ({wybrany_grunt}): {op_gruntu} bańki 5L")
                
                litry_biala = math.ceil(m2_total * 0.2) 
                koszt_materialow_detal += (litry_biala * baza_biale[produkt_biala])
                zakupy["ŚCIANY (GŁADZIE I MALOWANIE)"].append(f"Farba na sufit ({produkt_biala}): ~{math.ceil(litry_biala/10)} wiadra 10L")

                litry_kolor = math.ceil((pow_scian_total - (m2_laz*2)) * 0.2)
                koszt_materialow_detal += (litry_kolor * baza_kolory[produkt_kolor])
                zakupy["ŚCIANY (GŁADZIE I MALOWANIE)"].append(f"Farba na ściany ({produkt_kolor}): ~{math.ceil(litry_kolor/5)} wiadra 5L")

            # PODŁOGI I DRZWI
            if wylewka_samopoz:
                zakupy["PODŁOGI I DRZWI"].append(f"Wylewka samopoziomująca ({grubosc_wyl}mm): ~{worki_wylewki} worków (25kg)")
            if do_podl_fin:
                zakupy["PODŁOGI I DRZWI"].append(f"Podłoga ({typ_p}) + podkłady: {math.ceil(m2_total * 1.1)} m2")
            if do_drzwi:
                zakupy["PODŁOGI I DRZWI"].append(f"Drzwi wewnętrzne ({typ_d_wew}): {szt_d_wew} kpl.")
            if wymiana_wej:
                zakupy["PODŁOGI I DRZWI"].append(f"Drzwi wejściowe ({typ_d_wej}): 1 kpl.")

            # MEBLE
            if kuchnia_inv > 0: zakupy["ZABUDOWY MEBLOWE"].append(f"Kuchnia na wymiar (Budżet: {kuchnia_inv} PLN)")
            if szafy_inv > 0: zakupy["ZABUDOWY MEBLOWE"].append(f"Szafy/Wnęki (Budżet: {szafy_inv} PLN)")
            if laz_stolarz > 0: zakupy["ZABUDOWY MEBLOWE"].append(f"Zabudowy Łazienkowe (Budżet: {laz_stolarz} PLN)")

            # --- C. POZOSTAŁE KOSZTY (SZACUNKOWE) ---
            wyposazenie_total = koszt_mebli_total + koszt_ele_total + koszt_podloze_total + koszt_drzwi_total + koszt_materialow_detal
            koszty_utrzymania_total = (czynsz_mc + media_mc) * czas_operacji
            koszt_transakcyjny = (cena_zakupu * 0.02) + 4500
            
            calkowity_koszt_projektu = cena_zakupu + koszt_transakcyjny + bazowy_remont_szacunek + wyposazenie_total + koszty_utrzymania_total
            zysk_brutto = cena_sprzedazy - calkowity_koszt_projektu
            roi = (zysk_brutto / calkowity_koszt_projektu) * 100 if calkowity_koszt_projektu > 0 else 0

            # --- WYŚWIETLANIE NA EKRANIE ---
            r1, r2, r3 = st.columns(3)
            r1.metric("Łączny koszt Inwestycji", f"{round(calkowity_koszt_projektu):,} zł".replace(",", " "))
            r2.metric("PRZEWIDYWANY ZYSK", f"{round(zysk_brutto):,} zł".replace(",", " "))
            r3.metric("ROI %", f"{round(roi, 1)} %")

            zakupy = {k: v for k, v in zakupy.items() if len(v) > 0} # Filtracja pustych

            # ==============================================================
            # ZAPIS DO BAZY I NOWOCZESNY GENERATOR PDF
            # ==============================================================
            st.markdown("---")
            st.subheader("💾 Zapisz Projekt i Pobierz PDF")
            col_save, col_pdf = st.columns(2)
            
            with col_save:
                if st.button("Zapisz w Chmurze ProCalc", use_container_width=True, type="primary", key="zapisz_kompleks_btn"):
                    u_id = st.session_state.get("user_id")
                    if not u_id:
                        st.error("Błąd: Brak ID. Zaloguj się poprawnie.")
                    elif supabase:
                        try:
                            dane_do_zapisu = {
                                "suma_calkowita": round(calkowity_koszt_projektu),
                                "zysk_brutto": round(zysk_brutto),
                                "roi_procent": round(roi, 1),
                                "lista_zakupow": zakupy 
                            }
                            supabase.table("projekty").insert({
                                "user_id": u_id, "nazwa_projektu": nazwa_inwestycji,
                                "branza": "Kompleksowy Flip", "dane_json": dane_do_zapisu
                            }).execute()
                            st.success("✅ Projekt zapisany w chmurze!")
                            st.rerun() 
                        except Exception as e:
                            st.error(f"Błąd bazy: {e}")

            with col_pdf:
                if st.button("Generuj Nowoczesny Kosztorys (PDF)", use_container_width=True, key="pobierz_pdf_kompleks_btn"):
                    try:
                        from fpdf import FPDF
                        
                        def czysc_tekst(tekst):
                            pl_znaki = {'ą':'a','ć':'c','ę':'e','ł':'l','ń':'n','ó':'o','ś':'s','ź':'z','ż':'z','Ą':'A','Ć':'C','Ę':'E','Ł':'L','Ń':'N','Ó':'O','Ś':'S','Ź':'Z','Ż':'Z'}
                            for pl, ang in pl_znaki.items(): tekst = tekst.replace(pl, ang)
                            return tekst
                        
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.add_font('Inter', '', 'Inter-Regular.ttf', uni=True) 
                        
                        # --- DESIGN: CIEMNY BANER GÓRNY ---
                        pdf.set_fill_color(14, 23, 43) # Kolor granatowy z motywu ProCalc
                        pdf.rect(0, 0, 210, 25, 'F')
                        pdf.set_y(8)
                        pdf.set_font("Inter", "", 16)
                        pdf.set_text_color(255, 255, 255)
                        pdf.cell(190, 10, txt=czysc_tekst("PROCALC - KOSZTORYS INWESTORSKI"), ln=True, align='C')
                        
                        # --- NAZWA PROJEKTU ---
                        pdf.set_y(35)
                        pdf.set_text_color(0, 211, 149) # Kolor zielony ProCalc
                        pdf.set_font("Inter", "", 20)
                        pdf.cell(190, 10, txt=czysc_tekst(nazwa_inwestycji.upper()), ln=True, align='C')
                        pdf.ln(5)
                        
                        # --- DESIGN: RAMKA PODSUMOWANIA FINANSOWEGO ---
                        pdf.set_fill_color(248, 249, 250) # Jasnoszary
                        pdf.set_draw_color(0, 211, 149) # Zielona ramka
                        pdf.set_line_width(0.6)
                        pdf.rect(10, pdf.get_y(), 190, 35, 'DF')
                        
                        pdf.set_y(pdf.get_y() + 5)
                        pdf.set_text_color(50, 50, 50)
                        pdf.set_font("Inter", "", 12)
                        pdf.cell(190, 7, txt=czysc_tekst(f"Laczny koszt inwestycji: {round(calkowity_koszt_projektu):,} PLN".replace(",", " ")), ln=True, align='C')
                        pdf.cell(190, 7, txt=czysc_tekst(f"Budzet wyposazenia i materialow: {round(wyposazenie_total):,} PLN".replace(",", " ")), ln=True, align='C')
                        
                        pdf.set_text_color(0, 160, 110) # Ciemniejszy zielony do zysku
                        pdf.set_font("Inter", "", 14)
                        pdf.cell(190, 8, txt=czysc_tekst(f"Szacowany zysk netto: {round(zysk_brutto):,} PLN (ROI: {round(roi,1)}%)".replace(",", " ")), ln=True, align='C')
                        pdf.ln(15)
                        
                        # --- LISTA ZAKUPOWA ---
                        pdf.set_text_color(14, 23, 43)
                        pdf.set_font("Inter", "", 14)
                        pdf.cell(190, 10, txt=czysc_tekst("SZCZEGOLOWA LISTA ZAKUPOWA"), ln=True, border='B')
                        pdf.ln(5)
                        
                        for cat, items in zakupy.items():
                            # Nagłówek Kategorii (Zielone Tło)
                            pdf.set_fill_color(0, 211, 149)
                            pdf.set_text_color(255, 255, 255)
                            pdf.set_font("Inter", "", 11)
                            pdf.cell(190, 8, txt=czysc_tekst(f"  {cat}"), ln=True, fill=True)
                            
                            # Pozycje (Ciemnoszary Tekst)
                            pdf.set_text_color(70, 70, 70)
                            pdf.set_font("Inter", "", 10)
                            pdf.ln(2)
                            for item in items:
                                pdf.cell(5, 6, txt="", ln=0) # Wcięcie
                                pdf.cell(185, 6, txt=czysc_tekst(f"• {item}"), ln=True)
                            pdf.ln(4)
                            
                        # --- GENEROWANIE I POBIERANIE ---
                        pdf_output = pdf.output()
                        if isinstance(pdf_output, (bytearray, bytes)):
                            pdf_bytes = bytes(pdf_output)
                        elif isinstance(pdf_output, str):
                            pdf_bytes = pdf_output.encode('latin-1', 'replace')
                        else:
                            pdf_bytes = pdf_output

                        st.download_button(
                            label="📥 Pobierz Nowoczesny Kosztorys PDF",
                            data=pdf_bytes,
                            file_name=f"Kosztorys_ProCalc_{nazwa_inwestycji.replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            key="btn_native_pdf_download"
                        )
                        st.success("✅ Wygenerowano! Kliknij przycisk wyżej.")
                        
                    except Exception as e:
                        st.error(f"Błąd generowania PDF: {e}")
                    
# ==========================================
# MODUŁ: HARMONOGRAM (GANTT LIVE)
# ==========================================
elif branza == "Harmonogram":
    st.header("Harmonogram Prac Live PRO ")
    st.write("Zarządzaj terminami i pokazuj postęp inwestorowi w czasie rzeczywistym.")

    col_h1, col_h2 = st.columns([1, 2])

    with col_h1:
        st.subheader("Edycja Etapów")
        suma_dni = 0
        suma_postepu = 0
        
        for i, etap in enumerate(st.session_state.etapy_projektu):
            with st.expander(f"{etap['Zadanie']}"):
                etap['Dni'] = st.number_input(f"Dni trwania:", 1, 60, etap['Dni'], key=f"dni_{i}")
                etap['Postęp'] = st.slider(f"Postęp (%):", 0, 100, etap['Postęp'], key=f"pos_{i}")
            
            suma_dni += etap['Dni']
            suma_postepu += (etap['Postęp'] / 100) * etap['Dni']

        calkowity_progres = (suma_postepu / suma_dni) * 100 if suma_dni > 0 else 0

    with col_h2:
        st.subheader("Wizualizacja Projektu")
        st.metric("Całkowity czas remontu", f"{suma_dni} dni roboczych")
        st.progress(calkowity_progres / 100)
        st.write(f"Ogólny postęp inwestycji: **{round(calkowity_progres, 1)}%**")

        st.markdown("<br>", unsafe_allow_html=True)
        for etap in st.session_state.etapy_projektu:
            szerokosc = (etap['Dni'] / suma_dni) * 100
            progres_szerokosc = etap['Postęp']
            
            st.markdown(f"""
                <div style="margin-bottom: 10px;">
                    <div style="font-size: 12px; font-weight: bold;">{etap['Zadanie']} ({etap['Dni']} dni)</div>
                    <div style="background-color: #E9ECEF; border-radius: 5px; width: 100%; height: 20px;">
                        <div style="background-color: #00D395; height: 20px; border-radius: 5px; width: {progres_szerokosc}%; text-align: center; color: white; font-size: 10px; line-height: 20px;">
                            {etap['Postęp']}%
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    st.info("💡 **WSKAZÓWKA:** Docelowo w Panelu Inwestora ten widok będzie zamrożony, aby klient mógł tylko śledzić postępy, które Ty tu ustawisz.")

import base64

# Funkcja generująca link do PDF w formacie Base64
def create_pdf_link(file_path, link_name):
    try:
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        # Dodany atrybut download wymusza bezpieczne zapisanie pliku
        return f'<a href="data:application/pdf;base64,{base64_pdf}" download="{file_path}" style="text-decoration:none; color:#6C757D;">{link_name}</a>'
    except Exception:
        return f'<span style="color:#e74c3c;">{link_name} (Brak pliku)</span>'
        
# Przygotowanie linków
link_reg = create_pdf_link("Regulamin_ProCalc_v1.pdf", "Regulamin serwisu")
link_rodo = create_pdf_link("Polityka_Prywatnosci_ProCalc_v2.pdf", "Polityka prywatności (RODO)")

# ==========================================
# ROZSZERZONY FOOTER (Z PRZYCISKAMI)
# ==========================================
st.markdown(
    """
<hr style="margin-top: 50px; border-color: #E9ECEF;">
<div style="padding: 20px 0; text-align: center; color: #6C757D; font-size: 13px; line-height: 1.6;">
<div style="display: flex; justify-content: space-around; flex-wrap: wrap; max-width: 1200px; margin: 0 auto; text-align: left;">
        
<div style="min-width: 250px; margin-bottom: 20px; text-align: center;">
<strong style="color: #1E1E1E; font-size: 18px; color: #00D395;">ProCalc</strong><br>
Twój Cyfrowy Kosztorysant<br>
<br>
© 2026 Wszelkie prawa zastrzeżone.
</div>
        
<div style="min-width: 250px; margin-bottom: 20px; text-align: center;">
<strong style="color: #1E1E1E; font-size: 14px; text-transform: uppercase;">Dane firmy</strong><br>
[NAZWA TWOJEJ FIRMY]<br>
NIP: [WPISZ_NIP] | REGON: [WPISZ_REGON]<br>
[ULICA I NUMER]<br>
[KOD POCZTOWY I MIASTO]
</div>
        
<div style="min-width: 250px; margin-bottom: 20px; text-align: center;">
<strong style="color: #1E1E1E; font-size: 14px; text-transform: uppercase;">Kontakt & Pomoc</strong><br><br>
<a href="https://chat.whatsapp.com/TWOJ_LINK" target="_blank" style="text-decoration: none;">
<div style="background-color: #25D366; color: white; padding: 10px 15px; border-radius: 8px; font-weight: bold; margin-bottom: 10px; display: inline-block; width: 80%; box-shadow: 0 4px 6px rgba(37, 211, 102, 0.2);">🧪 Grupa dla Testerów (WA)</div>
</a><br>
<a href="https://wa.me/48123456789" target="_blank" style="text-decoration: none;">
<div style="background-color: #0E172B; color: white; padding: 10px 15px; border-radius: 8px; font-weight: bold; margin-bottom: 15px; display: inline-block; width: 80%; box-shadow: 0 4px 6px rgba(14, 23, 43, 0.2);">🤖 Support / Chat AI</div>
</a><br>
<a href="#" style="color: #00D395; text-decoration: none; font-weight: 600;">Polityka Prywatności</a> | 
<a href="#" style="color: #00D395; text-decoration: none; font-weight: 600;">Regulamin</a>
</div>
</div>
</div>
    """,
    unsafe_allow_html=True
)


