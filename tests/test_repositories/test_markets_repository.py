"""
Tests for MarketsRepository
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from repositories.markets_repository import MarketsRepository
from core.exceptions import DatabaseError


class TestMarketsRepository:
    """Test suite for MarketsRepository."""

    @pytest.fixture
    def repository(self, mock_db_manager):
        """Create a MarketsRepository instance with mocked database."""
        return MarketsRepository(mock_db_manager)

    @pytest.fixture
    def mock_cursor(self):
        """Create a mock cursor."""
        cursor = MagicMock()
        cursor.fetchone.return_value = None
        cursor.fetchall.return_value = []
        cursor.rowcount = 0
        return cursor

    @pytest.fixture
    def mock_conn_context(self, mock_db_manager, mock_cursor):
        """Setup mock connection context manager."""
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)

        mock_db_manager.get_connection.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_db_manager.get_connection.return_value.__exit__ = Mock(return_value=None)

        return mock_conn, mock_cursor

    # =========================================================================
    # create_tables Tests
    # =========================================================================

    @pytest.mark.unit
    def test_create_tables_success(self, repository, mock_conn_context):
        """Test successful table creation."""
        mock_conn, mock_cursor = mock_conn_context

        # Should not raise
        repository.create_tables()

        mock_cursor.execute.assert_called_once()

    @pytest.mark.unit
    def test_create_tables_failure(self, repository, mock_db_manager):
        """Test table creation failure."""
        mock_db_manager.get_connection.return_value.__enter__.side_effect = Exception("DB Error")

        with pytest.raises(DatabaseError):
            repository.create_tables()

    # =========================================================================
    # insert_stock_data Tests
    # =========================================================================

    @pytest.mark.unit
    def test_insert_stock_data_success(self, repository, mock_conn_context, sample_stock_data):
        """Test successful single stock insertion."""
        mock_conn, mock_cursor = mock_conn_context

        result = repository.insert_stock_data(sample_stock_data)

        assert result is True
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    @pytest.mark.unit
    def test_insert_stock_data_failure(self, repository, mock_conn_context, sample_stock_data):
        """Test stock insertion failure."""
        mock_conn, mock_cursor = mock_conn_context
        mock_cursor.execute.side_effect = Exception("Insert failed")

        with pytest.raises(DatabaseError):
            repository.insert_stock_data(sample_stock_data)

    # =========================================================================
    # insert_bulk_stock_data Tests
    # =========================================================================

    @pytest.mark.unit
    def test_insert_bulk_stock_data_success(self, repository, mock_conn_context, sample_stock_list):
        """Test successful bulk stock insertion."""
        mock_conn, mock_cursor = mock_conn_context

        result = repository.insert_bulk_stock_data(sample_stock_list)

        assert result == len(sample_stock_list)
        assert mock_cursor.execute.call_count == len(sample_stock_list)
        mock_conn.commit.assert_called_once()

    @pytest.mark.unit
    def test_insert_bulk_stock_data_empty_list(self, repository):
        """Test bulk insertion with empty list."""
        result = repository.insert_bulk_stock_data([])

        assert result == 0

    @pytest.mark.unit
    def test_insert_bulk_stock_data_failure(self, repository, mock_conn_context, sample_stock_list):
        """Test bulk insertion failure."""
        mock_conn, mock_cursor = mock_conn_context
        mock_cursor.execute.side_effect = Exception("Bulk insert failed")

        with pytest.raises(DatabaseError):
            repository.insert_bulk_stock_data(sample_stock_list)

    # =========================================================================
    # get_latest_stock_price Tests
    # =========================================================================

    @pytest.mark.unit
    def test_get_latest_stock_price_found(self, repository, mock_conn_context):
        """Test getting latest stock price when found."""
        mock_conn, mock_cursor = mock_conn_context
        mock_cursor.fetchone.return_value = (
            'AAPL', 'Apple Inc.', 175.50, 2.30, 1.33, 50000000, 2800000000000, datetime.now()
        )

        result = repository.get_latest_stock_price('AAPL')

        assert result is not None
        assert result['symbol'] == 'AAPL'
        assert result['price'] == 175.50

    @pytest.mark.unit
    def test_get_latest_stock_price_not_found(self, repository, mock_conn_context):
        """Test getting latest stock price when not found."""
        mock_conn, mock_cursor = mock_conn_context
        mock_cursor.fetchone.return_value = None

        result = repository.get_latest_stock_price('INVALID')

        assert result is None

    # =========================================================================
    # get_all_latest_stocks Tests
    # =========================================================================

    @pytest.mark.unit
    def test_get_all_latest_stocks_found(self, repository, mock_conn_context):
        """Test getting all latest stocks."""
        mock_conn, mock_cursor = mock_conn_context
        mock_cursor.fetchall.return_value = [
            ('AAPL', 'Apple Inc.', 175.50, 2.30, 1.33, 50000000, 2800000000000, datetime.now()),
            ('MSFT', 'Microsoft', 380.20, -1.50, -0.39, 30000000, 2700000000000, datetime.now()),
        ]

        result = repository.get_all_latest_stocks()

        assert len(result) == 2
        assert result[0]['symbol'] == 'AAPL'
        assert result[1]['symbol'] == 'MSFT'

    @pytest.mark.unit
    def test_get_all_latest_stocks_empty(self, repository, mock_conn_context):
        """Test getting all latest stocks when empty."""
        mock_conn, mock_cursor = mock_conn_context
        mock_cursor.fetchall.return_value = []

        result = repository.get_all_latest_stocks()

        assert result == []

    # =========================================================================
    # delete_old_records Tests
    # =========================================================================

    @pytest.mark.unit
    def test_delete_old_records_success(self, repository, mock_conn_context):
        """Test successful deletion of old records."""
        mock_conn, mock_cursor = mock_conn_context
        mock_cursor.rowcount = 50

        result = repository.delete_old_records(days=30)

        assert result == 50
        mock_conn.commit.assert_called_once()

    @pytest.mark.unit
    def test_delete_old_records_none_to_delete(self, repository, mock_conn_context):
        """Test deletion when no old records exist."""
        mock_conn, mock_cursor = mock_conn_context
        mock_cursor.rowcount = 0

        result = repository.delete_old_records(days=30)

        assert result == 0
