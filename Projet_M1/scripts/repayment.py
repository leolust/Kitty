def calculate_real_contrib(rest, sorted_contrib):
    while rest > 0:
        contrib_max = max(sorted_contrib.values()) # Contribution maximale
        max_contributors = [key for key, value in sorted_contrib.items() if value == contrib_max]
        occur_max = len(max_contributors) # Nombre d'occurences de la contribution maximale
        other = [v for v in sorted_contrib.values() if v < contrib_max]
        contrib_nd = max(other) if other else None # 2nd plus haute contribution
        if contrib_nd is None: # Si toutes les contributions sont égales, diviser le reste équitablement
            saving = round(rest / occur_max, 2)
            rest = 0
        else: # Sinon calculer l'écart
            gap = round(contrib_max - contrib_nd, 2)
            if rest <= gap * occur_max:
                saving = round(rest / occur_max, 2)
                rest = 0
            else:
                saving = gap
                rest -= saving * occur_max
        # Egaliser le remboursement des contributeurs ayant la contribution maximum
        for contributor in max_contributors:
            sorted_contrib[contributor] = round(sorted_contrib[contributor] - saving, 2)
    return sorted_contrib

def calculate_transactions(creditors, debtors, diclose):
    cost = 0
    transactions = []
    creditors_copy = creditors.copy()
    debtors_copy = debtors.copy()
    # Trier par montant croissant
    creditors_copy.sort(key=lambda x: x[1])
    debtors_copy.sort(key=lambda x: x[1])
    i = len(creditors_copy) - 1  # Index du créditeur avec le plus petit montant
    j = len(debtors_copy) - 1    # Index du débiteur avec le plus grand montant
    while i >= 0 and j >= 0:
        creditor, credit_amount = creditors_copy[i]
        debtor, debit_amount = debtors_copy[j]
        due = round(min(credit_amount, debit_amount), 2)        
        transactions.append((debtor, creditor, due))
        # Coût standard d'un remboursement : 10 / coût du remboursement d'un proche
        cost += 4 if debtor in diclose and creditor in diclose[debtor] else 10  
        # Mettre à jour les montants
        new_credit = round(credit_amount - due, 2)
        new_debit = round(debit_amount - due, 2)
        if new_credit <= 0.01:  # Créditeur remboursé
            i -= 1
        else:
            creditors_copy[i] = (creditor, new_credit) 
        if new_debit <= 0.01:  # Débiteur a remboursé
            j -= 1
        else:
            debtors_copy[j] = (debtor, new_debit)
    return cost, transactions

def transac_with_friends(creditors, debtors, diclose):
    cost = 0
    transactions = []
    creditors_copy = creditors.copy()
    debtors_copy = debtors.copy()
    credits_dict = {person: amount for person, amount in creditors_copy}
    debts_dict = {person: amount for person, amount in debtors_copy}
    debtors_copy.sort(key=lambda x: x[1], reverse=True)
    debtor_done = set()
    for debtor, debt_amount in debtors_copy:  
        if debtor not in debtor_done and debtor in diclose:
            # Filtrer les amis qui sont créditeurs
            friends_creditors = [(friend, credits_dict.get(friend, 0)) for friend in diclose[debtor] if friend in credits_dict and credits_dict.get(friend, 0) > 0]
            
            # Vérifier si les amis peuvent absorber toute la dette
            if sum(amount for _, amount in friends_creditors) >= debt_amount:
                # Essayer de rembourser uniquement les amis
                remaining_debt = debt_amount
                potential_transactions = []
                
                # Copie temporaire des crédits pour simuler
                temp_credits = dict(credits_dict)
                
                # Trier les amis créditeurs par montant (pour respecter l'algorithme original)
                friends_creditors.sort(key=lambda x: x[1])
                
                for friend, credit_amount in friends_creditors:
                    if credit_amount > 0:
                        transfer_amount = min(remaining_debt, credit_amount)
                        transfer_amount = round(transfer_amount, 2)
                        
                        if transfer_amount > 0:
                            potential_transactions.append((debtor, friend, transfer_amount))
                            temp_credits[friend] = round(temp_credits[friend] - transfer_amount, 2)
                            remaining_debt = round(remaining_debt - transfer_amount, 2)
                            
                            if remaining_debt <= 0.01:  # Dette soldée
                                break
                
                # Si nous pouvons solder la dette, effectuer les transactions
                if remaining_debt <= 0.01:
                    for d, c, amount in potential_transactions:
                        transactions.append((d, c, amount))
                        cost += 4  # Coût réduit pour les amis
                        print(f"Transaction amicale: {d} -> {c}: {amount}€ (Coût: 4€)")
                        
                        # Mettre à jour les montants
                        credits_dict[c] = round(credits_dict[c] - amount, 2)
                        debts_dict[d] = round(debts_dict[d] - amount, 2)
                    
                    debtor_done.add(debtor)
    
    # Reconstruire les listes des créditeurs et débiteurs restants
    remaining_creditors = [(person, amount) for person, amount in credits_dict.items() if amount > 0.01]
    remaining_debtors = [(person, amount) for person, amount in debts_dict.items() if amount > 0.01 and person not in debtor_done]
    
    # Traiter les dettes restantes avec l'algorithme standard
    remaining_cost, remaining_transactions = calculate_transactions(remaining_creditors, remaining_debtors, diclose)
    cost += remaining_cost
    transactions.extend(remaining_transactions)
    return cost, transactions

def repayment(contributions, expenses, diclose):
    sorted_contrib = dict(sorted(contributions.items(), key=lambda item: item[1], reverse=True))
    real_contrib = calculate_real_contrib(sum(contributions.values()) - sum(expenses.values()), sorted_contrib)
    # Calculer les dépenses réelles de chacun (combien il doit effectivement donner - combien il a effectivement depensé)
    real_expenses = {k: round(real_contrib.get(k, 0) - expenses.get(k, 0), 2) for k in set(real_contrib) | set(expenses)}
    # Séparer créditeurs et débiteurs
    creditors = [(person, -amount) for person, amount in real_expenses.items() if amount < 0]
    debtors = [(person, amount) for person, amount in real_expenses.items() if amount > 0]
    # Calculer les transactions
    minAction_cost, minAction_transactions = calculate_transactions(creditors, debtors, diclose)
    closeFirst_cost, closeFirst_transactions = transac_with_friends(creditors, debtors, diclose)
    print("Le cout de minAction est de:", minAction_cost)
    print("Le cout de closeFirst est de:", closeFirst_cost)
    # Choisir la méthode la moins coûteuse
    if minAction_cost <= closeFirst_cost:
        return minAction_transactions
    else:
        return closeFirst_transactions