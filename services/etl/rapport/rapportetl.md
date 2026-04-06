# Rapport ETL & Data Visualisation

**Projet** : HealthAI Coach — Backend Métier  
**Rôle** : ETL & Data Visualisation  
**Environnement** : Windows, VS Code, Python 3.10+, GitHub  
**Date** : 06/04/2026  

---

## 1. Pipeline ETL

### 1.1 Structure du pipeline

Le pipeline ETL est composé de trois fichiers principaux orchestrés
par run_pipeline.py :

| Fichier | Rôle |
|---------|------|
| ingestion.py | Extract — chargement et analyse des données brutes |
| nettoyage_v2.py | Transform — nettoyage et transformation des données |
| run_pipeline.py | Orchestrateur — enchaîne les étapes et gère les logs |

### 1.2 Étape Extract — ingestion.py

Le module d'ingestion charge les quatre datasets CSV depuis le dossier
data/raw/. Pour chaque source il effectue les opérations suivantes :

- Comptage des lignes brutes du fichier source avant chargement Pandas,
  permettant de détecter les lignes corrompues sautées par on_bad_lines='skip'
- Analyse de la structure : nombre de lignes chargées, colonnes, types
- Détection et comptage des doublons
- Détection des valeurs manquantes colonne par colonne
- Génération automatique du rapport d'inventaire au format Markdown

### 1.3 Étape Transform — nettoyage_v2.py

Deux stratégies de nettoyage distinctes sont appliquées selon la
destination des données :

**Nettoyage BDD (clean_bdd/) — livrable principal :**

| Action | Datasets concernés |
|--------|-------------------|
| Suppression des doublons | daily_food_nutrition (54 doublons) |
| Correction type Max_BPM str→float64 | gym_members_synthetic |
| Remplacement NULL critiques par "Non renseigné" | diet_recommendations |
| Normalisation noms de colonnes | Les 4 datasets |
| Conservation des NULL résiduels | Les 4 datasets |

**Nettoyage ML (clean_ml/) — optionnel :**

| Action | Détail |
|--------|--------|
| Suppression totale des NULL | dropna() sur les 4 datasets |
| Encodage colonnes texte | LabelEncoder |
| Normalisation colonnes numériques | StandardScaler |

La couche ML ne fait pas partie du périmètre demandé dans le cahier
des charges. Elle constitue une valeur ajoutée anticipant les besoins
futurs de l'équipe data science de HealthAI Coach.

### 1.4 Étape Load

Le chargement des données nettoyées vers la base PostgreSQL est pris
en charge par l'équipe backend. Le pipeline ETL livre les fichiers
clean_bdd/ en sortie selon le format attendu par l'équipe.

### 1.5 Orchestration et logs

L'orchestrateur run_pipeline.py enchaîne les étapes de manière
séquentielle avec la gestion suivante :

- Chaque étape est encadrée par un bloc try/except
- En cas d'échec le pipeline s'arrête avec sys.exit(1)
- Les logs sont écrits en console et dans pipeline.log
- Rotation automatique du fichier log à 1MB
- Un fichier lancer_pipeline.bat permet le lancement automatisé sur Windows

### 1.6 Bilan des données

| Dataset | Lignes brutes | Lignes clean_bdd | Lignes clean_ml | Doublons | Manquants |
|---------|--------------|-----------------|----------------|----------|-----------|
| daily_food_nutrition | 645 | 591 | 591 | 54 | 0 |
| diet_recommendations | 1000 | 1000 | 1000 | 0 | 861 |
| gym_members_exercise | 973 | 973 | 973 | 0 | 0 |
| gym_members_synthetic | 1800 | 1800 | 1352 | 0 | 481 |
| **TOTAL** | **4418** | **4364** | **3916** | **54** | **1342** |

---

## 2. Data Visualisation

### 2.1 Outil retenu

Power BI Desktop a été retenu pour la création du tableau de bord
analytique. Cet outil offre une prise en main rapide, une connexion
native aux fichiers CSV et des capacités de transformation de données
via Power Query. La publication sur Power BI Service via la
fonctionnalité de publication web publique permet l'intégration du
tableau de bord dans l'application web via un iframe sans contrainte
de licence.

