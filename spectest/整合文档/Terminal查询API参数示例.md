# 航站楼查询API参数示例

## 1. 单个航班出发航站楼查询

**接口：** `POST /api/v1/query/terminal/departure/match`

**请求体示例：**

```json
{
  "flightNumber": "3001",
  "flightSuffix": null,
  "departureAirport": "CAN",
  "arrivalAirport": null,
  "departureDate": "2026-03-24",
  "segment": null,
  "international": null
}
```

**完整参数示例（包含所有字段）：**

```json
{
  "flightNumber": "3001",
  "flightSuffix": "A",
  "departureAirport": "CAN",
  "arrivalAirport": "PEK",
  "departureDate": "2026-03-24",
  "segment": "CANPEK",
  "international": "I"
}
```

**字段说明：**

| 字段 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| flightNumber | String | 是 | 航班号（3-4位数字） | "3001" |
| flightSuffix | String | 否 | 航班号后缀 | "A" 或 null |
| departureAirport | String | 是 | 起飞航站（IATA三字代码） | "CAN" |
| arrivalAirport | String | 否 | 到达航站（IATA三字代码） | "PEK" 或 null |
| departureDate | String | 是 | 查询日期（yyyy-MM-dd） | "2026-03-24" |
| segment | String | 否 | 航段（起飞航站-到达航站） | "CANPEK" |
| international | String | 否 | 国际国内标识：I-国际，D-国内 | "I" 或 "D" |

**响应示例：**

```json
{
  "flightNumber": "3001",
  "departureTerminal": "T1",
  "arrivalTerminal": null,
  "departureMatchedLevel": "TERMINAL_R1",
  "arrivalMatchedLevel": null,
  "success": true,
  "message": "匹配成功"
}
```

---

## 2. 单个航班到达航站楼查询

**接口：** `POST /api/v1/query/terminal/arrival/match`

**请求体示例：**

```json
{
  "flightNumber": "3001",
  "flightSuffix": null,
  "departureAirport": null,
  "arrivalAirport": "PEK",
  "departureDate": "2026-03-24",
  "segment": null,
  "international": null
}
```

**完整参数示例：**

```json
{
  "flightNumber": "3001",
  "flightSuffix": "A",
  "departureAirport": "CAN",
  "arrivalAirport": "PEK",
  "departureDate": "2026-03-24",
  "segment": "CANPEK",
  "international": "I"
}
```

**响应示例：**

```json
{
  "flightNumber": "3001",
  "departureTerminal": null,
  "arrivalTerminal": "T3",
  "departureMatchedLevel": null,
  "arrivalMatchedLevel": "TERMINAL_R1",
  "success": true,
  "message": "匹配成功"
}
```

---

## 3. 批量出发航站楼查询

**接口：** `POST /api/v1/query/terminal/departure/batch`

**请求体示例（2个航班）：**

```json
{
  "requests": [
    {
      "flightNumber": "3001",
      "flightSuffix": null,
      "departureAirport": "CAN",
      "arrivalAirport": null,
      "departureDate": "2026-03-24",
      "segment": null,
      "international": null
    },
    {
      "flightNumber": "3002",
      "flightSuffix": "A",
      "departureAirport": "PEK",
      "arrivalAirport": null,
      "departureDate": "2026-03-24",
      "segment": null,
      "international": "I"
    }
  ]
}
```

**批量查询示例（5个航班）：**

```json
{
  "requests": [
    {
      "flightNumber": "3001",
      "flightSuffix": null,
      "departureAirport": "CAN",
      "arrivalAirport": null,
      "departureDate": "2026-03-24",
      "segment": null,
      "international": "D"
    },
    {
      "flightNumber": "3002",
      "flightSuffix": null,
      "departureAirport": "PEK",
      "arrivalAirport": null,
      "departureDate": "2026-03-24",
      "segment": null,
      "international": "I"
    },
    {
      "flightNumber": "3003",
      "flightSuffix": "B",
      "departureAirport": "SZX",
      "arrivalAirport": null,
      "departureDate": "2026-03-24",
      "segment": null,
      "international": "D"
    },
    {
      "flightNumber": "3004",
      "flightSuffix": null,
      "departureAirport": "SHA",
      "arrivalAirport": null,
      "departureDate": "2026-03-24",
      "segment": null,
      "international": "D"
    },
    {
      "flightNumber": "3005",
      "flightSuffix": "C",
      "departureAirport": "CTU",
      "arrivalAirport": null,
      "departureDate": "2026-03-24",
      "segment": null,
      "international": "D"
    }
  ]
}
```

