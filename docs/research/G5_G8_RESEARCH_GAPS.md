# G5–G8 Research Gaps

更新日: 2026-09-01

## Repository integration context

Standalone read-only workspaceで作成されたindexを、`origin/main@515955000d3df28b5b20e468a6312a006f7f95ea`から分離した`task/g5-g8-literature-index-integration-v1`へ統合した。`AGENTS.md`、`README.md`、`DESIGN.md`、`RESEARCH_LEDGER.md`、`MINIMAL_SUFFICIENT_ENGINEERING.md`、M6/Hokonavi review packets、PR #6 head `027d57b29f107717f4a57dc85c580632befd40a4`のcurrent G5–G8 reportsと照合済み。

照合で解消したresearch側の相違:

- A1/A2語彙をrepo正本に合わせ、独立確認receiptのないA2表記を除去した。
- CSA/ASC B651:23、PROWAG、Moya/Ohtsu、既存frozen M7 contract、PLATEAU文書/package versionの境界を現行repoに合わせた。
- source IDは38件すべて一意、P01–P17の全source参照は解決済み、DOI/title重複は0。

未解決なのは以下のevidence closureであり、production contractの変更ではない。

## Claude audit transfer-status remediation ledger

Bibliographyのstatusはsource全体のtransfer上限、problem-source mapは個別problemでの採用範囲とする。以下の4行は監査前から安全側に限定されており、その値をsupported statusとして維持し、拡張禁止testを追加した。

| Problem / source | Before | After | Reason |
|---|---|---|---|
| P04 / S005 | ADAPT (bibliography: DIRECT) | ADAPT | PLATEAUのschema capabilityはlocal pedestrian topology completenessを直接証明しない |
| P10 / S004 | STRUCTURE_ONLY (bibliography: DIRECT) | STRUCTURE_ONLY | 3D Tilesはdelivery/portrayal structureでありsource semanticsを直接移転しない |
| P11 / S005 | ADAPT (bibliography: DIRECT) | ADAPT | PLATEAU product specificationは個別remote endpoint uptimeの証拠ではない |
| P11 / S007 | ADAPT (bibliography: DIRECT) | ADAPT | portal update historyは個別endpoint reliabilityへ直接移転しない |

## Claude audit locator remediation ledger

| Source | Before | After | Reason |
|---|---|---|---|
| S017 | J-STAGE publisher root / DOIなし | `10.5610/jaee.24.3_1` | repo manifestのarticle IDを原著DOIへ解決 |
| S018 | J-STAGE publisher root / DOIなし | `10.5638/thagis.17.73` | repo manifestのarticle IDを原著DOIへ解決 |
| S034 | ACM publisher root / DOIなし / 2016 metadata | `10.1109/EMBC.2013.6609720` / 2013 IEEE EMBC metadata | 固有titleの原著recordに解決し、別publisher・別年の誤記を維持しない |

## Evidence gaps by problem

| Problem | Gap | Current handling | Required evidence |
|---|---|---|---|
| P01 | city packageごとのauthoritative source manifest未取得 | S005/S006のdefinitionのみ | 実際のPLATEAU/hazard package metadata |
| P02 | AblePath ingest sampleのaxis/vertical datum未確認 | normative packet ready | known control pointsと実ファイル |
| P03 | actual mixed/invalid geometry failure corpusなし | OGC + method packet | failing input samplesとrepair diff |
| P04 | Kyoto/Fujisawa critical junction ground truthなし | graph QA packet | crossing/grade/entrance field labels |
| P05 | target-area OSM completeness率未計測 | missing=unknown | timestamped tag coverage audit |
| P06 | hazard overlapとpedestrian impactのpaired observationなし | overclaim prohibited | event/scenario impact validation |
| P07 | AblePath cost vocabulary/units未提示 | label discipline only | metric registry and user interpretation test |
| P08 | Kyoto row-house debris/local blockage calibrationなし | S015 ADAPT only | local building/debris/road observations |
| P09 | 現行M6 packetにscoped clause比較はあるが、日本のedge別適用とprofile stateは未freeze | M6 BLOCKED_CONTRACT / NOT_COMPUTED | legal/domain applicability review + human freeze |
| P10 | target city PLATEAU instances/classes未取得 | spec capability only | application schema/instances/coverage report |
| P11 | actual failing tileset request/headers未提供 | protocol packet | request/response/CORS trace |
| P12 | facility operator/current operation evidence未提供 | state separation only | official operation record + field timestamp |
| P13 | project conflict cases未提供 | conflict model only | paired source records and adjudication |
| P14 | target source freshness requirements未決定 | timestamps required | source-owner refresh/expiry policy |
| P15 | AblePath UI/prototype/user tasks未提供 | evidence structure only | accessibility/usability study |
| P16 | intended paper-to-product transfers未列挙 | transfer taxonomy ready | transfer request per claim |
| P17 | itemized inventory/hash manifestがIMPORT ONLYになく812/121/116/5を独立再現できない | historical reported counts only | source workspace manifestが必要になった場合のみhuman-reviewed receiptを追加 |

## Paid / unavailable primary text

- EN 17210:2021 はofficial catalogue/source identityのみ。本文未取得のため DISCOVERY_ONLY。数値/条項を推測しない。
- CSA/ASC B651:23 は現行M6 packetでPreface、§1.2、§8.2.2（PDF pp.6, 27, 232）をscoped comparatorとしてA1-NUM / ADAPT確認済み。ただし日本の法的適用やAblePath profile境界には昇格しない。
- 取得不能なoptional PDFやDOI errorはgapとして残し、shortlistは利用可能なoriginal/official sourceで構成した。

## Contradictions requiring preservation

1. PROWAG version contradiction: older research/draft referencesの3 ftと2023 final R302.2の48 inch。平均禁止、version/jurisdictionを保持。
2. Debris population contradiction: S015 Mashiki wood frameとS016 Haiti C3。係数混合禁止。
3. Width definition contradiction: nominal surface widthとobstruction-adjusted minimum clear width。definitionを保持。
4. CityGML capability/implementation contradiction: ADE capability/研究提案とPLATEAU actual schema。instance確認前にimplementation claim禁止。
5. Hazard portal aggregation: layerごとにprovider/year/license/updateが異なる。単一timestamp扱い禁止。

## Source acquisition/tool gap

原source workspaceの作成時receiptでは、agent-reachのlocal launcher破損とExa backend offlineにより、公式domainに限定したWeb検索へfallbackしたと記録されている。OGC、国土交通省、国土地理院、U.S. Access Board、UK DfT、Accessibility Standards Canada、WHATWGのoriginal/official pagesを確認した履歴であり、現在のbackend稼働状態を表す記述ではない。

## Privacy

accessible-tourism-research-dataにはDB snapshotが存在したが、private research dataの内容はindexへ取り込んでいない。個人情報を含み得るraw evidenceはcommit対象外。
