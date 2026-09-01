# G5–G8 Source Cards

各cardの全metadataは G5_G8_MASTER_BIBLIOGRAPHY.csv を正本とする。ここでは実装agentが「使えるclaim / 使えないclaim」を素早く判断するための要点だけを示す。

## Official / normative core

### S001 OGC WKT2 CRS

- 使える: axis orderはcoordinate sequenceの意味を決める。CRS/axis/unitを明示検証する。
- 使えない: EPSG名だけで個別fileのtransformが正しいとは言えない。
- 箇所: Axis order section。Transfer: DIRECT。

### S002 OGC Simple Features

- 使える: geometry family、validity、predicateの定義。
- 使えない: valid geometry = valid accessibility semantics。
- 箇所: Clauses 6–8。Transfer: DIRECT。

### S003 CityGML 3.0

- 使える: conceptual model、semantics、ADE extension boundary。
- 使えない: PLATEAU datasetが特定ADEを実装済みというclaim。
- 箇所: Scope、Clauses 6–8。Transfer: DIRECT。

### S004 3D Tiles 1.1

- 使える: massive 3D contentのstreaming/rendering container。
- 使えない: source provenance、accessibility semantics、current facility state。
- 箇所: Overview / OGC 22-025r4。Transfer: DIRECT。

### S005 PLATEAU標準製品仕様書5.1

- 使える: current product classes、CRS、quality、distribution、metadata。
- 使えない: city packageに全classが存在するという推定。
- 箇所: Chapters 4–8、CityGML 3.0仕様案note。Transfer: DIRECT。

### S006–S008 Japan hazard official sources

- 使える: hazard category、scenario、provider、year、uncertainty、update。
- 使えない: overlapからのpassability/safety、polygon外安全、車いす閾値。
- 箇所: 各データ説明・注意事項、津波手引き1.6.4。Transfer: DIRECT/ADAPT。

### S009 PROWAG 2023

- 使える: current US final ruleのR302/R304/R407とversion。
- 使えない: 日本法、個人の最低通過能力、AblePath判定閾値。
- 重要矛盾: 旧3 ft引用とfinal R302.2 48 inchを混ぜない。
- Transfer: ADAPT。

### S010–S013 UK / Japan / Canada / EU standards

- 使える: jurisdiction、version、legal/guidance/standard statusの比較。
- 使えない: 横断的な最小値の合成。
- S012: 現行M6 evidence packetでB651:23のPreface、§1.2、§8.2.2（PDF pp.6, 27, 232）をA1-NUM / ADAPTとして確認済み。named-source比較候補であり、日本の適合基準やM6閾値ではない。
- S013: 本文未取得のDISCOVERY_ONLY / REJECT。数値・条項・production claimに使わない。

### S014 WHATWG Fetch/CORS

- 使える: remote fetch failureをHTTP/CORS policyとして分類。
- 使えない: physical facilityやdatasetの不存在。
- 箇所: Section 3.3。Transfer: DIRECT。

## Empirical and method core

### S015 Moya et al. 2020

- 使える: 益城木造のdebris extent分布、確率的入力、local calibrationの必要性。
- 使えない: 京町家の真値として扱う、新規・変更係数を未審査で追加する、欠落M7入力を推測する、deterministic blockageを主張する。
- 現行契約: Moya定数とM7 core/APIはrepoでA2 / ADAPTとして実装済み。本indexはそれを変更せず、per-field evidenceの接続可否だけを扱う。
- 箇所: pp.10–14、Eq.2–3/7。Transfer: ADAPT。

### S016 Yu & Gardoni 2022

- 使える: capacity-demand/fragility modelの構造。
- 使えない: Haiti C3係数、emergency vehicle幅のpedestrian転用。
- 箇所: pp.3–6、Eq.1–2、Table 1。Transfer: STRUCTURE_ONLY。

### S017 横屋ほか2024

- 使える: 日本のroad blockage推定にも観測不一致が残る検証例。
- 使えない: 78.8%をedge accuracyまたは京都精度とする。
- 箇所: p.1 abstract、results。Transfer: ADAPT。

### S018 亀井ほか2009

- 使える: 京都×建物被害×道路閉塞のlocal precedent。
- 使えない: 2009 citywide percentagesを現在の回廊へ移植。
- 箇所: pp.73–82。Transfer: ADAPT。

### S019 Costa et al. 2020

- 使える: hazard–damage–network–demandを分けるmethod。
- 使えない: vehicle traffic costをwheelchair routeへ転用。
- 箇所: Sections 2–4。Transfer: STRUCTURE_ONLY。

### S020 Coppola & Marshall 2021

- 使える: static obstruction込みminimum clear widthの必要性。
- 使えない: Cambridgeの22.2%を京都補正係数にする。
- 箇所: pp.7–9、Table 4。Transfer: ADAPT。

### S021 Li et al. 2018

- 使える: semi-automated sidewalk graph後のmanual QA/QC。
- 使えない: reported laborを現地調査工数へ読み替える。
- 箇所: Tables 1–2、pp.5–6。Transfer: ADAPT。

### S022 Treccani et al. 2022

- 使える: historic city MLS→2 m attribute segment→vector graph。
- 使えない: 98.7%をroute safety accuracyとする、PLATEAUをpoint cloud代替とする。
- 箇所: pp.497–503。Transfer: ADAPT。

### S023 Askari et al. 2025

- 使える: crowd/imagery auditとgovernment field dataのfeature別agreement/conflict。
- 使えない: どちらかを無条件ground truthにする。
- 箇所: pp.1–2、results。Transfer: ADAPT。

### S024–S025 OSM/VGI suitability

- 使える: accessibility tag incompleteness、route sensitivity、missing=unknown。
- 使えない: OSM tag欠落から物理feature欠如を推定、safe route claim。
- 箇所: methods/results。Transfer: ADAPT。

### S026–S027 Project Sidewalk / Tohme

- 使える: participatory audit、crowd+AI screening、provenance/QA。
- 使えない: image detectionから寸法・現況・operabilityを確定。
- 箇所: methods/evaluation。Transfer: ADAPT / STRUCTURE_ONLY。

### S028–S030 3D/indoor/personalized network models

- 使える: accessibility semantics、profile-specific network、fusion pipelineの構造。
- 使えない: research extensionをofficial PLATEAU schemaとして扱う、inferredをmeasuredに昇格。
- Transfer: STRUCTURE_ONLY / ADAPT。

### S031 Taniguchi et al. 2022

- 使える: Japan photogrammetry/DEM barrier extractionとfield geometric validation。
- 使えない: imagery/point cloudのない区間のgeometry。
- 箇所: Sections 3–5、pp.10/16。Transfer: ADAPT。

### S032 Ohtsu et al. 2020

- 使える: device、slope、assistanceでevacuation performanceが変わるempirical evidence。
- 使えない: 既存A2 comparatorをhuman freeze前にexecutable M6 production profileへbindする、自走能力や一般避難速度とみなす。
- 箇所: pp.6–9。Transfer: ADAPT。

### S033–S034 image extraction / smartphone observation

- 使える: candidate generation、conditional observation、profile/time metadata。
- 使えない: topology、universal passability、current stateの自動確定。

## Discovery-only indexes

### S035–S038

- 77本翻訳DOCX、deep-research 2件、PLATEAU調査DOCX。
- 用途: title/DOI/original候補の発見のみ。
- 禁止: 原著として引用、数値/式/pageのA1昇格、production claim。
- Transfer: REJECT。SOURCE_STATUS: DISCOVERY_ONLY。
