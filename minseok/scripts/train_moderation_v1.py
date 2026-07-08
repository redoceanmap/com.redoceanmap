"""유해 한국어 분류기 v1 학습 — KcELECTRA-base + Smilegate Unsmile(멀티라벨 10종).

왓처(수신 분류기)의 ModerationPort 구현이 사용할 모델을 만든다.
사용:
  venv/bin/python minseok/scripts/train_moderation_v1.py
출력:
  minseok/models/moderation/kcelectra-unsmile-v1/  (모델 + 토크나이저 + labels.json)
"""

import json
import sys
from pathlib import Path

import torch
from datasets import load_dataset
from sklearn.metrics import f1_score
from torch.utils.data import DataLoader
from transformers import AutoModelForSequenceClassification, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]  # minseok
OUT = ROOT / "models" / "moderation" / "kcelectra-unsmile-v1"

BASE = "beomi/KcELECTRA-base"
LABELS = ["여성/가족", "남성", "성소수자", "인종/국적", "연령", "지역", "종교", "기타 혐오", "악플/욕설", "clean"]
MAX_LEN = 128
BATCH = 32
EPOCHS = 2
LR = 3e-5


def main() -> None:
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"device={device}")

    ds = load_dataset("smilegate-ai/kor_unsmile")
    tokenizer = AutoTokenizer.from_pretrained(BASE)
    model = AutoModelForSequenceClassification.from_pretrained(
        BASE, num_labels=len(LABELS), problem_type="multi_label_classification",
        id2label={i: l for i, l in enumerate(LABELS)},
        label2id={l: i for i, l in enumerate(LABELS)},
    ).to(device)

    def collate(batch):
        enc = tokenizer(
            [b["문장"] for b in batch], truncation=True, max_length=MAX_LEN,
            padding=True, return_tensors="pt",
        )
        enc["labels"] = torch.tensor([b["labels"] for b in batch], dtype=torch.float)
        return enc

    train_loader = DataLoader(ds["train"], batch_size=BATCH, shuffle=True, collate_fn=collate)
    valid_loader = DataLoader(ds["valid"], batch_size=64, collate_fn=collate)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR)

    for epoch in range(EPOCHS):
        model.train()
        total = 0.0
        for step, batch in enumerate(train_loader):
            batch = {k: v.to(device) for k, v in batch.items()}
            out = model(**batch)
            out.loss.backward()
            optimizer.step()
            optimizer.zero_grad()
            total += out.loss.item()
            if step % 50 == 0:
                print(f"epoch {epoch + 1} step {step}/{len(train_loader)} loss {out.loss.item():.4f}", flush=True)
        print(f"epoch {epoch + 1} 평균 loss {total / len(train_loader):.4f}")

        # 검증
        model.eval()
        preds, golds = [], []
        with torch.no_grad():
            for batch in valid_loader:
                labels = batch.pop("labels")
                batch = {k: v.to(device) for k, v in batch.items()}
                logits = model(**batch).logits.sigmoid().cpu()
                preds.append((logits > 0.5).int())
                golds.append(labels.int())
        preds = torch.cat(preds).numpy()
        golds = torch.cat(golds).numpy()
        print(f"[valid] micro-F1 {f1_score(golds, preds, average='micro'):.4f} "
              f"| macro-F1 {f1_score(golds, preds, average='macro'):.4f} "
              f"| 악플/욕설 F1 {f1_score(golds[:, 8], preds[:, 8]):.4f} "
              f"| clean F1 {f1_score(golds[:, 9], preds[:, 9]):.4f}", flush=True)

    OUT.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(OUT)
    tokenizer.save_pretrained(OUT)
    (OUT / "labels.json").write_text(json.dumps(LABELS, ensure_ascii=False))
    print(f"저장 완료: {OUT}")


if __name__ == "__main__":
    main()
