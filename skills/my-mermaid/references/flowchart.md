# Flowchart & Block

## 选型

- **flowchart**：有分支、循环、条件路由时用。必须指定方向。
- **block**：无分支的方块级概览，节点数少（< 12）。

## 方向

必须指定 `TB`（上→下，适合流程步骤）或 `LR`（左→右，适合宽架构图）。

## 节点形状

```
A[矩形：实体/组件]    B(圆角：开始/结束)
C[(圆柱：数据库)]     D{菱形：决策/分支}
E[[方形：用户操作]]   F((圆形：连接点))
G[/平行四边形：输入输出/]
```

无特殊语义时默认用矩形 `[...]`。

## 连接与标签

```
A --> B         实线箭头
A -- 标签 --> B  带标签
A -.-> B        虚线（异步/可选）
A ==> B         粗线（强调）
A -->|是| B     条件标签
A -->|否| C
```

## subgraph 分组

```
subgraph 前端
  A[React] --> B[API Client]
end
subgraph 后端
  C[Server] --> D[(Database)]
end
B --> C
```

## 配色（classDef + class）

每种语义使用预定义的软色调。选择匹配语义的 class 应用即可，不必全用。

```
classDef frontend fill:#dbeafe,stroke:#3b82f6,color:#1e3a5f
classDef backend fill:#d1fae5,stroke:#10b981,color:#064e3b
classDef database fill:#ccfbf1,stroke:#14b8a6,color:#134e4a
classDef danger fill:#fee2e2,stroke:#ef4444,color:#7f1d1d
classDef warning fill:#fef3c7,stroke:#f59e0b,color:#78350f
classDef success fill:#dcfce7,stroke:#22c55e,color:#14532d
classDef infra fill:#ede9fe,stroke:#8b5cf6,color:#3b0764
classDef external fill:#f3f4f6,stroke:#9ca3af,color:#1f2937
classDef highlight fill:#fce7f3,stroke:#ec4899,color:#831843
classDef muted fill:#f9fafb,stroke:#d1d5db,color:#6b7280
```

配色语义对照：
- `frontend`：前端、UI、客户端
- `backend`：后端服务、API、业务逻辑
- `database`：数据库、缓存、消息队列等存储
- `danger`：错误路径、安全漏洞、已废弃
- `warning`：待定、风险、需关注
- `success`：最佳路径、已通过、推荐
- `infra`：基础设施、部署、配置
- `external`：第三方服务、外部系统
- `highlight`：核心节点、关键路径
- `muted`：次要节点、辅助信息

应用方式：`class A,B,C frontend`，一个节点可叠加多个 class（如 `class X frontend,highlight`）。

## block 特殊语法

```
block-beta
  columns 3
  Frontend:1 Backend:1 Database:1
```

block 不支持 classDef，直接用默认配色。

## 大小限制

- **flowchart**：超 30 节点或 40 边时提示拆分。按 subgraph 边界拆为多张子图。
- **block**：超 12 块时提示改用 flowchart。
