# Importation des bibliothèques nécessaires
import streamlit as st  # Streamlit est utilisé pour créer une interface utilisateur
import requests  # Pour effectuer des requêtes HTTP
from bs4 import BeautifulSoup  # Pour analyser le contenu HTML d'une page web
import nltk  # Natural Language Toolkit pour le traitement du texte
from transformers import BertTokenizer , BertForQuestionAnswering  # Hugging Face Transformers pour BERT
import torch  # PyTorch pour le calcul
import csv  # Pour la manipulation de fichiers CSV
import io
import pymupdf as fitz # PyMuPDF pour extraire du texte à partir de fichiers PDF
from summarizer import Summarizer  # Pour générer un résumé de texte

# Télécharger les ressources nécessaires pour NLTK et BERT
nltk.download('punkt')


# Fonction pour extraire la réponse à partir du modèle "question_answering"
def get_answer(question , context):
    # Charger le tokenizer et le modèle pré-entraînés BERT
    tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
    model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')

    # Prétraiter les données pour les alimenter au modèle BERT
    inputs = tokenizer(question , context , return_tensors='pt' , truncation=True , padding=True)
    with torch.no_grad():
        outputs = model(**inputs)

    # Trouver l'indice de début et de fin de la réponse
    answer_start = torch.argmax(outputs.start_logits)
    answer_end = torch.argmax(outputs.end_logits) + 1

    # Convertir les indices en texte
    answer = tokenizer.convert_tokens_to_string(
        tokenizer.convert_ids_to_tokens(inputs[ "input_ids" ][ 0 ][ answer_start:answer_end ]))
    return answer


# Fonction principale
def main():
    # Titre de l'application Streamlit
    st.title("Résumé des articles scientifiques")

    # Zone de saisie du lien de l'article
    link = st.text_input("Entrez le lien de l'article :")
    extract_button = st.button("Extraire le texte et générer le résumé")

    # Si le bouton "Extraire" est cliqué
    if extract_button:
        if link:
            if link.lower().endswith(".pdf"):  # Si le lien pointe vers un PDF
                response = requests.get(link)
                if response.status_code == 200:
                    pdf_stream = io.BytesIO(response.content)

                    # Ouvrir le PDF avec PyMuPDF
                    pdf_file = fitz.open(stream=pdf_stream , filetype="pdf")
                    article_text = ""
                    for page_num in range(pdf_file.page_count):
                        page = pdf_file.load_page(page_num)
                        page_text = page.get_text()
                        article_text += page_text

                    # Limiter la longueur du texte extrait pour répondre aux contraintes de BERT
                    max_length = 5120
                    if len(article_text) > max_length:
                        article_text = article_text[ :max_length ]

                    # Stocker le texte extrait dans la session de l'application Streamlit
                    st.session_state.article_text = article_text
                    st.success("Texte extrait avec succès !")

                    # Générer le résumé du texte extrait
                    summarizer = Summarizer()
                    summary = summarizer(article_text)
                    st.subheader("Résumé généré :")
                    st.write(summary)
            else:  # Si le lien pointe vers une page web
                response = requests.get(link)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content , 'html.parser')
                    # Extraire le texte de tous les paragraphes de la page web
                    article_text = ' '.join([ p.get_text() for p in soup.find_all('p') ])

                    # Stocker le texte extrait dans la session de l'application Streamlit
                    st.session_state.article_text = article_text
                    st.success("Texte extrait avec succès !")

                    # Créer un fichier CSV pour stocker le lien et le texte extrait
                    article_filename = link.replace("/" , "").replace(":" , "") + ".csv"
                    with open(article_filename , mode="w" , newline="" , encoding="utf-8") as file:
                        writer = csv.writer(file , delimiter=";")
                        writer.writerow([ "Lien" , "Texte extrait" ])
                        writer.writerow([ link , article_text ])

    # Si le texte de l'article a été extrait avec succès
    if "article_text" in st.session_state:
        # Affichage du texte extrait de l'article
        st.header("Texte extrait de l'article :")
        st.text_area("" , value=st.session_state.article_text , height=300)

        # Générer un résumé du texte extrait
        summarizer = Summarizer()
        summary = summarizer(st.session_state.article_text)
        st.subheader("Résumé généré :")
        st.write(summary)

        # Zone de saisie de la question de l'utilisateur
        user_input = st.text_input("Posez une question :")

        # Bouton pour obtenir la réponse à la question
        if st.button("Obtenir la réponse"):
            answer = get_answer(user_input , st.session_state.article_text)
            if answer.strip() == "" or answer == "[CLS]":
                answer = "La réponse n'existe pas dans cet article."
            st.subheader("Réponse:")
            st.write(answer)


# Point d'entrée du script
if __name__ == "__main__":
    main()
