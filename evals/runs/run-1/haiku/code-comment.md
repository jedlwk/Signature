# log returns from close price
df['ret'] = np.log(df['close']).diff()
