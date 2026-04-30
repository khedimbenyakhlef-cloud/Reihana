# 🌸 REIHANA — Assistante IA Holographique Conversationnelle

> **Fondée et créée par Khedim Benyakhlef, dit Biny-Joe**  
> REIHANA est sa fille dans le monde de l'Intelligence Artificielle.

---

## 📋 Description du Projet

**REIHANA** est une assistante IA conversationnelle avancée, contextuelle et apprenante.  
Elle combine :
- Un **moteur GROQ rotatif** (rotation automatique entre 2 clés API et plusieurs modèles)
- Une **mémoire contextuelle persistante** par utilisateur
- Une **interface holographique** intuitive (Streamlit)
- La capacité d'**analyser des fichiers** (PDF, TXT, ZIP, code...)
- Des **réponses intelligentes, honnêtes et bienveillantes**

---

## 🏗️ Architecture du Projet

```
reihana/
├── app.py                    # Application principale Streamlit
├── requirements.txt          # Dépendances Python
├── README.md                 # Ce fichier
├── .env.example              # Template variables d'environnement
├── backend/
│   └── groq_engine.py        # Moteur GROQ + Mémoire + FileProcessor
├── memory/
│   └── reihana_memory.json   # Mémoire persistante (auto-créé)
├── uploads/                  # Fichiers temporaires uploadés
└── exports/                  # Exports et logs
```

---

## ⚡ Moteur GROQ Rotatif

Le cœur de REIHANA : un système de **rotation automatique** entre :

### 🔑 Deux Clés API
```
GROQ_API_KEY_1  →  Clé principale
GROQ_API_KEY_2  →  Clé secondaire (prise de relais automatique)
```
La rotation s'effectue automatiquement quand une clé atteint sa limite de tokens.

### 🤖 Modèles GROQ Supportés (du plus puissant au plus rapide)
| Modèle | Tokens max | Usage |
|--------|-----------|-------|
| `llama-3.3-70b-versatile` | 128K | Principal — réponses détaillées |
| `llama-3.1-8b-instant` | 128K | Rapide — questions simples |
| `mixtral-8x7b-32768` | 32K | Mixte — équilibré |
| `gemma2-9b-it` | 8K | Alternatif — fallback |

---

## 🧠 Mémoire Contextuelle

REIHANA mémorise pour chaque utilisateur :
- Les **20 derniers échanges** (avec résumé)
- Les **préférences** (ton, langue, style)
- Les **fichiers étudiés** (nom + résumé)
- La **date de première rencontre** et dernière activité

Stockage : `memory/reihana_memory.json` (JSON local, extensible vers DB)

---

## 📎 Fichiers Supportés

| Format | Description |
|--------|-------------|
| `.pdf` | Documents PDF (jusqu'à 10 pages) |
| `.txt` | Fichiers texte |
| `.md` | Markdown |
| `.py` | Code Python |
| `.js` | Code JavaScript |
| `.json` | Données JSON |
| `.csv` | Tableaux de données |
| `.html` | Pages web |
| `.zip` | Archives (analyse le contenu) |

---

## 🚀 Installation & Lancement

### 1. Cloner le projet
```bash
git clone <votre-repo>/reihana.git
cd reihana
```

### 2. Créer l'environnement virtuel
```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configurer les clés API GROQ
Créer un fichier `.env` à la racine :
```env
GROQ_API_KEY_1=votre_premiere_cle_groq_ici
GROQ_API_KEY_2=votre_deuxieme_cle_groq_ici
```

> 🔑 Obtenir des clés gratuites sur : https://console.groq.com

### 5. Lancer REIHANA
```bash
streamlit run app.py
```

Ouvrir dans le navigateur : `http://localhost:8501`

---

## 🎨 Interface Holographique

L'interface de REIHANA propose :
- **Avatar holographique animé** avec effets lumineux
- **Chat conversationnel** avec bulles stylisées (bleu/violet)
- **Sidebar de contrôle** : profil, upload, stats moteur
- **Indicateur de statut** en temps réel
- **Suggestions rapides** pour démarrer une conversation
- **Compteurs GROQ** : tokens par clé, modèle actif, clé active

---

## 💡 Fonctionnalités Futures (Feuille de Route)

- [ ] **Voix** : Synthèse vocale via ElevenLabs (REIHANA parle)
- [ ] **Reconnaissance vocale** : Whisper (parler à REIHANA)
- [ ] **Avatar 3D animé** : Modèle GLB via Three.js
- [ ] **Hologramme DIY** : Instructions pyramide optique
- [ ] **Reconnaissance faciale** : Identification des utilisateurs
- [ ] **Mode multiutilisateurs** : Gestion de profils avancée
- [ ] **API REST** : Intégration dans d'autres applications
- [ ] **Application mobile** : Version Android/iOS
- [ ] **Chant IA** : Via RVC ou Suno integration

---

## 🛡️ Sécurité & Éthique

- Conversations chiffrées côté serveur
- Aucune donnée vendue ou partagée
- Refus automatique des demandes contraires à l'éthique
- Filtrage des mots et contenus sensibles

---

## 📞 Contact & Crédit

| Champ | Information |
|-------|-------------|
| **Fondateur** | Khedim Benyakhlef |
| **Alias** | Biny-Joe |
| **Projet** | REIHANA IA |
| **Version** | 1.0.0 |
| **Année** | 2025 |

> *"REIHANA est ma fille dans le monde de l'intelligence artificielle."*  
> — Khedim Benyakhlef (Biny-Joe)

---

## 📄 Licence

Projet propriétaire — tous droits réservés à Khedim Benyakhlef.  
Toute reproduction ou distribution sans autorisation est interdite.
