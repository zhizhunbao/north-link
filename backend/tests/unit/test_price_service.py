"""Unit tests for PriceService."""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import DuplicateException, NotFoundException
from app.core.pagination import PaginationParams
from app.modules.price.schemas import (
    PriceRecordCreate,
    ProductCreate,
    ProductUpdate,
)
from app.modules.price.service import PriceService


def make_mock_product(product_id: uuid.UUID | None = None, sku: str = "SKU-001"):
    p = MagicMock()
    p.id = product_id or uuid.uuid4()
    p.name = "Test Product"
    p.sku = sku
    p.brand = "Brand A"
    p.condition = "new"
    p.attributes = {}
    p.category = None
    p.price_records = []
    p.created_at = datetime.now(timezone.utc)
    return p


class TestPriceServiceProducts:
    """Tests for product CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_product_duplicate_sku(self, mock_db):
        existing = make_mock_product()
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=existing)
        )
        service = PriceService(mock_db)
        data = ProductCreate(
            name="Duplicate",
            sku="SKU-001",
            brand="Brand",
            condition="new",
            category_id=uuid.uuid4(),
        )
        with pytest.raises(DuplicateException):
            await service.create_product(data)

    @pytest.mark.asyncio
    async def test_get_product_detail_not_found(self, mock_db):
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=None)
        )
        service = PriceService(mock_db)
        with pytest.raises(NotFoundException):
            await service.get_product_detail(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_update_product_not_found(self, mock_db):
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=None)
        )
        service = PriceService(mock_db)
        data = ProductUpdate(name="New Name")
        with pytest.raises(NotFoundException):
            await service.update_product(uuid.uuid4(), data)

    @pytest.mark.asyncio
    async def test_update_product_success(self, mock_db):
        product = make_mock_product()
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=product)
        )
        service = PriceService(mock_db)
        data = ProductUpdate(name="Updated Product")
        result = await service.update_product(product.id, data)
        assert product.name == "Updated Product"

    @pytest.mark.asyncio
    async def test_delete_product_not_found(self, mock_db):
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=None)
        )
        service = PriceService(mock_db)
        with pytest.raises(NotFoundException):
            await service.delete_product(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_get_categories(self, mock_db):
        cats = [MagicMock(), MagicMock()]
        mock_db.execute.return_value = MagicMock(
            scalars=MagicMock(
                return_value=MagicMock(all=MagicMock(return_value=cats))
            )
        )
        service = PriceService(mock_db)
        result = await service.get_categories()
        assert len(result) == 2


class TestPriceServicePriceRecords:
    """Tests for price record operations."""

    @pytest.mark.asyncio
    async def test_create_price_record_product_not_found(self, mock_db):
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=None)
        )
        service = PriceService(mock_db)
        data = PriceRecordCreate(
            product_id=uuid.uuid4(),
            source="manual",
            region="CA",
            price=99.99,
            currency="CAD",
            price_type="retail",
        )
        with pytest.raises(NotFoundException):
            await service.create_price_record(data)


class TestPriceServiceCSVImport:
    """Tests for CSV import functionality."""

    @pytest.mark.asyncio
    async def test_csv_import_success(self, mock_db):
        product = make_mock_product(sku="IPHONE-001")
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=product)
        )
        service = PriceService(mock_db)
        csv_content = (
            "product_sku,source,region,price,currency,price_type\n"
            "IPHONE-001,web,CA,999.99,CAD,retail\n"
        )
        result = await service.import_csv(csv_content)
        assert result.total_rows == 1
        assert result.success_count == 1
        assert result.error_count == 0

    @pytest.mark.asyncio
    async def test_csv_import_missing_sku(self, mock_db):
        service = PriceService(mock_db)
        csv_content = (
            "product_sku,source,region,price,currency,price_type\n"
            ",web,CA,999.99,CAD,retail\n"  # empty SKU
        )
        result = await service.import_csv(csv_content)
        assert result.total_rows == 1
        assert result.error_count == 1
        assert "missing product_sku" in result.errors[0]

    @pytest.mark.asyncio
    async def test_csv_import_product_not_found(self, mock_db):
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=None)
        )
        service = PriceService(mock_db)
        csv_content = (
            "product_sku,source,region,price,currency,price_type\n"
            "NONEXISTENT,web,CA,999.99,CAD,retail\n"
        )
        result = await service.import_csv(csv_content)
        assert result.error_count == 1
        assert "not found" in result.errors[0]

    @pytest.mark.asyncio
    async def test_csv_import_empty_file(self, mock_db):
        service = PriceService(mock_db)
        csv_content = "product_sku,source,region,price,currency,price_type\n"
        result = await service.import_csv(csv_content)
        assert result.total_rows == 0
        assert result.success_count == 0


class TestPriceServiceFavorites:
    """Tests for favorite toggle."""

    @pytest.mark.asyncio
    async def test_toggle_favorite_add(self, mock_db):
        # No existing favorite
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=None)
        )
        service = PriceService(mock_db)
        result = await service.toggle_favorite(uuid.uuid4(), uuid.uuid4())
        assert result is True  # favorited
        mock_db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_toggle_favorite_remove(self, mock_db):
        existing_fav = MagicMock()
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=existing_fav)
        )
        mock_db.delete = AsyncMock()
        service = PriceService(mock_db)
        result = await service.toggle_favorite(uuid.uuid4(), uuid.uuid4())
        assert result is False  # removed
        mock_db.delete.assert_called_once_with(existing_fav)
