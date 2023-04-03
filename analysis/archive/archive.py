box = plt.boxplot(feature_all, showfliers=False, patch_artist=True, labels=["Slow", "Fast", "All"])
colors = [color_slow, color_fast, "black"]
for patch, median, color in zip(box['boxes'], box["medians"], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.5)
    patch.set_edgecolor(color)
    median.set_color(color)

# Add points for each participants and liens connecting the dots
for dat in feature_all:
    plt.plot(1, dat[0], marker='o', markersize=3, color=color_slow)
    plt.plot(2, dat[1], marker='o', markersize=3, color=color_fast)
    plt.plot(3, dat[2], marker='o', markersize=3, color="black")

    # Add line connecting the points
    plt.plot([1, 2], dat[:2], color="black", linewidth=0.5, alpha=0.5)
    plt.plot([2, 3], dat[1:], color="black", linewidth=0.5, alpha=0.5)
    #plt.plot([1, 3], dat[[0, 2]], color="black", linewidth=0.5, alpha=0.5)

# Add statistics
z, p = scipy.stats.wilcoxon(x=feature_all[:, 0], y=feature_all[:, 1])
sig = "bold" if p < 0.05 else "regular"
plt.text(1.5, np.max(feature_all) + 10, f"p = {np.round(p, 6)}", weight=sig)
plt.plot([1, 2], [np.max(feature_all) + 5, np.max(feature_all) + 5], color="black")

z, p = scipy.stats.wilcoxon(x=feature_all[:, 1], y=feature_all[:, 2])
sig = "bold" if p < 0.05 else "regular"
plt.text(2.5, np.max(feature_all) + 10, f"p = {np.round(p, 6)}", weight=sig)

z, p = scipy.stats.wilcoxon(x=feature_all[:, 0], y=feature_all[:, 2])
sig = "bold" if p < 0.05 else "regular"
plt.text(2, np.max(feature_all) + 20, f"p = {np.round(p, 6)}", weight=sig)

# Add y axis
feature_name_space = feature_name.replace("_", " ")
plt.ylabel(f"{feature_name_space}", fontsize=14)

# Alternative
x_names = ["Slow", "Fast", "All"]
plt.figure(figsize=(9, 3))
ax = sb.boxplot(x=dim1.ravel(), y=mean_activity.ravel(), hue=dim3.ravel(), showfliers=False)
sb.stripplot(x=dim1.ravel(), y=mean_activity.ravel(), hue=dim3.ravel(), dodge=True, ax=ax)
plt.ylabel("Pathway activity [%]", fontsize=14)
ax.tick_params(labelsize=12)
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles=[(handles[0], handles[2]), (handles[1], handles[3])],
          labels=['Direct', 'Indirect'],
          loc='lower left', handlelength=4,
          handler_map={tuple: HandlerTuple(ndivide=None)}, bbox_to_anchor=(1, 0.78))

# Add statistics
add_stat_annotation(ax, x=dim1.ravel(), y=mean_activity.ravel(), hue=dim3.ravel(),
                    box_pairs=[(("Go", "Direct"), ("No-Go", "Direct")),
                                 (("Go", "Indirect"), ("No-Go", "Indirect")),
                                 (("Go", "Direct"), ("Go", "Indirect")),
                                 (("No-Go", "Direct"), ("No-Go", "Indirect"))
                                ],
                    test='t-test_paired', text_format='simple', loc='inside', verbose=2)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.subplots_adjust(left=0.35, right=0.65)
