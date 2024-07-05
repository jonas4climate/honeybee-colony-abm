import matplotlib.pyplot as plt
import math
import numpy as np
import pandas as pd

FILE = "D:\\ABM\\abm-project\\continuous_model\\sensitivity_analysis\\04-07 average_dist_0.csv"

df = pd.read_csv(FILE)

df.head()
plt.scatter(df['Run'], df['extracted_nectar'])
plt.show()

plt.scatter(df["Run"], df["average distance"])
plt.show()

plt.scatter(df["average distance"], df["extracted_nectar"])
plt.show()