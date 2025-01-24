"""
Applicazione Streamlit per l'analisi intelligente delle opzioni di finanziamento.
Include gestione migliorata della risposta AI e formattazione robusta.
"""

import streamlit as st
import pandas as pd
from anthropic import Anthropic
from typing import List, Dict, Any, Optional

# [Le classi FinanziariaData e FinanceCalculator rimangono invariate]

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
        df_risultati = pd.DataFrame(risultati)
        return f"""Analizza queste opzioni di finanziamento in modo strutturato e dettagliato:

DETTAGLI FINANZIAMENTO:
- Importo: €{importo:.2f}
- Numero rate: {rate}

OPZIONI DISPONIBILI:
{df_risultati.to_string()}

Fornisci un'analisi strutturata seguendo esattamente questo schema:

SEZIONE 1: ANALISI COMPARATIVA
[Analizza ogni finanziaria, dalla più conveniente alla meno conveniente]

SEZIONE 2: VALUTAZIONE ECONOMICA
[Analizza costi e benefici di ogni opzione]

SEZIONE 3: RACCOMANDAZIONE FINALE
[Fornisci un consiglio chiaro sulla scelta migliore]

SEZIONE 4: SUGGERIMENTI PRATICI
[Elenca 3-4 consigli concreti per l'implementazione]

Usa un linguaggio chiaro e professionale, mantenendo questa struttura precisa."""

    def analizza_opzioni(self, importo: float, rate: int, risultati: List[Dict[str, Any]]) -> Optional[str]:
        try:
            prompt = self._genera_prompt(importo, rate, risultati)
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Estraiamo il contenuto della risposta e verifichiamo che sia una stringa
            content = response.content
            if not isinstance(content, str):
                # Se la risposta non è una stringa, convertiamola
                if hasattr(content, 'text'):
                    content = content.text
                else:
                    content = str(content)
            
            return content
            
        except Exception as e:
            st.error(f"Errore nell'analisi AI: {str(e)}")
            return None

class StreamlitUI:
    """Gestisce l'interfaccia utente dell'applicazione."""
    
    def __init__(self):
        self.findata = FinanziariaData()
        self.calculator = FinanceCalculator()
        self.analyzer = AIAnalyzer()

    # [I metodi render_header e render_inputs rimangono invariati]

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

    def process_ai_response(self, text: Optional[str]) -> List[Dict[str, str]]:
        """
        Processa la risposta AI e la converte in una struttura dati gestibile.
        
        Args:
            text: Il testo della risposta AI
            
        Returns:
            Lista di dizionari contenenti titolo e contenuto di ogni sezione
        """
        if not text or not isinstance(text, str):
            return []
            
        sections = []
        current_title = ""
        current_content = []
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Identifica le sezioni principali (in maiuscolo)
            if line.isupper() and ("SEZIONE" in line or "ANALISI" in line or 
                                 "VALUTAZIONE" in line or "RACCOMANDAZIONE" in line or 
                                 "SUGGERIMENTI" in line):
                if current_title and current_content:
                    sections.append({
                        'title': current_title,
                        'content': '\n'.join(current_content)
                    })
                current_title = line
                current_content = []
            else:
                current_content.append(line)
        
        # Aggiungi l'ultima sezione
        if current_title and current_content:
            sections.append({
                'title': current_title,
                'content': '\n'.join(current_content)
            })
            
        return sections

    def render_ai_analysis(self, analysis: Optional[str]):
        """Visualizza l'analisi AI con gestione migliorata della formattazione."""
        if not analysis:
            st.error("Non è stato possibile generare l'analisi AI. Riprova più tardi.")
            return
        
        st.header("Analisi Dettagliata")
        
        # Processa e visualizza le sezioni
        sections = self.process_ai_response(analysis)
        
        if not sections:
            st.warning("L'analisi non contiene sezioni riconoscibili.")
            st.write(analysis)  # Mostra il testo grezzo come fallback
            return
            
        for section in sections:
            st.subheader(section['title'])
            st.write(section['content'])
            st.markdown("---")

    def run(self):
        """Esegue l'applicazione con gestione errori migliorata."""
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
            st.exception(e)  # Mostra il traceback completo in sviluppo

if __name__ == "__main__":
    st.set_page_config(
        page_title="Analizzatore Finanziamenti",
        page_icon="💰",
        layout="wide"
    )
    
    app = StreamlitUI()
    app.run()