# Provenance des résultats

Les deux CSV de validation sont extraits des tableaux HTML enregistrés dans la cellule de comparaison finale du notebook original, exécutée avec le compteur 22. Les valeurs étaient arrondies à quatre décimales : aucune décimale supplémentaire n’est reconstituée.

Les trois fenêtres ont chacune 28 512 prévisions, soit 85 536 au total. La pondération des RMSLE au carré permet de retrouver les scores regroupés à l’arrondi affiché.

Après une nouvelle exécution, le notebook exporte des tableaux à précision complète dans `/kaggle/working/` ou `outputs/`. Remplacer alors ces deux CSV et mettre à jour les résultats du README si nécessaire.

## Résultat officiel Kaggle

`kaggle_submission.json` consigne le résultat de la soumission acceptée le 21 novembre 2026 : **RMSLE 0,43477**, statut **Complete**. Il a été relevé sur la capture de la page de soumissions fournie par l’auteur. Ce résultat porte sur le test de la compétition ; il est distinct du RMSLE de validation interne de 0,3972. Le nom du CSV soumis n’est pas visible sur cette capture.
