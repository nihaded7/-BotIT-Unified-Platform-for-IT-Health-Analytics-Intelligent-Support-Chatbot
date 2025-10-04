# generate_readme.py
readme = """# BotIT 🚀
Unified Platform for IT Health Analytics & Intelligent Support Chatbot

## 📌 Description
BotIT est une plateforme unifiée combinant :
- **Un module d’analyse de données & dashboard** pour transformer des données IT brutes (performance, sécurité, connectivité) en insights exploitables grâce à un pipeline de nettoyage, un scoring de criticité et des visualisations interactives.
- **Un chatbot intelligent (RAG-based)** pour assister les utilisateurs et les équipes IT dans la résolution de problèmes courants via une architecture hybride (base de connaissances + embeddings + FAISS + GPT).

Ce projet a été réalisé dans le cadre du **Projet de Fin d’Année (2024-2025)** à l’**ENSA Tétouan**, en partenariat avec **Lear Corporation Tanger**.

---
## ⚙️ Fonctionnalités principales
### 🔹 Dashboard d’analyse
- Chargement de fichiers CSV contenant des données systèmes.
- Pipeline configurable de **nettoyage des données** (suppression de doublons, gestion des valeurs manquantes, normalisation).
- **Détection d’anomalies & scoring de criticité** (CPU, RAM, disque, vulnérabilités CVE).
- Génération de **KPIs** et de **visualisations interactives** (Matplotlib, Seaborn).

### 🔹 Chatbot intelligent
- Architecture **RAG** (Retrieval-Augmented Generation).
- Utilisation de **Sentence-Transformers (all-MiniLM-L6-v2)** pour embeddings.
- Recherche vectorielle avec **FAISS**.
- Réponses raffinées avec **GPT-4o-mini**.
- Support de sessions multi-tours avec gestion du contexte.

---
## 🏗️ Architecture du projet
- **Frontend :** React.js (interface utilisateur, navigation entre Dashboard & Chatbot).
- **Backend :** FastAPI (Python) pour l’analyse de données et le pipeline du chatbot.
- **Base de connaissances :** Dataset structuré en paires *Problème → Solution*.
- **Pipeline IA :** Embeddings + FAISS + GPT.

---



## 🚀 Installation & Lancement
### 🔧 Prérequis
- Python 3.10+
- Node.js 18+

### 1️⃣ Backend (FastAPI)
\`\`\`bash
cd backend
pip install -r requirements.txt
uvicorn server:app --reload
\`\`\`

### 2️⃣ Frontend (React.js)
\`\`\`bash
cd frontend
npm install
npm run dev
\`\`\`

### 3️⃣ Accès
- **Dashboard :** http://localhost:5173
- **Chatbot :** via l’onglet navigation

---

## 📊 Démonstration
- **Dashboard :** Upload de CSV, visualisation des anomalies, KPIs.
- **Chatbot :** Dialogue en langage naturel avec support RAG.
![1](assets/01.png)

![3](assets/03.png)
![4](assets/04.png)
![5](assets/05.png)
![6](assets/06.png)
![7](assets/07.png)
![8](assets/08.png)
![8](assets/09.png)

![8](assets/10.png)

---

## 🔮 Améliorations futures
- Intégration **temps réel** avec SIEM / Intune / Splunk.
- Détection d’anomalies par **Machine Learning**.
- **Expansion automatique de la base de connaissances**.
- **Support multilingue** (EN, FR, AR).
- Applications **mobile et desktop**.

---

## 👩‍💻 Auteur
Projet réalisé par **EL ALAMI Nihad**
- **Filière :** science des données, Big Data & Intelligence Artificielle, ENSA Tétouan
- **Année :** 2024 – 2025
