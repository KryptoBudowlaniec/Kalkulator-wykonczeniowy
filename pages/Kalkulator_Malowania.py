import streamlit as st

# ==========================================
# 1. KONFIGURACJA STRONY (BARDZO WAŻNE DLA SEO!)
# ==========================================
st.set_page_config(
    page_title="Ile kosztuje malowanie ścian w 2026? | Kalkulator ProCalc",
    page_description="Oblicz dokładny koszt malowania ścian w 30 sekund. Aktualne ceny robocizny i materiałów na 2026 rok.",
    page_icon="🖌️",
    layout="centered"
)

# ==========================================
# 2. ARTYKUŁ SEO
# ==========================================
# Główny nagłówek H1
st.title("Ile kosztuje malowanie ścian w 2026?")

st.markdown("""
Koszt malowania ścian zależy od kilku rzeczy: stanu powierzchni, rodzaju farby oraz zakresu prac. 
W praktyce ceny w Polsce najczęściej mieszczą się w przedziale:
""")

# Wyciągamy ceny do ładnych "Metryk" (jak w podsumowaniu koszyka)
col1, col2 = st.columns(2)
col1.metric("Robocizna", "od 15 do 25 zł/m²")
col2.metric("Materiały", "+ farby, grunt, folie")

st.markdown("""
W przypadku nowych mieszkań (stan deweloperski) malowanie jest tańsze, bo ściany są równe. 
Przy remontach koszt rośnie, bo często dochodzi:
* poprawki gładzi
* szlifowanie
* gruntowanie
* zabezpieczenie pomieszczenia
""")

st.divider()

# Sekcja: Od czego zależy cena
st.subheader("Od czego zależy cena malowania?")
st.info("""
Na budowie wygląda to prosto – ale szczegóły robią różnicę:
* ✔️ **Stan ścian** – nowe vs stare (duża różnica w czasie pracy)
* ✔️ **Liczba warstw** – 1 czy 2 (a czasem 3 przy zmianie koloru)
* ✔️ **Rodzaj farby** – tania vs premium
* ✔️ **Zabezpieczenie pomieszczenia** – folie, taśmy
* ✔️ **Kolory** – białe vs ciemne (ciemne = więcej pracy)
""")

# Dwie kolumny na wycenę i błędy
c_left, c_right = st.columns(2)

with c_left:
    st.success("""
    **Przykładowa wycena (dla mieszkania ok. 50 m²)**
    * Robocizna: 2600 – 4300 zł
    * Materiały: 700 – 1800 zł
    * **Razem: 3400 – 6100 zł**
    
    *To oczywiście orientacyjne wartości – dokładna cena zależy od konkretnego przypadku.*
    """)

with c_right:
    st.warning("""
    **Najczęstsze błędy przy wycenie**
    Z doświadczenia (20 lat w branży) najczęściej ludzie:
    * ❌ nie doliczają gruntowania
    * ❌ zapominają o foliach i taśmach
    * ❌ zaniżają ilość farby
    * ❌ nie uwzględniają poprawek ścian
    
    **Efekt? Strata czasu albo pieniędzy.**
    """)

st.divider()

# ==========================================
# 3. WEZWANIE DO AKCJI (CALL TO ACTION)
# ==========================================
st.subheader("Sprawdź dokładną wycenę dla Twojego projektu")
st.markdown("""
Zamiast liczyć „na oko”, możesz sprawdzić dokładną ilość materiałów i koszt:
👉 **wpisz metraż, wybierz farbę i poziom trudności** 👉 **kalkulator policzy wszystko automatycznie** Skorzystaj z narzędzia poniżej i zobacz wycenę w 30 sekund. 👇
""")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 4. DARMOWY KALKULATOR (SZYBKA WYCENA)
# ==========================================
st.header(" Szybki Kalkulator Malowania")
st.write("Sprawdź orientacyjne koszty dla swojego metrażu.")

with st.container(border=True):
    # Proste suwaki dla darmowego użytkownika
    c_calc1, c_calc2 = st.columns(2)
    m2_scian = c_calc1.number_input("Powierzchnia do malowania [m²]:", min_value=10, value=50, step=5)
    stan_scian = c_calc2.selectbox("Stan ścian:", ["Dobre (tylko malowanie)", "Wymagają drobnych poprawek i gruntowania", "Zły stan (dużo szpachlowania)"])
    rodzaj_farby = st.radio("Klasa farby:", ["Standardowa (akrylowa/lateksowa)", "Premium (ceramiczna, plamoodporna)"])
    
    # Prosta logika szacowania (ukryta przed klientem)
    # Stawki robocizny (szacunkowe)
    stawka_robocizny = 25.0
    if "poprawek" in stan_scian: stawka_robocizny += 15.0
    elif "Zły" in stan_scian: stawka_robocizny += 30.0
    
    # Stawki materiału (szacunkowe)
    stawka_material = 8.0 if "Standardowa" in rodzaj_farby else 16.0
    if "poprawek" in stan_scian or "Zły" in stan_scian: stawka_material += 5.0 # doliczamy grunt/gips
    
    # Obliczenia
    koszt_rob = m2_scian * stawka_robocizny
    koszt_mat = m2_scian * stawka_material
    koszt_total = koszt_rob + koszt_mat
    
    st.markdown("---")
    st.subheader("Szacunkowy wynik:")
    
    res1, res2, res3 = st.columns(3)
    res1.metric("Robocizna", f"~ {koszt_rob:,.0f} zł".replace(",", " "))
    res2.metric("Materiały", f"~ {koszt_mat:,.0f} zł".replace(",", " "))
    res3.metric("Razem brutto", f"~ {koszt_total:,.0f} zł".replace(",", " "))
    
    st.caption("Powyższa wycena ma charakter wyłącznie orientacyjny oparty na średnich stawkach rynkowych.")

# ==========================================
# 5. UPSELL (ZACHĘTA DO WERSJI PRO)
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)
st.info("###  Chcesz wycenić projekt co do złotówki?")
st.write("""
W profesjonalnej wersji ProCalc otrzymasz:
*  **Dokładną listę zakupów** (ile wiader farby, rolek taśmy i litrów gruntu kupić).
*  **Możliwość edycji własnych stawek** robocizny i materiałów.
*  **Profesjonalny Kosztorys PDF** z Twoim logo, gotowy do wysłania klientowi.
""")

if st.button("🚀 Otwórz pełny kalkulator (Wersja PRO)", type="primary", use_container_width=True):
    # Zmień "kalkulator.py" na nazwę pliku, w którym masz główną aplikację
    st.switch_page("kalkulator.py")
