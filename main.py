from matching_engine.order_book import OrderBook

def print_banner():
    """
    Exibe o banner inicial da aplicação.
    """
    print("\n" + "="*60)
    print(" "*15 + "PS MS - Matching Engine")
    print("="*60)

def print_help():
    """
    Exibe a lista de comandos disponíveis no sistema.
    """
    print("\nComandos Disponíveis:")
    print("-" * 60)
    print("  limit <buy|sell> <price> <qty>  - Colocar uma Limit Order")
    print("  market <buy|sell> <qty>          - Colocar uma Market Order")
    print("  peg <buy|sell> <qty>             - Colocar uma Pegged Order")
    print("  cancel <order_id>                - Cancelar uma order")
    print("  edit <order_id> <price> <qty>    - Editar uma order")
    print("  print                            - Exibir Order Book")
    print("  help                             - Mostrar comandos")
    print("  exit                             - Sair")
    print("-" * 60)

def print_prompt():
    """
    Solicita entrada do usuário e retorna o comando formatado.
    
    Returns:
        str: Comando inserido pelo usuário (sem espaços extras)
    """
    return input("\n Insira o comando (escreva 'help' para comandos): ").strip()

def main():
    """
    Função principal que executa o loop de interação com o usuário.
    
    Cria um order book e processa comandos até que o usuário digite 'exit'.
    Trata erros e exibe mensagens apropriadas.
    """
    order_book = OrderBook()
    
    print_banner()
    
    while True:
        try:
            command = print_prompt()
            
            if not command:
                continue
            
            if command.lower() == 'exit':
                print("\nSaindo")
                break
            
            if command.lower() == 'help':
                print_help()
                continue
            
            order_book.parse_command(command)
            
        except ValueError as e:
            print(f"\nError: {e}")
            print("Escreva 'help' para ver comandos.")
        except IndexError:
            print("\nError: Formato de comando inválido. Parâmetros ausentes.")
            print("Escreva 'help' para ver comandos.")
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            print("Escreva 'help' para ver comandos.")

if __name__ == "__main__":
    main()
