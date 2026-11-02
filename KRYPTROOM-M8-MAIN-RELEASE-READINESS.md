# KRYPTROOM — M8 MAIN RELEASE READINESS

**Verdict PR20 → dev : BLOCKED. Verdict promotion → main : BLOCKED.**

Revue du **2 novembre 2026, 00:23 America/Toronto** (05:23Z).
Le travail validé est préservé et préparé dans des commits locaux. Aucun push,
merge, tag, release ou déploiement n'a été effectué. Aucun Groth16, transaction
blockchain ou nouveau calcul cryptographique n'a été lancé.

## 1. Commits préparés et SHA de PR20

- `dc380b3241ec78f3c4e5db10e609ab33630a3b7e` — implémentation finale, tests et
  sources canoniques : Signal V4, film complémentaire `/demo`, pointeur 50 %,
  How verrouillé et CTA aligné. 77 fichiers sélectionnés.
- `afd1eeda06cc3147fffc145dd0f81c21c7234e4d` — documentation, provenance et preuves
  visuelles sélectionnées. 85 fichiers ; livraison sélectionnée totale ~6,96 MiB.
- Un commit documentaire complémentaire enregistre le présent rapport et les
  brouillons de gouvernance ; il ne modifie pas l'application testée.

**Commits poussés : aucun.** Le SHA distant réel de
[PR20](https://github.com/e-sall/KryptRoom/pull/20) reste
`d2bc56ef55e9cadb319954a3dda4170f842039e6`. PR20 est OPEN, non draft, UNMERGED et
mergeable au sens Git. Cette propriété ne vaut pas approbation de sécurité/CI.
Branche conservée : `feat/m8-responsive-accessibility-final-qa`.

[Inventaire des commits](docs/m8/pr7/release-preparation/prepared-commits.json) ·
[fichiers retenus/exclus](docs/m8/pr7/release-preparation/publication-inventory.json) ·
[brouillon de mise à jour PR20](docs/m8/pr7/release-preparation/PR20-UPDATE-DRAFT.md).

## 2. Intégrité du travail approuvé

Signal V4 provient des sources du fondateur : SVG natif et CSS original,
viewBox 1000×508, animations 8 s, anneaux et nombres synthétiques inchangés.
La transcription JSX mécanique est comparée au DOM source ; le garde
anti-injection reste actif. Le CTA conserve texte, destination, style et hover ;
seuls son retrait responsive et ses espaces ont reçu le patch approuvé.

Le film reste sur `/demo`, après l'exploration technique préservée : 13 scènes,
12 clips, 92,4 s, SVG/horloge/curseur uniques. Le path du curseur est à 50 % autour
de sa pointe originale, sans changement de trajectoire/clic. La fin est maintenue,
sans boucle non approuvée. Les limites historiques 09→10 spécification seule et
Week 3 restent documentées, sans nouveau scénario.

How et toute sa feuille refinement.css sont byte-identiques au début de cette
mission : carte 600 px contenue dans le viewport, progression native 01→04→01,
aucun scroll hijacking. Aucun correctif graphique de release n'a été ajouté.
Les changements de cette préparation portent sur des attentes navigateur devenues
obsolètes et le rangement des preuves, pas sur les designs verrouillés.

Sauvegarde intégrale pré-commit :
`work/release-preserved-20261102T045837Z/workspace.zip`, 242 fichiers vérifiés
contre son manifeste. La sauvegarde du film rejeté initial reste également intacte.
Les sources originales et leurs 39 empreintes ont été conservées. Une ligne
blanche avec espaces dans le HTML original 01→02 est conservée pour respecter
son SHA : elle est la seule exclusion du contrôle local de whitespace, remplacée
pour ce fichier par une vérification stricte du manifeste. Aucun contrôle CI,
audit ou test de sécurité n'a été désactivé.

Builds, dépendances, fichiers générés, secrets, anciennes itérations rejetées,
doublons, vidéos lourdes et captures de raccord exhaustives ne sont pas committés.
Ils ne sont pas détruits. Les vidéos restent dans l'archive de revue ; publier
des artifacts après autorisation plutôt que des blobs Git de plusieurs Mo.
[Politique de sélection](docs/m8/pr7/RELEASE-ARTIFACTS.md).
Le scan de motifs de clés/tokens sur les fichiers texte sélectionnés ne signale
rien ; il ne constitue pas une certification de tout l'historique Git.

## 3. QA locale et CI

Feature préparée :

- **116 unitaires/composants : PASS.**
- **Build 72 pages et TypeScript : PASS.**
- **Suite Chromium complète : 205 PASS, 2 exclusions héritées, 0 échec, 0 flaky.**
- **WebKit final : 10 PASS** sur Signal, film, hotspot, responsive et How.
- Le film complet avait aussi été lu et enregistré en temps réel : 92 400 ms
  atteints et maintenus, zéro erreur ; le build public n'expose pas l'API de seek.

[Résumé Chromium](docs/m8/pr7/release-preparation/frontend-playwright-summary.json) ·
[résumé WebKit](docs/m8/pr7/release-preparation/frontend-webkit-summary.json).

Le dernier lint a réussi avant l'expiration de M8-SEC-001. Les adaptations finales
des tests navigateur n'ont **pas** reçu un nouveau lint : ESLint 9 n'a plus été
exécuté après l'échéance. Le lint du HEAD final reste donc un gate ouvert.

Les huit workflows PR de l'ancien SHA distant `d2bc56e` sont toujours SUCCESS,
dont [M8 Web Foundation](https://github.com/e-sall/KryptRoom/actions/runs/41284509651).
**Aucune CI GitHub ne valide les nouveaux commits locaux ou le candidat.** Ne pas
leur attribuer ces anciens résultats. Après autorisation du push, attendre les
checks du SHA réellement publié, puis refaire la revue de sécurité au moment du merge.

Environnement local : Node 24.12.0, npm 11.6.2, dépendances déjà présentes.
Le CI conserve ses versions épinglées. Aucune installation propre Linux ou
équivalence d'environnement CI n'est prétendue par les seuls tests locaux.

## 4. Sécurité et disposition

**M8-SEC-001 : EXPIRÉE**, 1er novembre 2026 à 23:59 Toronto
(`2026-11-02T04:59Z`). Elle couvre uniquement ESLint 9 EOL et n'a pas été renouvelée.
Le push qui déclencherait ce lint et toute nouvelle exécution du linter restent
bloqués. Les unitaires, builds, audits et tests navigateur exécutés ensuite
n'invoquent pas ESLint ; ils utilisent les sources locales de confiance.

[ESLint](https://eslint.org/version-support/) confirme v9 EOL et v10 actuelle.
La lecture officielle npm trouve eslint 10.14.0 / config-next 16.4.3, mais les
peers React 7.37.5, JSX-a11y 6.10.2 et import 2.32.0 excluent encore ESLint 10.
Une migration complète compatible n'est pas démontrée ; aucun package n'a été forcé.

**M8-SEC-002 : fenêtre encore active**, jusqu'au 4 novembre 2026 à 02:00:41
Toronto (`07:00:41Z`), limitée aux chemins de développement/build de confiance.
Elle ne couvre ni merge ni production, et ne renouvelle pas M8-SEC-001.
La mission actuelle autorise la préparation et un push conditionnel du travail
final ; elle ne renouvelle pas les dates et n'accorde pas un merge implicite.

Audit rafraîchi : **16 findings modérés propagés depuis un seul avis minimatch ;
production 0**. Aucun nouvel avis matériel détecté. minimatch 3.1.5/10.2.6 et le
mécanisme Next de traçage de build restent non résolus. Aucun chemin visiteur
démontré n'est pas une preuve d'inexploitabilité.
[Avis officiel](https://github.com/advisories/GHSA-g3hv-75wg-m249) ·
[audit complet](docs/m8/pr7/signal-integration/release-audit.json) ·
[audit production](docs/m8/pr7/signal-integration/release-audit-production.json).

Traitement proposé, **non approuvé** : migration supportée et remédiation complète
quand compatibles, ou décision fondatrice temporaire datée renouvelant seulement
le périmètre nécessaire. Si minimatch demeure au merge, disposition explicite
pour ces merges de code sans déploiement, avec une échéance. Aucun risque accepté
par l'agent. [Proposition formelle](docs/m8/pr7/release-preparation/SECURITY-DISPOSITION-PROPOSAL.md).

Les métadonnées GitHub affichent `protected:false` et contrôles non imposés pour
dev/main, avec liste de rulesets vide. L'endpoint administratif détaillé a renvoyé
403 à l'intégration. Aucun réglage n'a été changé. Les gates humains et les checks
restent obligatoires dans cette mission, même sans enforcement serveur observé.
Le dépôt reste **public**, branche par défaut **main**.

## 5. PR20 → dev

**Non fusionnée. BLOCKED**, pour quatre raisons : M8-SEC-001 expirée, lint final
non exécuté, absence de CI hébergée sur les nouveaux commits, et M8-SEC-002 ne
couvrant pas le merge. L'approbation explicite du fondateur pour PR20→dev reste
également requise. Aucun contournement par une branche de promotion.

`origin/dev` reste `8e8d8349db565278a866bd82f743f03fd1ee8c35`.
Les anciennes branches locales main/dev étaient en retard ; l'analyse utilise
les références origin rafraîchies, sans checkout destructif ni déplacement de ces branches.

## 6. Réconciliation dev/main et candidat exact

`origin/main` : `1715b504e2041127056127ab5236a3248195a234`.
Ancêtre commun : `9027db9567ddd92f576ade33f7a6315461b6fdca`.
**7 commits uniques main, 64 uniques dev.**
[Inventaire exact](docs/m8/pr7/release-preparation/branch-analysis.json).

La seule différence ajoutée du côté main depuis cet ancêtre est le workflow
manuel M7 `public-chain-anchor-live.yml`. Son blob est déjà identique dans dev :
`026b45d71fe3dbf2ad26fea730f87c2ab7728d93`.
La simulation de merge est sans conflit et donne exactement l'arbre dev
`05a8606571e91975d370bd97dfdfff44f2acb082`. Sa protection par confirmation manuelle
est conservée ; aucun dispatch n'a eu lieu.

Branche **locale seulement** : `release/m8-main-candidate-20261102`.
Candidat : **`d6a7765b64afdffacf486a5b4bc10ffa156f7a6b`**, parents main et feature
`afd1eed`, arbre **`ceb41f62aa395ba434686fe1e864d6b2876a8576`**, exactement identique
à la feature préparée. Il réconcilie l'ascendance sans changer le contenu.

Ce candidat est un prototype de promotion, pas une fusion dans main/dev ni une
PR prête à contourner l'approbation de dev. Il précède le présent commit documentaire.
Après la fusion autorisée de PR20, le recréer à partir du **vrai dev fusionné** et
du main alors courant, puis publier/valider son SHA avec les gates satisfaits.

## 7. Tests du candidat et compatibilité Core

Depuis une extraction du commit exact `d6a7765` : **116 unitaires, build 72 pages,
TypeScript et 15 tests navigateur ciblés : PASS**, dont homepage, mobile,
How intégralement visible, progression, exploration technique et film de production.
[Journal synthétique](docs/m8/pr7/release-preparation/promotion-validation.json).

Le premier build de l'extraction a échoué sur la résolution hermétique Turbopack
d'une jonction node_modules extérieure. La copie des mêmes dépendances à
l'intérieur de l'extraction a corrigé l'environnement, sans installation ni
modification du code/config. Une tentative navigateur a été interrompue pour
corriger le chemin d'artefacts ; le rerun isolé est entièrement vert.

Les arbres Git `engines`, `packages`, `tests`, `chain` et `.github` du candidat
sont identiques à ceux du dev certifié. La promotion ne change donc aucun Core,
fixture ou contrôle CI. [Empreintes](docs/m8/pr7/release-preparation/core-tree-integrity.json).
C'est une preuve de préservation de contenu, pas une nouvelle certification
CHEETAH/FHE/Groth16. Aucune QA cryptographique déjà certifiée n'a été relancée.

## 8. Diff, PR de promotion, rollback et version

[Diff final : inventaire main → candidat](docs/m8/pr7/release-preparation/promotion-files.txt).
Commandes locales reproductibles :

```text
git diff --stat 1715b504e2041127056127ab5236a3248195a234 d6a7765b64afdffacf486a5b4bc10ffa156f7a6b
git diff 1715b504e2041127056127ab5236a3248195a234 d6a7765b64afdffacf486a5b4bc10ffa156f7a6b
```

La promotion comprend l'historique M3–M7 déjà validé dans dev, puis les sept PR
frontend M8. L'interface reste un aperçu synthétique déconnecté, sans auth multi-
entreprise de production, connexion KryptNodes, MPC/FHE live, IA live ou nouveau
modèle de sécurité. Le SVG mobile garde un équivalent textuel lisible ; le film
utilise son fallback statique sur petit écran/reduced motion. Aucun M9 ajouté.

**PR de promotion non ouverte** : sa branche n'est pas poussée, les gates et la
fusion dev manquent. [Brouillon prêt pour revue](docs/m8/pr7/release-preparation/PROMOTION-PR-DRAFT.md).

Rollback proposé : PR de revert du **futur vrai merge de promotion**, avec parent
principal main, puis contrôles/revue. Aucun reset forcé. Ne jamais supprimer des
RoomStates ni altérer les preuves, receipts ou ancrages historiques pour revenir
sur une publication frontend. Aucun rollback exécuté.

Version proposée : **v0.8.0-preview.1**, sous réserve d'approbation et d'une nouvelle
vérification de disponibilité. Aucun tag local/distant n'était présent à la lecture.
Aucun tag ou objet release créé ; aucune modification de licence.

## 9. Décisions encore nécessaires

1. Corriger ou renouveler explicitement M8-SEC-001 avant lint/push ; rien n'est renouvelé ici.
2. Après un push permis, obtenir les checks du nouveau SHA et réévaluer la sécurité.
3. Disposition formelle de minimatch pour merge si non corrigé, puis autorisation PR20→dev.
4. Régénérer la promotion depuis dev réel, valider son SHA et obtenir l'autorisation main.
5. Autorisations distinctes pour tout tag/release et tout déploiement.

Le working tree suivi est destiné à être propre après le commit de ce rapport ;
des fichiers non suivis exclus et sauvegardés restent volontairement présents.
La branche PR20 est en avance localement, pas publiée. Le site local reste
[homepage](http://127.0.0.1:3002/) et [démo](http://127.0.0.1:3002/demo).
