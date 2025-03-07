## 📌 README - Bot Discord "HappyB" 🎂
# 🎯 Description du Projet
HappyB est un bot Discord conçu pour gérer et rappeler les anniversaires des membres d'un serveur. Grâce à ses fonctionnalités avancées, il permet aux utilisateurs d'enregistrer, consulter, mettre à jour et supprimer leurs dates d'anniversaire.

🚀 Le bot enregistre les anniversaires dans une base de données PostgreSQL hébergée sur Railway, garantissant la persistance des données même après un redéploiement.

# 🛠 Fonctionnalités Principales
#### ✅ Ajout d'un anniversaire (/anniv add @User JJ-MM)
#### ✅ Affichage de tous les anniversaires triés par date (/anniv list)
#### ✅ Affichage d'un anniversaire spécifique (/anniv for @User)
#### ✅ Mise à jour d'un anniversaire (/anniv update @User JJ-MM)
#### ✅ Suppression d'un anniversaire (/anniv delete @User)
#### ✅ Rappels automatiques (1 mois et 2 semaines avant l'anniversaire)

# 🚀 Installation et Déploiement
### 1️⃣ Prérequis
- Python 3.8+
- Git
- Railway.app
- PostgreSQL

### 2️⃣ Cloner le projet
- git clone https://github.com/VOTRE-USERNAME/HappyB.git
- cd HappyB

### 3️⃣ Installer les dépendances
- pip install -r requirements.txt

### 4️⃣ Créer un fichier .env
Ajoutez les informations sensibles dans un fichier .env :
- DISCORD_TOKEN=VOTRE_TOKEN_DISCORD
- DATABASE_URL=URL_DE_VOTRE_BASE_POSTGRESQL
- BIRTHDAY_CHANNEL_ID=ID_DU_CHANNEL

### 5️⃣ Lancer le bot en local
- python bot.py

# ☁️ Déploiement sur Railway
### 1️⃣ Créer un compte sur Railway.app
### 2️⃣ Créer un nouveau projet et ajouter PostgreSQL
### 3️⃣ Déployer le projet à partir de GitHub
### 4️⃣ Ajouter les variables d’environnement (DATABASE_URL, DISCORD_TOKEN, etc.)
### 5️⃣ Railway démarre automatiquement votre bot 🎉

# 📜 Exemples de Commandes
## Commande                                          Description
### /anniv add @User 10-02                  Ajoute l'anniversaire du membre
### /anniv list                                             Affiche tous les anniversaires triés par date
### /anniv for @User                               Affiche l'anniversaire d'un utilisateur
### /anniv update @User 05-08          Met à jour l'anniversaire
### /anniv delete @User                         Supprime un anniversaire

# 🛠 Technologies Utilisées
- Langage : Python 🐍
- Frameworks : discord.py
- Base de données : PostgreSQL 📊
- Hébergement : Railway.app ☁️