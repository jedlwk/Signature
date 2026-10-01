# log ret from close, so daily changes add up over time
df['ret'] = np.log(df['close']).diff()
