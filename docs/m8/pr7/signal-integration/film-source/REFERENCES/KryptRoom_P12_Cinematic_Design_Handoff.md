# KRYPTROOM · PROTOTYPE 12
## FINAL CINEMATIC DESIGN HANDOFF · REVIEW DRAFT (NON DESIGN LOCKED)

Date : 2026-11-01. Destinataire : `02 — KryptRoom Build`.

**DÉCISION : film commercial muet, 100 % automatique, homepage, boucle et suspension hors viewport. Aucun bouton, timeline, sélecteur ni clic visiteur.**

**STATUT HONNÊTE : les 13 compositions et 12 transitions ont été validées individuellement. Le film unifié n'est PAS approuvé ni testé dans cette livraison. Le premier HTML `KryptRoom_Cinematic_Demo_13_Scenes.html` était un slideshow rejeté et doit être ignoré.**

## 1. Orchestration continue

Le film a **une horloge globale** et **une surface SVG stable** (`viewBox="0 0 1120 620"`). La barre de navigation, le logo original et le chrome applicatif ne disparaissent pas entre les clips. Chaque événement est déclenché par le curseur produit : mouvement Bézier slow-fast-slow, hover, micro-pause, press/click, retour visuel, statut de l'action, modification progressive du contenu. Aucun écran ne remplace brusquement un précédent uniquement parce que son numéro de scène change.

Les transitions approuvées sont des **plans séquentiels**. Ne pas les rejouer avec 12 `requestAnimationFrame` indépendants : dissocier chaque `render(localT)` de son horloge, retirer uniquement les contrôles d'évaluation, conserver les SVG et keyframes, puis leur fournir `localT = globalT - offset`. Ne pas régénérer une nouvelle UI approximative.

**Durée nominale des 12 clips : 92.4 secondes (01:32.4).** Elle ne comprend ni le maintien de conclusion ni un raccord de boucle. Cette durée est la somme des durées codées dans les sources validées. Il ne faut pas reprendre la durée 1:31.5 annoncée pour le montage rejeté.

### Chronologie exacte de référence

| Clip | Version | Fenêtre globale | Durée | Source identifiée | Statut |
|---|---|---|---:|---|---|
| 01→02 | V2 | 00:00.0–00:06.7 | 6.7s | `krmotion0202v2` | Source préservée |
| 02→03 | V1 | 00:06.7–00:15.3 | 8.6s | `kr-transition-0203-v1` | Source préservée |
| 03→04 | V1 | 00:15.3–00:22.5 | 7.2s | `kr-motion-0304-v1` | Source préservée |
| 04→05 | V1 | 00:22.5–00:31.2 | 8.7s | `kr-motion-0405-v1` | Source préservée |
| 05→06 | V1 | 00:31.2–00:39.3 | 8.1s | `kr-motion-0506-v1` | Source préservée |
| 06→07 | V1 | 00:39.3–00:47.8 | 8.5s | `kr-motion-0607-v1` | Source préservée |
| 07→08 | V1 | 00:47.8–00:56.3 | 8.5s | `kr-transition-0708-v1` | Source préservée |
| 08→09 | V1 | 00:56.3–01:04.9 | 8.6s | `kr-motion-0809-v1` | Source préservée |
| 09→10 | V2 | 01:04.9–01:08.2 | 3.3s | `kr-0910-micro-v2` | **Référence chat seule** |
| 10→11 | V2 | 01:08.2–01:17.6 | 9.4s | `kr-cinematic-1011-v2` | Source préservée |
| 11→12 | V2 | 01:17.6–01:24.8 | 7.2s | `kr-motion-1112-v2` | Source préservée |
| 12→13 | V2 | 01:24.8–01:32.4 | 7.6s | `kr-motion-1213-v2` | Source préservée |

**Événements à préserver** :

