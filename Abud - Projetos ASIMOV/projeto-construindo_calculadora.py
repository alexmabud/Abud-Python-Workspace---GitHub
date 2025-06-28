print("Calculadora")
print("1 - Soma")
print("2 - Subtração")
print("3 - Multiplicação")
print("4 - Divisão")
print("5 - Exponencial")

opcao = input("Escolha uma opção: ")

x = float(input("Digite o primeiro número: "))
y = float(input("Digite o segundo número: "))

if opcao == "1":
    print(f"{x} + {y} = {x + y}")
elif opcao == "2":
    print(f"{x} - {y} = {x - y}")
elif opcao == "3":
    print(f"{x} * {y} = {x * y}")
elif opcao == "4":
    if y == 0:
        print("Erro: Divisão por zero!")
    else:
        print(f"{x} / {y} = {x / y}")
elif opcao == "5":
    print(f"{x} ^ {y} = {x ** y}")
else:
    print("Opção inválida!")