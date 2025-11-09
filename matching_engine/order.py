class Order:
    """
    Representa uma ordem no sistema de matching.
    
    Attributes:
        id_order (int): Identificador único da ordem
        type (str): Tipo da ordem ('limit', 'market', 'peg')
        side (str): Lado da ordem ('buy' ou 'sell')
        price (float): Preço da ordem (-1 para market orders)
        qty (float): Quantidade da ordem
    """
    
    def __init__(self, id_order, type, side, price, qty):
        """
        Inicializa uma nova ordem.
        
        Args:
            id_order (int): Identificador único da ordem
            type (str): Tipo da ordem ('limit', 'market', 'peg')
            side (str): Lado da ordem ('buy' ou 'sell')
            price (float): Preço da ordem (-1 para market orders)
            qty (float): Quantidade da ordem
        """
        self.id_order = id_order
        self.type = type
        self.side = side
        self.price = price
        self.qty = qty