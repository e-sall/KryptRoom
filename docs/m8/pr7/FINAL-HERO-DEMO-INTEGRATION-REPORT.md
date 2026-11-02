# KRYPTROOM M8 — FINAL HERO & DEMO INTEGRATION REPORT

> Résultats de l’intégration locale avant préparation des commits. La publication
> et les gates actuels sont régis par KRYPTROOM-M8-MAIN-RELEASE-READINESS.md.
> Les enregistrements complets et captures de raccord restent archivés hors Git ;
> voir RELEASE-ARTIFACTS.md. Le CTA a ensuite reçu son patch local d’alignement.


**READY FOR FOUNDER FINAL VISUAL REVIEW — intégration locale, non publiée.**

## Aperçus réels

- Homepage : **http://127.0.0.1:3002/** ; [accès direct à The Signal](http://127.0.0.1:3002/#product-demo).
- Démo technique préservée : **http://127.0.0.1:3002/demo** ;
  [film complémentaire](http://127.0.0.1:3002/demo#product-walkthrough).
- [Captures finales des deux pages, Chromium et WebKit](signal-integration/page-captures/README.md).
- Deux boucles CSS natives de V4 enregistrées (vidéo conservée dans l’archive locale, voir RELEASE-ARTIFACTS.md).
- Lecture réelle du film entier (vidéo conservée dans l’archive locale, voir RELEASE-ARTIFACTS.md),
  [journal de lecture](signal-integration/playback/result.json).

Le serveur existant utilise les dépendances présentes et reste lié à 127.0.0.1.
Relance si nécessaire, depuis le checkout actuel, dans `apps/web` :
`npm run dev -- --port 3002`. Aucun déploiement public.

## 1. Source canonique V4 et fidélité

Archive fournie : `KryptRoom_The_Signal_V4_Source.zip`, SHA-256
`91f2b805f4551d836095660a8bf3b6ce10a5f00492b18eff49969529a260fb9b`.
Les trois fichiers originaux sont conservés sans modification dans
[signal-source](signal-integration/signal-source/). Le HTML contient le code
complet de la référence `kryptroom-the-signal-v4-lean` ; le nom de bloc n'est pas
un identifiant littéral dans le ZIP. Sa véritable racine est `#kr-signal-v4`.
Le SVG natif est également fourni, avec le viewBox `0 0 1000 508`.
Empreintes exactes : [provenance.json](signal-integration/provenance.json).

Intégration depuis le HTML AppBlock, sans reconstruction visuelle. Le garde
anti-injection existant interdit le HTML brut dans l'application : une première
approche a été rejetée par ce test et retirée. Les balises ont ensuite été
transcrites mécaniquement en JSX, avec uniquement les noms d'attributs React.
Le test compare récursivement tous les éléments SVG, attributs et textes avec
le DOM de la source originale, et vérifie le CSS original textuellement.
Le contrôle anti-injection est conservé intégralement, sans exception.

Composition, textes, couleurs, logo, anneaux (370/430,300,r55), point (400,300),
pistes 346 et remplissages 173/115.33/57.67 sont conservés. Les quatre animations
`kr4rings`, `kr4dot`, `kr4metric`, `kr4bars` gardent leurs keyframes, durée 8 s,
courbes et boucle infinie d'origine. Les trois barres partagent leur groupe
animé unique. Les valeurs et styles aux bornes de boucle sont continus ; aucun
écran n'est remplacé. Autoplay silencieux, sans curseur, lecteur ou navigation
dans le showcase. Le lien `/demo` est placé à l'extérieur de cette composition.

Le conteneur garde le ratio 1000/508 et une largeur maximale de 1000 CSS px.
Desktop : cadrage sous la navbar vérifié aux quatre tailles demandées.
Tablette et mobile : aucune déformation/coupe/scrollbar horizontale. Le SVG
reste inchangé ; ses petits textes deviennent naturellement petits à 320–390 px.
Un équivalent textuel lisible est ajouté **hors du SVG** sur ces écrans ; aucune
nouvelle composition mobile prétendument verrouillée n'est annoncée.
Reduced motion affiche les remplissages finaux statiques grâce au CSS fourni.

Les 12 signaux sont des données synthétiques illustratives, jamais une
cardinalité PSI réelle ou un calcul effectué dans le navigateur.

## 2. Film restauré dans /demo

La sauvegarde `work/rejected-p12-20261102T025508Z/snapshot.zip` reste intacte,
SHA-256 `d72309468b1f0eb4a9ff56248eda3e72c05375aabaeba335eb8190133f1086c4`.
Ses 214 fichiers ont été revérifiés avant récupération. Les 39 empreintes du
manifeste original de provenance ont également été revérifiées dans les copies
restaurées. [Sources originales](signal-integration/film-source/manifest.json).
Le montage HTML V1 rejeté n'a pas servi de base.

Le film devient **KryptRoom · Product Walkthrough**, après l'expérience technique
existante. Un lien de découverte figure en tête de `/demo`. Explore/Presentation,
sélection de S2 et inspection de ses états restent fonctionnels. Le composant
`interactive-demo.tsx` est strictement identique à celui du début de mission.

13 scènes, 12 clips, horloge nominale de 92 400 ms, même surface SVG 1120×620,
mêmes trajectoires, clics et renderers. Une horloge globale et un curseur uniques.
Autoplay à l'entrée dans le viewport, arrêt hors écran/onglet masqué, reprise
sans rattrapage. Aucun contrôle public, son, lecteur vidéo ou exécution réelle.
La dernière image est maintenue ; aucune boucle 13→01 inventée.

La récupération conserve les limites déjà documentées : 09→10 V2 reste
l'adaptation explicite de spécification du film préservé, le source original
exact n'ayant pas été récupéré ; la divergence Week 3 entre résumé et détail
reste inchangée. Aucun nouveau scénario ou raccord n'est introduit.
Sur petits écrans <=700 px et reduced motion, le fallback statique préservé
remplace le film détaillé ; aucune certification de lecture mobile complète.

### Curseur exactement à 50 %

Seul le path vectoriel du pointeur reçoit
`translate(1 1) scale(.5) translate(-1 -1)`. La pointe originale est (1,1) :
cette transformation la conserve exactement, avec un facteur .5 sur X et Y.
La translation du calque curseur, les positions/timings de clic et les ripples
originaux sont inchangés. Le test navigateur vérifie la matrice et le point fixe,
plus le clic WEEK 1 à (362,474). Les quinze clics source, changements de workspace,
55 échantillons de raccord et recherches temporelles dans les deux sens passent.

## 3. Validations exécutées

- Lint sans avertissement, typecheck, build de production **72 pages** : PASS.
- **116 unitaires/composants** : PASS, dont fidélité SVG/CSS et garde anti-injection.
  La première exécution parallèle a subi des délais dépassés sous contention
  locale ; la suite entière passe avec un worker, sans augmenter les délais.
- **36 scénarios Chromium sur le build de production** : 33 homepage/marketing
  desktop/tablette/mobile et 3 film. Absence de l'API de revue en production,
  suspension, reprise et maintien à 92 400 ms vérifiés. Fallback mobile vérifié.
- **20 scénarios locaux Chromium/WebKit** validés avec reruns ciblés : source V4,
  timeline partagée, boucles, reduced motion, responsive, exploration technique,
  curseur, film et non-régression How. La suspension du film maintenant placé
  en bas de `/demo` est testée en revenant en haut de page, réellement hors écran.
  Une précision flottante WebKit de 0.000076 px est tolérée sous 0.001 px, sans
  changement de largeur CSS ni contournement de débordement.
- Lecture intégrale **réelle**, sans seek ni horloge simulée : douze clips vus,
  fin 92 400 ms, image finale maintenue, zéro erreur navigateur. Mesure globale
  95.827 s incluant navigation/polling/maintien, distincte de la durée du film.
- [Captures représentatives du film](signal-integration/film-captures/README.md), dont treize
  scènes et cinq images autour de chacune des onze frontières internes de clips.
  [16 captures finales des pages](signal-integration/page-captures/README.md).
- Axe sur les deux nouvelles surfaces et contrôles de page marketing : zéro
  violation détectée dans les périmètres exécutés. Les tests de production
  conservent les contrôles GET local uniquement, absence d'API/RPC et de stockage.

Pas de Firefox, device physique, certification Safari/WCAG complète, suite
cryptographique lourde, Groth16 ou transaction blockchain.

## 4. How It Works verrouillé et préservation

`how-it-works.tsx` et **tout refinement.css** sont byte-identiques au début de
cette mission ; leurs empreintes figurent dans provenance.json. Les différences
visibles par rapport au HEAD Git publié sont les corrections locales approuvées
précédemment, préservées ici sans modification. Les tests dans les deux moteurs
revérifient la carte 600 px entièrement sous la navbar, aux quatre tailles desktop,
les bords/rectangles de texte et SVG, la progression 01→04→01 à la molette seule,
la hauteur constante, et la sortie vers Technology. Reduced motion à 640 px de
hauteur, clavier et mobile passent. Aucune réintroduction des grands blocs.

M1–M7, fixtures, preuves/receipts/ancrage historiques, CI, dépendances/lockfile,
logo partagé, portrait et scènes de la démo technique sont inchangés.

## 5. Audits, gates et GitHub

[Audit complet](signal-integration/signal-audit.json) : **16 findings modérés**,
tous propagés depuis GHSA-g3hv-75wg-m249. [Production](signal-integration/signal-audit-production.json) : **0**.
minimatch 3.1.5/10.2.6 et le mécanisme Next de build tracing restent non corrigés.
Aucun chemin visiteur démontré ne constitue pas une preuve d'inexploitabilité.
Pas de dépendance installée/forcée, suppression d'audit, permission CI changée
ou nouveau risque accepté. Sources de build : ZIP fondateur inspecté et sauvegarde
déjà inspectée, empreintes vérifiées ; aucun build de contribution non fiable.

M8-SEC-001 reste ESLint 9 EOL seulement, jusqu'au **1er novembre 2026 23:59
America/Toronto** (2 novembre 04:59Z). M8-SEC-002 reste indépendante, jusqu'au
**4 novembre 02:00:41 Toronto** (07:00:41Z). Aucune prolongation implicite.
La fenêtre temporelle était encore valide à la revue 23:40:44 Toronto.

**Publication conservée en attente de disposition explicite.** Le document
[M8-SEC-002](M8-SEC-002.md) autorise expressément « publication of the preserved
V7.2 work ». Cette mission introduit maintenant deux nouvelles surfaces : cette
autorisation de publication n'est pas élargie implicitement. Le développement
local et sa validation suivent l'autorisation explicite de cette mission.
Avant publication, confirmer la couverture de cette intégration et réévaluer
M8-SEC-001 ; toute opération dépendante après son expiration exige une décision
distincte. Pas de renouvellement ou acceptation de risque par l'agent.

GitHub vérifié : [PR20](https://github.com/e-sall/KryptRoom/pull/20) **OPEN,
UNMERGED, mergeable**, branche feat/m8-responsive-accessibility-final-qa, base dev
`8e8d8349db565278a866bd82f743f03fd1ee8c35`. HEAD local/distant inchangé :
`d2bc56ef55e9cadb319954a3dda4170f842039e6`.
Travail local volontairement non committé, sauvegardé avant intégration dans
`work/before-signal-20261102T042250Z/`. Aucun nouveau HEAD publié ou résultat CI
GitHub ne peut donc être attribué à cette intégration. Main/dev non modifiées.

## 6. Fichiers et décisions restantes

Application : `signal-artwork.tsx`, `signal-v4-source.ts`, `signal-v4.tsx`,
`signal-v4.css`, montage dans home-page.tsx ; restauration de `cinematic/` avec
nouveau libellé/ancre et pointeur réduit ; montage complémentaire dans
`src/app/[section]/page.tsx`. Le style du lien de découverte garde une cible de
44 px hors de la surface cinématique. Aucun changement du scénario.

Tests : nouveaux signal-v4/cinematic unitaires, browser signal-integration,
cinematic.review et walkthrough ; homepage/V4/V5 adaptés au contrat V4 ; ordre
des sections actualisé dans home.test.tsx. Contrôles confidentialité/accessibilité
préservés. Configuration locale de revue séparée, aucune modification de workflow.
Documentation, preuves visuelles, sources et empreintes dans signal-integration/,
CHANGELOG, TODO et décisions. Fichiers générés préexistants conservés ; Next peut
actualiser next-env.d.ts pour son mode dev/build, sans restauration destructive.

Restent la revue visuelle des deux pages, la disposition de publication sous
exception et une autorisation distincte pour toute fusion. V4 est DESIGN LOCKED
par décision fondateur ; son intégration et le film sur `/demo` restent à voir.
Ni le film continu ni M8 ne sont déclarés définitivement approuvés ou terminés.

## CTA final approuvé

Le lien extérieur reste exactement « Explore the full product walkthrough → »
vers `/demo#product-walkthrough`. Grille responsive avec retrait 5 % (50 px au
format desktop 1000 px), contenu aligné en haut, marge supérieure supprimée et
marge inférieure réduite à 24 px. Aucune modification du SVG ou de How.
[1440 px](signal-integration/cta-patch/after-1440.png) · [mobile](signal-integration/cta-patch/after-390.png).
