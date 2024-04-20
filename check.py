import pandas as pd

df = pd.read_csv("saved_states/saved_state_200_2.csv")
duplicates = df.duplicated(subset=["x_coordinate", "y_coordinate"], keep=False)

if duplicates.any():
    print("Duplicate x,y coordinates found:")
    print(df[duplicates])
else:
    print("No duplicate x,y coordinates found.")
