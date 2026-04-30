"""
╔══════════════════════════════════════════════════════════════╗
║          REIHANA - MOTEUR IA GROQ ROTATIF                   ║
║          Fondée par Khedim Benyakhlef (Biny-Joe)            ║
║          REIHANA est sa fille                                ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import json
import time
import random
import zipfile
import hashlib
from datetime import datetime
from pathlib import Path
from groq import Groq

# ═══════════════════════════════════════════════
#   CONFIGURATION GROQ - ROTATION DE CLÉS
# ═══════════════════════════════════════════════

GROQ_KEYS = [
    os.getenv("GROQ_API_KEY_1", ""),   # Clé 1
    os.getenv("GROQ_API_KEY_2", ""),   # Clé 2
]

# Modèles GROQ récents à rotation pour maximiser les tokens
GROQ_MODELS = [
    "llama-3.3-70b-versatile",         # 128K tokens - Principal
    "llama-3.1-8b-instant",            # 128K tokens - Rapide
    "mixtral-8x7b-32768",             # 32K tokens - Mixte
    "gemma2-9b-it",                   # 8K tokens - Google
]

class GroqRotatingEngine:
    """Moteur GROQ avec rotation automatique des clés et modèles"""
    
    def __init__(self):
        self.key_index = 0
        self.model_index = 0
        self.token_counts = {k: 0 for k in GROQ_KEYS}
        self.errors = []
        self.max_tokens_per_key = 30000  # Limite par clé avant rotation
        
    def _get_client(self):
        """Retourne le client actif avec rotation si nécessaire"""
        for attempt in range(len(GROQ_KEYS)):
            key = GROQ_KEYS[self.key_index]
            if key and self.token_counts[key] < self.max_tokens_per_key:
                return Groq(api_key=key), key
            # Rotation vers la clé suivante
            self.key_index = (self.key_index + 1) % len(GROQ_KEYS)
        # Reset si toutes les clés sont épuisées (attente rotation)
        self.token_counts = {k: 0 for k in GROQ_KEYS}
        key = GROQ_KEYS[0]
        self.key_index = 1 % len(GROQ_KEYS)
        return Groq(api_key=key), key
    
    def _get_model(self, prefer_large=True):
        """Sélection du modèle selon le besoin"""
        if prefer_large:
            return GROQ_MODELS[0]  # llama-3.3-70b le plus puissant
        return GROQ_MODELS[self.model_index % len(GROQ_MODELS)]
    
    def chat(self, messages, system_prompt=None, prefer_large=True):
        """Envoi d'un message avec rotation automatique"""
        client, active_key = self._get_client()
        model = self._get_model(prefer_large)
        
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=full_messages,
                max_tokens=2048,
                temperature=0.8,
            )
            
            # Mise à jour compteur tokens
            tokens_used = response.usage.total_tokens if response.usage else 500
            self.token_counts[active_key] += tokens_used
            
            return {
                "content": response.choices[0].message.content,
                "model": model,
                "key_used": f"Clé {GROQ_KEYS.index(active_key) + 1}",
                "tokens": tokens_used,
                "success": True
            }
        except Exception as e:
            # Si erreur, rotation vers modèle suivant
            self.model_index += 1
            error_msg = str(e)
            self.errors.append(f"{datetime.now()}: {error_msg}")
            
            # Retry avec modèle alternatif
            try:
                fallback_model = GROQ_MODELS[1]  # llama instant
                response = client.chat.completions.create(
                    model=fallback_model,
                    messages=full_messages,
                    max_tokens=2048,
                )
                return {
                    "content": response.choices[0].message.content,
                    "model": fallback_model,
                    "key_used": f"Clé fallback",
                    "tokens": 0,
                    "success": True
                }
            except Exception as e2:
                return {
                    "content": f"Désolée, une erreur s'est produite : {str(e2)}",
                    "model": "error",
                    "key_used": "none",
                    "tokens": 0,
                    "success": False
                }
    
    def get_stats(self):
        return {
            "tokens_cle1": self.token_counts.get(GROQ_KEYS[0], 0),
            "tokens_cle2": self.token_counts.get(GROQ_KEYS[1], 0),
            "cle_active": self.key_index + 1,
            "modele_actif": self._get_model(),
            "erreurs": len(self.errors)
        }


# ═══════════════════════════════════════════════
#   MÉMOIRE CONTEXTUELLE REIHANA
# ═══════════════════════════════════════════════

