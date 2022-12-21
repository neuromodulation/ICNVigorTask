#peak_speed_all_long = np.reshape(peak_speed_all, (n_par, 2, n_trials*2))

# Compute significance for each sample
#t_all, p_all = stats.ttest_rel(peak_speed_all_long[:,0,:], peak_speed_all_long[:,1,:], axis=0)
#sig_samp = np.where(p_all < 0.05)[0]
