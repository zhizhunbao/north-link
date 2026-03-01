# 单元测试报告

> 136 个用例 | 13 个测试文件 | 全部通过 | 耗时 3.01s

---

## 模块明细

### 认证模块 (auth)

| 文件 | 用例数 | 状态 |
|------|--------|------|
| test_auth.py | 8 | ✅ |
| test_auth_service.py | 9 | ✅ |
| test_schemas.py | 6 | ✅ |

覆盖场景:
- JWT access/refresh token 生成与验证
- token 类型交叉验证 (access 不能当 refresh 用)
- 登录认证 (成功/密码错误/用户不存在/账号禁用)
- 密码修改 (成功/旧密码错误/用户不存在)
- bcrypt 哈希生成与唯一性
- Pydantic schema 验证 (LoginRequest/PasswordChange/TokenResponse/UserResponse)

### 利润计算器 (calculator)

| 文件 | 用例数 | 状态 |
|------|--------|------|
| test_calculator.py | 11 | ✅ |

覆盖场景:
- 风险评估: 高利润→低风险, 中利润→中风险, 低利润→高风险, 边界值
- 利润计算: 盈利场景, 亏损场景, 数量乘数, 零收入防除零, 零成本最大利润
- 结果不可变性, 精度四舍五入

### 加密模块 (encryption)

| 文件 | 用例数 | 状态 |
|------|--------|------|
| test_encryption.py | 9 | ✅ |

覆盖场景:
- AES-256 加密返回 bytes, 密文长度 > 16 bytes
- 不同调用产生不同密文 (随机 IV)
- 加密→解密往返一致性
- 空字符串/Unicode/长字符串/特殊字符往返

### 异常处理 (exceptions)

| 文件 | 用例数 | 状态 |
|------|--------|------|
| test_exceptions.py | 9 | ✅ |

覆盖场景:
- NotFoundException (基本/带标识符/继承关系)
- DuplicateException (基本/带字段)
- ValidationException (默认 code/自定义 code)
- AuthenticationException (默认/自定义消息)

### 分页 (pagination)

| 文件 | 用例数 | 状态 |
|------|--------|------|
| test_pagination.py | 11 | ✅ |

覆盖场景:
- PaginationParams 默认值, offset 计算 (page 1/2/3)
- PaginatedResponse 总页数 (整除/有余数/零总数/page_size 为零/单条)

### 物流服务 (logistics)

| 文件 | 用例数 | 状态 |
|------|--------|------|
| test_logistics_service.py | 19 | ✅ |

覆盖场景:
- 货代 CRUD: 获取不存在/成功, 创建验证 est_days, 创建成功, 删除, 更新验证/成功
- 发货: 创建 shipment, 获取不存在, 状态机合法/非法转换, delivered 设置时间, tracking number
- 推荐: 构建推荐, pick_best 返回/跳过/过滤, 空列表, 返回 top 3

### 商户服务 (merchant)

| 文件 | 用例数 | 状态 |
|------|--------|------|
| test_merchant_service.py | 13 | ✅ |

覆盖场景:
- 获取详情 (不存在/成功), 分页列表
- 创建 (敏感字段加密/无可选字段)
- 更新 (不存在/成功/手机号加密), 删除 (不存在)
- 报价 (商户不存在/成功), 分类列表, 匹配空结果

### 比价服务 (price)

| 文件 | 用例数 | 状态 |
|------|--------|------|
| test_price_service.py | 13 | ✅ |

覆盖场景:
- 商品: 重复 SKU, 详情不存在, 更新不存在/成功, 删除不存在, 分类列表
- 价格记录: 商品不存在
- CSV 导入: 成功/缺少 SKU/商品不存在/空文件
- 收藏: 添加/移除

### 推荐服务 (recommendation)

| 文件 | 用例数 | 状态 |
|------|--------|------|
| test_recommendation_service.py | 21 | ✅ |

覆盖场景:
- 风险分类: 低/中/高风险 8 个边界值
- 评分: 加拿大价格为零/负数返回 None, 利润为负返回 None, 有效商品返回结果
- 评分组件权重, 历史加成, 利润率 clamp, 字段填充
- 服务: 无数据返回空, top N 推荐, 排除负利润, 日期格式, 按分数降序

### 设置服务 (settings)

| 文件 | 用例数 | 状态 |
|------|--------|------|
| test_settings_service.py | 7 | ✅ |

覆盖场景:
- 列表, 获取不存在/成功, 更新成功/不存在, 批量更新, 导出数据格式