- **01→02** : Demo profile → sélection de Manufacturer ; mouvement `(803,436) → (80,583) → (126,477)` ; menu contextuel, clics vers 2,12 s et 3,85 s, navigation vers ~4,17 s.
- **02→03** : `Create Room` vers 1,90 s, invitation envoyée ; sélection de Logistics Partner via le workspace switcher vers 5,80 s ; scène invitation dès ~6,39 s.
- **03→04** : `Accept & open Room` vers 1,96 s ; entrée dans Room ~2,70–3,03 s ; quatre datasets `Not linked` ; Logistics Partner action principale.
- **04→05** : clic `Connect local datasets` vers 2,04 s ; protection locale distincte Manufacturer/Logistics, une ligne hexadécimale par entrée, police de 10 px ; au dernier frame, Manufacturer protégé et Logistics toujours en progression.
- **05→06** : finalise les deux protections ~2,83 s ; Computations devient accessible ~3,10 s ; navigation de `(969,451)` à `(92,293)` ; clic ~5,32 s ; Library affiche Supply Chain Risk sélectionné, Delivery Performance et Shared Coverage disponibles.
- **06→07** : clic `Run private analysis` vers 1,94 s, progression des états illustratifs ; à la fin, compute en cours, output `Pending`.
- **07→08** : computation synthétique 67→100 %, authorization policy check entre ~2,59 et 3,57 s ; clic Analytics ~5,75 s ; Gallery a **une seule analyse Ready** et **deux Not run**, **aucun KPI dans la galerie**.
- **08→09** : curseur `(97,344) → (325,490)` ; clic `Open dashboard` ~2,01 s ; 12 signaux, 6/4/2, courbe hebdomadaire et barres ; curseur finit **(930,511)** au-dessus de `Open detailed dashboard`.
- **09→10 V2** : **micro-interaction 3,3 s, PAS de nouvelle page** ; curseur (930,510), clic ~0,74 s ; seul le panneau droit devient `Risk details`, Production `6 of 12 · 50%`, Manufacturer 2 inputs, Logistics Partner 2 inputs, puis CTA `Ask AI about these risks` ; les KPI et le graphique à gauche restent immobiles. Source `kr-0910-micro-v2` dans la présente conversation, non exportée en copie portable.
- **10→11 V2** : clic Ask AI ~1,14 s ; vrai changement d'espace ~1,60–1,95 s ; saisie entre 2,30 et 5,50 s de la question **en une seule ligne**, clic Send ~6,38 s ; scène se termine sur `AI working`, jamais sur une réponse prématurée.
- **11→12 V2** : traitement AI → **large panneau de lecture** à ~1,70–2,18 s ; une conclusion, trois cartes (`6/12 50%`, `4/12 33%`, `2/12 17%`), trois recommandations espacées, provenance discrète en pied ; aucune zone étroite ou défilement artificiel.
- **12→13 V2** : curseur `(680,410) → (362,474)`, **clic directement sur `01 · WEEK 1` ~2,05 s**. La carte morph vers le détail ~2,37–3,37 s ; arrivée dans `From insight to action.`, trois colonnes/timeline, `Review action` sur chacune, aucune approbation, assignation ou exécution.

## 2. Inventaire des treize scènes

| Scène | Version visuelle | Rôle | Source récupérée |
|---|---|---|---|
| 01 | V6 monochrome | Native SVG Scene01 | `SOURCE_MESSAGES/SCENE_01_V6.svg` |
| 02 | V1 | Create a Room | `SOURCE_MESSAGES/SCENE_02_V1.txt` |
| 03 | V1 | Invitation Received | `SOURCE_MESSAGES/SCENE_03_V1.txt` |
| 04 | V1.2 | Joined Room / buttons corrected | `SOURCE_MESSAGES/SCENE_04_V1_2.txt` |
| 05 | V1.2 | Local protected inputs / one-line hex | `SOURCE_MESSAGES/SCENE_05_V1_2.txt` |
| 06 | V1 | Analysis Library | `SOURCE_MESSAGES/SCENE_06_V1.txt` |
| 07 | V1 | Private computation in progress | `SOURCE_MESSAGES/SCENE_07_V1.txt` |
| 08 | V1 | Analytics Gallery | `SOURCE_MESSAGES/SCENE_08_V1.txt` |
| 09 | V1 | Risk overview | `SOURCE_MESSAGES/SCENE_09_V1.txt` |
| 10 | V1 static overridden by T09_10 V2 | Risk detail | `SOURCE_MESSAGES/SCENE_10_REFERENCE_V1.txt` |
| 11 | V1.1 static overridden by T10_11 V2 | Ask AI | `SOURCE_MESSAGES/SCENE_11_REFERENCE_V1_1.txt` |
| 12 | V1 static overridden by T11_12 V2 | AI recommendation summary | `SOURCE_MESSAGES/SCENE_12_REFERENCE_V1.txt` |
| 13 | V1 static overridden by T12_13 V2 | From insight to action | `SOURCE_MESSAGES/SCENE_13_REFERENCE_V1.txt` |

