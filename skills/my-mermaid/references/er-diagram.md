# ER Diagram

## 选型

数据库表关系、实体关联。Schema 定义、ORM 模型中的外键分析。

## 语法

```
erDiagram
  USER ||--o{ ORDER: places
  ORDER ||--|{ ORDER_ITEM: contains
  PRODUCT ||--o{ ORDER_ITEM: "ordered in"

  USER {
    int id PK
    varchar name
    varchar email UK
    timestamp created_at
  }
  ORDER {
    int id PK
    int user_id FK
    decimal total
    varchar status
  }
```

- `||--o{` 一对多，`}o--o{` 多对多，`||--||` 一对一
- `PK` 主键，`FK` 外键，`UK` 唯一键
- 关系标签放在 `:` 后，描述业务语义（用双引号包裹含空格的标签）
- 属性使用数据库类型（int/varchar/text/timestamp/decimal/bool）

## 配色

erDiagram 自动着色，不支持 classDef。同一实体的属性自动同色，不同实体色相区分。

## 大小限制

超 12 个实体时提示拆分（按业务边界，如"用户域"/"订单域"）。每个实体属性不超过 8 个，省略次要字段。
