def calculate_real_contrib(rest, sorted_contrib):
    while rest > 0:
        print(sorted_contrib)
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
            # Calculer l'écart
            gap = round(contrib_max - contrib_nd, 2)
            print("gap  :", gap)
            print("rest:", rest)
            if rest <= gap * occur_max:
                saving = round(rest / occur_max,2)
                rest = 0
            else:
                saving = gap
                rest -= saving * occur_max
        for contributor in max_contributors:
            sorted_contrib[contributor] -= saving
    return sorted_contrib

def repayment(contributions, expenses):
    rest = sum(contributions.values()) - sum(expenses.values())
    sorted_contrib = dict(sorted(contributions.items(), key=lambda item: item[1], reverse=True))
    # Calculer les dépenses réelles
    real_contrib = calculate_real_contrib(rest, sorted_contrib)
    return real_contrib

# Test de la fonction
contributions = {'A': 10, 'B': 10, 'C': 10, 'D': 10.55, 'E': 9.45, 'F': 15, 'G': 15, 'H': 20} # 100
expenses = {'D': 43, 'F': 7, 'A': 10, 'H': 10}                                                #  70

test = repayment(contributions, expenses)
print("\nresultat:")
print(test)
print(sum(test.values()))
