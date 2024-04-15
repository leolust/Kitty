def calculate_real_contrib(rest, sorted_contrib):
    while rest > 0:
        # Trouver la contribution maximale
        contrib_max = next(iter(sorted_contrib.values()))
        # Lister les contributeurs à la contribution maximale
        max_contributors = [key for key, value in sorted_contrib.items() if value == contrib_max]
        occur_max = len(max_contributors)
        # Trouver la deuxième plus grande contribution
        contrib_nd = next(iter(filter(lambda x: x < contrib_max, sorted_contrib.values())), None)
        # Si toutes les contributions sont égales, diviser le reste équitablement
        if contrib_nd is None:
            saving = round(rest / occur_max,2)
            rest = 0
        else:
            # Sinon calculer l'écart
            gap = round(contrib_max - contrib_nd, 2)
            if rest <= gap * occur_max:
                saving = round(rest / occur_max,2)
                rest = 0
            else:
                saving = gap
                rest -= saving * occur_max
        for contributor in max_contributors:
            sorted_contrib[contributor] -= saving
    return sorted_contrib

def minimize_transactions(real_expenses):
    sorted_transactions = sorted(real_expenses.items(), key=lambda x: x[1])

    transactions = []

    i = 0
    j = len(sorted_transactions) - 1

    while i < j:
        debtor, debtor_amount = sorted_transactions[i]
        creditor, creditor_amount = sorted_transactions[j]

        transaction_amount = min(-debtor_amount, creditor_amount)

        transactions.append((debtor, creditor, round(transaction_amount, 2)))

        sorted_transactions[i] = (debtor, round(debtor_amount + transaction_amount, 2))
        sorted_transactions[j] = (creditor, round(creditor_amount - transaction_amount, 2))

        if sorted_transactions[i][1] == 0:
            i += 1
        if sorted_transactions[j][1] == 0:
            j -= 1

    return transactions

def repayment(contributions, expenses):
    # Trier les contributions
    sorted_contrib = dict(sorted(contributions.items(), key=lambda item: item[1], reverse=True))
    # Calculer les contributions réelles
    real_contrib = calculate_real_contrib(sum(contributions.values()) - sum(expenses.values()), sorted_contrib)
    print(real_contrib)
    # Calculer les dettes
    real_expenses = {k: real_contrib.get(k, 0) - expenses.get(k, 0) for k in set(real_contrib) | set(expenses)}
    print(real_expenses)
    # Calculer les transactions
    transactions = minimize_transactions(real_expenses)
    return transactions

# Test de la fonction
contributions = {'A': 10, 'B': 8, 'C': 10, 'D': 10.55, 'E': 9.45, 'F': 15, 'G': 15, 'H': 22} # 100
expenses = {'D': 43, 'F': 7, 'A': 30, 'H': 10}                                               #  90

test = repayment(contributions, expenses)
print("\nresultat:")
print(test)
#print(sum(test.values()))
for debtor, creditor, amount in test:
    print(f"{debtor} rembourse {amount} à {creditor}")