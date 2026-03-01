# 严重问题 (Critical)

> 需要在部署前修复

---

## CR-001 — JWT Secret 硬编码默认值

- 文件: `backend/app/config.py`
- 行: `jwt_secret: str = "dev-secret-change-in-production"`
- 风险: 如果生产环境未设置 `JWT_SECRET` 环境变量，将使用硬编码的默认值，攻击者可伪造任意 JWT token
- 建议: 生产环境启动时校验 `jwt_secret` 不等于默认值，或在 `app_env != "development"` 时强制要求设置

```python
# config.py — 添加启动校验
from pydantic import model_validator

class Settings(BaseSettings):
    ...
    @model_validator(mode="after")
    def _check_production_secrets(self):
        if self.app_env == "production" and self.jwt_secret == "dev-secret-change-in-production":
            raise ValueError("JWT_SECRET must be set in production")
        return self
```

---

## CR-002 — Encryption Key 硬编码 + 截断/填充逻辑

- 文件: `backend/app/core/encryption.py`
- 行: `key[:32].ljust(32, b"\0")`
- 风险:
  1. 默认 `encryption_key = "dev-encryption-key-32-bytes-long!"` 是 33 字节，被截断为 32 字节，但如果用户设置了短密钥，会用 `\0` 填充，削弱加密强度
  2. 生产环境未设置时使用默认密钥，所有加密数据可被解密
- 建议: 同 CR-001，生产环境强制校验；密钥长度不足时抛出异常而非填充

---

## CR-003 — MerchantService.delete_merchant 执行了 3 次查询

- 文件: `backend/app/modules/merchant/service.py`
- 方法: `delete_merchant`
- 问题: 同一个 merchant 被查询了 3 次（第一次检查存在、第二次无用的 select、第三次再查一遍才 delete）

```python
# 当前代码 (冗余)
async def delete_merchant(self, merchant_id: uuid.UUID) -> None:
    result = await self.db.execute(select(Merchant).where(Merchant.id == merchant_id))
    if not result.scalar_one_or_none():
        raise NotFoundException("Merchant", str(merchant_id))
    await self.db.execute(select(Merchant).where(Merchant.id == merchant_id))  # ← 无用
    merchant = (await self.db.execute(select(Merchant).where(Merchant.id == merchant_id))).scalar_one()
    await self.db.delete(merchant)

# 建议修复
async def delete_merchant(self, merchant_id: uuid.UUID) -> None:
    result = await self.db.execute(select(Merchant).where(Merchant.id == merchant_id))
    merchant = result.scalar_one_or_none()
    if not merchant:
        raise NotFoundException("Merchant", str(merchant_id))
    await self.db.delete(merchant)
```
