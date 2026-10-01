```python
# log rets so daily changes add up over time, first row is nan from diff
df['ret'] = np.log(df['close']).diff()
```
