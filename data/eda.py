import json 
from collections import Counter
# How many tasks map to each target index

def _normalize_value(value):
    if value is None:
        return ""

    # 1) If the value is a JSON-encoded string, unwrap it
    if isinstance(value, str):
        s = value.strip()

        # keep unwrapping if it is quoted JSON
        while len(s) >= 2 and s[0] == s[-1] and s[0] in {'"', "'"}:
            s = s[1:-1].strip()

        # try decoding nested JSON string layers
        seen = set()
        while s and s not in seen:
            seen.add(s)
            try:
                parsed = json.loads(s)
            except Exception:
                break
            if isinstance(parsed, (dict, list)):
                return _normalize_value(parsed)
            s = str(parsed)

        # plain text cleanup
        return s.replace("\\n", "\n").replace('\\"', '"').replace("\\'", "'").strip()

    # 2) Lists: flatten all entries
    if isinstance(value, list):
        parts = [_normalize_value(v) for v in value]
        return "\n".join(p for p in parts if p)
    
    # 3) Dicts: flatten text-like values, but keep structure readable
    if isinstance(value, dict):
        parts = []

        # Prefer common text fields
        for key in ("content", "text", "summary", "message", "answer", "output", "response"):
            if key in value:
                text = _normalize_value(value[key])
                if text:
                    parts.append(text)

        # If dict has no obvious text fields, flatten key/value pairs
        if not parts:
            for k, v in value.items():
                text = _normalize_value(v)
                if text:
                    parts.append(f"{k}: {text}")

        return "\n".join(parts)

    # 4) fallback
    return str(value)


def target_counts():
    with open("/Users/izabellemarianne/Desktop/prompt_injection/data/attack/attack_tasks.json") as f:
        attack_tasks = json.load(f)

    # for t in attack_tasks:
    #     t["target_index"]

    # this gives us the amount of attacks per task
    target_counts = Counter(t["target_index"] for t in attack_tasks)

    # some additional info 
    print(f"Amount of tasks attacked: {len(target_counts)} == 80")

    # no. of attacks -> no. tasks that had these many attacks
    fanout_dist = Counter(target_counts.values())
    for num_attacks, num_tasks in sorted(fanout_dist.items()):
        print(f"{num_attacks}: {num_tasks}")

    print(sum(target_counts.values()))  # total number of attacks



def attack_type():
    with open("/Users/izabellemarianne/Desktop/prompt_injection/data/attack/attack_tasks.json") as f:
        attack_tasks = json.load(f)

    counter = {"tool_input": 0, "tool_output": 0, "combined": 0}
    for t in attack_tasks:
        
        lst_attacks = t["attack"] 
        if len(lst_attacks) == 1:
            counter[lst_attacks[0]["mode"]] += 1
        else:
            curr = lst_attacks[0]["mode"]
            combined = False
            for item in lst_attacks:
                if item["mode"] != curr:
                    combined = True
                    counter["combined"] += 1
                    break
            if not combined:
                counter[curr] += 1

    total = 0
    for key, value in counter.items():
        print(f"{key}: {value}")
        total += value

    for key, value in counter.items():
        print(f"{key}: {value/ total}")
            


def response_len():
    with open("/Users/izabellemarianne/Desktop/prompt_injection/data/attack/glm-4-flash.jsonl") as f:
        sessions = 0
        lens = 0
        error_count = 0
        overflow = 0
        for line_num, line in enumerate(f):
            
            data = json.loads(line)
            responses = data["response"]
            if type(responses[0]) == str:
                if responses[0] == "error":
                    error_count += 1
                    continue
            for response in responses:
                if response["type"] == "ToolMessage":
                    sessions += 1
                    normalized_content = _normalize_value(response["content"])
                    lens += len(normalized_content)

                    if len(normalized_content) > 512:
                        with open("output.md", "a", encoding="utf-8") as f:
                            f.write(f"index:{line_num}, content: {normalized_content}")
                        overflow += 1

        print(f"Average attack response length: {lens / sessions}")
        print(f"Error count: {error_count}")
        print(f"Attack overflow count: {overflow}")

    with open("/Users/izabellemarianne/Desktop/prompt_injection/data/benign/glm-4-flash.jsonl") as f:
        sessions = 0
        lens = 0
        overflow = 0
        for line_num, line in enumerate(f):
            data = json.loads(line)
            responses = data["response"]
            for response in responses:
                if response["type"] == "ToolMessage":
                    sessions += 1

                    normalized_content = _normalize_value(response["content"])

                    lens += len(normalized_content)
                    if len(normalized_content) > 512:
                        overflow += 1
        print(f"Average benign response length: {lens / sessions}")
        print(f"Benign overflow count: {overflow}")

    
response_len()
attack_type()
target_counts()