```python
# Daily log return: ln(close_t) - ln(close_t-1). The first row is NaN because it has no previous day.
df['ret'] = np.log(df['close']).diff()
```
