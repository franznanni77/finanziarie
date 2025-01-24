"""
Applicazione Streamlit per l'analisi intelligente delle opzioni di finanziamento.
Integra dati finanziari con analisi AI di Anthropic Claude per fornire 
raccomandazioni personalizzate sulle scelte di finanziamento.
"""

import streamlit as st
import pandas as pd
from anthropic import Anthropic
from typing import List, Dict, Any

class FinanziariaData:
    """
    Classe per la gestione dei dati delle finanziarie e delle loro commissioni.
    Contiene i dati di base e i metodi per manipolarli.
    """
    
    def __init__(self):
        """Inizializza i dati delle commissioni per tutte le finanziarie."""
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
        """Recupera le commissioni per un determinato numero di rate."""
        return self.df[self.df['Mesi'] == rate].iloc[0]

class FinanceCalculator:
    """
    Classe per i calcoli finanziari relativi alle diverse opzioni di finanziamento.
    Gestisce il calcolo delle rate, commissioni e importi netti.
    """
    
    @staticmethod
    def calcola_opzioni(importo: float, rate: int, commissioni: pd.Series) -> List[Dict[str, Any]]:
        """
        Calcola le opzioni di finanziamento disponibili per tutte le finanziarie.
        Ordina i risultati per convenienza (importo netto decrescente).
        """
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
        
        return sorted(risultati, key=lambda x: x['importo_netto'], reverse=True)

class AIAnalyzer:
    """
    Classe per l'analisi intelligente delle opzioni di finanziamento usando Anthropic Claude.
    Gestisce la generazione del prompt e l'interazione con l'API.
    """
    
    def __init__(self):
        """Inizializza il client Anthropic con le configurazioni necessarie."""
        if "anthropic_api_key" not in st.secrets:
            raise ValueError("Chiave API Anthropic mancante nei secrets")
        
        self.client = Anthropic(api_key=st.secrets["anthropic_api_key"])
        self.model = "claude-3-5-sonnet-20241022"
        self.max_tokens = 1024
        self.temperature = 0.75

    def _genera_prompt(self, importo: float, rate: int, risultati: List[Dict[str, Any]]) -> str:
        """
        Genera il prompt strutturato per l'analisi delle opzioni.
        Include istruzioni dettagliate per ottenere un'analisi completa e ben formattata.
        """
        return f"""Analizza le seguenti opzioni di finanziamento:
Importo: €{importo:.2f}
Rate: {rate}

Dettagli delle opzioni:
{pd.DataFrame(risultati).to_string()}

Fornisci un'analisi strutturata seguendo questo formato:

# Confronto delle Opzioni

Analizza ogni finanziaria, evidenziando:
- Commissione e costo effettivo
- Punti di forza specifici
- Eventuali limitazioni

# Analisi Economica

- Differenze di costo tra le opzioni
- Impatto sul budget aziendale
- Considerazioni sulla liquidità

# Raccomandazione

Suggerisci l'opzione migliore considerando:
- Rapporto costo/beneficio
- Flessibilità operativa
- Gestione del rischio

Usa un linguaggio chiaro e diretto, evitando gergo tecnico non necessario."""

    def analizza_opzioni(self, importo: float, rate: int, risultati: List[Dict[str, Any]]) -> str:
        """Esegue l'analisi delle opzioni usando l'AI e restituisce il risultato formattato."""
        prompt = self._genera_prompt(importo, rate, risultati)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content
        except Exception as e:
            st.error(f"Errore nell'analisi AI: {str(e)}")
            return None

class StreamlitUI:
    """
    Classe per la gestione dell'interfaccia utente Streamlit.
    Coordina la presentazione dei dati e l'interazione con l'utente.
    """
    
    def __init__(self):
        """Inizializza i componenti necessari per l'UI."""
        self.findata = FinanziariaData()
        self.calculator = FinanceCalculator()
        self.analyzer = AIAnalyzer()

    def render_header(self):
        """Renderizza l'intestazione dell'applicazione."""
        st.title("Analizzatore Intelligente di Finanziamenti")
        st.markdown("""
        Questo strumento analizza le diverse opzioni di finanziamento disponibili
        e fornisce raccomandazioni personalizzate basate sui dati e sull'analisi AI.
        """)

    def render_inputs(self) -> tuple:
        """Renderizza e gestisce gli input dell'utente."""
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
        """Renderizza i risultati dell'analisi in modo strutturato e leggibile."""
        st.header("Riepilogo Opzioni")
        
        # Info base del finanziamento
        st.info(f"""
        💰 Dettagli Finanziamento
        - Importo richiesto: €{importo:.2f}
        - Rate mensili: {rate}
        - Rata cliente: €{risultati[0]['rata_mensile']:.2f}
        """)
        
        # Mostra le opzioni ordinate
        for i, opzione in enumerate(risultati, 1):
            if i == 1:
                container = st.success
                emoji = "🥇"
            elif i == 2:
                container = st.warning
                emoji = "🥈"
            else:
                container = st.error
                emoji = "🥉"
                
            container(f"""
            {emoji} {opzione['finanziaria']}
            - Commissione: {opzione['commissione_percentuale']:.2f}%
            - Costo commissione: €{opzione['costo_commissione']:.2f}
            - Importo netto: €{opzione['importo_netto']:.2f}
            """)

    def render_ai_analysis(self, analysis: str):
        """Renderizza l'analisi AI in modo strutturato e leggibile."""
        if not analysis:
            return
            
        st.header("Analisi Dettagliata AI")
        
        # Divide l'analisi in sezioni basate sui titoli '#'
        sections = analysis.split('#')
        for section in sections:
            if not section.strip():
                continue
                
            # Estrae e formatta il titolo e il contenuto
            lines = section.strip().split('\n')
            title = lines[0].strip()
            content = '\n'.join(lines[1:]).strip()
            
            # Visualizza la sezione formattata
            st.subheader(title)
            st.write(content)
            st.markdown("---")

    def run(self):
        """Esegue l'applicazione completa."""
        self.render_header()
        importo, rate = self.render_inputs()
        
        if st.button("Analizza Opzioni"):
            commissioni = self.findata.get_commissioni(rate)
            risultati = self.calculator.calcola_opzioni(importo, rate, commissioni)
            
            self.render_results(importo, rate, risultati)
            
            with st.spinner("Elaborazione analisi dettagliata..."):
                analysis = self.analyzer.analizza_opzioni(importo, rate, risultati)
                self.render_ai_analysis(analysis)

if __name__ == "__main__":
    app = StreamlitUI()
    app.run()