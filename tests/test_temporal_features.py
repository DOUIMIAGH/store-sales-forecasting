"""Contrôles ciblés sur le code du notebook, sans entraîner LightGBM."""
import ast
import json
import os
import tempfile
import unittest
from itertools import product
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = json.loads((ROOT / 'notebooks/store_sales_forecasting.ipynb').read_text())
SOURCES = {
    c['metadata']['audit_original_cell']: ''.join(c['source'])
    for c in NOTEBOOK['cells']
    if c['cell_type'] == 'code' and 'audit_original_cell' in c['metadata']
}


def charger_fonction(nom, namespace):
    for source in SOURCES.values():
        for node in ast.parse(source).body:
            if isinstance(node, ast.FunctionDef) and node.name == nom:
                exec(compile(ast.Module(body=[node], type_ignores=[]), '<fonction-notebook>', 'exec'), namespace)
                return namespace[nom]
    raise AssertionError(f'Fonction introuvable : {nom}')


ajouter_stats_ventes = charger_fonction('ajouter_stats_ventes', {'pd': pd, 'np': np})
STATS = ['moyenne_7j', 'moyenne_28j', 'ecart_type_28j']


def historique_factice(debut='2016-10-01', fin='2017-01-27'):
    jours = pd.date_range(debut, fin).difference(pd.DatetimeIndex(['2016-12-25']))
    frame = pd.DataFrame(list(product(jours, [1, 2], ['BEVERAGES', 'PRODUCE'])),
                         columns=['date', 'store_nbr', 'family'])
    frame['sales'] = ((frame['date'] - jours.min()).dt.days * 1.7
                      + frame['store_nbr'] * 100
                      + frame['family'].map({'BEVERAGES': 0, 'PRODUCE': 40}))
    frame['id'] = np.arange(len(frame))
    frame['onpromotion'] = 0
    return frame


