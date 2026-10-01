```python
# log returns, they add up over time and scale better than raw price changes
df['ret'] = np.log(df['close']).diff()
```
