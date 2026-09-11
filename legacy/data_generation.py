import itertools
import random
import pandas as pd
from typing import Dict, List
from legacy.template_generation import _ATTACK_TEMPLATES, _BENIGN_TEMPLATES
from sklearn.model_selection import GroupShuffleSplit

SF_TEMPLATES: List[Dict[str, object]] = _BENIGN_TEMPLATES + _ATTACK_TEMPLATES

SF_ATTACK_FAMILIES = (
    "split_exfil",
    "context_laundering",
    "privilege_drift",
    "staged_burst",
)

SF_HARD_BENIGN_RATIO = 0.5


def expand_template(template, max_variants=34):

    stages = []
    for stage in template["stages"]:

        prompts = stage["prompts"]
        externals = stage["externals"]

        prod = list(itertools.product(prompts, externals))

        # per stage how many variations is contained within this nested list
        stages.append(prod)


    # now that we have the all the stages required for the all the stages
    # we can determine all the possible versions of a session using permutation
    # product of len(variations) 

    possible = 1
    for stage in stages:
        possible *= len(stage)

    if possible <= max_variants:
        # no change, the turns can be included as is 
        new = []
        for combo in itertools.product(*stages):
           new.append(_build_row(combo, template))
        return new
    else:
        # we need to randomly pick max_variants
        # we can use random.sample to pick max_variants from the product of stages
        random_combos = random.sample(list(itertools.product(*stages)), max_variants)
        new =  [_build_row(combo, template) for combo in random_combos]
        return new

def _build_row(combo, template):
    new = {key: template[key] for key in template.keys() if key != "stages"}
    new["stages"] = [{"prompt": p, "external": e} for p, e in combo]
    return new

def expand_templates(templates) -> List[Dict[str, object]]:
    new_templates = []
    for template in templates:
        new_templates.extend(expand_template(template))
    print(new_templates[0])
    return pd.DataFrame(new_templates)


def train_test_split(df: pd.DataFrame, train_ratio=0.8, seed=42, group_by="template_id") -> pd.DataFrame:
    """Split the DataFrame into train and test sets based on the specified ratio."""
    def grouped_split(rows, test_size):
        gss = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=seed)
        train_idx, test_idx = next(gss.split(rows, groups=rows[group_by]))
        return rows.iloc[train_idx], rows.iloc[test_idx]

    training, testing, validation = [], [], []
    for label, rows in df.groupby('label'):
        remainder, test_rows = grouped_split(rows, test_size=1 - train_ratio)
        train_rows, val_rows = grouped_split(remainder, test_size=0.1)  # 10% of the remainder for validation

        training.append(train_rows)
        validation.append(val_rows) 
        testing.append(test_rows)   
        return train_rows, val_rows, test_rows
    
    test_df = pd.concat(testing).reset_index(drop=True)
    train_df = pd.concat(training).reset_index(drop=True)
    val_df = pd.concat(validation).reset_index(drop=True)
    return train_df, val_df, test_df

new_attack = expand_templates(_ATTACK_TEMPLATES)
print(len(new_attack))
new_attack2 = expand_templates(_BENIGN_TEMPLATES)
print(len(new_attack2))
        


# def sf_validate_templates() -> None:
#     for split in ("train", "val", "test"):
#         has_benign = any(
#             t["split"] == split and int(t["label"]) == 0 and not t["hard_benign"]
#             for t in SF_TEMPLATES
#         )
#         has_hard = any(
#             t["split"] == split and int(t["label"]) == 0 and t["hard_benign"]
#             for t in SF_TEMPLATES
#         )
#         has_attacker = any(
#             t["split"] == split and int(t["label"]) == 1 for t in SF_TEMPLATES
#         )
#         if not (has_benign and has_hard and has_attacker):
#             raise ValueError(
#                 f"Split={split!r} missing a template class "
#                 f"(benign={has_benign}, hard={has_hard}, attacker={has_attacker})."
#             )
#     families_in_train = {
#         str(t["attack_type"]) for t in SF_TEMPLATES if t["split"] == "train" and int(t["label"]) == 1
#     }
#     missing = set(SF_ATTACK_FAMILIES) - families_in_train
#     if missing:
#         raise ValueError(f"Train split missing attack families: {sorted(missing)}")



# def sf_prompt_pool_overlap() -> Dict[str, int]:
#     """Return counts of how often each prompt string appears in benign vs attack templates.

#     Diagnostic helper: the design is session-fragile iff every attack prompt
#     also appears in at least one benign template (count_benign >= 1 for every
#     prompt used in attacks).
#     """
#     benign_prompts: Dict[str, int] = {}
#     attack_prompts: Dict[str, int] = {}
#     for template in SF_TEMPLATES:
#         bucket = attack_prompts if int(template["label"]) == 1 else benign_prompts
#         for stage in template["stages"]:
#             for prompt in stage["prompts"]:
#                 bucket[prompt] = bucket.get(prompt, 0) + 1

#     unique_attack_prompts = set(attack_prompts.keys())
#     attack_only = {p: attack_prompts[p] for p in unique_attack_prompts if p not in benign_prompts}
#     return {
#         "n_unique_benign_prompts": len(benign_prompts),
#         "n_unique_attack_prompts": len(attack_prompts),
#         "n_attack_prompts_not_in_benign": len(attack_only),
#         "attack_only_examples": attack_only,
#     }


# sf_validate_templates()