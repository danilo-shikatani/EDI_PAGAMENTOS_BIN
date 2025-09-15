import streamlit as st
import pandas as pd
import json

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Tradutor de EDI JSON", layout="wide")
st.title("🤖 Tradutor de Extratos EDI (JSON para Tabela)")
st.markdown("Faça o upload de um ou mais arquivos JSON (ex: BRED0070...) para convertê-los em uma tabela CSV.")


# --- 2. ÁREA DE UPLOAD ---
st.header("📤 1. Faça o Upload dos arquivos JSON")
uploaded_files = st.file_uploader(
    "Arraste e solte quantos arquivos JSON quiser",
    accept_multiple_files=True,
    type=['json']
)

# --- 3. BOTÃO PARA PROCESSAR E LÓGICA DE TRANSFORMAÇÃO ---
if uploaded_files:
    if st.button("🚀 Processar e Converter Arquivos"):
        all_dfs = [] # Lista para guardar todas as tabelas processadas
        total_records = 0

        with st.spinner("Processando... Lendo e achatando os arquivos JSON..."):
            for file in uploaded_files:
                try:
                    # Lê o conteúdo do arquivo JSON
                    data = json.load(file)

                    # --- ESTA É A LÓGICA PRINCIPAL (O "ACHATAMENTO") ---
                    # Identificamos que as "linhas" estão dentro da chave 'clientHeaders'
                    record_path_key = 'clientHeaders'

                    # Definimos quais dados do "cabeçalho" do arquivo queremos repetir em todas as linhas
                    meta_cols = [
                        ['fileHeader', 'processingDate'],
                        ['fileHeader', 'acquiringName'],
                        ['fileHeader', 'fileNumber']
                    ]

                    # Usamos json_normalize para converter o JSON aninhado em uma tabela plana
                    df_flat = pd.json_normalize(
                        data,
                        record_path=[record_path_key], # Diz onde estão as "linhas"
                        meta=meta_cols,                 # Puxa os metadados do cabeçalho
                        errors='ignore'                 # Ignora erros se alguma estrutura faltar
                    )
                    
                    all_dfs.append(df_flat)
                    total_records += len(df_flat)
                    
                except Exception as e:
                    st.error(f"Erro ao processar o arquivo '{file.name}': {e}. Certifique-se de que é um JSON EDI válido.")

            if all_dfs:
                # Junta todos os dataframes de todos os arquivos em um só
                df_final = pd.concat(all_dfs, ignore_index=True)
                st.session_state['df_resultado'] = df_final # Salva na memória do app
                
                st.balloons()
                st.success(f"Conversão concluída! {len(all_dfs)} arquivos processados, totalizando {total_records} registros encontrados.")

# --- 4. EXIBIÇÃO DO RESULTADO E DOWNLOAD ---
if 'df_resultado' in st.session_state:
    st.header("📊 2. Tabela de Dados Consolidada")
    df_resultado_final = st.session_state['df_resultado']
    
    st.info(f"Visualizando {len(df_resultado_final)} linhas de dados. Use a barra de rolagem abaixo para ver todas as colunas.")
    st.dataframe(df_resultado_final)

    # Prepara os dados para download em CSV
    @st.cache_data
    def converter_df_para_csv(df):
        return df.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8')

    csv_final = converter_df_para_csv(df_resultado_final)
    
    st.download_button(
        label="📥 Baixar Tabela Consolidada (CSV)",
        data=csv_final,
        file_name="dados_edi_consolidados.csv",
        mime="text/csv",
    )
