# log returns so daily changes add up to total return
df['ret'] = np.log(df['close']).diff()