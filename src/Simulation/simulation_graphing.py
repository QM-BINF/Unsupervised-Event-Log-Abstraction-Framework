import pandas as pd
from matplotlib import pyplot as plt

data = pd.read_csv("src/Simulation/LogGeneration.csv")
data.to_excel("src/Simulation/LogGeneration.xlsx")

plt.hist(data["activities"], bins = 15)
plt.title("Histogram of # Activity Classes (15 bins)")
plt.xlabel("Number of activity classes")
plt.ylabel("Count")
plt.savefig("src/Simulation/Hist_Activities.png")
plt.close()


plt.hist(data["simulation_duration"], bins = 15)
plt.title("Histogram of the Simulation Duration (15 bins)")
plt.xlabel("Simulation duration (in days)")
plt.ylabel("Count")
plt.savefig("src/Simulation/Hist_SimulationDuration.png")
plt.close()