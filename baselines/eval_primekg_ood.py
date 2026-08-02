"""disease-OOD로 PrimeKG 임베딩 feature의 기여를 잰다.

네 갈래를 같은 분할·같은 시드로 돌려 비교한다.
  A 기존 feature만
  B 기존 + gene-only KG 점수 (2026-07-10 브릿지 실험에서 쓴 것)
  C 기존 + PrimeKG 임베딩
  D 기존 + 둘 다

분할은 질환 단위 GroupKFold — 학습에서 본 병은 평가에 안 나온다.
"""
import os, json
import warnings

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold

warnings.filterwarnings("ignore")
BASE = os.path.dirname(os.path.abspath(__file__))

ft = json.load(open(f"{BASE}/data/FEATURE_TABLE.json"))
kg = {r["rid"]: r["kg_score"] for r in json.load(open(f"{BASE}/data/kg_features.json"))}
pk = {r["rid"]: r for r in json.load(open(f"{BASE}/data/primekg_features.json"))}

PKG = [f"pkg_{m}_{t}" for t in ("emb", "sgc1", "sgc2", "sgc3") for m in ("cos", "l2")]

rows = []
for r in ft:
    if r["y"] is None:
        continue
    d = {
        "disease": r["disease"],
        "y": 1 if r["y"] >= 1 else 0,
        "gwas_support": r["gwas_support"],
        "genetic_score": r["genetic_score"],
        "net_zscore": r["net_zscore"],
        "action_type": r["action_type"],
        "modality": r["modality"],
        "year": r["year"],
        "kg_score": kg.get(r["rid"]),
    }
    p = pk.get(r["rid"], {})
    for c in PKG:
        d[c] = p.get(c)
    d["pkg_hit"] = p.get("pkg_dis_hit", 0) and p.get("pkg_drug_hit", 0)
    rows.append(d)

df = pd.DataFrame(rows)
for c in ("action_type", "modality"):
    df[c] = df[c].astype("category")

BASE_F = ["gwas_support", "genetic_score", "net_zscore", "action_type", "modality", "year"]
ARMS = {
    "A 기존": BASE_F,
    "B +gene-only KG": BASE_F + ["kg_score"],
    "C +PrimeKG": BASE_F + PKG + ["pkg_hit"],
    "D +둘 다": BASE_F + ["kg_score"] + PKG + ["pkg_hit"],
}

PARAMS = dict(objective="binary", learning_rate=0.05, num_leaves=31,
              min_child_samples=30, n_estimators=300, verbose=-1)


def ef_at(y, s, frac=0.10):
    """상위 frac 안의 양성 비율 / 전체 양성 비율."""
    n = max(1, int(len(y) * frac))
    top = np.argsort(-s)[:n]
    base = y.mean()
    return (y[top].mean() / base) if base > 0 else np.nan


print(f"라벨행 {len(df)}  양성 {int(df.y.sum())}  질환 {df.disease.nunique()}  "
      f"PrimeKG 매칭 {int(df.pkg_hit.sum())} ({df.pkg_hit.mean():.1%})")
print()

res = {a: {"auc": [], "ef": [], "auc_hit": []} for a in ARMS}
for seed in (0, 1, 2):
    gkf = GroupKFold(n_splits=5, shuffle=True, random_state=seed)
    for tr, te in gkf.split(df, df.y, groups=df.disease):
        dtr, dte = df.iloc[tr], df.iloc[te]
        if dte.y.nunique() < 2:
            continue
        for arm, feats in ARMS.items():
            m = lgb.LGBMClassifier(**PARAMS, random_state=seed)
            m.fit(dtr[feats], dtr.y)
            s = m.predict_proba(dte[feats])[:, 1]
            y = dte.y.values
            res[arm]["auc"].append(roc_auc_score(y, s))
            res[arm]["ef"].append(ef_at(y, s))
            h = dte.pkg_hit.values.astype(bool)
            if h.sum() > 20 and len(set(y[h])) == 2:
                res[arm]["auc_hit"].append(roc_auc_score(y[h], s[h]))

print(f"{'갈래':<18}{'AUC':>16}{'EF@10%':>16}{'AUC(매칭행만)':>18}")
for arm in ARMS:
    r = res[arm]
    f = lambda k: f"{np.mean(r[k]):.3f}±{np.std(r[k]):.3f}"
    print(f"{arm:<18}{f('auc'):>16}{f('ef'):>16}{f('auc_hit'):>18}")

print()
m = lgb.LGBMClassifier(**PARAMS, random_state=0)
m.fit(df[ARMS["D +둘 다"]], df.y)
imp = sorted(zip(ARMS["D +둘 다"], m.feature_importances_), key=lambda x: -x[1])
print("D 갈래 feature 중요도 (gain 아님, split 횟수)")
for k, v in imp:
    print(f"  {k:<20}{v}")
