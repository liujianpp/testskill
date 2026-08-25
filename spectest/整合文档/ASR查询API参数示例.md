# ASR查询API参数示例

## 1. 单个航班ASR查询

**接口：** `POST /api/v1/query/asr/match`

**请求体示例：**

```json
{
  "flightNumber": "3001",
  "flightSuffix": null,
  "departureAirport": "CAN",
  "departureDate": "2026-03-24",
  "office": null
}
```

**完整参数示例（包含所有字段）：**

```json
{
  "flightNumber": "3001",
  "flightSuffix": "A",
  "departureAirport": "CAN",
  "departureDate": "2026-03-24",
  "office": "CAN001"
}
```

**字段说明：**

| 字段 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| flightNumber | String | 是 | 航班号（3-4位数字） | "3001" |
| flightSuffix | String | 否 | 航班号后缀 | "A" 或 null |
| departureAirport | String | 是 | 起飞航站（IATA三字代码） | "CAN" |
| departureDate | String | 是 | 查询日期（yyyy-MM-dd） | "2026-03-24" |
| office | String | 否 | OFFICE号 | "CAN001" 或 null |

**响应示例：**

```json
{
  "flightNumber": "3001",
  "asrValue": "Y",
  "matchedLevel": "ASR_R1",
  "allowSeatSelection": true,
  "success": true,
  "message": "匹配成功"
}
```

---

## 2. 批量ASR查询

**接口：** `POST /api/v1/query/asr/batch`

**请求体示例（2个航班）：**

```json
{
  "requests": [
    {
      "flightNumber": "3001",
      "flightSuffix": null,
      "departureAirport": "CAN",
      "departureDate": "2026-03-24",
      "office": null
    },
    {
      "flightNumber": "3002",
      "flightSuffix": "A",
      "departureAirport": "PEK",
      "departureDate": "2026-03-24",
      "office": "PEK001"
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
      "departureDate": "2026-03-24",
      "office": null
    },
    {
      "flightNumber": "3002",
      "flightSuffix": null,
      "departureAirport": "PEK",
      "departureDate": "2026-03-24",
      "office": null
    },
    {
      "flightNumber": "3003",
      "flightSuffix": "B",
      "departureAirport": "SZX",
      "departureDate": "2026-03-24",
      "office": null
    },
    {
      "flightNumber": "3004",
      "flightSuffix": null,
      "departureAirport": "SHA",
      "departureDate": "2026-03-24",
      "office": "SHA001"
    },
    {
      "flightNumber": "3005",
      "flightSuffix": "C",
      "departureAirport": "CTU",
      "departureDate": "2026-03-24",
      "office": null
    }
  ]
}
```

**响应示例：**

```json
[
  {
    "flightNumber": "3001",
    "asrValue": "Y",
    "matchedLevel": "ASR_R1",
    "allowSeatSelection": true,
    "success": true,
    "message": "匹配成功"
  },
  {
    "flightNumber": "3002",
    "asrValue": "N",
    "matchedLevel": "ASR_R2",
    "allowSeatSelection": false,
    "success": true,
    "message": "匹配成功"
  }
]
```

---

## 3. cURL测试命令

### 单个查询测试

```bash
curl -X POST "http://localhost:8080/api/v1/query/asr/match" \
  -H "Content-Type: application/json" \
  -d '{
    "flightNumber": "3001",
    "flightSuffix": null,
    "departureAirport": "CAN",
    "departureDate": "2026-03-24",
    "office": null
  }'
```

### 批量查询测试

```bash
curl -X POST "http://localhost:8080/api/v1/query/asr/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {
        "flightNumber": "3001",
        "flightSuffix": null,
        "departureAirport": "CAN",
        "departureDate": "2026-03-24",
        "office": null
      },
      {
        "flightNumber": "3002",
        "flightSuffix": "A",
        "departureAirport": "PEK",
        "departureDate": "2026-03-24",
        "office": "PEK001"
      }
    ]
  }'
```

---

## 4. 常见查询场景

### 场景1：查询无后缀航班
```json
{
  "flightNumber": "3001",
  "flightSuffix": null,
  "departureAirport": "CAN",
  "departureDate": "2026-03-24",
  "office": null
}
```

### 场景2：查询带后缀航班
```json
{
  "flightNumber": "3001",
  "flightSuffix": "A",
  "departureAirport": "CAN",
  "departureDate": "2026-03-24",
  "office": null
}
```

### 场景3：指定OFFICE号查询
```json
{
  "flightNumber": "3001",
  "flightSuffix": null,
  "departureAirport": "CAN",
  "departureDate": "2026-03-24",
  "office": "CAN001"
}
```

### 场景4：批量查询不同航站
```json
{
  "requests": [
    {"flightNumber": "3001", "departureAirport": "CAN", "departureDate": "2026-03-24"},
    {"flightNumber": "3002", "departureAirport": "PEK", "departureDate": "2026-03-24"},
    {"flightNumber": "3003", "departureAirport": "SZX", "departureDate": "2026-03-24"}
  ]
}
```

---

## 5. 参数校验规则

- **flightNumber**: 必填，3-4位数字，格式符合正则 `^\d{3,4}$`
- **departureAirport**: 必填，IATA三字代码
- **departureDate**: 必填，格式 `yyyy-MM-dd`
- **flightSuffix**: 可选，不填或填null表示无后缀
- **office**: 可选，OFFICE号

---

## 6. 错误响应示例

### 参数校验失败
```json
{
  "timestamp": "2026-03-24T10:30:00",
  "status": 400,
  "error": "Bad Request",
  "message": "航班号格式错误，应为3-4位数字",
  "path": "/api/v1/query/asr/match"
}
```

### 无匹配结果
```json
{
  "flightNumber": "9999",
  "asrValue": null,
  "matchedLevel": null,
  "allowSeatSelection": null,
  "success": false,
  "message": "ASR参数缺失"
}
```
