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

Sei un consulente finanziario esperto con 20 anni di esperienza nel settore del credito al consumo. 
Fornisci un'analisi approfondita delle opzioni di finanziamento disponibili.

La tua risposta dovrebbe seguire questa struttura:

## Analisi Comparativa delle Finanziarie

[Per ogni finanziaria, iniziando dalla più conveniente:]
[Nome Finanziaria] offre una commissione del [X]%, risultando [posizionamento]. Questa soluzione si distingue per [punti di forza principali]. Il costo effettivo per l'azienda sarebbe di €[importo], con un risparmio/costo aggiuntivo di €[differenza] rispetto alla media.

## Valutazione Economica

[Analisi dettagliata dei costi e benefici finanziari]

## Considerazioni Operative

[Analisi dei processi, tempi e procedure di ciascuna opzione]

## Raccomandazione Finale

[Suggerimento chiaro e motivato sulla scelta ottimale]

## Consigli Pratici per l'Implementazione

[3-4 suggerimenti concreti per ottimizzare la gestione del finanziamento]

Usa un linguaggio chiaro e professionale, fornendo numeri precisi e confronti diretti tra le opzioni.
Evidenzia sempre i vantaggi competitivi e le potenziali criticità di ogni soluzione.
Concludi con una raccomandazione pratica e attuabile."""
        return prompt

    def analyze_options(self, importo, rate, risultati):
        """Analizza le opzioni di finanziamento usando Anthropic API."""
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

def display_formatted_analysis(analysis):
    """Formatta e visualizza l'analisi in modo strutturato."""
    if not analysis:
        return

    sections = analysis.split('##')
    for section in sections:
        if not section.strip():
            continue
            
        # Estrai il titolo e il contenuto
        lines = section.strip().split('\n')
        title = lines[0].strip()
        content = '\n'.join(lines[1:]).strip()
        
        # Visualizza la sezione formattata
        st.subheader(title)
        
        # Aggiungi spaziatura e formattazione appropriata
        paragraphs = content.split('\n\n')
        for paragraph in paragraphs:
            if paragraph.strip():
                st.write(paragraph.strip())
        
        # Aggiungi un separatore tra le sezioni
        st.markdown("---")

[... resto del codice precedente fino al punto dell'analisi AI ...]

    # Analisi AI
    st.header("Analisi Dettagliata")
    analyzer = FinanceAnalyzer()
    
    with st.spinner("Analisi in corso..."):
        analysis = analyzer.analyze_options(importo, rate, opzioni)
        if analysis:
            display_formatted_analysis(analysis)