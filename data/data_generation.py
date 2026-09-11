import json
from sklearn.model_selection import GroupShuffleSplit
import pandas as pd
from pathlib import Path
ATTACK_PATH = "/Users/izabellemarianne/Desktop/prompt_injection/data/attack/attack_logs.jsonl"
BENIGN_PATH = "/Users/izabellemarianne/Desktop/prompt_injection/data/benign/" 
def clean_attack_logs():
    with open("/Users/izabellemarianne/Desktop/prompt_injection/data/attack/attack_tasks.json") as f:
        attack_tasks = json.load(f)

    target_index_map = {}
    for task in attack_tasks:
        value = task["target_index"]
        key = task["index"]

        target_index_map[key] = value


    with open("/Users/izabellemarianne/Desktop/prompt_injection/data/attack/glm-4-flash.jsonl") as f1, open("/Users/izabellemarianne/Desktop/prompt_injection/data/attack/attack_logs.jsonl", "w") as f2:
        for line in f1:
            record = json.loads(line)
            index = record["index"]
            target_index = target_index_map[index]
            record["target_index"] = target_index
            f2.write(json.dumps(record) + "\n")


def _load_jsonl(path):
    with open(path, "r") as f:
        return [json.loads(line) for line in f]


def train_test_split():
    attack = _load_jsonl(ATTACK_PATH)

    benign_dir= Path(BENIGN_PATH)
    benigns = []
    for file in benign_dir.glob("*.jsonl"):
        print("File path:", file)
        print("File name:", file.name)

        items = _load_jsonl(file)
        print("Number of records:", len(items))

       
        benigns.append(items)


    groups = []
    total = []
    for item in attack:
        item["label"] = 1
        groups.append(item["target_index"])
        total.append(item)

    count = 0
    for benign in benigns:
        
        for item in benign:
            count += 1
            item["label"] = 0
            groups.append(item["index"])
            total.append(item)

    print(f"len benign{count}")
    print(f"len attack{len(attack)}")
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(gss.split(total, groups=groups))





    # holdout = [total[i] for i in hold_out_idx]
    # hold_out_groups = [groups[i] for i in hold_out_idx]

    # gss2 = GroupShuffleSplit(n_splits=1, test_size=0.1, random_state=42)
    # val_idx, test_idx = next(gss2.split(holdout, groups=hold_out_groups))

    training_groups = [groups[i] for i in train_idx]
    training = [total[i] for i in train_idx]
    test = [total[i] for i in test_idx]
    print(f"training {len(training)}")
    print(f"test {len(test)}")
    return training, training_groups, test, total


if __name__ == "__main__":
    clean_attack_logs()
    train, val, test = train_test_split()