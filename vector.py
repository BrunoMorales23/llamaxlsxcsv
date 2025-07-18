import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"

from langchain_ollama import OllamaEmbeddings
#from langchain_community.vectorstores import Chroma
#from langchain.vectorstores import Chroma
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import pandas as pd

#aca va la lectura del documento
#archivo = "C:/Users/bmorales/Downloads/BD-Adm&Finanzas-DS_Backup (1).xlsx"
archivo ="C:/Users/MarsuDIOS666/Desktop/llama/inputs/CSV UTF.csv"
#archivo = "C:/Users/MarsuDIOS666/Desktop/llama/inputs/BD-Adm&Finanzas-DS_Backup.csv"
#df = pd.read_excel(archivo)
df = pd.read_csv(archivo, sep=';', encoding='utf-8', index_col=False)
#df = pd.read_csv(archivo)
print(df)
print(df.shape)
print(df.iloc[400])

#embeddings = OllamaEmbeddings(model="mxbai_embed_large")
embeddings = OllamaEmbeddings(model="nomic-embed-text")

db_location = "./chrome_langchain_db"
add_documents = not os.path.exists(db_location)

vector_store = Chroma(
    collection_name="Testing",
    persist_directory=db_location,
    embedding_function=embeddings
)

if add_documents:
    documents = []
    ids = []

    for i, row in df.iterrows():
        content = f"""
        Año - mes: {row.get('Año - mes', '')}
        Fecha: {row.get('Fecha', '')}
        Tipo: {row.get('Tipo', '')}
        Comprobante: {row.get('Comprobante', '')}
        Cliente: {row.get('Cliente', '')}
        """

        doc = Document(
            page_content=content.strip(),
            metadata={"id": str(i)},
        )

        documents.append(doc)
        ids.append(str(i))

    # Batching
    MAX_BATCH_SIZE = 5461
    total = len(documents)
    print(f"Agregando {total} documentos en batches de {MAX_BATCH_SIZE}...")

    for i in range(0, total, MAX_BATCH_SIZE):
        batch_docs = documents[i:i + MAX_BATCH_SIZE]
        batch_ids = ids[i:i + MAX_BATCH_SIZE]
        vector_store.add_documents(documents=batch_docs, ids=batch_ids)
        print(f"Batch agregado: {i} al {min(i + MAX_BATCH_SIZE, total)}")

    print(f"{total} documentos agregados a la base.")

#if add_documents:
#    vector_store.add_documents(documents=documents, ids=ids)
#    print(f"{len(documents)} documentos agregados a la base.")

retriever = vector_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "k": df.shape[0],
        "score_threshold": 0.6
    }
)
