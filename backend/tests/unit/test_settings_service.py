"""Unit tests for SettingsService."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import NotFoundException
from app.modules.settings.service import SettingsService


def make_mock_setting(key: str = "test_key", value: str = "test_value"):
    s = MagicMock()
    s.key = key
    s.value = value
    s.description = "A test setting"
    return s


class TestSettingsService:
    """Tests for SettingsService."""

    @pytest.mark.asyncio
    async def test_list_settings(self, mock_db):
        settings = [make_mock_setting("k1"), make_mock_setting("k2")]
        mock_db.execute.return_value = MagicMock(
            scalars=MagicMock(
                return_value=MagicMock(all=MagicMock(return_value=settings))
            )
        )
        service = SettingsService(mock_db)
        result = await service.list_settings()
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_setting_not_found(self, mock_db):
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=None)
        )
        service = SettingsService(mock_db)
        with pytest.raises(NotFoundException):
            await service.get_setting("nonexistent_key")

    @pytest.mark.asyncio
    async def test_get_setting_success(self, mock_db):
        setting = make_mock_setting("company_name", "NorthLink")
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=setting)
        )
        service = SettingsService(mock_db)
        result = await service.get_setting("company_name")
        assert result.value == "NorthLink"

    @pytest.mark.asyncio
    async def test_update_setting_success(self, mock_db):
        setting = make_mock_setting("theme", "light")
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=setting)
        )
        service = SettingsService(mock_db)
        result = await service.update_setting("theme", "dark")
        assert setting.value == "dark"
        mock_db.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_setting_not_found(self, mock_db):
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=None)
        )
        service = SettingsService(mock_db)
        with pytest.raises(NotFoundException):
            await service.update_setting("nonexistent", "value")

    @pytest.mark.asyncio
    async def test_bulk_update_existing(self, mock_db):
        setting = make_mock_setting("lang", "zh")
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=setting)
        )
        service = SettingsService(mock_db)
        result = await service.bulk_update({"lang": "en"})
        assert setting.value == "en"




    @pytest.mark.asyncio
    async def test_export_data_format(self, mock_db):
        settings = [
            make_mock_setting("company", "NorthLink"),
            make_mock_setting("currency", "CAD"),
        ]
        mock_db.execute.return_value = MagicMock(
            scalars=MagicMock(
                return_value=MagicMock(all=MagicMock(return_value=settings))
            )
        )
        service = SettingsService(mock_db)
        result = await service.export_data()
        assert "exported_at" in result
        assert "settings" in result
        assert len(result["settings"]) == 2
        assert result["settings"][0]["key"] == "company"
