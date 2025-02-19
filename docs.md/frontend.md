# Documentation Fonctionnelle : Application Streamlit de Classification de Documents

## 1. **Contexte et Objectif**
L'application Streamlit constitue une interface utilisateur destinée aux employés d'une agence d'intérim. Elle permet de :
- **Soumettre des documents** liés aux candidats (pièce d'identité, CV, etc.) pour classification automatique.
- **Consulter et corriger les prédictions** effectuées par le modèle de classification.

Cette interface s'intègre dans un système plus large comprenant :
- **Un backend de prédiction** pour le traitement des images.
- **Un orchestrateur** gérant les flux de données.
- **Un système de stockage S3** pour conserver les documents, les résultats d'OCR, et les retours utilisateurs.

---

## 2. **Utilisateurs Cibles**
- **Employés d'agence d'intérim** : Principalement ceux en charge de la gestion des candidatures.
- **Équipe d'administration (via une interface séparée)** : Consomme les feedbacks pour améliorer le modèle de classification.

---

## 3. **Structure et Fonctionnalités**

### **Page 1 : Soumission des Documents**
- **Entrée de référence** : Champ texte pour saisir une référence unique liée au candidat.
- **Téléversement de fichiers** : Possibilité d'uploader plusieurs fichiers (ex. : CV, ID, etc.).
- **Envoi des documents au backend** via une requête POST.
- **Affichage des résultats** : UUID, message de réponse et statut de l’opération.

#### **Flux d'envoi :**
1. L’utilisateur saisit la référence et téléverse les fichiers.
2. L’application envoie une requête `POST` au backend (`/predict`).
3. Le backend retourne un `UUID` et un message.
4. En cas d’erreur (référence dupliquée, etc.), un message d’alerte s’affiche.

---

### **Page 2 : Consultation et Correction des Prédictions**
- **Recherche de prédictions** : Saisie de la référence pour récupérer les prédictions (`GET /predict/{reference}`).
- **Affichage des prédictions** : Liste des images avec leur classe prédite.
- **Correction des classes** : Formulaire interactif permettant de corriger la classification.
- **Enregistrement des corrections** : Sauvegarde des feedbacks vers le S3.

#### **Flux de correction :**
1. L’utilisateur saisit la référence.
2. L’application récupère les prédictions (`GET`).
3. L’utilisateur consulte et corrige les classifications via des menus déroulants.
4. Une fois validées, les corrections sont :
   - **Enregistrées localement** (`corrections/{uuid}/prediction/feedback.csv`).
   - **Envoyées au S3** (`s3://{bucket}/{uuid}/prediction/feedback.csv`).
5. L’interface d’administration consomme ensuite ces fichiers pour ajuster les futures itérations du modèle.

---

## 4. **Intégrations Techniques**
- **Backend Prediction API** : 
  - `POST /predict` : Envoi des documents pour classification.
  - `GET /predict/{reference}` : Récupération des prédictions.
- **Stockage S3** : 
  - Stocke les documents téléversés.
  - Stocke les résultats de l'OCR et les feedbacks des utilisateurs.
- **Interface d'Administration** : 
  - Intègre les fichiers de feedback (`feedback.csv`) dans le pipeline d'entraînement.

---

## 5. **Structure des Fichiers de Feedback (`feedback.csv`)**
| Colonne           | Description                          |
|--------------------|--------------------------------------|
| `Image`           | Nom du fichier image (chemin complet) |
| `Classe Prédite`  | Classe prédite par le modèle        |
| `Classe Réelle`   | Classe corrigée par l’utilisateur   |

---

## 6. **Erreurs Possibles et Gestion**
| Scénario                     | Message affiché                |
|-----------------------------|------------------------------|
| Référence non unique        | "La référence doit être unique." |
| API non disponible          | "Erreur 500 : Service indisponible." |
| Aucun fichier téléversé     | "Veuillez sélectionner un fichier." |
| Prédiction introuvable      | "Référence invalide."        |

---

## 7. **Conclusion**
Cette documentation décrit les objectifs, les utilisateurs cibles et le fonctionnement technique de l'application de classification de documents. L’intégration des feedbacks dans le pipeline de réentraînement permettra d'améliorer continuellement les performances du modèle.
