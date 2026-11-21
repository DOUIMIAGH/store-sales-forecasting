# Formulation pour le CV

**Prévision des ventes — Python, pandas, LightGBM | Projet personnel**

- Analyse de **3 millions d’observations** couvrant **1 782 séries magasin–famille** ; construction de variables historiques et calendaires pour prévoir les ventes à 16 jours.
- Comparaison de cinq approches sur trois fenêtres chronologiques : **RMSLE de validation interne de 0,3972**, soit **12,5 % de réduction** face à une référence saisonnière logarithmique.
- Soumission acceptée à **Kaggle Store Sales – Time Series Forecasting** : **RMSLE officiel de 0,43477** sur le jeu de test de la compétition.

Les 3 millions de lignes décrivent l’exploration ; l’entraînement final utilise 677 160 lignes préparées. Le score interne provient des trois fenêtres utilisées pendant le développement. Le score Kaggle est celui de la soumission du 21 novembre 2026. Aucun classement ni percentile n’est revendiqué.
