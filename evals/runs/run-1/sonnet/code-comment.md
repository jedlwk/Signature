# log returns so daily changes add up and are comparable across prices
df['ret'] = np.log(df['close']).diff()
