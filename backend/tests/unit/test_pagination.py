"""Unit tests for core/pagination.py."""

import pytest

from app.core.pagination import PaginatedResponse, PaginationParams


class TestPaginationParams:
    """Tests for PaginationParams."""

    def test_default_values(self):
        params = PaginationParams()
        assert params.page == 1
        assert params.page_size == 20

    def test_offset_page_1(self):
        params = PaginationParams(page=1, page_size=20)
        assert params.offset == 0

    def test_offset_page_2(self):
        params = PaginationParams(page=2, page_size=20)
        assert params.offset == 20

    def test_offset_page_3_size_10(self):
        params = PaginationParams(page=3, page_size=10)
        assert params.offset == 20

    def test_custom_page_size(self):
        params = PaginationParams(page=1, page_size=50)
        assert params.page_size == 50


class TestPaginatedResponse:
    """Tests for PaginatedResponse."""

    def test_total_pages_exact_division(self):
        resp = PaginatedResponse(items=[], total=40, page=1, page_size=20)
        assert resp.total_pages == 2

    def test_total_pages_with_remainder(self):
        resp = PaginatedResponse(items=[], total=41, page=1, page_size=20)
        assert resp.total_pages == 3

    def test_total_pages_zero_total(self):
        resp = PaginatedResponse(items=[], total=0, page=1, page_size=20)
        assert resp.total_pages == 0

    def test_total_pages_page_size_zero(self):
        resp = PaginatedResponse(items=[], total=10, page=1, page_size=0)
        assert resp.total_pages == 0

    def test_items_stored_correctly(self):
        items = [1, 2, 3]
        resp = PaginatedResponse(items=items, total=3, page=1, page_size=20)
        assert resp.items == items

    def test_total_pages_single_item(self):
        resp = PaginatedResponse(items=[], total=1, page=1, page_size=20)
        assert resp.total_pages == 1
