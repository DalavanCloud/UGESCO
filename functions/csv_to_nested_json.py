from ugesco import *

# data doit être remplacé par le csv issu d'open refine
df = pd.read_csv("data/data.csv")

records = []
for key, grp in df.groupby(['PrimaryId', 'FirstName', 'LastName', 'City']):
    rec = get_nested_rec(key, grp)
    records.append(rec)

records = dict(data=records)

print(json.dumps(records, indent=4, cls=MyEncoder))
