"""매칭된 행만 따로 떼어 PrimeKG 임베딩에 신호가 있는지 본다.

앞 실험은 28%만 매칭돼 효과가 희석됐을 수 있다.
여기서는 매칭행(양쪽 노드 다 있는 행)만 쓰고 세 갈래를 비교한다.
  기존만 / PrimeKG만 / 둘 다
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
pk = {r["rid"]: r for r in json.load(open(f"{BASE}/data/primekg_features.json"))}
PKG = [f"pkg_{m}_{t}" for t in ("emb", "sgc1", "sgc2", "sgc3") for m in ("cos", "l2")]

rows = []
for r in ft:
    p = pk.get(r["rid"], {})
    if r["y"] is None or p.get("pkg_cos_emb") is None:
        continue
    d = {k: r[k] for k in ("disease", "gwas_support", "genetic_score", "net_zscore",
                           "action_type", "modality", "year")}
    d["y"] = 1 if r["y"] >= 1 else 0
    for c in PKG:
        d[c] = p[c]
    rows.append(d)

df = pd.DataFrame(rows)
for c in ("action_type", "modality"):
    df[c] = df[c].astype("category")

BASE_F = ["gwas_support", "genetic_score", "net_zscore", "action_type", "modality", "year"]
ARMS = {"기존만": BASE_F, "PrimeKG만": PKG, "둘 다": BASE_F + PKG}
PARAMS = dict(objective="binary", learning_rate=0.05, num_leaves=31,
              min_child_samples=20, n_estimators=300, verbose=-1)


def ef_at(y, s, frac=0.10):
    n = max(1, int(len(y) * frac))
    return y[np.argsort(-s)[:n]].mean() / y.mean() if y.mean() > 0 else np.nan


print(f"매칭 라벨행 {len(df)}  양성 {int(df.y.sum())} ({df.y.mean():.1%})  질환 {df.disease.nunique()}")
res = {a: {"auc": [], "ef": []} for a in ARMS}
for seed in (0, 1, 2):
    for tr, te in GroupKFold(n_splits=5, shuffle=True, random_state=seed).split(df, df.y, df.disease):
        dtr, dte = df.iloc[tr], df.iloc[te]
        y = dte.y.values
        if len(set(y)) < 2:
            continue
        for arm, feats in ARMS.items():
            m = lgb.LGBMClassifier(**PARAMS, random_state=seed)
            m.fit(dtr[feats], dtr.y)
            s = m.predict_proba(dte[feats])[:, 1]
            res[arm]["auc"].append(roc_auc_score(y, s))
            res[arm]["ef"].append(ef_at(y, s))

print(f"{'갈래':<14}{'AUC':>16}{'EF@10%':>16}")
for a in ARMS:
    r = res[a]
    print(f"{a:<14}{np.mean(r['auc']):.3f}±{np.std(r['auc']):.3f}   "
          f"{np.mean(r['ef']):.3f}±{np.std(r['ef']):.3f}")

# 임베딩 코사인 자체가 양성/음성을 가르는지 (모델 없이)
print("\n코사인 단독 (학습 없이 점수로만)")
for t in ("emb", "sgc1", "sgc2", "sgc3"):
    c = df[f"pkg_cos_{t}"].values
    print(f"  cos_{t}: AUC {roc_auc_score(df.y, c):.3f}  "
          f"양성평균 {c[df.y == 1].mean():+.3f}  음성평균 {c[df.y == 0].mean():+.3f}")
