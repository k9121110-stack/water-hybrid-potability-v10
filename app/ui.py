import requests
import streamlit as st

st.set_page_config(page_title="Су сапасын скринингтеу",page_icon="💧")
st.title("Ауыз су сапасын алдын ала скринингтеу")
st.caption("Оқу жобасы. Зертханалық талдауды немесе ресми қауіпсіздік қорытындысын алмастырмайды.")
api=st.text_input("API мекенжайы","http://127.0.0.1:8000")
fields={"ph":"pH","Hardness":"Қаттылық (mg/L)","Solids":"Еріген заттар (mg/L)","Chloramines":"Хлораминдер (mg/L)",
"Sulfate":"Сульфат (mg/L)","Conductivity":"Өткізгіштік (μS/cm)","Organic_carbon":"Органикалық көміртек (mg/L)",
"Trihalomethanes":"Тригалометандар (μg/L)","Turbidity":"Лайлылық (NTU)"}
with st.form("sample"):
    values={}
    for key,label in fields.items():
        raw=st.text_input(label,value="",help="Бос қалдырсаңыз Pipeline медианамен толтырады.")
        if raw.strip():
            try: values[key]=float(raw)
            except ValueError: st.error(f"{label}: сан енгізіңіз.")
        else: values[key]=None
    submitted=st.form_submit_button("Бағалау")
if submitted:
    try:
        response=requests.post(api.rstrip("/")+"/explain",json=values,timeout=20)
        if response.ok:
            result=response.json(); st.subheader(result["decision"])
            if result["probability_potable"] is not None: st.metric("Potable ықтималдығы",f'{result["probability_potable"]:.1%}')
            st.write(result["explanation"])
            if result["fired_rules"]: st.json(result["fired_rules"])
        else: st.error(f"API қатесі {response.status_code}: {response.text}")
    except requests.RequestException as exc: st.error(f"API-ға қосыла алмады: {exc}")
