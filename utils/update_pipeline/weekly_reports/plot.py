import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
months = ["Jan\n'20","Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec","Jan\n'21","Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def make_plot():
    df = pd.read_excel("/Users/kristophernolte/Documents/AG_Thorn/stats_repo.xlsx")
    ax = plt.subplot(111)
    ax.plot(df["Month"],df["All"], color="steelblue", linestyle="dashed", label="total number")
    ax.bar(df["Month"],df["Releases"], color="darkseagreen", edgecolor="black", label="monthly releases", lw=1)
    plt.xticks(df["Month"], months[:len(df["Month"])],rotation=0)
    plt.fill_between(df["Month"],df["All"], alpha = 0.5, color="steelblue")
    plt.ylim(0)
    plt.xlim(1,len(df["Month"])+0.5)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    plt.legend()
    #plt.show()
    plt.title("")
    plt.savefig("SARS-CoV-release-plot.svg", transparent = True)
    plt.savefig("SARS-CoV-release-plot.png", dpi=300)


make_plot()