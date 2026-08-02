"""A(기존) 대 C(+PrimeKG)를 같은 fold에서 짝지어 비교한다.

평균±표준편차는 fold마다 난이도가 달라 차이를 가린다.
같은 fold 안의 차이를 15개(5-fold x 3seed) 모아 부호를 센다.
"""
import os, json
import warnings

import lightgbm as lgb
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold

warnings.filterwarnings("ignore")
BASE = os.path.dirname(os.path.abspath(__file__))

ft = json.load(open(f"{BASE}/data/FEATURE_TABLE.json"))
pk = {r["rid"]: r for r in json.load(open(f"{BASE}/data/primekg_features.json"))}
PKG = [f"pkg_{m}_{t}" for t in ("emb", "sgc1", "sgc2", "sgc3") for m in ("cos", "l2")]

rows = []
for r in ft:
    if r["y"] is None:
        continue
    d = {k: r[k] for k in ("disease", "gwas_support", "genetic_score", "net_zscore",
                           "action_type", "modality", "year")}
    d["y"] = 1 if r["y"] >= 1 else 0
    p = pk.get(r["rid"], {})
    for c in PKG:
        d[c] = p.get(c)
    rows.append(d)

df = pd.DataFrame(rows)
for c in ("action_type", "modality"):
    df[c] = df[c].astype("category")

BASE_F = ["gwas_support", "genetic_score", "net_zscore", "action_type", "modality", "year"]
PARAMS = dict(objective="binary", learning_rate=0.05, num_leaves=31,
              min_child_samples=30, n_estimators=300, verbose=-1)


def ef_at(y, s, frac=0.10):
    n = max(1, int(len(y) * frac))
    top = np.argsort(-s)[:n]
    return y[top].mean() / y.mean() if y.mean() > 0 else np.nan


dA, dE = [], []
for seed in (0, 1, 2):
    gkf = GroupKFold(n_splits=5, shuffle=True, random_state=seed)
    for tr, te in gkf.split(df, df.y, groups=df.disease):
        dtr, dte = df.iloc[tr], df.iloc[te]
        y = dte.y.values
        if len(set(y)) < 2:
            continue
        out = {}
        for tag, feats in (("A", BASE_F), ("C", BASE_F + PKG)):
            m = lgb.LGBMClassifier(**PARAMS, random_state=seed)
            m.fit(dtr[feats], dtr.y)
            s = m.predict_proba(dte[feats])[:, 1]
            out[tag] = (roc_auc_score(y, s), ef_at(y, s))
        dA.append(out["C"][0] - out["A"][0])
        dE.append(out["C"][1] - out["A"][1])

dA, dE = np.array(dA), np.array(dE)
print(f"fold {len(dA)}개")
for name, d in (("AUC", dA), ("EF@10%", dE)):
    t, p = stats.ttest_rel(d, np.zeros_like(d))
    print(f"{name:<8} C-A 평균 {d.mean():+.4f}  중앙값 {np.median(d):+.4f}  "
          f"오른 fold {int((d > 0).sum())}/{len(d)}  대응 t검정 p={p:.3f}")
