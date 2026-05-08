# P7 Excel导出与基础操作日志

## 阶段目标

P7 完成档案列表按当前筛选条件导出 Excel，并补齐登录、导出和关键业务操作日志，便于后续追溯。

本阶段同时新增管理员可见的操作日志页面，用于查看系统关键操作记录。

## 已实现范围

- 档案 Excel 导出接口：`GET /api/archives/export`
- 导出支持当前筛选条件：关键词、台账类型、内部档案类型、归档部门、状态
- 导出字段与当前纸质/电子台账字段一致
- 导出文件名包含日期时间
- 前端档案列表“导出Excel”按钮真实下载
- 登录成功写入操作日志
- 档案新增、编辑、软删除继续写入操作日志
- 用户管理和系统设置继续写入操作日志
- 导出 Excel 写入操作日志
- 操作日志分页查询接口：`GET /api/operation-logs`
- 管理员操作日志页面

## 权限规则

- 档案列表导出需要登录，不限制管理员。
- 操作日志接口和操作日志页面仅管理员可访问。
- 普通用户仍可查看档案列表和数据统计，但看不到“操作日志”菜单。

## 导出字段

```text
纸质档案：档案编号、档案名称、纸质份数、档案类型、内部档案类型、状态、保管期限、归档部门、归档人、归档日期、存放位置、责任人。

电子档案：档案编号、档案名称、档案类型、内部档案类型、状态、保管期限、归档部门、归档人、归档日期、存放路径、责任人。
```

## 接口约定

档案导出：

```text
GET /api/archives/export?archive_medium=paper&keyword=&internal_archive_type=&department_id=&status_id=
GET /api/archives/export?archive_medium=electronic&keyword=&internal_archive_type=&department_id=&status_id=
```

返回 `.xlsx` 文件流，不使用统一 JSON 响应包装。

操作日志列表：

```text
GET /api/operation-logs?keyword=&module=&operation_type=&date_from=&date_to=&page=1&page_size=10
```

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "items": [],
    "total": 0,
    "page": 1,
    "page_size": 10
  }
}
```

日志对象包含：

```json
{
  "id": 1,
  "user": {
    "id": 1,
    "username": "admin",
    "real_name": "admin"
  },
  "module": "档案管理",
  "operation_type": "导出Excel",
  "target_id": "archives_export",
  "target_name": "档案目录导出",
  "operation_detail": "导出档案目录 120 条，筛选条件：全部档案",
  "ip_address": "127.0.0.1",
  "created_at": "2026-05-07T10:00:00+08:00"
}
```

## 验收结果

- 后端 Python 编译检查通过。
- Alembic 当前 head 可升级。
- 登录成功会写入登录日志。
- 无 Token 导出返回 401。
- 登录用户可导出 `.xlsx`。
- 管理员可查询操作日志。
- 普通用户查询操作日志返回 403。
- 前端生产构建通过。

## 下一阶段入口

P8 进入 Docker 化与本地部署，整理可部署版本和内网服务器部署基础。
