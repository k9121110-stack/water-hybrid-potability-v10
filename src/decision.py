"""Expert rules -> ML probability -> conservative post-rules."""
from .rules import FEATURES, inspect_input

def decide(data, artifact):
    errors, fired = inspect_input(data)
    threshold=float(artifact.get("threshold",0.5))
    if errors:
        return {"decision":"invalid_input","probability_potable":None,"threshold":threshold,"fired_rules":errors+fired,"important_features":[],
                "explanation":"Кіріс дерегін түзетіп қайта жіберіңіз."}
    import pandas as pd
    frame=pd.DataFrame([{feature:data.get(feature) for feature in FEATURES}],columns=FEATURES)
    probability=float(artifact["model"].predict_proba(frame)[0][1])
    margin=float(artifact.get("review_margin",0.05))
    if abs(probability-threshold)<=margin:
        label="manual_review"
        fired.append({"rule_id":"R17","message":"Ықтималдық шекке жақын; маманның тексеруі қажет."})
    else:
        label="potable_screening" if probability>=threshold else "not_potable_screening"
    if label=="potable_screening" and {x["rule_id"] for x in fired}.intersection({"R14","R15","R16"}):
        label="manual_review"
        fired.append({"rule_id":"R18","message":"ML оң нәтиже берді, бірақ операциялық белгі маман тексеруін талап етеді."})
    medians=artifact.get("medians",{})
    effects=[]
    for feature in FEATURES:
        changed=frame.copy()
        if feature in medians: changed.loc[0,feature]=medians[feature]
        altered=float(artifact["model"].predict_proba(changed)[0][1])
        effects.append({"feature":feature,"probability_change":probability-altered,"absolute_change":abs(probability-altered)})
    top_features=sorted(effects,key=lambda x:x["absolute_change"],reverse=True)[:3]
    return {"decision":label,"probability_potable":probability,"threshold":threshold,"fired_rules":fired,"important_features":top_features,
            "explanation":"Үздік белгілер: енгізілген мәнді оқу жиынындағы медианамен алмастырғандағы модель ықтималдығының өзгерісі (жеке әсердің жуықтауы, себеп-салдар емес). Бұл скрининг қана; қауіпсіздікті зертхана анықтайды."}