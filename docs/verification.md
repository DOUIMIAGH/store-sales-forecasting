# Revue du projet Store Sales

Revue initiale : 28 octobre 2026. Mise à jour : 21 novembre 2026. Revue du code, des sorties enregistrées et de la méthode, suivie d’une préparation du dépôt.

## Conclusion

La démarche est cohérente pour un projet personnel de recherche de stage : exploration, références explicites, variables historiques disponibles à l’origine, validation chronologique et analyse d’erreurs. Aucun défaut bloquant de construction temporelle n’a été identifié dans le code fourni. Cela ne constitue pas une preuve d’absence de tout défaut, ni une certification de généralisation.

Le notebook original contient **25 cellules, dont 23 cellules de code**, **sept graphiques de données** et aucune sortie de type `error`. Les compteurs enregistrés vont de 2 à 23 puis 25 ; ces compteurs ne prouvent pas un lancement intégral en session propre. Le dernier export annonce **28 512 prévisions** et présente les cinq premiers identifiants. Le fichier CSV complet n’a pas été fourni séparément.

Empreinte SHA-256 du notebook reçu : `dd345b529f973e200d511ad1a29baf68e17af9705b3aed5e0685628dc5528847`.

## Constats méthodologiques

| Point | Conclusion de la revue |
|---|---|
| Taille du jeu | 54 × 33 × 1 684 = 3 000 888 lignes explorées ; cohérent avec la sortie de chargement. |
| Taille de la validation | 1 782 × 16 = 28 512 lignes par fenêtre ; trois fenêtres sans chevauchement donnent 85 536 prévisions. |
| Entraînement | Données préparées depuis le 31 juillet 2016, pas les 3 millions de lignes. Réentraînement final : 677 160 lignes jusqu’au 15 août 2017. |
| Décalages | Jointures par dates exactes ; les retards 16, 21 et 28 jours précèdent l’origine pour chaque horizon de 1 à 16 jours. |
| Statistiques | Grille quotidienne, décalage avant le calcul, conservation des dates absentes sous forme de NaN. Moyennes et écart-type par série. |
| Validation | Réentraînement sur le passé pour chaque origine. Le précalcul sur une table commune reste compatible avec les retards minimaux de 16 jours. |
| Transformation de cible | Apprentissage sur log1p(sales), retour avec expm1 et limitation à zéro ; compatible avec le RMSLE calculé. |
| Agrégation | Racine de la moyenne pondérée des RMSLE au carré ; ne pas utiliser directement la moyenne des RMSLE. |
| Calendrier | Sélection des événements nationaux planifiés aux dates effectives ; absence de jointure multipliant les lignes. Aucun indicateur d’événement imprévu utilisé. |
| Promotions | Données fournies dans le test, supposées connues ; hypothèse à documenter pour une utilisation réelle. |
| Diagnostic par famille | Le résultat 24/33 concerne le modèle initial et la dernière fenêtre, pas le modèle enrichi. |
| Graphiques | Sept figures enregistrées ; deux diagnostics du magasin 1 concernent les étapes initiales. Le graphique d’importance du modèle enrichi est dominé par les moyennes historiques. |
| Soumission | Modèle final séparé des modèles de validation ; ordre des identifiants, valeurs finies et non négatives contrôlés par le code de la dernière cellule. |
| Évaluations | Les trois fenêtres ont participé à la sélection des variantes : 0,3972 reste un score interne. Une soumission officielle distincte a obtenu 0,43477 sur le test de la compétition le 21 novembre 2026. |

## Corrections apportées

