import streamlit as st
import pandas as pd
import numpy as np

# Creiamo il dataframe con i dati delle commissioni
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

def calcola_opzioni_finanziamento(importo, rate):
    """
    Calcola e ordina tutte le opzioni di finanziamento disponibili
    """
    # Ottieni le commissioni per il numero di rate selezionato
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
    
    # Ordina i risultati per importo netto decrescente (più alto = migliore)
    return sorted(risultati, key=lambda x: x['importo_netto'], reverse=True)

# Configurazione della pagina Streamlit
st.title('Calcolatore Finanziamenti')

# Input utente
col1, col2 = st.columns(2)
with col1:
    importo = st.number_input('Inserisci l\'importo da finanziare (€)', min_value=1.0, value=1000.0)
with col2:
    rate = st.number_input('Inserisci il numero di rate', min_value=1, max_value=24, value=12)

if st.button('Calcola'):
    # Calcola la rata mensile per il cliente (senza interessi)
    rata_mensile = importo / rate
    
    # Ottieni le opzioni ordinate
    opzioni_ordinate = calcola_opzioni_finanziamento(importo, rate)
    
    # Mostra i risultati
    st.header('Risultati')
    
    # Informazioni per il cliente
    st.info(f"""
    📊 Dettagli del finanziamento richiesto:
    - Importo totale: €{importo:.2f}
    - Rata mensile per il cliente: €{rata_mensile:.2f}
    - Numero rate: {rate}
    """)
    
    # Mostra le opzioni in ordine
    for i, opzione in enumerate(opzioni_ordinate, 1):
        if i == 1:
            container = st.success  # Verde per la migliore opzione
        elif i == len(opzioni_ordinate):
            container = st.error    # Rosso per la peggiore opzione
        else:
            container = st.warning  # Giallo per le opzioni intermedie
            
        container(f"""
        💰 Opzione {i}: {opzione['finanziaria']}
        - Commissione: {opzione['commissione_percentuale']:.2f}%
        - Costo commissione: €{opzione['costo_commissione']:.2f}
        - Importo netto per l'azienda: €{opzione['importo_netto']:.2f}
        """)
    
    # Mostra tabella comparativa dettagliata
    st.subheader('Tabella comparativa dettagliata')
    df_confronto = pd.DataFrame(opzioni_ordinate)
    df_confronto.set_index('finanziaria', inplace=True)
    st.dataframe(df_confronto.style.format({
        'commissione_percentuale': '{:.2f}%',
        'costo_commissione': '€{:.2f}',
        'importo_netto': '€{:.2f}'
    }))