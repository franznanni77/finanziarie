from anthropic import Anthropic
import streamlit as st
import pandas as pd

class FinanceAnalyzer:
    def __init__(self):
        """Inizializza l'analizzatore con il client Anthropic."""
        try:
            if "anthropic_api_key" not in st.secrets:
                raise ValueError("La chiave API Anthropic non è configurata nei secrets di Streamlit")
            
            self.client = Anthropic(api_key=st.secrets["anthropic_api_key"])
            self.model = "claude-3-5-sonnet-20241022"
            self.max_tokens = 1024
            self.temperature = 0.75
        except Exception as e:
            st.error(f"Errore nell'inizializzazione del client Anthropic: {str(e)}")
            raise

    def generate_prompt(self, importo, rate, risultati):
        """Genera il prompt per l'analisi delle opzioni di finanziamento."""
        prompt = f"""Analizza le seguenti opzioni di finanziamento per un importo di €{importo:.2f} da rateizzare in {rate} mesi:

Dati delle finanziarie:
{pd.DataFrame(risultati).to_string()}

Ricordati che stai lavorando come un consulente finanziario con 20 anni di esperienza nel settore del credito al consumo.
Per favore:

1. Analizza ogni opzione di finanziamento considerando:
   - L'impatto delle commissioni sul margine aziendale
   - La convenienza relativa tra le opzioni
   - Eventuali vantaggi operativi specifici di ogni finanziaria

2. Valuta i trade-off tra:
   - Costo immediato vs benefici a lungo termine
   - Facilità di gestione pratica
   - Rapporto con il cliente finale

3. Fornisci 3 raccomandazioni concrete basate su:
   - L'importo specifico richiesto
   - La durata del finanziamento
   - Il profilo di rischio dell'operazione

Concludi con un riassunto strategico di 2-3 paragrafi evidenziando:
- Non citare mai il tuo ruolo
- L'impatto della scelta sulla gestione finanziaria dell'azienda
- Le opportunità di ottimizzazione identificate
- I potenziali rischi da considerare

Considera il contesto del mercato italiano del credito al consumo nelle tue raccomandazioni.
Formatta la risposta in modo chiaro e strutturato."""
        return prompt

    def analyze_options(self, importo, rate, risultati):
        """
        Analizza le opzioni di finanziamento usando Anthropic API.
        
        Args:
            importo (float): Importo da finanziare
            rate (int): Numero di rate
            risultati (list): Lista dei risultati per ogni finanziaria
            
        Returns:
            str: Analisi dettagliata delle opzioni
        """
        try:
            prompt = self.generate_prompt(importo, rate, risultati)
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            return message.content
            
        except Exception as e:
            st.error(f"Errore nell'analisi delle opzioni: {str(e)}")
            return None

def calcola_opzioni_finanziamento(importo, rate, df):
    """Calcola le opzioni di finanziamento disponibili."""
    commissioni = df[df['Mesi'] == rate].iloc[0]
    
    risultati = []
    for finanziaria in ['Sella Appago', 'Cofidis PagoDIL', 'Compass HeyLight']:
        if commissioni[finanziaria] == 0:
            continue
            
        commissione = commissioni[finanziaria] / 100
        costo_commissione = importo * commissione
        importo_netto = importo - costo_commissione
        
        risultati.append({
            'finanziaria': finanziaria,
            'commissione_percentuale': commissioni[finanziaria],
            'costo_commissione': costo_commissione,
            'importo_netto': importo_netto
        })
    
    return sorted(risultati, key=lambda x: x['importo_netto'], reverse=True)

# Configurazione della pagina Streamlit
st.title('Analizzatore Intelligente Finanziamenti')

# Caricamento dati commissioni
data = {
    'Mesi': range(1, 25),
    'Sella Appago': [0, 2.30, 2.30, 4.75, 5.05, 5.35, 5.75, 6.05, 6.45, 6.85, 7.15, 
                     7.35, 7.35, 7.60, 7.85, 8.26, 8.53, 8.95, 9.38, 9.82, 10.27, 
                     10.70, 11.14, 11.54],
    'Cofidis PagoDIL': [0, 0, 5.10, 5.50, 5.90, 6.10, 6.30, 6.40, 6.50, 6.60, 6.70,
                        6.80, 6.95, 7.10, 7.25, 7.40, 7.55, 7.70, 7.85, 8.00, 8.15,
                        8.30, 8.45, 8.60],
    'Compass HeyLight': [4.63, 5.00, 5.36, 5.72, 6.08, 6.32, 6.56, 6.80, 7.15, 7.39,
                        7.62, 7.85, 8.09, 8.32, 8.55, 8.78, 9.01, 9.24, 9.59, 9.81,
                        10.04, 10.27, 10.49, 10.72]
}
df = pd.DataFrame(data)

# Input utente
col1, col2 = st.columns(2)
with col1:
    importo = st.number_input('Inserisci l\'importo da finanziare (€)', min_value=1.0, value=1000.0)
with col2:
    rate = st.number_input('Inserisci il numero di rate', min_value=1, max_value=24, value=12)

if st.button('Analizza Opzioni'):
    # Calcola opzioni
    opzioni = calcola_opzioni_finanziamento(importo, rate, df)
    
    # Mostra risultati base
    st.header('Riepilogo Opzioni')
    rata_mensile = importo / rate
    
    st.info(f"""
    📊 Dettagli del finanziamento:
    - Importo totale: €{importo:.2f}
    - Rata mensile cliente: €{rata_mensile:.2f}
    - Numero rate: {rate}
    """)
    
    # Mostra opzioni ordinate
    for i, opzione in enumerate(opzioni, 1):
        container = st.success if i == 1 else st.warning if i == 2 else st.error
        container(f"""
        💰 Opzione {i}: {opzione['finanziaria']}
        - Commissione: {opzione['commissione_percentuale']:.2f}%
        - Costo commissione: €{opzione['costo_commissione']:.2f}
        - Importo netto: €{opzione['importo_netto']:.2f}
        """)
    
    # Analisi AI
    st.header("Analisi Dettagliata AI")
    analyzer = FinanceAnalyzer()
    
    with st.spinner("Analisi in corso..."):
        analysis = analyzer.analyze_options(importo, rate, opzioni)
        if analysis:
            st.markdown(analysis)