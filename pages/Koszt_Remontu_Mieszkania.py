import streamlit as st

# ==========================================
# 1. KONFIGURACJA STRONY (SEO)
# ==========================================
st.set_page_config(
    page_title="Ile kosztuje remont mieszkania w 2026? Cennik i Kalkulator | ProCalc",
    page_description="Sprawdź aktualne ceny remontów mieszkań w 2026 roku. Oblicz koszt robocizny i materiałów za m2 dla standardu ekonomicznego i premium.",
    layout="centered"
)

# =========================================
# 2. ARTYKUŁ SEO
# =========================================
st.title("Ile kosztuje remont mieszkania w 2026 roku?")

st.markdown("""
Planujesz generalny remont mieszkania z rynku wtórnego lub wykończenie stanu deweloperskiego? W 2026 roku koszty usług budowlanych i materiałów wykończeniowych wymagają solidnego zaplanowania budżetu. 

Średni koszt wykończenia mieszkania pod klucz (robocizna + materiały) waha się obecnie w granicach:
""")

col1, col2, col3 = st.columns(3)
col1.metric("Standard Ekonomiczny", "od 2 200 zł / m²")
col2.metric("Standard Średni", "od 3 500 zł / m²")
col3.metric("Premium / Wysoki", "od 5 000+ zł / m²")

st.divider()

st.subheader("Co pochłania największą część budżetu?")
st.markdown("""
Generalny remont to nie tylko malowanie i panele. Najdroższe etapy, które decydują o ostatecznej cenie, to:
*  **Łazienka:** To zdecydowanie najdroższe pomieszczenie (często 20 000 - 40 000 zł za samo pomieszczenie).
*  **Kuchnia i zabudowa stolarska:** Meble na wymiar i sprzęt AGD potrafią podwoić koszty.
*  **Instalacje:** Wymiana starej elektryki (miedź) i hydrauliki w wielkiej płycie to ogromne koszty ukryte.
*  **Prace przygotowawcze:** Zrywanie starych płytek, kucie, równanie ścian i wylewki.
""")

c_left, c_right = st.columns(2)

with c_left:
    st.success("""
    **Przykładowy budżet (Mieszkanie 50 m², stan deweloperski, standard średni):**
    *  Robocizna wykończeniowa: ~ 45 000 zł
    *  Materiały budowlane (kleje, gładzie): ~ 20 000 zł
    *  Materiały wykończeniowe (płytki, podłogi, drzwi): ~ 40 000 zł
    *  Kuchnia i łazienka (wyposażenie): ~ 45 000 zł
    * **👉 Razem: ok. 150 000 zł**
    """)

with c_right:
    st.warning("""
    **3 największe błędy inwestorów:**
    * ❌ **Brak poduszki finansowej:** Zawsze doliczaj 10-15% budżetu na niespodziewane wydatki (krzywe ściany, awarie).
    * ❌ **Pozorne oszczędności:** Tania farba kryje na 3 razy (płacisz więcej za robociznę). Tanie panele szybko się ścierają.
    * ❌ **Liczenie "na oko":** Bez dokładnego przedmiaru ilości płytek, kleju i profili przepłacisz za nadmiar materiału lub koszty transportu.
    """)

st.divider()

# ==========================================
# 3. WEZWANIE DO AKCJI & SZYBKI KALKULATOR
# ==========================================
st.subheader("Oszacuj koszt swojego remontu")
st.write("Wpisz metraż swojego mieszkania, aby poznać orientacyjny budżet potrzebny na remont w 2026 roku.")

with st.container(border=True):
    c_calc1, c_calc2 = st.columns(2)
    m2_mieszkania = c_calc1.number_input("Powierzchnia mieszkania [m²]:", min_value=15, value=50, step=5)
    zakres_prac = c_calc2.selectbox("Zakres prac:", [
        "Stan deweloperski (wykończenie od zera)", 
        "Generalny remont (rynek wtórny, z kuciem i instalacjami)",
        "Tylko odświeżenie (malowanie, podłogi, bez kucia łazienki)"
    ])
    
    standard = st.radio("Standard wykończenia:", ["Ekonomiczny (markety budowlane)", "Średni (dobre marki, panele winylowe)", "Premium (drewno, spiek, meble na wymiar)"])
    
    # Logika szacowania
    cena_za_m2 = 0
    if "odświeżenie" in zakres_prac:
        cena_za_m2 = 800 if "Ekonomiczny" in standard else (1500 if "Średni" in standard else 2500)
    elif "deweloperski" in zakres_prac:
        cena_za_m2 = 2200 if "Ekonomiczny" in standard else (3500 if "Średni" in standard else 5000)
    else: # Generalny wtórny (najdroższy bo demontaże)
        cena_za_m2 = 2800 if "Ekonomiczny" in standard else (4200 if "Średni" in standard else 6000)
        
    koszt_szacunkowy = m2_mieszkania * cena_za_m2
    
    st.markdown("---")
    st.subheader("Szacunkowy całkowity budżet (Materiały + Robocizna):")
    st.metric("", f"~ {koszt_szacunkowy:,.0f} zł".replace(",", " "))
    st.caption("Powyższa kwota jest szacunkiem uśrednionym. Dokładny kosztorys zależy od projektu.")

# ==========================================
# 4. UPSELL DO APLIKACJI PRO
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)
st.info("###  Potrzebujesz dokładnego kosztorysu dla banku lub wykonawcy?")
st.write("""
Zamiast zgadywać, wyceń swój remont etap po etapie. W profesjonalnej aplikacji ProCalc:
*  **Dodasz konkretne wymiary** ścian, podłóg i sufitów.
*  **Wygenerujesz listę zakupów** z dokładnością do jednego worka kleju czy wkrętu.
*  **Pobierzesz gotowy PDF** z wyceną robocizny i materiałów.
""")

if st.button("🚀 Przejdź do profesjonalnego Kalkulatora ProCalc", type="primary", use_container_width=True):
    st.switch_page("kalkulator.py")