**Règle de priorité des états finaux :** les scènes 10, 11, 12 et 13 doivent utiliser l'état visuel d'arrivée de leurs transitions approuvées les plus récentes, pas leur ancien prototype statique V1. Scène 04 = correction V1.2 (bouton Logistics primaire). Scène 05 = V1.2 (hex à taille fixe sur une ligne). Scène 01 = fichier SVG native V6 monochrome, conservé sans altération.

## 3. Invariants graphiques

- Canonical `viewBox`: `0 0 1120 620`, sans zoom de caméra.
- Chrome : fond `#181818`, sidebar `#1D1D1E`, panneaux `#252526`, texte `#F1F0EB`, accent bleu-gris `#9DB7CB`.
- Logo asymétrique en trois paths, géométrie originale inchangée :

```svg
<g transform="translate(19 12) scale(1.22)">
  <path d="M1 6 L7 3 L7 27 L1 24 Z" fill="#F1F0EB"/>
  <path d="M9 12 L20 3 L16 12 L9 19 Z" fill="#A6A7A1"/>
  <path d="M9 19 L16 12 L21 26 L14 23 Z" fill="#747671"/>
</g>
```

- Dans chaque navigation, seul le **contenu concerné** change après événement produit. La navigation latérale et le curseur ne sont pas redessinés à chaque scene marker.
- Cartes, positions, typographie, micro-animations, durées et courbes sont importées de la source de transition. Les petits ajustements autorisés sont **des patches de raccord**, jamais une réinterprétation des scènes validées.

## 4. Raccords identifiés et correctifs obligatoires

**Pourquoi la V1 était un slideshow :** elle assemblait des générateurs d'écran et les remplaçait à des bornes temporelles. L'UI n'avait pas de continuité d'attributs SVG, les interactions précédentes étaient remplacées par des transitions d'opacité génériques, les trajectoires de curseur n'étaient pas orchestrées d'un clip à l'autre.

| Raccord | Problème constaté dans les sources | Patch à proposer pour QA |
|---|---|---|
| 01→02 / 02→03 | le curseur finit vers `(126,477)` mais 02→03 commence `(862,464)` | relier durant la pause initiale de 02→03 par un trajet courbe, sans couper la page ni changer les clics de Room Creation |
| 02→03 / 03→04 | fin `(127,471)`, début `(953,439)` | déplacement crédible pendant la fin du switch workspace / avant la cible `Accept`, sans apparition brusque |
| 03→04 / 04→05 | `(949,500)` → `(981,399)` | correction de repos du curseur avant le trajet de `Connect local datasets` |
| 04→05 / 05→06 | `(869,501)` → `(969,451)` | courte reprise de déplacement sur une pause existante |
| 05→06 / 06→07 | `(92,293)` → `(670,456)` | retour naturel du curseur depuis la sidebar vers le CTA `Run private analysis` avant l'approche approuvée |
| 06→07 / 07→08 | curseur masqué durant le compute | garder une unique couche curseur, rendre masquage intentionnel et restituer à la prochaine action |
| 07→08 / 08→09 | position `(97,344)` en fin et début, mais visibilité change | réapparition discrète à la même coordonnée ; préserver la galerie `Ready/Not run` |
| 08→09 / 09→10 | `(930,511)` → `(930,510)` | raccord presque parfait, ne pas redessiner le dashboard ni les KPI |
| 09→10 / 10→11 | `(930,510)` → `(886,476)` | 50px de raccord anticipé, conserver l'état CTA `Ask AI` survolé |
| 10→11 / 11→12 | AI `Working` au départ ; réponse n'est pas visible | conserver le header Ask AI et le même texte, agrandir uniquement le panneau de lecture au moment prévu |
| 11→12 / 12→13 | sortie finale large → identique au départ 12→13 | ne pas repositionner les cartes ; le curseur arrive sur `01 · WEEK 1` et clique |
| 13→01 | **aucune transition de boucle validée** | designer un raccord de retour sans slideshow ni faux clic, à soumettre à validation séparée |

