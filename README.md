# PS MS - Matching Engine - Guilherme Kaidei

Sistema de matching engine para ordens de compra e venda, implementado em Python. Este projeto simula o funcionamento de um livro de ordens (order book), com suporte a diferentes tipos de ordens e execução automática de trades.

O projeto é um matching engine que gerencia um order book com dois dicionários ordenados:
- **Bids (Compras)**: Ordenados por preço decrescente (maior preço primeiro)
- **Asks (Vendas)**: Ordenados por preço crescente (menor preço primeiro)

O sistema executa automaticamente trades quando ordens compatíveis são encontradas, tanto para ordens limit quanto market, além de suportar ordens pegged que se ajustam ao melhor preço disponível.

Decidi optar por preencher limit orders que gerariam um trade, já que isso é o comportamento esperado em um sistema real de matching engine e faz mais sentido com a lógica de matching implementada.

## Funcionalidades

- Criação e gerenciamento de ordens (limit e market)
- Matching automático de ordens compatíveis

## Funcionalidades Bonus
- Visualização livro
- Soluções que respeitem a ordem de chegada das ordens
- Cancelamento de ordens
- Edição de ordens (respeitando a prioridade na fila)
- Pegged Orders


## Tipos de Ordens

### 1. Limit Order
Ordem com preço específico que só executa nesse preço.
```
limit buy 100.0 10.0   # Compra 10 unidades a R$ 100,00
limit sell 105.0 5.0   # Vende 5 unidades a R$ 105,00
```

### 2. Market Order
Ordem executada imediatamente ao melhor preço disponível.
```
market buy 10.0   # Compra 10 unidades ao melhor preço de venda
market sell 5.0   # Vende 5 unidades ao melhor preço de compra
```

### 3. Pegged Order
Ordem que se ajusta automaticamente para sempre ficar no topo do book (melhor preço).
```
peg buy 10.0    # Sempre no melhor preço de compra
peg sell 5.0    # Sempre no melhor preço de venda
```

## Instalação

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passos

1. Clone o repositório:
```bash
git clone https://github.com/guikaidei/ps-ms.git
cd ps-ms
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute a aplicação:
```bash
python main.py
```

## Como Usar

Ao iniciar a aplicação, você verá um prompt interativo:

```
==============================================================
               PS MS - Matching Engine
==============================================================

 Insira o comando (escreva 'help' para comandos):
```

Digite seus comandos e pressione Enter. Use `help` para ver todos os comandos disponíveis.

## comandos Disponíveis

| Comando | Sintaxe | Descrição |
|---------|---------|-----------|
| **limit** | `limit <buy\|sell> <price> <qty>` | Cria uma ordem limit |
| **market** | `market <buy\|sell> <qty>` | Cria uma ordem market |
| **peg** | `peg <buy\|sell> <qty>` | Cria uma ordem pegged |
| **cancel** | `cancel <order_id>` | Cancela uma ordem existente |
| **edit** | `edit <order_id> <price> <qty>` | Edita preço e quantidade de uma ordem |
| **print** | `print` | Exibe o estado atual do order book |
| **help** | `help` | Mostra a lista de comandos |
| **exit** | `exit` | Encerra a aplicação |

## Arquitetura

### Estrutura do Projeto

```
ps-ms/
├── matching_engine/
│   ├── __init__.py
│   ├── order.py          # Classe Order
│   └── order_book.py     # Classe OrderBook (matching engine)
├── tests/
│   ├── test_order.py
│   └── test_order_book.py
├── main.py               # Interface CLI
├── requirements.txt
└── README.md
```

### Componentes Principais

#### 1. Order (`order.py`)
Representa uma ordem individual no sistema.

**Atributos:**
- `id_order`: Identificador único
- `type`: Tipo da ordem ('limit', 'market', 'peg')
- `side`: Lado ('buy' ou 'sell')
- `price`: Preço (ou -1 para market orders)
- `qty`: Quantidade

#### 2. OrderBook (`order_book.py`)
Gerencia o livro de ordens e executa o matching.

**Métodos principais:**

- **`parse_command(command: str)`**: Interpreta comandos de texto
- **`insert_order(order_attr: list)`**: Insere nova ordem e tenta matching
- **`match_order(order: Order)`**: Executa matching de uma ordem
- **`cancel_order(id_order: int)`**: Cancela ordem existente
- **`edit_order(id_order, new_price, new_qty)`**: Edita ordem existente
- **`print_order_book()`**: Exibe estado do order book
- **`uptade_pegged(side: str)`**: Atualiza ordens pegged

**Estruturas de dados:**
- `bids`: SortedDict com ordens de compra (preço decrescente)
- `asks`: SortedDict com ordens de venda (preço crescente)
- `orders_by_id`: Dicionário para acesso rápido por ID

## Exemplos de Uso

### Exemplo 1: Trade Simples
```
> limit sell 100.0 10.0
Limit sell order 0 placed at price 100.0 for qty 10.0

> limit buy 100.0 10.0
Trade, price: 100.0, qty: 10.0
Limit order 1 fully executed
```

### Exemplo 2: Ordem Parcialmente Executada
```
> limit sell 100.0 15.0
Limit sell order 0 placed at price 100.0 for qty 15.0

> limit buy 100.0 10.0
Trade, price: 100.0, qty: 10.0
Limit order 1 fully executed

> print

======================================================================
                         ORDER BOOK
======================================================================

BIDS (Buy Orders):
----------------------------------------------------------------------
  No buy orders

ASKS (Sell Orders):
----------------------------------------------------------------------
  Order ID:   0 | Price:   100.00 | Qty:     5.00
  Price Level:   100.00 | Total Qty:     5.00 | Total Price:   100.00
----------------------------------------------------------------------
```

### Exemplo 3: Market Order
```
> limit sell 100.0 5.0
Limit sell order 0 placed at price 100.0 for qty 5.0

> market buy 5.0
Trade, price: 100.0, qty: 5.0
Market order 1 executed successfully
```

### Exemplo 4: Pegged Order
```
> limit buy 100.0 10.0
Limit buy order 0 placed at price 100.0 for qty 10.0

> peg buy 5.0
Pegged buy order 1 placed at price 100.0 for qty 5.0

> limit buy 101.0 8.0
Order ID 1 cancelled.
Limit buy order 1 placed at price 101.0 for qty 5.0
Limit buy order 2 placed at price 101.0 for qty 8.0
Order ID 1 edited to Price: 101.0, Qty: 5.0.
```

### Exemplo 5: Cancelamento e Edição
```
> limit buy 100.0 10.0
Limit buy order 0 placed at price 100.0 for qty 10.0

> cancel 0
Order ID 0 cancelled.

> limit buy 100.0 10.0
Limit buy order 1 placed at price 100.0 for qty 10.0

> edit 1 105.0 15.0
Order ID 1 cancelled.
Limit buy order 1 placed at price 105.0 for qty 15.0
Order ID 1 edited to Price: 105.0, Qty: 15.0.
```

## Testes

O projeto inclui testes unitários usando pytest.

### Executar todos os testes:
```bash
python3 -m pytest 
```
ou 
```bash
python -m pytest
```


### Executar testes específicos:
```bash
python3 -m pytest tests/test_order.py
python3 -m pytest tests/test_order_book.py
```

ou 
```bash
python -m pytest tests/test_order.py
python -m pytest tests/test_order_book.py
```
