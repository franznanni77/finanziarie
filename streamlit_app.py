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

def calcola_migliore_finanziaria(importo, rate):
    """
    Calcola la migliore opzione di finanziamento basata sull'importo e il numero di rate
    """
    # Ottieni le commissioni per il numero di rate selezionato
    commissioni = df[df['Mesi'] == rate].iloc[0]
    
    risultati = {}
    for finanziaria in ['Sella Appago', 'Cofidis PagoDIL', 'Compass HeyLight']:
        if commissioni[finanziaria] == 0:
            continue
            
        commissione = commissioni[finanziaria] / 100
        costo_commissione = importo * commissione
        costo_totale = importo - costo_commissione
        
        risultati[finanziaria] = {
            'commissione_percentuale': commissioni[finanziaria],
            'costo_commissione': costo_commissione,
            'importo_netto': costo_totale
        }
    
    # Trova la finanziaria con il costo più basso (importo netto più alto)
    migliore_finanziaria = max(risultati.items(), key=lambda x: x[1]['importo_netto'])
    return migliore_finanziaria, risultati

# Configurazione della pagina Streamlit
st.title('Calcolatore Finanziamenti')

# Input utente
importo = st.number_input('Inserisci l\'importo da finanziare (€)', min_value=1.0, value=1000.0)
rate = st.number_input('Inserisci il numero di rate', min_value=1, max_value=24, value=12)

if st.button('Calcola'):
    # Calcola la rata mensile per il cliente (senza interessi)
    rata_mensile = importo / rate
    
    # Trova la migliore opzione di finanziamento
    migliore, tutti_risultati = calcola_migliore_finanziaria(importo, rate)
    
    # Mostra i risultati
    st.header('Risultati')
    
    # Informazioni per il cliente
    st.subheader('Informazioni per il cliente')
    st.write(f'Rata mensile: €{rata_mensile:.2f}')
    st.write(f'Numero rate: {rate}')
    st.write(f'Importo totale: €{importo:.2f}')
    
    # Informazioni per l'azienda
    st.subheader('Analisi delle opzioni di finanziamento')
    
    # Crea una tabella comparativa
    risultati_df = pd.DataFrame.from_dict(
        {k: {
            'Commissione (%)': v['commissione_percentuale'],
            'Costo commissione (€)': v['costo_commissione'],
            'Importo netto (€)': v['importo_netto']
        } for k, v in tutti_risultati.items()
    }).T
    
    st.dataframe(risultati_df.style.format({
        'Commissione (%)': '{:.2f}%',
        'Costo commissione (€)': '€{:.2f}',
        'Importo netto (€)': '€{:.2f}'
    }))
    
    # Evidenzia la migliore opzione
    st.success(f'''
    Migliore opzione: {migliore[0]}
    - Commissione: {migliore[1]["commissione_percentuale"]:.2f}%
    - Costo commissione: €{migliore[1]["costo_commissione"]:.2f}
    - Importo netto: €{migliore[1]["importo_netto"]:.2f}
    ''')