import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    jointProbability = float()
    one_gene_list = []
    two_gene_list = []
    trait_list = []
    no_trait_list = []
    no_gene_list = []

    if len(one_gene) != 0:
        for person in one_gene:
            one_gene_list.append(person)

    if len(two_genes) != 0:
        for person in two_genes:
            two_gene_list.append(person)

    for person in people:
        if person not in one_gene_list and person not in two_gene_list:
            no_gene_list.append(person)

    if len(have_trait) != 0:
        for person in have_trait:
            trait_list.append(person)

    for person in people:
        if person not in trait_list:
            no_trait_list.append(person)

    def findGene(person, number):
        prob1 = float()
        prob2 = float()
        prob3 = float()
        prob4 = float()
        probability = float()
        mother = str(people[person]['mother'])
        father = str(people[person]['father'])

        if mother == 'None' and father == 'None':
            if number == 'one':
                return PROBS['gene'][1]
            elif number == 'two':
                return PROBS['gene'][2]
            elif number == 'none':
                return PROBS['gene'][0]

        else:
            if mother in one_gene_list:
                prob1 = 0.5 * (1 - PROBS['mutation'])
                prob2 = 0.5 * PROBS['mutation']
            else: # either has two genes or no genes
                prob1 = (1 - PROBS['mutation'])
                prob2 = PROBS['mutation']

            if father in one_gene_list:
                prob3 = 0.5 * (1 - PROBS['mutation'])
                prob4 = 0.5 * PROBS['mutation']
            else: # either has two genes or no genes
                prob3 = (1 - PROBS['mutation'])
                prob4 = PROBS['mutation']

        if number == 'one':
            if mother in one_gene_list:
                if father in one_gene_list:
                    probability = prob1 * prob3 + prob3 * prob1 + prob2 * prob3 + prob4 * prob1 + prob2 * prob4 * 2
                elif father in two_gene_list:
                    probability = prob1 * prob4 + prob1 * prob3 + prob2 * prob4
                else: # father has no genes
                    probability = prob1 * prob3 + prob1 * prob4 + prob2 * prob3

            elif mother in two_gene_list:
                if father in one_gene_list:
                    probability = prob1 * prob3 + prob2 * prob3 + prob2 * prob4
                elif father in two_gene_list:
                    probability = prob1 * prob4 + prob2 * prob3
                else: # father has no genes
                    probability = prob1 * prob3 + prob2 * prob4

            else: #mother has no genes
                if father in one_gene_list:
                    probability = prob1 * prob3 + prob1 * prob4 + prob2 * prob3
                elif father in two_gene_list:
                    probability = prob1 * prob3 + prob2 * prob4
                else:
                    probability = prob2 * prob3 + prob1 * prob4

        elif number == 'two':
            if mother in one_gene_list:
                if father in one_gene_list:
                    probability = prob1 * prob3 + prob2 * prob4 + prob1 * prob4 + prob2 * prob3
                elif father in two_gene_list:
                    probability = prob1 * prob3 + prob2 * prob3
                else: # father has no genes
                    probability = prob1 * prob4 + prob2 * prob4

            elif mother in two_gene_list:
                if father in one_gene_list:
                    probability = prob1 * prob3 + prob1 * prob4
                elif father in two_gene_list:
                    probability = prob1 * prob3
                else: # father has no genes
                    probability = prob1 * prob4

            else: # mother has no genes
                if father in one_gene_list:
                    probability = prob2 * prob3 + prob2 * prob4
                elif father in two_gene_list:
                    probability = prob2 * prob3
                else: # father has no genes
                    probability = prob2 * prob4

        elif number == 'none':
            if mother in one_gene_list:
                if father in one_gene_list:
                    probability = prob1 * prob3 + prob2 * prob4 + prob1 * prob4 + prob2 * prob3
                elif father in two_gene_list:
                    probability = prob1 * prob4 + prob2 * prob4
                else: # father has no genes
                    probability = prob1 * prob3 + prob2 * prob3

            elif mother in two_gene_list:
                if father in one_gene_list:
                    probability = prob2 * prob3 + prob2 * prob4
                elif father in two_gene_list:
                    probability = prob2 * prob4
                else: # father has no genes
                    probability = prob2 * prob3

            else: # mother has no genes
                if father in one_gene_list:
                    probability = prob1 * prob3 + prob1 * prob4
                elif father in two_gene_list:
                    probability = prob1 * prob4
                else: # father has no genes
                    probability = prob1 * prob3

        return probability

    def findTrait(person, confirmation):

        probability = float()

        if confirmation == 'yes':
            if person in two_gene_list:
                probability = PROBS['trait'][2][True]
            elif person in one_gene_list:
                probability = PROBS['trait'][1][True]
            else:
                probability = PROBS['trait'][0][True]

        elif confirmation == 'no':
            if person in two_gene_list:
                probability = PROBS['trait'][2][False]
            elif person in one_gene_list:
                probability = PROBS['trait'][1][False]
            else:
                probability = PROBS['trait'][0][False]

        return probability


    for person in one_gene:
        if jointProbability != 0:
            jointProbability *= findGene(person, 'one')
        else:
            jointProbability = findGene(person, 'one')

    for person in two_genes:
        if jointProbability != 0:
            jointProbability *= findGene(person, 'two')
        else:
            jointProbability = findGene(person, 'two')

    for person in no_gene_list:
        if jointProbability != 0:
            jointProbability *= findGene(person, 'none')
        else:
            jointProbability = findGene(person, 'none')

    for person in trait_list:
        jointProbability *= findTrait(person, 'yes')

    for person in no_trait_list:
        jointProbability *= findTrait(person, 'no')

    return jointProbability

def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in one_gene:
        probabilities[person]['gene'][1] += p

    for person in two_genes:
        probabilities[person]['gene'][2] += p

    for person in probabilities:
        if person not in one_gene and person not in two_genes:
            probabilities[person]['gene'][0] += p

    for person in have_trait:
        probabilities[person]['trait'][True] += p

    for person in probabilities:
        if person not in have_trait:
            probabilities[person]['trait'][False] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:

        sum_trait = probabilities[person]['trait'][True] + probabilities[person]['trait'][False]
        if sum_trait != 0:
            probabilities[person]['trait'][True] = probabilities[person]['trait'][True] / sum_trait
            probabilities[person]['trait'][False] = probabilities[person]['trait'][False] / sum_trait

        sum_gene = probabilities[person]['gene'][2] + probabilities[person]['gene'][1] + probabilities[person]['gene'][0]
        if sum_gene != 0:
            probabilities[person]['gene'][2] = probabilities[person]['gene'][2] / sum_gene
            probabilities[person]['gene'][1] = probabilities[person]['gene'][1] / sum_gene
            probabilities[person]['gene'][0] = probabilities[person]['gene'][0] / sum_gene

if __name__ == "__main__":
    main()