Les chiffres entre parenthèses sont des points dans l'espace **1120×620**. Ce sont des repères de QA, pas des ordres de redessiner le curseur.

**Attention au wording approuvé :** la réponse scene12 présente `Review production constraints`, `Review transit handoffs`, `Prioritize joint mitigation`, alors que le détail final scène13 précise `Investigate production bottlenecks`, `Review transit handoffs`, `Monitor shared risk trends weekly`. Le passage a été accepté comme transition visuelle, mais l'équivalence sémantique de Week 3 n'est pas démontrée. Ne **pas** changer silencieusement ces textes. Soumettre un correctif de cohérence distinct avant le final lock.

## 5. Contrat runtime pour Build

### Horloge unique et rendu pur

```ts
type Clip = { id: string; startMs: number; durationMs: number; render(localMs: number): void };
const globalClipOffsets = [0, 6700, 15300, 22500, 31200, 39300, 47800, 56300, 64900, 68200, 77600, 84800]; // ms
// Le renderer global réutilise les mêmes <g> et attributs SVG entre deux clips.
// Une seule boucle requestAnimationFrame; aucune boucle par composant ou scène.
// clip.render(clamp(globalMs - clip.startMs, 0, clip.durationMs))
```

Construire `renderAt(globalMs)` **déterministe et idempotente** : la même position temporelle donne exactement le même frame quel que soit l'historique des appels, afin que les tests de raccord et les captures de QA soient reproductibles. Ne pas brancher les clips sur les boutons originaux. Une seule instance de curseur, idéalement issue des mêmes paths originaux et placée en calque supérieur.

La progression des caractères, barres de chargement, compteurs et lignes de graphe provient des expressions originales `t`-dépendantes. Ne pas remplacer par un compteur de scènes ou `opacity=1/0` à une borne. La validation UI doit vérifier les états cumulés, pas la simple visibilité d'un écran.

### Homepage sans UI de lecteur

- `autoplay` seulement lorsque `IntersectionObserver` constate l'entrée dans le viewport. Aucun play, pause, replay, stepper, progress bar, compteur ni sélecteur visible.
- Sans son, sans demande de permissions, sans clic. Même les clics montrés à l'écran sont seulement des animations illustratives du curseur.
- Si hors viewport, onglet masqué ou `document.hidden`, suspendre la progression de **l'horloge du film**, et les `requestAnimationFrame`. Au retour, reprendre au même frame sans rattrapage brutal du temps écoulé. État invisible au visiteur.
- À la conclusion, conserver un bref temps de lecture puis boucler par le **raccord 13→01 à valider** ; ne pas faire de `innerHTML = scene01` instantané ni de fondu plein écran arbitraire.
- `requestAnimationFrame` + `document.visibilityState` + `IntersectionObserver`, cleanup des observers et frames au unmount. Éviter la double accélération si la page entre/sort rapidement du viewport.
- Les labels de contrôle dans les AppBlocks servent uniquement à la revue et **doivent être retirés de la homepage**. Le renderer doit rester scrubbable via API **de développement non visible**, permettant les snapshots QA.

### Responsive et accessibilité

- Conserver le **même SVG source** sur desktop et tablette et vérifier 1366×768 et 1440×900 ; redimensionner le conteneur de façon proportionnelle, sans changer la caméra.
- Mobile : **pas de redessin automatique ni de crop arbitraire**. Définir un fallback lisible / une composition alternative avant de promettre une lecture détaillée à 390px. La version mobile dédiée est à valider, car les textes de 10–12px du viewBox deviennent illisibles à cette largeur.
- `prefers-reduced-motion: reduce` : afficher un cadre informatif statique (sans autoplay, sans slideshow), avec texte alternatif sur le parcours. Ne pas accélérer le film pour compenser.
- Accessibilité : `aria-label` décrivant la démo, éléments purement décoratifs masqués à la lecture d'écran, visibilité de `Concept preview · Synthetic data` discrète mais durable.
- Performance : aucun Canvas raster par défaut ni captures bitmap des scènes, sauf recours à un fallback explicitement validé ; conserver SVG vectoriel et animations d'attributs, éviter rerender de tout le DOM à 60 fps.

