# Pie / XY Chart

## Pie

占比分布、构成分析。

```
pie showData
  title 代码语言占比
  "Python": 45
  "JavaScript": 30
  "Shell": 15
  "其他": 10
```

- `showData` 显示具体数值（可选，数据差异小时有助于读图）
- 标签简短（≤ 6 字），用双引号包裹
- 数值为绝对值，渲染时自动转为百分比

### 配色

pie 各扇区自动分配颜色，不支持 classDef。如需控制色序，将重要/需突出的项放前面（前几项的默认色辨识度更高）。

### 大小限制

超 8 个扇区时提示精简——小占比项合并为"其他"。

---

## XY Chart

性能 benchmark 对比、多指标柱状图。

```
xychart-beta
  title "Web 框架 QPS 对比 (req/s)"
  x-axis ["Express", "Fastify", "Hono", "Elysia"]
  y-axis "QPS" 0 --> 60000
  bar [12000, 28000, 35000, 45000]
  line [14000, 26000, 34000, 46000]
```

- `bar` 柱状图，`line` 折线图——可同时使用
- x-axis 类别用方括号 `["A", "B"]`，y-axis `最小值 --> 最大值`
- 数值用绝对数字，不写单位

### 配色

xychart 不支持 classDef。可用 `bar` + `line` 区分两组数据（如实际值 vs 目标值）。

### 大小限制

x-axis 超 8 个类别时提示精简或分组。y-axis 范围应恰好覆盖数据极值（留约 10% 头部空间）。