- Ajout d’une introduction, de sections, d’un schéma du protocole et de précisions sur les unités et les hypothèses.
- Identification d’un dossier contenant ensemble les cinq CSV requis, avec emplacement local et variable d’environnement possibles ; arrêt explicite si le dossier reste ambigu.
- Utilisation de ce même dossier pour le calendrier et les magasins.
- Chemins de sortie compatibles avec Kaggle et une exécution locale ; export des figures et des versions de paquets lors de la prochaine exécution.
- Assertions supplémentaires de qualité et d’alignement des identifiants.
- Noms distincts pour les bilans par jour de semaine et par famille.
- Limitation de la source des retards de la soumission aux 28 derniers jours nécessaires, ce qui évite de copier et joindre tout l’historique pour ces retards.
- Explication des étapes initiales et de leurs résultats, de la soumission à retenir et des limites de la validation.
- Ajout du README, des dépendances, des tableaux archivés, des contrôles ciblés et de la formulation pour le CV.

Les paramètres des modèles, les fenêtres d’évaluation et les statistiques n’ont pas été modifiés. Les sorties de modèles sont celles de l’exécution originale. Aucune sortie de modèle n’a été inventée ; le seul nouveau graphique est un schéma méthodologique.

## Vérifications exécutées

- Compilation syntaxique des 23 cellules de code originales et des 26 cellules de code révisées : réussie.
- Six tests ciblés exécutés, tous réussis : dossier de données explicite ; refus d’un dossier incomplet ; conservation des catégories et identifiants ; comparaison à des fenêtres calendaires manuelles avec un 25 décembre absent ; invariance aux ventes futures ; identité des variables entre les chemins réels de préparation en validation et en soumission.
- Les tests utilisent le code extrait du notebook lui-même, sur des données synthétiques. Ils n’entraînent pas de modèle et ne mesurent pas de performance prédictive réelle.
- Environnement des contrôles ciblés : pandas 2.2.3, NumPy 2.3.5. LightGBM n’est pas installé dans cet environnement de revue.
- Les cinq RMSLE regroupés recalculés à partir des scores de fenêtres arrondis concordent à quatre décimales avec les sorties enregistrées :

| Méthode | Recalcul sur valeurs arrondies | Sortie regroupée enregistrée |
|---|---:|---:|
| Moyenne simple | 0.464135 | 0.4641 |
| Moyenne logarithmique | 0.453895 | 0.4539 |
| LightGBM | 0.406817 | 0.4068 |
| LightGBM + calendrier | 0.406292 | 0.4063 |
| LightGBM + calendrier + statistiques | 0.397224 | 0.3972 |

- Les valeurs recalculées ci-dessus ne restituent pas la précision complète de l’exécution Kaggle ; elles contrôlent la cohérence de ses arrondis.
- Le modèle avec statistiques bat les variantes initiale et avec calendrier sur les trois fenêtres.
- Inspection visuelle du schéma généré et de l’importance des variables : figures lisibles ; aucun graphique de données n’a été recalculé ou modifié.


## Exécution et soumission du 21 novembre 2026

L’auteur a fourni une capture Kaggle de la version 1 indiquant une exécution complète réussie en **183,1 secondes**, sans accélérateur, avec **1,67 Mo** de sorties. La liste de sorties comprend `submission.csv` et `submission_amelioree.csv`, ainsi que les graphiques de comparaison et d’importance des variables.

Une seconde capture de la page de soumissions de la compétition indique **Complete**, avec le **score officiel RMSLE de 0,43477**, pour « Store Sales — Exploration et prévision des ventes – Version 1 ». La capture de résultat ne détaille pas le nom du CSV ; la documentation recommande `submission_amelioree.csv`, produit par le modèle retenu. Le score officiel est donc présenté comme résultat de la soumission du projet.

Le notebook du dépôt contient les mêmes étapes de modélisation et les sorties archivées, avec des ajouts de documentation, de chargement portable et de contrôles. L’exécution Kaggle observée n’est pas présentée comme une reproduction locale de cette révision exacte. Les contrôles locaux de publication compilent les cellules et vérifient les caractéristiques temporelles sur données synthétiques ; les CSV réels ne sont pas inclus dans ce dépôt.

Le résultat officiel est enregistré séparément dans `results/kaggle_submission.json`. Les tableaux internes conservent leur précision d’origine de quatre décimales. Aucune nouvelle performance prédictive n’a été calculée pendant la préparation de la publication.
