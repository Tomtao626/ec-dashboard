# 边缘计算管理平台(ec-dashboard)

## 环境搭建

安装django库

```bash
pip install django -i https://pypi.douban.com/simple
```

安装djangorestframework
```bash
pip install djangorestframework -i https://pypi.douban.com/simple
```
安装djangorestframework-simplejwt
```bash
pip install djangorestframework-simplejwt -i https://pypi.douban.com/simple
```

安装 kubernetes库
```bash
pip install kubernetes -i https://pypi.douban.com/simple
```

## 功能开发

### 节点管理
- 查看节点情况（单个/列表，节点情况包括：基本信息和运行状况）
- 获取节点纳管的Token
- 节点标签管理（用于调度Pod）

### 应用管理
- 创建Pod
- 删除Pod  
- 查看Pod（单个/指定节点的列表，节点情况包括：基本信息和运行状况）

### 设备管理
- 创建DeviceModel（指定名称以及字段信息）
- 删除DeviceModel
- 更新DeviceModel（字段信息）
- 查询（单个/列表）

---

- 创建Device（指定名称、DeviceModel名称、节点信息）
- 删除Device
- 更新Device（更新字段的期望值）
- 查询（单个/列表）

### 路由管理
- 创建RuleEndpoint（名称、路由类型、配置信息）
- 删除RuleEndpoint
- 更新RuleEndpoint（路由类型、配置信息）
- 查询（单个/列表）
---
- 创建Rule（名称、起点和终点的路由、配置信息）
- 删除Rule
- 更新Rule（起点和终点的路由、配置信息）
- 查询（单个/列表）

### 模型管理
- 模型上传
- 模型展示（单个/列表）
- 模型下发（从云到边下发模型）

### 数据管理
- 数据上传
- 数据展示