## 6. Vérité produit et sécurité de la démo

- **SYNTHETIC FIXTURES ONLY.** Les chiffres 12 total / Production 6 (50%) / Transit 4 (33%) / Other 2 (17%) sont illustratifs, pas des données d'entreprise.
- 2 organisations indépendantes, 2 inputs protégés chacune. Aucun dataset brut, identifiant ou ligne jointe visible.
- Étapes `Computing`, `Protected`, `Authorized`, `Working`, Ask AI et provenance désignent des **états de démo simulés**, pas une exécution réelle ni une preuve cryptographique vérifiée.
- Ne prétendre ni accéder aux registres privés, ni avoir un résultat réel du modèle IA, ni avoir publié un anchor blockchain.
- Les propositions Week 1–3 restent **Not assigned / Proposed / Review action**. Aucun statut « Approved », « Completed », « Executed » ni effets réels de clic ne doivent apparaître.

## 7. QA à effectuer par Build (AUCUN TEST NAVIGATEUR PRÉTENDUMENT EFFECTUÉ ICI)

1. Frames : captures à `T−16 ms`, `T` et `T+16 ms` à chaque raccord, plus `T−200 ms` et `T+200 ms`. **Aucun frame vide, retour de page, saut du logo ou téléport de curseur visible.**
2. Pixel / attribut : éléments stables (logo, sidebar, workspace avatar, topbar) identiques avant/après quand le contexte produit ne change pas ; tous les textes de petite taille lisibles.
3. Cursor : échantillonner tous les `cursorPosition(t)` après la connexion des courbes. Pointer dans la cible au moment exact du clic, pas sur fond ou autre bouton ; aucune double flèche affichée.
4. States : Gallery 1 Ready et 2 Not run, sans KPI ; Analytics 12/6/4/2 ; 09→10 microinteraction seulement panneau droit ; AI question **une seule ligne** ; traitement avant réponse ; trois recommandations ; final **clic WEEK 1**.
5. Temps : valider la somme **92.4 s**, le pacing des 12 clips et le temps de lecture du cadre final. Aucun `setTimeout` de scène concurrent.
6. Autoplay : entrer/sortir de viewport, changer d'onglet, revenir, throttling CPU, retour arrière d'onglet ; absence de barre et de boutons en DOM public ; sans audio.
7. Accessibility : reduced motion affiche fallback statique ; chargement sans JS et SVG non disponible se dégradent proprement.
8. Loop : seulement après approbation de `13→01`, valider que la fin et le début ne ressemblent ni à un cut de slide ni à un simple crossfade sans action.

## 8. Ordre d'intégration et décision attendue

**Build doit travailler à partir des sources individuelles dans cette archive, pas à partir du montage rejeté.**

1. Importer les sources du registre et identifier les `<g>` SVG stables, contenus variables et fonctions `render(t)` ; préserver textuellement les paths approuvés.
2. Mettre en place le seul `MovieClock`, le seul SVG parent et un calque curseur universel ; supprimer les contrôles public et les boucles `requestAnimationFrame` des extraits tout en conservant leurs expressions de mouvement.
3. Ajouter les raccords un par un, en contrôlant chaque départ/arrivée sur la base des derniers frames approuvés. Pour 09→10 V2, récupérer le code dans ce chat plutôt que la V1 rejetée.
4. Faire valider séparément les **deux décisions ouvertes** : le copy discrepancy Week 3 et le pont de boucle Scene13→01. Vérifier aussi la lisibilité mobile avant le final lock.
5. Présenter un **véritable film cinématique** dans la homepage en environnement de prévisualisation avec revue founder. **Ne pas annoncer DESIGN LOCKED** avant le visionnement et l'accord explicite.

**Statut de ce document : handoff technique préparé, sources partielles identifiées, montage continu non réalisé et non approuvé.**
