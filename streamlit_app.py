import streamlit as st
import pandas as pd
from anthropic import Anthropic
from typing import List, Dict, Any, Optional

class FinanziariaData:
    """Gestisce i dati delle commissioni per le diverse finanziarie."""
    
    def __init__(self):
        # Inizializza il dataset con le commissioni per ogni finanziaria
        self.data = {
            'Mesi': range(1, 25),
            'Sella Appago': [
                0, 2.30, 2.30, 4.75, 5.05, 5.35, 5.75, 6.05, 6.45, 6.85, 7.15,
                7.35, 7.35, 7.60, 7.85, 8.26, 8.53, 8.95, 9.38, 9.82, 10.27,
                10.70, 11.14, 11.54
            ],
            'Cofidis PagoDIL': [
                0, 0, 5.10, 5.50, 5.90, 6.10, 6.30, 6.40, 6.50, 6.60, 6.70,
                6.80, 6.95, 7.10, 7.25, 7.40, 7.55, 7.70, 7.85, 8.00, 8.15,
                8.30, 8.45, 8.60
            ],
            'Compass HeyLight': [
                4.63, 5.00, 5.36, 5.72, 6.08, 6.32, 6.56, 6.80, 7.15, 7.39,
                7.62, 7.85, 8.09, 8.32, 8.55, 8.78, 9.01, 9.24, 9.59, 9.81,
                10.04, 10.27, 10.49, 10.72
            ]
        }
        self.df = pd.DataFrame(self.data)

    def get_commissioni(self, rate: int) -> pd.Series:
        """Recupera le commissioni per un dato numero di rate."""
        return self.df[self.df['Mesi'] == rate].iloc[0]

class FinanceCalculator:
    """Calcola le opzioni di finanziamento disponibili."""
    
    @staticmethod
    def calcola_opzioni(importo: float, rate: int, commissioni: pd.Series) -> List[Dict[str, Any]]:
        """Calcola e ordina le opzioni di finanziamento per tutte le finanziarie."""
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
                'importo_netto': importo_netto,
                'rata_mensile': importo / rate
            })
        
        # Ordina per importo netto decrescente (più alto = migliore)
        return sorted(risultati, key=lambda x: x['importo_netto'], reverse=True)

class AIAnalyzer:
    """Gestisce l'analisi AI delle opzioni di finanziamento."""
    
    def __init__(self):
        """Inizializza il client Anthropic con le configurazioni necessarie."""
        try:
            if "anthropic_api_key" not in st.secrets:
                raise ValueError("Chiave API Anthropic mancante nei secrets")
            
            self.client = Anthropic(api_key=st.secrets["anthropic_api_key"])
            self.model = "claude-3-5-sonnet-20241022"
            self.max_tokens = 1024
            self.temperature = 0.75
        except Exception as e:
            st.error(f"Errore di inizializzazione: {str(e)}")
            raise

    def genera_analisi(self, importo: float, rate: int, risultati: List[Dict[str, Any]]) -> str:
        """Genera il testo del prompt per l'analisi."""
        df_risultati = pd.DataFrame(risultati)
        return f"""Sei un esperto consulente finanziario. Analizza queste opzioni di finanziamento:

DATI FINANZIAMENTO:
Importo: €{importo:.2f}
Rate: {rate}

OPZIONI:
{df_risultati.to_string()}

Fornisci un'analisi strutturata seguendo questo schema:

1. ANALISI COMPARATIVA
[Per ogni finanziaria, dalla più conveniente]

2. VALUTAZIONE ECONOMICA
[Analisi costi/benefici]

3. RACCOMANDAZIONE FINALE
[Consiglio motivato sulla scelta migliore]

4. CONSIGLI PRATICI
[3-4 suggerimenti per l'implementazione]"""

    def analizza_opzioni(self, importo: float, rate: int, risultati: List[Dict[str, Any]]) -> Optional[str]:
        """Esegue l'analisi delle opzioni usando l'AI."""
        try:
            # Genera e invia il prompt
            prompt = self.genera_analisi(importo, rate, risultati)
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Estrai il contenuto della risposta
            if hasattr(response.content, 'text'):
                return response.content.text
            return str(response.content)
            
        except Exception as e:
            st.error(f"Errore nell'analisi AI: {str(e)}")
            return None

class StreamlitUI:
    """Gestisce l'interfaccia utente dell'applicazione."""
    
    def __init__(self):
        """Inizializza i componenti dell'applicazione."""
        self.findata = FinanziariaData()
        self.calculator = FinanceCalculator()
        self.analyzer = AIAnalyzer()

    def render_header(self):
        """Visualizza l'intestazione dell'applicazione."""
        st.title("💰 Analizzatore Finanziamenti")
        st.markdown("""
        Questo strumento analizza le opzioni di finanziamento disponibili e fornisce
        raccomandazioni personalizzate basate su analisi AI.
        """)

    def render_inputs(self) -> tuple:
        """Gestisce gli input dell'utente."""
        col1, col2 = st.columns(2)
        with col1:
            importo = st.number_input(
                'Importo da finanziare (€)',
                min_value=1.0,
                value=1000.0,
                step=100.0
            )
        with col2:
            rate = st.number_input(
                'Numero di rate',
                min_value=1,
                max_value=24,
                value=12
            )
        return importo, rate

    def render_results(self, importo: float, rate: int, risultati: List[Dict[str, Any]]):
        """Visualizza i risultati dell'analisi."""
        st.header("Riepilogo Opzioni")
        
        # Mostra il riepilogo del finanziamento
        st.info(f"""
        💰 Dettagli Finanziamento:
        - Importo totale: €{importo:.2f}
        - Numero rate: {rate}
        - Rata mensile: €{risultati[0]['rata_mensile']:.2f}
        """)
        
        # Mostra le opzioni ordinate
        for i, opzione in enumerate(risultati, 1):
            container = st.success if i == 1 else st.warning if i == 2 else st.error
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            
            container(f"""
            {emoji} {opzione['finanziaria']}
            - Commissione: {opzione['commissione_percentuale']:.2f}%
            - Costo commissione: €{opzione['costo_commissione']:.2f}
            - Importo netto: €{opzione['importo_netto']:.2f}
            """)

    def render_ai_analysis(self, analysis: str):
        """Visualizza l'analisi AI in modo strutturato."""
        if not analysis:
            st.error("Non è stato possibile generare l'analisi AI. Riprova più tardi.")
            return

        st.header("Analisi Dettagliata")
        st.markdown(analysis)

    def run(self):
        """Esegue l'applicazione completa."""
        try:
            self.render_header()
            importo, rate = self.render_inputs()
            
            if st.button("Analizza Opzioni"):
                with st.spinner("Elaborazione in corso..."):
                    # Calcola le opzioni
                    commissioni = self.findata.get_commissioni(rate)
                    risultati = self.calculator.calcola_opzioni(importo, rate, commissioni)
                    
                    # Visualizza i risultati
                    self.render_results(importo, rate, risultati)
                    
                    # Genera e visualizza l'analisi AI
                    analysis = self.analyzer.analizza_opzioni(importo, rate, risultati)
                    self.render_ai_analysis(analysis)
                    
        except Exception as e:
            st.error(f"Si è verificato un errore: {str(e)}")

if __name__ == "__main__":
    # Configura la pagina Streamlit
    st.set_page_config(
        page_title="Analizzatore Finanziamenti",
        page_icon="💰",
        layout="wide"
    )
    
    # Avvia l'applicazione
    app = StreamlitUI()
    app.run()