**响应示例：**

```json
[
  {
    "flightNumber": "3001",
    "departureTerminal": "T1",
    "arrivalTerminal": null,
    "departureMatchedLevel": "TERMINAL_R1",
    "arrivalMatchedLevel": null,
    "success": true,
    "message": "匹配成功"
  },
  {
    "flightNumber": "3002",
    "departureTerminal": "T2",
    "arrivalTerminal": null,
    "departureMatchedLevel": "TERMINAL_R5",
    "arrivalMatchedLevel": null,
    "success": true,
    "message": "匹配成功"
  }
]
```

---

## 4. 批量到达航站楼查询

**接口：** `POST /api/v1/query/terminal/arrival/batch`

**请求体示例（3个航班）：**

```json
{
  "requests": [
    {
      "flightNumber": "3001",
      "flightSuffix": null,
      "departureAirport": null,
      "arrivalAirport": "PEK",
      "departureDate": "2026-03-24",
      "segment": null,
      "international": null
    },
    {
      "flightNumber": "3002",
      "flightSuffix": null,
      "departureAirport": "CAN",
      "arrivalAirport": "PVG",
      "departureDate": "2026-03-24",
      "segment": null,
      "international": "I"
    },
    {
      "flightNumber": "3003",
      "flightSuffix": "B",
      "departureAirport": "SZX",
      "arrivalAirport": "SHA",
      "departureDate": "2026-03-24",
      "segment": "SZXSHA",
      "international": "D"
    }
  ]
}
```

---

## 5. cURL测试命令

### 出发航站楼查询

```bash
curl -X POST "http://localhost:8080/api/v1/query/terminal/departure/match" \
  -H "Content-Type: application/json" \
  -d '{
    "flightNumber": "3001",
    "flightSuffix": null,
    "departureAirport": "CAN",
    "arrivalAirport": null,
    "departureDate": "2026-03-24",
    "segment": null,
    "international": null
  }'
```

### 到达航站楼查询

```bash
curl -X POST "http://localhost:8080/api/v1/query/terminal/arrival/match" \
  -H "Content-Type: application/json" \
  -d '{
    "flightNumber": "3001",
    "flightSuffix": null,
    "departureAirport": null,
    "arrivalAirport": "PEK",
    "departureDate": "2026-03-24",
    "segment": null,
    "international": null
  }'
```

### 批量出发航站楼查询

```bash
curl -X POST "http://localhost:8080/api/v1/query/terminal/departure/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {
        "flightNumber": "3001",
        "departureAirport": "CAN",
        "departureDate": "2026-03-24"
      },
      {
        "flightNumber": "3002",
        "departureAirport": "PEK",
        "departureDate": "2026-03-24"
      }
    ]
  }'
```

### 批量到达航站楼查询

```bash
curl -X POST "http://localhost:8080/api/v1/query/terminal/arrival/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {
        "flightNumber": "3001",
        "arrivalAirport": "PEK",
        "departureDate": "2026-03-24"
      },
      {
        "flightNumber": "3002",
        "arrivalAirport": "PVG",
        "departureDate": "2026-03-24"
      }
    ]
  }'
```

---

## 6. 常见查询场景

### 场景1：查询国内航班出发航站楼
```json
{
  "flightNumber": "3001",
  "flightSuffix": null,
  "departureAirport": "CAN",
  "arrivalAirport": null,
  "departureDate": "2026-03-24",
  "segment": null,
  "international": "D"
}
```

### 场景2：查询国际航班到达航站楼
```json
{
  "flightNumber": "3001",
  "flightSuffix": "A",
  "departureAirport": null,
  "arrivalAirport": "PEK",
  "departureDate": "2026-03-24",
  "segment": null,
  "international": "I"
}
```

### 场景3：查询指定航段航站楼
```json
{
  "flightNumber": "3001",
  "flightSuffix": null,
  "departureAirport": "CAN",
  "arrivalAirport": "PEK",
  "departureDate": "2026-03-24",
  "segment": "CANPEK",
  "international": null
}
```