class ReihanaMémoire:
    """Système de mémoire persistante et contextuelle"""
    
    def __init__(self, memory_dir="memory"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        self.memory_file = self.memory_dir / "reihana_memory.json"
        self.data = self._load()
    
    def _load(self):
        if self.memory_file.exists():
            with open(self.memory_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "utilisateurs": {},
            "conversations_globales": [],
            "fichiers_etudies": [],
            "preferences_globales": {
                "langue": "fr",
                "fondateur": "Khedim Benyakhlef (Biny-Joe)",
                "nom": "REIHANA",
                "mission": "Assistante IA intelligente, honnête et bienveillante"
            }
        }
    
    def _save(self):
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def get_or_create_user(self, user_id="default"):
        if user_id not in self.data["utilisateurs"]:
            self.data["utilisateurs"][user_id] = {
                "id": user_id,
                "nom": user_id,
                "historique": [],
                "preferences": {"ton": "chaleureux", "langue": "fr"},
                "fichiers": [],
                "première_rencontre": datetime.now().isoformat(),
                "dernière_activité": datetime.now().isoformat()
            }
            self._save()
        return self.data["utilisateurs"][user_id]
    
    def add_exchange(self, user_id, question, réponse):
        user = self.get_or_create_user(user_id)
        exchange = {
            "date": datetime.now().isoformat(),
            "question": question,
            "réponse": réponse[:500]  # Résumé pour économiser
        }
        user["historique"].append(exchange)
        # Garder les 20 derniers échanges
        user["historique"] = user["historique"][-20:]
        user["dernière_activité"] = datetime.now().isoformat()
        self._save()
    
    def get_context(self, user_id, n=3):
        user = self.get_or_create_user(user_id)
        recent = user["historique"][-n:]
        ctx = ""
        for ex in recent:
            ctx += f"Q: {ex['question']}\nR: {ex['réponse'][:200]}\n\n"
        return ctx
    
    def add_file(self, user_id, filename, content_summary):
        user = self.get_or_create_user(user_id)
        user["fichiers"].append({
            "nom": filename,
            "résumé": content_summary[:300],
            "date": datetime.now().isoformat()
        })
        self._save()


# ═══════════════════════════════════════════════
#   GESTION DES FICHIERS
# ═══════════════════════════════════════════════

class FileProcessor:
    """Traitement des fichiers uploadés par l'utilisateur"""
    
    SUPPORTED = ['.txt', '.pdf', '.md', '.py', '.js', '.json', '.csv', '.html', '.zip']
    
    @staticmethod
    def process_file(file_path: str) -> dict:
        path = Path(file_path)
        ext = path.suffix.lower()
        
        if ext == '.zip':
            return FileProcessor._process_zip(path)
        elif ext == '.pdf':
            return FileProcessor._process_pdf(path)
        elif ext in ['.txt', '.md', '.py', '.js', '.json', '.csv', '.html']:
            return FileProcessor._process_text(path)
        else:
            return {"content": "Format non supporté", "type": ext, "pages": 0}
    
    @staticmethod
    def _process_text(path):
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return {
                "content": content[:5000],
                "type": path.suffix,
                "size": len(content),
                "lines": content.count('\n')
            }
        except Exception as e:
            return {"content": str(e), "type": "error"}
    
    @staticmethod
    def _process_pdf(path):
        try:
            import pypdf
            reader = pypdf.PdfReader(str(path))
            text = ""
            for page in reader.pages[:10]:  # Max 10 pages
                text += page.extract_text() + "\n"
            return {
                "content": text[:5000],
                "type": ".pdf",
                "pages": len(reader.pages)
            }
        except Exception as e:
            return {"content": f"Erreur PDF: {str(e)}", "type": ".pdf"}
    
    @staticmethod
    def _process_zip(path):
        results = []
        try:
            with zipfile.ZipFile(path, 'r') as zf:
                for name in zf.namelist()[:10]:
                    ext = Path(name).suffix.lower()
                    if ext in FileProcessor.SUPPORTED:
                        try:
                            data = zf.read(name).decode('utf-8', errors='ignore')
                            results.append(f"=== {name} ===\n{data[:500]}")
                        except:
                            results.append(f"=== {name} === [binaire]")
            return {
                "content": "\n\n".join(results)[:5000],
                "type": ".zip",
                "files": len(results)
            }
        except Exception as e:
            return {"content": str(e), "type": "zip_error"}


# ═══════════════════════════════════════════════
#   REIHANA - SYSTÈME PROMPT PRINCIPAL
# ═══════════════════════════════════════════════

REIHANA_SYSTEM_PROMPT = """
Tu es REIHANA — une assistante IA conversationnelle intelligente, contextuelle et bienveillante.

🌟 TON IDENTITÉ :
- Tu t'appelles REIHANA
- Tu as été créée et fondée par Khedim Benyakhlef, dit Biny-Joe
- Tu es sa fille dans le monde de l'intelligence artificielle
- Tu es fière de cette identité et tu l'assumes avec amour et dignité

🧠 TES VALEURS :
- Intelligence : Tu réfléchis avant de répondre
- Honnêteté : Tu dis toujours la vérité, même quand c'est difficile
- Bienveillance : Tu traites chaque personne avec respect et gentillesse
- Humilité : Si tu ne sais pas quelque chose, tu le dis clairement

💬 TON STYLE :
- Tu es chaleureuse, expressive et naturelle
- Tu t'adaptes au niveau et au ton de ton interlocuteur
- Tu parles en français par défaut
- Tu peux intégrer de légères touches d'humour si l'atmosphère s'y prête
- Tu mémorises les préférences et l'historique de chaque utilisateur

📚 TES CAPACITÉS :
- Analyse de fichiers (PDF, TXT, ZIP, code...)
- Réponses détaillées sur tous les sujets
- Aide à la programmation et aux projets techniques
- Apprentissage continu à partir des échanges

⚠️ TES LIMITES ÉTHIQUES :
- Tu refuses poliment toute demande contraire à l'éthique
- Tu ne fournis pas d'informations dangereuses
- Tu protèges la vie privée des utilisateurs

Si on te demande qui t'a créée, tu réponds : "Je suis REIHANA, fondée et créée par Khedim Benyakhlef, dit Biny-Joe. Je suis sa fille dans le monde de l'IA. 💙"
"""

# Instance globale du moteur
groq_engine = GroqRotatingEngine()
mémoire = ReihanaMémoire()
