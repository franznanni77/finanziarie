"""
Applicazione Streamlit per l'analisi intelligente delle opzioni di finanziamento.
Include gestione degli errori migliorata e formattazione robusta della risposta AI.
"""

import streamlit as st
import pandas as pd
from anthropic import Anthropic
from typing import List, Dict, Any, Optional

class FinanziariaData:
    """Gestisce i dati delle finanziarie e le loro commissioni."""
    
    def __init__(self):
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
        return self.df[self.df['Mesi'] == rate].iloc[0]

class FinanceCalculator:
    """Calcola le opzioni di finanziamento disponibili."""
    
    @staticmethod
    def calcola_opzioni(importo: float, rate: int, commissioni: pd.Series) -> List[Dict[str, Any]]:
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
    """Gestisce l'analisi AI delle opzioni di finanziamento."""
    
    def __init__(self):
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

    def _genera_prompt(self, importo: float, rate: int, risultati: List[Dict[str, Any]]) -> str:
        return """Analizza le seguenti opzioni di finanziamento:
        
Dettagli:
- Importo: €{importo:.2f}
- Rate: {rate}

Opzioni disponibili:
{pd.DataFrame(risultati).to_string()}

Fornisci un'analisi strutturata usando questa formattazione:

ANALISI COMPARATIVA DELLE FINANZIARIE

[Analisi dettagliata di ogni opzione, dalla più conveniente alla meno conveniente]

VALUTAZIONE ECONOMICA

[Analisi dei costi e benefici]

RACCOMANDAZIONE FINALE

[Suggerimento chiaro sulla scelta migliore]

CONSIGLI PRATICI

[3-4 suggerimenti per l'implementazione]"""

    def analizza_opzioni(self, importo: float, rate: int, risultati: List[Dict[str, Any]]) -> Optional[str]:
        try:
            prompt = self._genera_prompt(importo, rate, risultati)
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            
            if not response or not response.content:
                raise ValueError("Risposta AI non valida")
                
            return response.content
            
        except Exception as e:
            st.error(f"Errore nell'analisi AI: {str(e)}")
            return None

class StreamlitUI:
    """Gestisce l'interfaccia utente dell'applicazione."""
    
    def __init__(self):
        self.findata = FinanziariaData()
        self.calculator = FinanceCalculator()
        self.analyzer = AIAnalyzer()

    def render_header(self):
        st.title("Analizzatore Intelligente di Finanziamenti")
        st.markdown("""
        Analizza le opzioni di finanziamento disponibili e ricevi raccomandazioni 
        personalizzate basate su analisi AI.
        """)

    def render_inputs(self) -> tuple:
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
        st.header("Riepilogo Opzioni")
        
        st.info(f"""
        💰 Dettagli Finanziamento:
        - Importo richiesto: €{importo:.2f}
        - Rate mensili: {rate}
        - Rata cliente: €{risultati[0]['rata_mensile']:.2f}
        """)
        
        for i, opzione in enumerate(risultati, 1):
            container = st.success if i == 1 else st.warning if i == 2 else st.error
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            
            container(f"""
            {emoji} {opzione['finanziaria']}
            - Commissione: {opzione['commissione_percentuale']:.2f}%
            - Costo commissione: €{opzione['costo_commissione']:.2f}
            - Importo netto: €{opzione['importo_netto']:.2f}
            """)

    def format_ai_response(self, text: str) -> str:
        """Formatta la risposta AI per una migliore leggibilità."""
        if not text:
            return ""
        
        # Rimuove spazi extra e formatta le sezioni
        sections = []
        current_section = []
        
        for line in text.split('\n'):
            line = line.strip()
            if line.isupper() and len(line) > 10:  # Probabilmente un titolo di sezione
                if current_section:
                    sections.append('\n'.join(current_section))
                current_section = [f"## {line}"]
            elif line:
                current_section.append(line)
                
        if current_section:
            sections.append('\n'.join(current_section))
            
        return '\n\n'.join(sections)

    def render_ai_analysis(self, analysis: Optional[str]):
        """Visualizza l'analisi AI con gestione degli errori migliorata."""
        if not analysis:
            st.error("Non è stato possibile generare l'analisi AI. Riprova più tardi.")
            return
        
        st.header("Analisi Dettagliata AI")
        
        # Formatta e visualizza l'analisi
        formatted_analysis = self.format_ai_response(analysis)
        sections = formatted_analysis.split('##')
        
        for section in sections:
            if not section.strip():
                continue
            
            lines = section.strip().split('\n')
            title = lines[0].strip()
            content = '\n'.join(lines[1:]).strip()
            
            if title and content:
                st.subheader(title)
                st.write(content)
                st.markdown("---")

    def run(self):
        """Esegue l'applicazione con gestione degli errori migliorata."""
        try:
            self.render_header()
            importo, rate = self.render_inputs()
            
            if st.button("Analizza Opzioni"):
                with st.spinner("Elaborazione in corso..."):
                    commissioni = self.findata.get_commissioni(rate)
                    risultati = self.calculator.calcola_opzioni(importo, rate, commissioni)
                    
                    self.render_results(importo, rate, risultati)
                    
                    analysis = self.analyzer.analizza_opzioni(importo, rate, risultati)
                    self.render_ai_analysis(analysis)
                    
        except Exception as e:
            st.error(f"Si è verificato un errore: {str(e)}")

if __name__ == "__main__":
    st.set_page_config(
        page_title="Analizzatore Finanziamenti",
        page_icon="💰",
        layout="wide"
    )
    
    app = StreamlitUI()
    app.run()