### 2.2 Datasets utilisés pour la visualisation

Deux datasets ont été sélectionnés parmi les quatre disponibles pour
alimenter le tableau de bord :

| Dataset | Lignes | Justification |
|---------|--------|---------------|
| gym_members_exercise | 973 | Données activité physique, aucune valeur manquante, directement exploitable |
| diet_recommendations | 1000 | Données nutritionnelles et profils de santé, couvre la dimension nutrition |

Ces deux sources couvrent ensemble l'ensemble des indicateurs demandés
dans le cahier des charges : métriques utilisateurs, analyses
nutritionnelles, statistiques fitness et KPIs business.

### 2.3 Transformations Power Query

Au-delà du nettoyage effectué par le pipeline Python, des transformations
complémentaires sont réalisées dans Power BI via Power Query :

**Création d'identifiants uniques** : Les datasets ne disposant pas
d'identifiants utilisateurs natifs, un index ID est généré
automatiquement via Table.AddIndexColumn pour permettre les jointures
et le suivi individuel des enregistrements.

**Création d'indicateurs calculés** : Des colonnes calculées sont
construites dans Power Query pour enrichir les données brutes et
répondre aux besoins analytiques du tableau de bord. Ces indicateurs
permettent notamment de segmenter les utilisateurs par tranches, de
qualifier les niveaux d'activité et d'analyser les tendances
nutritionnelles de manière plus fine.

**Nettoyage complémentaire** : Renommage des colonnes pour un affichage
lisible, formatage des types de données pour les visuels.

### 2.4 Indicateurs du tableau de bord

Le tableau de bord couvre les grandes catégories d'indicateurs demandées
dans le cahier des charges :

- Métriques utilisateurs : segmentation et répartition des profils
- Analyses nutritionnelles : tendances et apports par profil
- Statistiques fitness : activité physique et performance
- KPIs business : indicateurs d'engagement et de progression

Les visuels précis seront présentés en démonstration lors de la
soutenance.

### 2.5 Intégration dans l'application web

Le tableau de bord est publié sur Power BI Service via la
fonctionnalité de publication web publique. L'équipe frontend intègre
le tableau de bord dans l'application via un iframe :
```html
<iframe 
  src="https://app.powerbi.com/view?r=XXXXXX"
  width="100%" 
  height="600px"
  frameborder="0">
</iframe>
```

---

## 3. Difficultés rencontrées

**Anomalie de type Max_BPM** : La colonne Max_BPM du dataset synthétique
était stockée en str au lieu de float64, provoquant des erreurs lors
des calculs numériques. Corrigée via pd.to_numeric(errors='coerce').

**Gestion des valeurs manquantes** : Le dataset diet_recommendations
présentait jusqu'à 33% de valeurs manquantes sur certaines colonnes
critiques. Après analyse, les valeurs ont été remplacées par
"Non renseigné" plutôt que supprimées afin de conserver l'intégralité
des 1000 enregistrements.

**Module scikit-learn absent** : Lors de la première exécution dans
l'environnement virtuel .venv, le module scikit-learn n'était pas
installé. Résolu via pip install scikit-learn et mise à jour du
requirements.txt.

**Lignes corrompues non détectées** : Le paramètre on_bad_lines='skip'
de Pandas sautait silencieusement des lignes sans les comptabiliser.
Corrigé en ajoutant un comptage des lignes brutes du fichier source
avant le chargement Pandas, permettant de détecter et documenter
les écarts.

---

## 4. Perspectives d'évolution

**Orchestration avancée** : Intégration du pipeline dans Apache Airflow
pour une planification fine des exécutions et un monitoring centralisé.

**Données en temps réel** : Connexion du pipeline aux APIs des objets
connectés pour ingérer des données biométriques en temps réel,
remplaçant les fichiers CSV statiques actuels.

**Enrichissement du tableau de bord** : Une fois la plateforme en
production, les KPIs business seront alimentés par les données réelles
de l'application et intégrés au tableau de bord existant.

**Module ML** : La couche clean_ml/ constitue une base prête à l'emploi
pour les futures équipes data science souhaitant entraîner des modèles
de recommandation personnalisée sur les données de HealthAI Coach.