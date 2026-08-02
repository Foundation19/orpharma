"""FEATURE_TABLE의 각 행에 PrimeKG 임베딩 기반 feature를 붙인다.

질환명 -> PrimeKG 질환노드, 약이름 -> PrimeKG 약노드로 찾고
emb / sgc1 / sgc2 / sgc3 각각에서 코사인유사도와 L2거리를 뽑는다.

출력: labeling/runs/legacy/primekg_features.json  (rid별)
"""
import os, json
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))

ft = json.load(open(f"{BASE}/data/FEATURE_TABLE.json"))
canon = json.load(open(f"{BASE}/data/drug_canon.json"))
pmap = json.load(open(f"{BASE}/data/primekg_map.json"))

name_by_rid = {r["rid"]: (r.get("orig_name") or "") for r in canon}

dis_idx = {k.strip().lower(): v for k, v in pmap["dis_by_name"].items()}
drug_idx = {k.strip().lower(): v for k, v in pmap["drug_by_name"].items()}

# 이름으로 못 찾은 질환은 MONDO로 한 번 더 본다.
# PrimeKG 노드 하나가 여러 MONDO를 묶어 갖는 경우가 있어 밑줄로 풀어 편다.
d2m = json.load(open(f"{BASE}/data/dis2mondo.json"))
dis_by_mondo = {}
for k, v in pmap["dis_by_mondo"].items():
    for part in k.split("_"):
        dis_by_mondo.setdefault(part.lstrip("0") or "0", v)


def norm_drug(s):
    """이름 표기 차이만 흡수한다. 유사어 추정은 하지 않는다."""
    s = s.strip().lower()
    for suf in (" group", " sodium", " hydrochloride", " sulfate", " acetate",
                " citrate", " tartrate", " maleate", " mesylate", " phosphate"):
        if s.endswith(suf):
            s = s[: -len(suf)].strip()
    return s


def lookup(table, raw):
    if not raw:
        return None
    s = raw.strip().lower()
    if s in table:
        return table[s]
    s2 = norm_drug(raw)
    return table.get(s2)


mats = {}
for tag in ("emb", "sgc1", "sgc2", "sgc3"):
    a = np.load(f"{BASE}/data/primekg_{tag}.npy").astype(np.float32)
    n = np.linalg.norm(a, axis=1, keepdims=True)
    n[n == 0] = 1.0
    mats[tag] = (a, a / n)

out = []
hit_d = hit_g = hit_both = 0
for r in ft:
    rid = r["rid"]
    di = lookup(dis_idx, r["disease"])
    if di is None:
        m = d2m.get(r["disease"].strip().lower())
        if m:
            di = dis_by_mondo.get(m.split("_")[-1].lstrip("0") or "0")
    gi = lookup(drug_idx, name_by_rid.get(rid, ""))
    hit_d += di is not None
    hit_g += gi is not None
    rec = {"rid": rid, "pkg_dis_hit": int(di is not None), "pkg_drug_hit": int(gi is not None)}
    if di is not None and gi is not None:
        hit_both += 1
        for tag, (raw, unit) in mats.items():
            rec[f"pkg_cos_{tag}"] = float(unit[di] @ unit[gi])
            rec[f"pkg_l2_{tag}"] = float(np.linalg.norm(raw[di] - raw[gi]))
    else:
        for tag in mats:
            rec[f"pkg_cos_{tag}"] = None
            rec[f"pkg_l2_{tag}"] = None
    out.append(rec)

json.dump(out, open(f"{BASE}/data/primekg_features.json", "w"))

N = len(ft)
print(f"rows            {N}")
print(f"disease matched {hit_d} ({hit_d/N:.1%})")
print(f"drug matched    {hit_g} ({hit_g/N:.1%})")
print(f"both matched    {hit_both} ({hit_both/N:.1%})")

lab = [r for r in ft if r["y"] is not None]
lr = {r["rid"] for r in lab}
both_lab = sum(1 for r in out if r["rid"] in lr and r["pkg_cos_emb"] is not None)
print(f"labeled rows    {len(lab)}, both matched {both_lab} ({both_lab/len(lab):.1%})")
