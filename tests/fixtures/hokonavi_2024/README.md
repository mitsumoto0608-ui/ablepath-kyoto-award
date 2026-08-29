# SYNTHETIC fixture

このフォルダは契約テスト専用の `SYNTHETIC` データであり、実在地点・実測値・ほこナビ公開データを表さない。

- `source_network.geojson`: 2024年版field名を使った合成node/link。floor `0/1/-1/1.5`、in_out `1/2/3`、direction `1/2/3/99`、stairs/elevator/escalator/ramp、mixed `r_method=121`を含む。同一`start_time`で`99`、意味ある空欄、属性欠落を分ける。`start_time`はpolicy-only例で40 mappingの件数外。
- `expected_internal.json`: adapter実装後に期待する静的network表現の契約例。全FULL出力、全mappingのoutput/sidecar/reject到達、各edgeのexact loss ID、原値provenanceを含む。sourceに存在しないM7/scenario値は含めない。

値は `FIXTURE_VALUE`。実データへ流用しない。
