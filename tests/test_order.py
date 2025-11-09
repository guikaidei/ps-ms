import pytest
from matching_engine.order import Order


class TestOrder:
    """Testes simples para a classe Order"""
    
    def test_create_limit_order(self):
        """Testa a criação de uma ordem limit"""
        order = Order(id_order=1, type='limit', side='buy', price=100.0, qty=10.0)
        
        assert order.id_order == 1
        assert order.type == 'limit'
        assert order.side == 'buy'
        assert order.price == 100.0
        assert order.qty == 10.0
    
    def test_create_market_order(self):
        """Testa a criação de uma ordem market"""
        order = Order(id_order=2, type='market', side='sell', price=-1, qty=5.0)
        
        assert order.id_order == 2
        assert order.type == 'market'
        assert order.side == 'sell'
        assert order.price == -1
        assert order.qty == 5.0
    
    def test_create_peg_order(self):
        """Testa a criação de uma ordem peg"""
        order = Order(id_order=3, type='peg', side='buy', price=99.5, qty=15.0)
        
        assert order.id_order == 3
        assert order.type == 'peg'
        assert order.side == 'buy'
        assert order.price == 99.5
        assert order.qty == 15.0
    
    def test_modify_order_qty(self):
        """Testa modificação da quantidade de uma ordem"""
        order = Order(id_order=4, type='limit', side='buy', price=100.0, qty=10.0)
        order.qty = 20.0
        
        assert order.qty == 20.0
    
    def test_modify_order_price(self):
        """Testa modificação do preço de uma ordem"""
        order = Order(id_order=5, type='limit', side='sell', price=100.0, qty=10.0)
        order.price = 105.0
        
        assert order.price == 105.0
