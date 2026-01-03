"""
compresse une liste de prénoms en les remplaçant par un index
# Exemple d'utilisation
comp = FrenchNameCompressor()
src = ["alice", "bob le chat"]
c = comp.compress(src)
d = comp.decompress(c)
"""

from browser import window

class FrenchNameCompressor:
    def __init__(self):
        # TOP 300 prénoms insee 2023 par len décroissante
        self.top = ['marie-christine', 'jean-françois', 'marie-thérèse', 'jean-pierre', 'jean-claude', 'jean-michel', 'christophe', 'jacqueline', 'marguerite', 'christiane', 'christelle', 'bernadette', 'anne-marie', 'jean-marie', 'jean-louis', 'emmanuelle', 'antoinette', 'dominique', 'christian', 'françoise', 'catherine', 'madeleine', 'alexandre', 'sébastien', 'christine', 'stéphanie', 'véronique', 'guillaume', 'geneviève', 'elisabeth', 'georgette', 'charlotte', 'henriette', 'micheline', 'gabrielle', 'alexandra', 'jean-marc', 'josephine', 'jean-paul', 'pierrette', 'angelique', 'philippe', 'françois', 'nathalie', 'isabelle', 'frédéric', 'stéphane', 'sandrine', 'marcelle', 'jeannine', 'paulette', 'germaine', 'patricia', 'brigitte', 'laurence', 'juliette', 'virginie', 'lucienne', 'raymonde', 'claudine', 'danielle', 'caroline', 'benjamin', 'florence', 'mathilde', 'emmanuel', 'laetitia', 'béatrice', 'mireille', 'delphine', 'michelle', 'jean-luc', 'valentin', 'baptiste', 'jonathan', 'fabienne', 'jocelyne', 'amandine', 'francine', 'huguette', 'clémence', 'fernande', 'matthieu', 'severine', 'aurélien', 'jacques', 'bernard', 'nicolas', 'georges', 'monique', 'patrick', 'maurice', 'laurent', 'martine', 'suzanne', 'thierry', 'camille', 'antoine', 'olivier', 'raymond', 'valérie', 'charles', 'vincent', 'chantal', 'gabriel', 'aurélie', 'michèle', 'gilbert', 'thérèse', 'colette', 'clément', 'anthony', 'francis', 'corinne', 'pauline', 'raphaël', 'josette', 'mathieu', 'patrice', 'sylvain', 'fabrice', 'mélanie', 'ginette', 'quentin', 'evelyne', 'florian', 'ludovic', 'josiane', 'fernand', 'liliane', 'mickael', 'simonne', 'pascale', 'mohamed', 'sabrina', 'justine', 'yannick', 'solange', 'auguste', 'etienne', 'richard', 'michael', 'vanessa', 'gregory', 'edouard', 'daniele', 'william', 'arlette', 'morgane', 'estelle', 'jessica', 'eugénie', 'lucette', 'florent', 'pierre', 'michel', 'jeanne', 'marcel', 'claude', 'daniel', 'robert', 'gérard', 'joseph', 'sylvie', 'julien', 'pascal', 'nicole', 'louise', 'hélène', 'thomas', 'denise', 'yvonne', 'sophie', 'céline', 'didier', 'maxime', 'simone', 'lucien', 'andrée', 'albert', 'yvette', 'emilie', 'romain', 'odette', 'jerome', 'cécile', 'franck', 'gilles', 'claire', 'elodie', 'alexis', 'audrey', 'adrien', 'gisèle', 'arthur', 'arnaud', 'victor', 'cedric', 'roland', 'nadine', 'annick', 'damien', 'benoît', 'marion', 'marthe', 'karine', 'nathan', 'marine', 'jeremy', 'eliane', 'xavier', 'fabien', 'eugène', 'carole', 'sandra', 'myriam', 'amélie', 'samuel', 'gaston', 'joëlle', 'lionel', 'maryse', 'marius', 'mathis', 'océane', 'magali', 'angèle', 'muriel', 'berthe', 'martin', 'marie', 'andré', 'louis', 'alain', 'roger', 'henri', 'david', 'renée', 'bruno', 'serge', 'julie', 'annie', 'lucie', 'alice', 'lucas', 'sarah', 'manon', 'jules', 'emile', 'chloé', 'denis', 'kevin', 'laura', 'maria', 'hervé', 'anaïs', 'elise', 'agnès', 'clara', 'odile', 'simon', 'aline', 'cyril', 'irène', 'sonia', 'laure', 'fanny', 'julia', 'nadia', 'ethan', 'nelly', 'jean', 'rené', 'paul', 'anne', 'eric', 'marc', 'yves', 'emma', 'hugo', 'joël', 'léon', 'théo', 'anna', 'enzo', 'rose', 'loïc', 'jade', 'inès', 'rémi', 'axel', 'yann', 'adam', 'lola', 'rémy', 'lina', 'guy', 'léa', 'léo', 'tom', 'eva']

        # mapping rapide name -> index
        self.name_to_index = {name: i for i, name in enumerate(self.top)}

        # choisir la fonction d'échappement : RegExp.escape si disponible, sinon fallback
        if hasattr(window.RegExp, "escape"):
            esc_fn = window.RegExp.escape
        else:
            esc_fn = self._escape_for_js_regex

        # construire alternation échappée
        escaped_names = [esc_fn(name) for name in self.top]
        alternation = '|'.join(escaped_names)
        self.pattern_str = r'(' + alternation + r')'
        # RegExp JS global (g). Pas d'i car tout est en lower-case.
        self.pattern_re = window.RegExp.new(self.pattern_str, "g")
        self.decomp_re = window.RegExp.new(r'([A-Z]{2})', "g")

    @staticmethod
    def _escape_for_js_regex(s):
        # fallback simple pour échapper les métacaractères regex en JS
        specials = r"\^$.|?*+()[]{}\/"
        out = []
        for ch in s:
            if ch in specials:
                out.append('\\' + ch)
            else:
                out.append(ch)
        return ''.join(out)

    @staticmethod
    def _encode(n):
        a = n // 26
        b = n % 26
        orda=ord('A')
        return chr(orda + a) + chr(orda + b)

    @staticmethod
    def _decode(code):
        orda=ord('A')
        return (ord(code[0]) - orda) * 26 + (ord(code[1]) - orda)

    def compress(self, liste_prenoms):
        """Remplace chaque prénom (déjà en lower-case) par xy en utilisant RegExp JS."""
        def repl_js(*args):
            # args[1] = groupe capturé (le prénom)
            name = str(args[1]) if len(args) >= 2 else str(args[0])
            idx = self.name_to_index.get(name)
            return self._encode(idx) if idx is not None else str(args[0])

        out = []
        for s in liste_prenoms:
            js_str = window.String.new(s)
            replaced = js_str.replace(self.pattern_re, repl_js)
            out.append(str(replaced))
        return out

    def decompress(self, compressed):
        """Remplace chaque xy par le prénom correspondant en utilisant RegExp JS."""
        def repl_code_js(*args):
            code = str(args[1])
            idx = self._decode(code)
            return self.top[idx] if 0 <= idx < len(self.top) else str(args[0])

        out = []
        for s in compressed:
            js_str = window.String.new(s)
            replaced = js_str.replace(self.decomp_re, repl_code_js)
            out.append(str(replaced))
        return out