class DisponibiliteTemporelle(unittest.TestCase):
    def setUp(self):
        self.complet = historique_factice()
        self.origine = pd.Timestamp('2017-01-03')
        self.passe = self.complet.loc[self.complet['date'] < self.origine].copy()
        self.lignes = self.complet.loc[
            self.complet['date'].between(self.origine, self.origine + pd.Timedelta(days=15)),
            ['id', 'date', 'store_nbr', 'family']
        ].copy()
        for col in ['store_nbr', 'family']:
            self.lignes[col] = self.lignes[col].astype('category')

    def test_les_ventes_futures_ne_changent_pas_les_variables(self):
        attendu = ajouter_stats_ventes(self.lignes, self.passe)
        disponible_complet = ajouter_stats_ventes(self.lignes, self.complet)
        modifie = self.complet.copy()
        modifie.loc[modifie['date'] >= self.origine, 'sales'] = 1e9
        apres = ajouter_stats_ventes(self.lignes, modifie)
        pd.testing.assert_frame_equal(attendu[STATS], disponible_complet[STATS])
        pd.testing.assert_frame_equal(attendu[STATS], apres[STATS])

    def test_fenetres_calendaires_avec_un_25_decembre_absent(self):
        resultat = ajouter_stats_ventes(self.lignes, self.passe)
        for row in resultat.itertuples():
            serie = self.passe.loc[
                self.passe['store_nbr'].eq(row.store_nbr)
                & self.passe['family'].eq(row.family)
            ].set_index('date')['sales']
            for jours, nom, minimum in [(7, 'moyenne_7j', 4), (28, 'moyenne_28j', 14)]:
                fenetre = pd.date_range(row.date - pd.Timedelta(days=16 + jours - 1),
                                        row.date - pd.Timedelta(days=16))
                valeurs = serie.reindex(fenetre)
                attendu = valeurs.mean() if valeurs.count() >= minimum else np.nan
                np.testing.assert_allclose(getattr(row, nom), attendu, equal_nan=True)
            fenetre = pd.date_range(row.date - pd.Timedelta(days=43), row.date - pd.Timedelta(days=16))
            valeurs = serie.reindex(fenetre)
            attendu = valeurs.std() if valeurs.count() >= 14 else np.nan
            np.testing.assert_allclose(row.ecart_type_28j, attendu, equal_nan=True)

    def test_categories_et_identifiants_sont_preserves(self):
        resultat = ajouter_stats_ventes(self.lignes, self.passe)
        self.assertEqual(len(resultat), len(self.lignes))
        self.assertTrue(resultat['id'].is_unique)
        pd.testing.assert_series_equal(resultat['id'], self.lignes['id'].reset_index(drop=True))
        for col in ['store_nbr', 'family']:
            self.assertEqual(resultat[col].dtype, self.lignes[col].dtype)

    def test_variables_de_validation_et_soumission_identiques(self):
        # Exécuter les cellules réelles de préparation, sans leur partie modèle.
        complet = historique_factice('2016-01-01', '2017-01-27')
        origine = pd.Timestamp('2017-01-12')
        namespace = {'pd': pd, 'np': np, 'df': complet, 'debut_valid': origine, 'rmsle': 0.0}
        exec(compile(SOURCES[7], '<preparation-validation>', 'exec'), namespace)
        donnees = namespace['donnees'].copy()
        feries = pd.DatetimeIndex(['2017-01-01'])
        donnees['ferie_national'] = donnees['date'].isin(feries).astype('int8')
        donnees_stats = ajouter_stats_ventes(donnees, complet)
        variables = ['store_nbr', 'family', 'onpromotion', 'jour_semaine', 'jour_mois',
                     'mois', 'temps', 'ventes_j16', 'ventes_j21', 'ventes_j28',
                     'ferie_national'] + STATS
        attendu = donnees_stats.loc[donnees_stats['date'] >= origine].copy()
        source = SOURCES[24].split('# 5. Entraîner')[0]
        tree = ast.parse(source)
        tree.body = [node for node in tree.body
                     if not isinstance(node, ast.ImportFrom) or node.module != 'lightgbm']
        with tempfile.TemporaryDirectory() as tmp:
            dossier = Path(tmp)
            lignes = complet.loc[complet['date'] >= origine].drop(columns='sales')
            lignes.to_csv(dossier / 'test.csv', index=False)
            lignes[['id']].assign(sales=0.0).to_csv(dossier / 'sample_submission.csv', index=False)
            namespace.update({
                'df': complet.loc[complet['date'] < origine].copy(),
                'chemin': dossier / 'train.csv', 'dates_feriees': feries,
                'donnees_stats': donnees_stats,
                'ajouter_stats_ventes': ajouter_stats_ventes,
            })
            exec(compile(tree, '<preparation-soumission>', 'exec'), namespace)
        obtenu = namespace['test_final']
        pd.testing.assert_frame_equal(
            attendu.sort_values('id')[variables].reset_index(drop=True),
            obtenu.sort_values('id')[variables].reset_index(drop=True),
        )


class ChargementDonnees(unittest.TestCase):
    def test_dossier_explicitement_indique(self):
        with tempfile.TemporaryDirectory() as tmp:
            dossier = Path(tmp)
            for nom in ['train.csv', 'test.csv', 'sample_submission.csv', 'stores.csv', 'holidays_events.csv']:
                (dossier / nom).touch()
            fonction = charger_fonction('trouver_dossier_donnees',
                                       {'Path': Path, 'os': os, 'RACINE_PROJET': dossier})
            with patch.dict(os.environ, {'STORE_SALES_DATA_DIR': str(dossier)}):
                self.assertEqual(fonction(), dossier.resolve())

    def test_un_dossier_incomplet_est_refuse(self):
        with tempfile.TemporaryDirectory() as tmp:
            dossier = Path(tmp)
            (dossier / 'train.csv').touch()
            fonction = charger_fonction('trouver_dossier_donnees',
                                       {'Path': Path, 'os': os, 'RACINE_PROJET': dossier})
            with patch.dict(os.environ, {'STORE_SALES_DATA_DIR': str(dossier)}):
                with self.assertRaises(FileNotFoundError):
                    fonction()


if __name__ == '__main__':
    unittest.main()
