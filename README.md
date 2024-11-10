# Chatbot pour résumer les articles scientifiques

Ce projet est un ChatBot qui est conçu pour extraire le contenu textuel à partir d’articles scientifiques au format PDF ou HTML, générer des résumés concis de ces articles et répondre aux questions posées par l’utilisateur concernant leur contenu.

## Installation

utiliser pip pour installer requirements.txt

```bash
pip install -r requirements.txt
```

## Run application

```bash
streamlit run "yourpath\NLP.py"
```

## NB
Si vous rencontrez un problème du static folder vous créez un folder et nommmez "static" changez le variable STATIC_DIRECTORY qui est dans sites-package/frontend/config.py en "yourpath/static"
