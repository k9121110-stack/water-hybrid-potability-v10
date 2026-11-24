"""Transparent conservative expert rules for water screening."""
import math

FEATURES = ["ph","Hardness","Solids","Chloramines","Sulfate","Conductivity","Organic_carbon","Trihalomethanes","Turbidity"]

def inspect_input(data):
    errors, fired = [], []
    for name, value in data.items():
        if name not in FEATURES:
            errors.append({"rule_id":"R00","message":f"Белгісіз өріс: {name}"})
            continue
        if value is None:
            fired.append({"rule_id":f"R{19+FEATURES.index(name):02d}","message":f"{name} бос; Pipeline медианамен толтырады."})
            continue
        try: number = float(value)
        except (TypeError, ValueError):
            errors.append({"rule_id":"R00","message":f"{name} сан болуы керек."}); continue
        if not math.isfinite(number):
            errors.append({"rule_id":"R00","message":f"{name} шекті сан болуы керек."}); continue
        if name == "ph" and not 0 <= number <= 14:
            errors.append({"rule_id":"R01","message":"pH физикалық 0–14 шкаласынан тыс."})
        elif name != "ph" and number < 0:
            errors.append({"rule_id":f"R{FEATURES.index(name)+1:02d}","message":f"{name} теріс мән бола алмайды."})
    # WHO describes this as a usual operational range, not a health-based limit.
    ph = data.get("ph")
    if ph is not None and isinstance(ph,(int,float)) and math.isfinite(float(ph)) and not 6.5 <= float(ph) <= 8.5:
        fired.append({"rule_id":"R14","message":"pH 6.5–8.5 аралығынан тыс: жеке өзі қауіпсіздік қорытындысы емес."})
    # WHO value is for monochloramine; Kaggle's field does not specify the chemical species.
    chloramines=data.get("Chloramines")
    if chloramines is not None and isinstance(chloramines,(int,float)) and float(chloramines)>3:
        fired.append({"rule_id":"R15","message":"Хлорамин >3 mg/L: бірлік пен үлгі түрін зертханада растаңыз."})
    turbidity=data.get("Turbidity")
    if turbidity is not None and isinstance(turbidity,(int,float)) and float(turbidity)>1:
        fired.append({"rule_id":"R16","message":"Лайлылық >1 NTU: залалсыздандыру тиімділігін тексеру белгісі."})
    return errors, fired
