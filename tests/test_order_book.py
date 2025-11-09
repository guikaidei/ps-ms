import pytest
from matching_engine.order_book import OrderBook
from matching_engine.order import Order


class TestOrderBook:
    """Testes simples para a classe OrderBook"""
    
    def test_create_order_book(self):
        """Testa a criação de um order book vazio"""
        book = OrderBook()
        
        assert len(book.bids) == 0
        assert len(book.asks) == 0
        assert len(book.orders_by_id) == 0
        assert book.next_id == 0
    
    def test_add_limit_buy_order(self, capsys):
        """Testa adicionar uma ordem de compra limit"""
        book = OrderBook()
        book.parse_command('limit buy 100.0 10.0')
        
        captured = capsys.readouterr()
        assert 'Limit buy order 0 placed at price 100.0 for qty 10.0' in captured.out
        assert len(book.bids) == 1
        assert book.next_id == 1
    
    def test_add_limit_sell_order(self, capsys):
        """Testa adicionar uma ordem de venda limit"""
        book = OrderBook()
        book.parse_command('limit sell 100.0 10.0')
        
        captured = capsys.readouterr()
        assert 'Limit sell order 0 placed at price 100.0 for qty 10.0' in captured.out
        assert len(book.asks) == 1
        assert book.next_id == 1
    
    def test_cancel_order(self, capsys):
        """Testa cancelar uma ordem"""
        book = OrderBook()
        book.parse_command('limit buy 100.0 10.0')
        book.parse_command('cancel 0')
        
        captured = capsys.readouterr()
        assert 'Order ID 0 cancelled.' in captured.out
        assert len(book.bids) == 0
        assert len(book.orders_by_id) == 0
    
    def test_cancel_nonexistent_order(self, capsys):
        """Testa cancelar uma ordem que não existe"""
        book = OrderBook()
        book.parse_command('cancel 999')
        
        captured = capsys.readouterr()
        assert 'Order ID 999 not found.' in captured.out
    
    def test_matching_buy_sell(self, capsys):
        """Testa matching entre ordem de compra e venda"""
        book = OrderBook()
        book.parse_command('limit sell 100.0 10.0')
        book.parse_command('limit buy 100.0 10.0')
        
        captured = capsys.readouterr()
        assert 'Trade, price: 100.0, qty: 10.0' in captured.out
        assert 'Limit order 1 fully executed' in captured.out
    
    def test_market_buy_order(self, capsys):
        """Testa ordem market de compra"""
        book = OrderBook()
        book.parse_command('limit sell 100.0 5.0')
        book.parse_command('market buy 5.0')
        
        captured = capsys.readouterr()
        assert 'Trade, price: 100.0, qty: 5.0' in captured.out
        assert 'Market order 1 executed successfully' in captured.out
    
    def test_market_sell_order(self, capsys):
        """Testa ordem market de venda"""
        book = OrderBook()
        book.parse_command('limit buy 100.0 5.0')
        book.parse_command('market sell 5.0')
        
        captured = capsys.readouterr()
        assert 'Trade, price: 100.0, qty: 5.0' in captured.out
        assert 'Market order 1 executed successfully' in captured.out
    
    def test_edit_order(self, capsys):
        """Testa editar uma ordem"""
        book = OrderBook()
        book.parse_command('limit buy 100.0 10.0')
        book.parse_command('edit 0 105.0 15.0')
        
        captured = capsys.readouterr()
        assert 'Order ID 0 cancelled.' in captured.out
        assert 'Order ID 0 edited to Price: 105.0, Qty: 15.0.' in captured.out
    
    def test_peg_buy_order(self, capsys):
        """Testa ordem peg de compra"""
        book = OrderBook()
        book.parse_command('limit buy 100.0 10.0')
        book.parse_command('peg buy 5.0')
        
        captured = capsys.readouterr()
        assert 'Pegged buy order 1 placed at price 100.0 for qty 5.0' in captured.out
    
    def test_peg_sell_order(self, capsys):
        """Testa ordem peg de venda"""
        book = OrderBook()
        book.parse_command('limit sell 100.0 10.0')
        book.parse_command('peg sell 5.0')
        
        captured = capsys.readouterr()
        assert 'Pegged sell order 1 placed at price 100.0 for qty 5.0' in captured.out
    
    def test_invalid_command(self):
        """Testa comando inválido"""
        book = OrderBook()
        
        with pytest.raises(ValueError, match='Invalid command'):
            book.parse_command('invalid')
    
    def test_empty_command(self):
        """Testa comando vazio"""
        book = OrderBook()
        
        with pytest.raises(ValueError, match='Empty command'):
            book.parse_command('')
    
    def test_print_empty_order_book(self, capsys):
        """Testa imprimir order book vazio"""
        book = OrderBook()
        book.parse_command('print')
        
        captured = capsys.readouterr()
        assert 'ORDER BOOK' in captured.out
        assert 'No buy orders' in captured.out
        assert 'No sell orders' in captured.out
    
    def test_print_order_book_with_orders(self, capsys):
        """Testa imprimir order book com ordens"""
        book = OrderBook()
        book.parse_command('limit buy 100.0 10.0')
        book.parse_command('limit sell 105.0 5.0')
        book.parse_command('print')
        
        captured = capsys.readouterr()
        assert 'ORDER BOOK' in captured.out
        assert 'Order ID:   0' in captured.out
        assert 'Order ID:   1' in captured.out