### 场景4：带后缀航班查询
```json
{
  "flightNumber": "3001",
  "flightSuffix": "A",
  "departureAirport": "CAN",
  "arrivalAirport": null,
  "departureDate": "2026-03-24",
  "segment": null,
  "international": null
}
```

### 场景5：批量查询不同航站
```json
{
  "requests": [
    {
      "flightNumber": "3001",
      "departureAirport": "CAN",
      "departureDate": "2026-03-24",
      "international": "D"
    },
    {
      "flightNumber": "3002",
      "departureAirport": "PEK",
      "departureDate": "2026-03-24",
      "international": "I"
    },
    {
      "flightNumber": "3003",
      "departureAirport": "SZX",
      "departureDate": "2026-03-24",
      "international": "D"
    }
  ]
}
```

---

## 7. 参数校验规则

- **flightNumber**: 必填，3-4位数字
- **departureAirport**: 出发查询时必填
- **arrivalAirport**: 到达查询时必填
- **departureDate**: 必填，格式 `yyyy-MM-dd`
- **flightSuffix**: 可选
- **segment**: 可选，航段代码
- **international**: 可选，I（国际）或 D（国内）

---

## 8. 错误响应示例

### 参数校验失败
```json
{
  "timestamp": "2026-03-24T10:30:00",
  "status": 400,
  "error": "Bad Request",
  "message": "航班号不能为空",
  "path": "/api/v1/query/terminal/departure/match"
}
```

### 无匹配结果
```json
{
  "flightNumber": "9999",
  "departureTerminal": null,
  "arrivalTerminal": null,
  "departureMatchedLevel": null,
  "arrivalMatchedLevel": null,
  "success": false,
  "message": "无匹配规则"
}
```

---

## 9. Postman测试集合

### 导入以下JSON为Postman Collection

```json
{
  "info": {
    "name": "航站楼查询API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "单个出发航站楼查询",
      "request": {
        "method": "POST",
        "header": [],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"flightNumber\": \"3001\",\n  \"flightSuffix\": null,\n  \"departureAirport\": \"CAN\",\n  \"arrivalAirport\": null,\n  \"departureDate\": \"2026-03-24\",\n  \"segment\": null,\n  \"international\": null\n}"
        },
        "url": {
          "raw": "http://localhost:8080/api/v1/query/terminal/departure/match",
          "protocol": "http"
        }
      }
    },
    {
      "name": "单个到达航站楼查询",
      "request": {
        "method": "POST",
        "header": [],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"flightNumber\": \"3001\",\n  \"flightSuffix\": null,\n  \"departureAirport\": null,\n  \"arrivalAirport\": \"PEK\",\n  \"departureDate\": \"2026-03-24\",\n  \"segment\": null,\n  \"international\": null\n}"
        },
        "url": {
          "raw": "http://localhost:8080/api/v1/query/terminal/arrival/match",
          "protocol": "http"
        }
      }
    },
    {
      "name": "批量出发航站楼查询",
      "request": {
        "method": "POST",
        "header": [],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"requests\": [\n    {\n      \"flightNumber\": \"3001\",\n      \"departureAirport\": \"CAN\",\n      \"departureDate\": \"2026-03-24\"\n    },\n    {\n      \"flightNumber\": \"3002\",\n      \"departureAirport\": \"PEK\",\n      \"departureDate\": \"2026-03-24\"\n    }\n  ]\n}"
        },
        "url": {
          "raw": "http://localhost:8080/api/v1/query/terminal/departure/batch",
          "protocol": "http"
        }
      }
    },
    {
      "name": "批量到达航站楼查询",
      "request": {
        "method": "POST",
        "header": [],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"requests\": [\n    {\n      \"flightNumber\": \"3001\",\n      \"arrivalAirport\": \"PEK\",\n      \"departureDate\": \"2026-03-24\"\n    },\n    {\n      \"flightNumber\": \"3002\",\n      \"arrivalAirport\": \"PVG\",\n      \"departureDate\": \"2026-03-24\"\n    }\n  ]\n}"
        },
        "url": {
          "raw": "http://localhost:8080/api/v1/query/terminal/arrival/batch",
          "protocol": "http"
        }
      }
    }
  ]
}
```
