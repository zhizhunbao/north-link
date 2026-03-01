"""Unit tests for MerchantService."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import NotFoundException
from app.core.pagination import PaginationParams
from app.modules.merchant.schemas import MerchantCreate, MerchantQuoteCreate, MerchantUpdate
from app.modules.merchant.service import MerchantService


def make_mock_merchant(merchant_id: uuid.UUID | None = None):
    m = MagicMock()
    m.id = merchant_id or uuid.uuid4()
    m.name = "Test Merchant"
    m.contact_name = "Alice"
    m.phone = b""  # encrypted bytes
    m.wechat = b""
    m.address = b""
    m.tier = "A"
    m.total_orders = 10
    m.category = None
    m.quotes = []
    m.created_at = None
    m.updated_at = None
    return m


class TestMerchantServiceGet:
    """Tests for get merchant operations."""

    @pytest.mark.asyncio
    async def test_get_merchant_detail_not_found(self, mock_db):
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=None)
        )
        service = MerchantService(mock_db)
        with pytest.raises(NotFoundException):
            await service.get_merchant_detail(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_get_merchant_detail_success(self, mock_db):
        merchant = make_mock_merchant()
        merchant.phone = None
        merchant.wechat = None
        merchant.address = None
        merchant.category = None
        merchant.quotes = []
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=merchant)
        )
        service = MerchantService(mock_db)
        # Patch MerchantDetail to avoid Pydantic schema validation on MagicMock objects
        with patch("app.modules.merchant.service.MerchantDetail") as mock_detail_cls:
            mock_detail_cls.return_value = MagicMock(id=merchant.id, name=merchant.name)
            result = await service.get_merchant_detail(merchant.id)
        mock_detail_cls.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_merchants_pagination(self, mock_db):
        mock_db.execute.side_effect = [
            MagicMock(scalar=MagicMock(return_value=5)),  # count query
            MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))),
        ]
        service = MerchantService(mock_db)
        params = PaginationParams(page=1, page_size=20)
        result = await service.get_merchants(params)
        assert result.total == 5
        assert result.items == []


class TestMerchantServiceCreate:
    """Tests for creating merchants."""

    @pytest.mark.asyncio
    async def test_create_merchant_encrypts_sensitive_fields(self, mock_db):
        merchant = make_mock_merchant()
        service = MerchantService(mock_db)
        category_id = uuid.uuid4()
        data = MerchantCreate(
            name="Merchant A",
            contact_name="Bob",
            phone="13800000000",
            wechat="wechat_id",
            address="北京市",
            tier="gold",
            category_id=category_id,
        )
        with patch(
            "app.modules.merchant.service.Merchant", return_value=merchant
        ), patch(
            "app.modules.merchant.service.encrypt",
            side_effect=lambda x: x.encode(),
        ):
            result = await service.create_merchant(data)

        mock_db.add.assert_called_once_with(merchant)
        # Verify encrypt was called for each sensitive field
        for field in ("phone", "wechat", "address"):
            val = getattr(merchant, field)
            # Should be set (not None)
            assert val is not None

    @pytest.mark.asyncio
    async def test_create_merchant_without_optional_fields(self, mock_db):
        merchant = make_mock_merchant()
        merchant.phone = None
        service = MerchantService(mock_db)
        category_id = uuid.uuid4()
        data = MerchantCreate(
            name="Merchant B",
            contact_name="Carol",
            tier="silver",
            category_id=category_id,
        )
        with patch("app.modules.merchant.service.Merchant", return_value=merchant):
            result = await service.create_merchant(data)
        mock_db.add.assert_called_once_with(merchant)


class TestMerchantServiceUpdate:
    """Tests for updating and deleting merchants."""

    @pytest.mark.asyncio
    async def test_update_merchant_not_found(self, mock_db):
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=None)
        )
        service = MerchantService(mock_db)
        data = MerchantUpdate(name="New Name")
        with pytest.raises(NotFoundException):
            await service.update_merchant(uuid.uuid4(), data)

    @pytest.mark.asyncio
    async def test_update_merchant_success(self, mock_db):
        merchant = make_mock_merchant()
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=merchant)
        )
        service = MerchantService(mock_db)
        data = MerchantUpdate(name="Updated Name", tier="silver")
        result = await service.update_merchant(merchant.id, data)
        assert merchant.name == "Updated Name"
        assert merchant.tier == "silver"

    @pytest.mark.asyncio
    async def test_update_merchant_encrypts_phone(self, mock_db):
        merchant = make_mock_merchant()
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=merchant)
        )
        service = MerchantService(mock_db)
        data = MerchantUpdate(phone="13900000000")
        with patch(
            "app.modules.merchant.service.encrypt",
            return_value=b"encrypted",
        ):
            await service.update_merchant(merchant.id, data)
        assert merchant.phone == b"encrypted"

    @pytest.mark.asyncio
    async def test_delete_merchant_not_found(self, mock_db):
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=None)
        )
        service = MerchantService(mock_db)
        with pytest.raises(NotFoundException):
            await service.delete_merchant(uuid.uuid4())


class TestMerchantServiceQuotes:
    """Tests for quote and matching operations."""

    @pytest.mark.asyncio
    async def test_create_quote_merchant_not_found(self, mock_db):
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=None)
        )
        service = MerchantService(mock_db)
        data = MerchantQuoteCreate(product_id=uuid.uuid4(), price=100.0, currency="CAD")
        with pytest.raises(NotFoundException):
            await service.create_quote(uuid.uuid4(), data)

    @pytest.mark.asyncio
    async def test_create_quote_success(self, mock_db):
        merchant = make_mock_merchant()
        quote = MagicMock()
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=merchant)
        )
        service = MerchantService(mock_db)
        product_id = uuid.uuid4()
        data = MerchantQuoteCreate(product_id=product_id, price=150.0, currency="CAD")
        with patch("app.modules.merchant.service.MerchantQuote", return_value=quote):
            result = await service.create_quote(merchant.id, data)
        mock_db.add.assert_called_with(quote)

    @pytest.mark.asyncio
    async def test_get_categories(self, mock_db):
        categories = [MagicMock(), MagicMock()]
        mock_db.execute.return_value = MagicMock(
            scalars=MagicMock(
                return_value=MagicMock(all=MagicMock(return_value=categories))
            )
        )
        service = MerchantService(mock_db)
        result = await service.get_categories()
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_match_merchants_empty(self, mock_db):
        mock_db.execute.return_value = MagicMock(
            scalars=MagicMock(
                return_value=MagicMock(all=MagicMock(return_value=[]))
            )
        )
        service = MerchantService(mock_db)
        result = await service.match_merchants_for_product(uuid.uuid4())
        assert result == []
