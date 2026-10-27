"""Instructor script: generates the RAW (dirty) dataset for the capstone.
Seeded so results are reproducible. Keep private - it reveals the injected errors."""
import numpy as np, pandas as pd, random
rng = np.random.default_rng(2026); random.seed(2026)
N = 5000

# disease: (weight, mean_age, sd_age, mean_cost_GHS, sd_cost)
D = {
 "Malaria":(22,14,12,350,120), "Hypertension":(16,56,13,900,300),
 "Diabetes":(10,52,14,1400,450), "Typhoid":(9,24,12,500,160),
 "Pneumonia":(8,22,24,1100,350), "Tuberculosis":(6,38,14,1800,500),
 "Cholera":(4,28,16,650,200), "HIV/AIDS":(6,36,11,2200,600),
 "Asthma":(5,26,16,700,220), "Anaemia":(6,30,20,600,200),
 "Sickle Cell Disease":(4,17,12,1500,450), "Hepatitis B":(4,40,13,1700,500),
}
regions = ["Greater Accra","Ashanti","Western","Western North","Central","Eastern","Volta",
           "Oti","Northern","Savannah","North East","Upper East","Upper West","Bono",
           "Bono East","Ahafo"]
rw = np.array([20,18,7,3,8,9,6,2,6,2,2,4,3,5,3,2],float); rw/=rw.sum()

names = list(D); w = np.array([D[k][0] for k in names],float); w/=w.sum()
dis = rng.choice(names,N,p=w)
age = np.array([np.clip(rng.normal(D[d][1],D[d][2]),0,95) for d in dis]).round().astype(float)
cost = np.array([max(80,rng.normal(D[d][3],D[d][4])) for d in dis])
cost = (cost*(1+(age>60)*0.15)).round(2)
gender = rng.choice(["Male","Female"],N,p=[0.46,0.54])
region = rng.choice(regions,N,p=rw)
dates = pd.to_datetime("2022-01-01")+pd.to_timedelta(rng.integers(0,1095,N),unit="D")
df = pd.DataFrame({"Admission_Date":dates.strftime("%Y-%m-%d"),"Region":region,
                   "Age":age,"Gender":gender,"Disease":dis,"Treatment_Cost_GHS":cost})

# ---------- inject dirt ----------
def typo(s):
    i=random.randrange(len(s)); op=random.choice(["drop","swap","dup","sub"])
    if op=="drop" and len(s)>3: return s[:i]+s[i+1:]
    if op=="swap" and i<len(s)-1: return s[:i]+s[i+1]+s[i]+s[i+2:]
    if op=="dup": return s[:i]+s[i]+s[i:]
    return s[:i]+random.choice("aeiou")+s[i+1:]
fixed = {"Malaria":["Malaria","Malria","Malarria","malaria","MALARIA","Maleria"],
 "Typhoid":["Typhoid","Typhiod","Tyfoid","typhoid ","Typoid"],
 "Hypertension":["Hypertension","Hypertention","Hipertension","hypertension","High BP","Hypertenshun"],
 "Diabetes":["Diabetes","Diabetis","Diabeties","diabetes ","Diabates"],
 "Tuberculosis":["Tuberculosis","Tuberclosis","TB","Tubeculosis","tuberculosis"],
 "Cholera":["Cholera","Cholra","Colera","cholera "],
 "HIV/AIDS":["HIV/AIDS","HIV AIDS","HIV/Aids","Hiv/aids","HIV"],
 "Pneumonia":["Pneumonia","Pnuemonia","Neumonia","pneumonia","Pnemonia"],
 "Asthma":["Asthma","Asthama","Athsma","asthma ","Ashtma"],
 "Anaemia":["Anaemia","Anemia","Anaemea","anaemia","Anaemia "],
 "Sickle Cell Disease":["Sickle Cell Disease","Sickle cell","Sickle Cel Disease","SCD","sickle cell disease"],
 "Hepatitis B":["Hepatitis B","Hepatitis-B","Hepatits B","Hep B","hepatitis b"]}
mask = rng.random(N)<0.30
df.loc[mask,"Disease"] = [random.choice(fixed[d][1:]) for d in df.loc[mask,"Disease"]]

gv = {"Male":["M","male","MALE","Mle","Man","m "],"Female":["F","female","FEMALE","Femal","Fem","Woman","f"]}
mask = rng.random(N)<0.18
df.loc[mask,"Gender"] = [random.choice(gv[g]) for g in df.loc[mask,"Gender"]]

for col,p in [("Age",0.07),("Treatment_Cost_GHS",0.09)]:
    df.loc[rng.random(N)<p,col]=np.nan
df.loc[rng.random(N)<0.02,"Gender"]=np.nan
df.loc[rng.random(N)<0.015,"Region"]=np.nan
# region casing/whitespace noise
m = rng.random(N)<0.04
df.loc[m,"Region"] = df.loc[m,"Region"].astype(str).str.upper().replace("NAN",np.nan)
m = rng.random(N)<0.03
df.loc[m,"Region"] = df.loc[m,"Region"].astype(str).str.replace("Greater Accra","Gt. Accra").replace("nan",np.nan)

# a few impossible values + duplicates
idx = rng.choice(N,12,replace=False); df.loc[idx[:6],"Age"]=[250,-5,199,430,-1,150]
df.loc[idx[6:],"Treatment_Cost_GHS"]=[-500,-120,-900,-75,-60,-300]
df = pd.concat([df,df.sample(40,random_state=1)]).sample(frac=1,random_state=7).reset_index(drop=True)
df = df.iloc[:5000] if len(df)>5000 else df
df.to_csv("health_disease_raw.csv",index=False)
print(df.shape); print(df.isna().sum()); print(df.Disease.nunique(),df.Gender.nunique())
