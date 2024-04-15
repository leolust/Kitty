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

def calculate_transactions(real_expenses):
    # Trie des dépenses réelles 
    sorted_transactions = sorted(real_expenses.items(), key=lambda x: x[1])
    print("Sorted transactions:")
    print(sorted_transactions)
    transactions = []
    i = 0
    j = len(sorted_transactions) - 1
    while i < j:
        print("e")
        creditor, creditor_amount = sorted_transactions[i]
        debtor, debtor_amount = sorted_transactions[j]
        # Calcul du dû
        due = min(-creditor_amount, debtor_amount)
        # Ajout d'une transaction à la liste des transactions finale
        transactions.append((debtor, creditor, round(due, 2)))
        # Retrait du montant de la transaction
        sorted_transactions[i] = (creditor, round(creditor_amount + due, 2))
        sorted_transactions[j] = (debtor, round(debtor_amount - due, 2))
        # Si une personne est remboursée, on passe à la suivante
        if sorted_transactions[i][1] == 0: 
            i += 1
        # Si une personne a remboursé sa dette, on passe à la suivante
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
    return calculate_transactions(real_expenses)