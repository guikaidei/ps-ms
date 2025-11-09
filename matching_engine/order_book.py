from sortedcontainers import SortedDict
from matching_engine.order import Order

class OrderBook:
    """
    Implementa um livro de ordens (order book) com matching engine.
    
    O OrderBook mantém dois dicionários ordenados: bids (ordens de compra) e asks (ordens de venda).
    Implementa lógica de matching para executar trades quando ordens compatíveis são encontradas.
    
    Attributes:
        bids (SortedDict): Dicionário ordenado de ordens de compra (preço decrescente)
        asks (SortedDict): Dicionário ordenado de ordens de venda (preço crescente)
        orders_by_id (dict): Mapeamento de ID para ordem para acesso rápido
        next_id (int): Próximo ID disponível para uma nova ordem
    """
    
    def __init__(self):
        """
        Inicializa um novo order book vazio.
        
        Bids são ordenadas por preço decrescente (maior preço primeiro).
        Asks são ordenadas por preço crescente (menor preço primeiro).
        """
        self.bids = SortedDict(lambda x: -x)
        self.asks = SortedDict()
        self.orders_by_id = {}
        self.next_id = 0

    def parse_command(self, command: str):
        """
        Interpreta e executa um comando de texto.
        
        Args:
            command (str): Comando a ser executado
            
        Raises:
            ValueError: Se o comando for inválido ou tiver parâmetros incorretos
            
        Comandos suportados:
            - print: Exibe o order book
            - limit <buy|sell> <price> <qty>: Cria uma ordem limit
            - market <buy|sell> <qty>: Cria uma ordem market
            - peg <buy|sell> <qty>: Cria uma ordem pegged
            - cancel <order_id>: Cancela uma ordem
            - edit <order_id> <price> <qty>: Edita uma ordem existente
        """
        command_parts = command.split()
        
        if not command_parts:
            raise ValueError('Empty command')
        
        if command_parts[0] == 'print':
            self.print_order_book()
        elif command_parts[0] in ['limit', 'market', 'peg']:
            if command_parts[0] == 'limit' and len(command_parts) < 4:
                raise ValueError(f'Limit order requires 3 parameters: <buy|sell> <price> <qty>')
            elif command_parts[0] == 'market' and len(command_parts) < 3:
                raise ValueError(f'Market order requires 2 parameters: <buy|sell> <qty>')
            elif command_parts[0] == 'peg' and len(command_parts) < 3:
                raise ValueError(f'Peg order requires 2 parameters: <buy|sell> <qty>')
            
            if command_parts[1] not in ['buy', 'sell']:
                raise ValueError(f'Side must be "buy" or "sell", got "{command_parts[1]}"')
            
            self.insert_order(command_parts)
        elif command_parts[0] == 'cancel':
            if len(command_parts) < 2:
                raise ValueError('Cancel requires 1 parameter: <order_id>')
            try:
                order_id = int(command_parts[1])
            except ValueError:
                raise ValueError(f'Order ID must be an integer, got "{command_parts[1]}"')
            self.cancel_order(order_id)
        elif command_parts[0] == 'edit':
            if len(command_parts) < 3:
                raise ValueError('Edit requires a minimum of 3 parameters: <order_id> <qty>')
            try:
                if len(command_parts) == 3:
                    order_id = int(command_parts[1])
                    new_qty = float(command_parts[2])
                    new_price = None
                else:
                    order_id = int(command_parts[1])
                    new_price = float(command_parts[2])
                    new_qty = float(command_parts[3])
            except ValueError as e:
                raise ValueError(f'Invalid parameter types for edit command: {e}')
            self.edit_order(order_id, new_price, new_qty)
        else:
            raise ValueError(f'Invalid command: "{command_parts[0]}"')


    def insert_order(self, order_attr: list):
        """
        Insere uma nova ordem no order book e tenta fazer matching.
        
        Args:
            order_attr (list): Lista com atributos da ordem
                             [type, side, price, qty] para limit orders
                             [type, side, qty] para market/peg orders
                             
        Comportamento:
            - Market orders: Executadas imediatamente contra o melhor preço disponível
            - Limit orders: Matching primeiro, depois inserção no book se houver quantidade restante
            - Peg orders: Colocadas no melhor preço do lado correspondente
        """

        if order_attr[0] == 'market':
            try:
                qty = float(order_attr[2])
            except ValueError:
                raise ValueError(f'Quantity must be a number, got "{order_attr[2]}"')

            if len(order_attr) == 4:
                order_id = int(order_attr[3])
            else:
                order_id = self.next_id
                self.next_id += 1

            order = Order(order_id, order_attr[0], order_attr[1], -1, qty)
            order = self.match_order(order)

            if order.qty > 0:
                print(f'Unfilled quantity: {order.qty} (market order cancelled)')
            else:
                print(f'Market order {order.id_order} executed successfully')

        elif order_attr[0] == 'limit':
            try:
                price = float(order_attr[2])
                qty = float(order_attr[3])
            except ValueError:
                raise ValueError(f'Price and quantity must be numbers')
            
            if len(order_attr) == 5:
                order_id = int(order_attr[4])
            else:
                order_id = self.next_id
                self.next_id += 1

            order = Order(order_id, order_attr[0], order_attr[1], price, qty)
            order = self.match_order(order)

            if order.qty > 0:
                if order.side == 'buy':
                    if order.price in self.bids.keys():
                        self.bids[order.price].append(order)
                    else:
                        self.bids[order.price] = [order]
                        if self.bids.peekitem(0)[0] == order.price:
                            self.uptade_pegged('buy')
                    
                    self.orders_by_id[order.id_order] = order
                    print(f'Limit buy order {order.id_order} placed at price {price} for qty {order.qty}')
                elif order.side == 'sell':
                    if order.price in self.asks.keys():
                        self.asks[order.price].append(order)
                    else:
                        self.asks[order.price] = [order]
                        if self.asks.peekitem(0)[0] == order.price:
                            self.uptade_pegged('sell')
                    
                    self.orders_by_id[order.id_order] = order
                    print(f'Limit sell order {order.id_order} placed at price {price} for qty {order.qty}')
            else:
                print(f'Limit order {order.id_order} fully executed')

        elif order_attr[0] == 'peg':
            try:
                qty = float(order_attr[2])
            except ValueError:
                raise ValueError(f'Quantity must be a number, got "{order_attr[2]}"')

            if len(order_attr) == 4:
                order_id = int(order_attr[3])
            else:
                order_id = self.next_id
                self.next_id += 1

            if order_attr[1] == 'buy':
                if self.bids:
                    best_price = self.bids.peekitem(0)[0]
                    order = Order(order_id, order_attr[0], order_attr[1], best_price, qty)
                    self.bids[order.price].append(order)
                    self.orders_by_id[order.id_order] = order
                    print(f'Pegged buy order {order.id_order} placed at price {best_price} for qty {qty}')
                else:
                    print('No bids in the order book to peg against. Order not placed.')
            elif order_attr[1] == 'sell':
                if self.asks:
                    best_price = self.asks.peekitem(0)[0]
                    order = Order(order_id, order_attr[0], order_attr[1], best_price, qty)
                    self.asks[order.price].append(order)
                    self.orders_by_id[order.id_order] = order
                    print(f'Pegged sell order {order.id_order} placed at price {best_price} for qty {qty}')
                else:
                    print('No asks in the order book to peg against. Order not placed.')
                

    




    def match_order(self, order: Order):
        """
        Executa o matching de uma ordem contra o order book.
        
        Args:
            order (Order): Ordem a ser processada para matching
            
        Returns:
            Order: A ordem com quantidade atualizada (0 se totalmente executada)
            
        Comportamento:
            - Buy orders fazem match com asks (ordens de venda)
            - Sell orders fazem match com bids (ordens de compra)
            - Market orders executam ao melhor preço disponível
            - Limit orders executam apenas ao preço especificado ou melhor
            - Trades são impressos conforme acontecem
        """
        trades = {}

        if order.side == 'buy':
            if order.type == 'market':
                while order.qty > 0 and len(self.asks) > 0:
                    passive_order = self.asks.peekitem(0)[1][0]
                    if passive_order.qty > order.qty:
                        if passive_order.price in trades.keys():
                            trades[passive_order.price] += order.qty
                        else:
                            trades[passive_order.price] = order.qty
                        passive_order.qty -= order.qty
                        order.qty = 0
                        
                    else:
                        order.qty -= passive_order.qty
                        if passive_order.price in trades.keys():
                            trades[passive_order.price] += passive_order.qty
                        else:
                            trades[passive_order.price] = passive_order.qty
                        del self.orders_by_id[passive_order.id_order]
                        self.asks.peekitem(0)[1].pop(0)
                        if not self.asks.peekitem(0)[1]:
                            self.asks.popitem(0)

            elif order.type == 'limit':
                if order.price in self.asks.keys():
                    while order.qty and self.asks[order.price]:
                        passive_order = self.asks[order.price][0]

                        if passive_order.qty > order.qty:
                            if passive_order.price in trades.keys():
                                trades[passive_order.price] += order.qty
                            else:
                                trades[passive_order.price] = order.qty
                            passive_order.qty -= order.qty
                            order.qty = 0
                        
                        else:
                            order.qty -= passive_order.qty
                            if passive_order.price in trades.keys():
                                trades[passive_order.price] += passive_order.qty
                            else:
                                trades[passive_order.price] = passive_order.qty
                            del self.orders_by_id[passive_order.id_order]
                            self.asks[order.price].pop(0)
                    
                    if not self.asks[order.price]:
                        self.asks.pop(order.price)

        
        else:
            if order.type == 'market':
                while order.qty > 0 and len(self.bids) > 0:
                    passive_order = self.bids.peekitem(0)[1][0]
                    if passive_order.qty > order.qty:
                        if passive_order.price in trades.keys():
                            trades[passive_order.price] += order.qty
                        else:
                            trades[passive_order.price] = order.qty
                        passive_order.qty -= order.qty
                        order.qty = 0
                        
                    else:
                        order.qty -= passive_order.qty
                        if passive_order.price in trades.keys():
                            trades[passive_order.price] += passive_order.qty
                        else:
                            trades[passive_order.price] = passive_order.qty
                        del self.orders_by_id[passive_order.id_order]
                        self.bids.peekitem(0)[1].pop(0)
                        if not self.bids.peekitem(0)[1]:
                            self.bids.popitem(0)

            else:
                if order.price in self.bids.keys():
                    while order.qty and self.bids[order.price]:
                        passive_order = self.bids[order.price][0]

                        if passive_order.qty > order.qty:
                            if passive_order.price in trades.keys():
                                trades[passive_order.price] += order.qty
                            else:
                                trades[passive_order.price] = order.qty
                            order.qty = 0
                            passive_order.qty -= order.qty
                        
                        else:
                            order.qty -= passive_order.qty
                            if passive_order.price in trades.keys():
                                trades[passive_order.price] += passive_order.qty
                            else:
                                trades[passive_order.price] = passive_order.qty
                            del self.orders_by_id[passive_order.id_order]
                            self.bids[order.price].pop(0)
                    
                    if not self.bids[order.price]:
                        self.bids.pop(order.price)
                    
                
        for trade in trades.items():
            print(f"Trade, price: {trade[0]}, qty: {trade[1]}")

        return order
    
    def print_order_book(self):
        """
        Exibe o estado atual do order book de forma formatada.
        
        Mostra todas as ordens de compra (bids) e venda (asks) organizadas
        por nível de preço, incluindo IDs, preços e quantidades.
        """
        print("\n" + "="*70)
        print(" "*25 + "ORDER BOOK")
        print("="*70)
        
        print("\nBIDS (Buy Orders):")
        print("-" * 70)
        if not self.bids:
            print("  No buy orders")
        else:
            for price in self.bids:
                total_qty = 0

                for order in self.bids[price]:
                    total_qty += order.qty
                    print(f"  Order ID: {order.id_order:3d} | Price: {order.price:8.2f} | Qty: {order.qty:8.2f}")

                print(f"  Price Level: {price:8.2f} | Total Qty: {total_qty:8.2f}")
                print("-" * 70)

        print("\nASKS (Sell Orders):")
        print("-" * 70)
        if not self.asks:
            print("  No sell orders")
        else:
            for price in self.asks:
                total_qty = 0
                total_price = 0

                for order in self.asks[price]:
                    total_qty += order.qty
                    total_price += order.price
                    print(f"  Order ID: {order.id_order:3d} | Price: {order.price:8.2f} | Qty: {order.qty:8.2f}")

                print(f"  Price Level: {price:8.2f} | Total Qty: {total_qty:8.2f}")
                print("-" * 70)
        print()

    def cancel_order(self, id_order: int):
        """
        Cancela uma ordem existente no order book.
        
        Args:
            id_order (int): ID da ordem a ser cancelada
            
        Returns:
            Order: A ordem cancelada, ou None se não encontrada
            
        Remove a ordem do book e do índice de ordens por ID.
        """
        if id_order in self.orders_by_id:
            order_found = self.orders_by_id[id_order]
            
            if order_found.side == 'buy':
                for order in self.bids[order_found.price]:
                    if order.id_order == id_order:
                        self.bids[order_found.price].remove(order)
                        
                    if not self.bids[order_found.price]:
                        self.bids.pop(order_found.price)
            else:
                for order in self.asks[order_found.price]:
                    if order.id_order == id_order:
                        self.asks[order_found.price].remove(order)
                        
                    if not self.asks[order_found.price]:
                        self.asks.pop(order_found.price)
                    

            del self.orders_by_id[id_order]

            print(f"Order ID {id_order} cancelled.")

            return order_found
        
        else:
            print(f"Order ID {id_order} not found.")
            return None
    
    def edit_order(self, id_order: int, new_price: float, new_qty: float):
        """
        Edita uma ordem existente cancelando-a e reinserindo com novos valores.
        
        Args:
            id_order (int): ID da ordem a ser editada
            new_price (float): Novo preço da ordem
            new_qty (float): Nova quantidade da ordem
            
        A edição mantém o ID da ordem mas pode resultar em novo posicionamento
        no order book e possível matching se o novo preço cruzar o spread.
        """
        order_to_edit = self.cancel_order(id_order)
        
        if order_to_edit:
            if order_to_edit.type == 'limit':
                if new_price is None:
                    print(f"New price must be provided for limit orders.")
                    return
                order_to_edit.price = new_price
                order_to_edit.qty = new_qty
                
                self.insert_order([order_to_edit.type, order_to_edit.side, str(order_to_edit.price), str(order_to_edit.qty), id_order])

                print(f"Order ID {id_order} edited to Price: {new_price}, Qty: {new_qty}.")
            elif order_to_edit.type == 'peg':
                order_to_edit.qty = new_qty
                
                self.insert_order([order_to_edit.type, order_to_edit.side, str(order_to_edit.qty), id_order])

                print(f"Pegged Order ID {id_order} edited to Qty: {new_qty}.")
        
        else:
            print(f"Order ID {id_order} could not be edited because it was not found.")


    def uptade_pegged(self, side: str):
        """
        Atualiza ordens pegged quando o melhor preço muda.
        
        Args:
            side (str): Lado do book a atualizar ('buy' ou 'sell')
            
        Ordens pegged são automaticamente atualizadas para sempre ficarem
        no topo do book (melhor preço) quando uma nova ordem melhor é inserida.
        """
        if side == 'buy':
            best_price = self.bids.peekitem(0)[0]
            if len(self.bids) > 1:
                for order in self.bids[self.bids.peekitem(1)[0]]:
                    if order.type == 'peg':
                        self.edit_order(order.id_order, best_price, order.qty)
        elif side == 'sell':
            best_price = self.asks.peekitem(0)[0]
            if len(self.asks) > 1:
                for order in self.asks[self.asks.peekitem(1)[0]]:
                    if order.type == 'peg':
                        self.edit_order(order.id_order, best_price, order.qty)

