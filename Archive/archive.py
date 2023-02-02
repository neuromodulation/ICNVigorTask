#peak_speed_all_long = np.reshape(peak_speed_all, (n_par, 2, n_trials*2))

# Compute significance for each sample
#t_all, p_all = stats.ttest_rel(peak_speed_all_long[:,0,:], peak_speed_all_long[:,1,:], axis=0)
#sig_samp = np.where(p_all < 0.05)[0]

def fill_outliers(array):
    """Fill outliers in 1D array using the mean of surrounding non-outliers"""
    # Get index of outliers
    idx_outlier = np.where(np.abs(zscore(array)) > 3)[0]
    idx_non_outlier = np.where(np.abs(zscore(array)) <= 3)[0]
    # Fill each outlier with mean of closest non outlier
    for idx in idx_outlier:
        # Get index of the closest non-outlier before and after
        where_before = np.where(idx_non_outlier < idx)[0]
        where_after = np.where(idx_non_outlier > idx)[0]
        if len(where_before) > 0 and len(where_after) > 0:  # Middle sample
            array[idx] = np.mean([array[idx_non_outlier[where_before[-1]]], array[idx_non_outlier[where_after[0]]]])
        elif len(where_before) == 0 and len(where_after) > 0:  # First sample
            array[idx] = np.mean([array[idx_non_outlier[where_after[1]]], array[idx_non_outlier[where_after[0]]]])
        elif len(where_before) > 0 and len(where_after) == 0:  # Last sample
            array[idx] = np.mean([array[idx_non_outlier[where_before[-2]]], array[idx_non_outlier[where_before[-1]]]])
    return array

def plot_conds(array, var=None, color_slow="#00863b", color_fast="#3b0086"):
    """array = (conds x blocks x trials)
    Plot data divided into two conditions, if given add the variance as shaded area"""
    # Plot without the first 5 movements
    plt.plot(array[0, :, :].flatten()[5:], label="Slow", color=color_slow, linewidth=3)
    plt.plot(array[1, :, :].flatten()[5:], label="Fast", color=color_fast, linewidth=3)
    # Add line at 0
    plt.axhline(0, linewidth=2, color="black", linestyle="dashed")
    x = np.arange(len(array[0, :, :].flatten()[5:]))
    # add variance as shaded area
    if var is not None:
        plt.fill_between(x, array[0, :, :].flatten()[5:] - var[0, :, :].flatten()[5:], array[0, :, :].flatten()[5:] + var[0, :, :].flatten()[5:]
                         , color=color_slow, alpha =0.25)
        plt.fill_between(x, array[1, :, :].flatten()[5:] - var[1, :, :].flatten()[5:],
                         array[1, :, :].flatten()[5:] + var[1, :, :].flatten()[5:]
                         , color=color_fast, alpha=0.25)