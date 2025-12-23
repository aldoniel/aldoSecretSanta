from browser import window

class FrenchNameCompressor:
    def __init__(self):
        # TOP list déjà en lower-case et triée (les plus longs en premier)
        self.top = [
            'sébastienne','christophe','véronique','catherine','elisabeth','dominique','alexandre',
            'priscille','madeleine','christine','sébastien','nathanaël','pascaline','christian',
            'emmanuel','sandrine','mireille','nathalie','laetitia','ludivine','caroline','baptiste',
            'isabelle','patricia','gauthier','philippe','timothée','stéphane','thibault','laurence',
            'françois','aurélie','mohamed','camille','adeline','edouard','thierry','ludovic','nicolas',
            'sabrina','corinne','martine','raymond','morgane','mathieu','mickaël','bernard','laurent',
            'sylvain','céleste','jacques','georges','olivier','bastien','estelle','isidore','mélanie',
            'patrick','fabrice','francis','colette','yasmine','antoine','vincent','valérie','gustave',
            'monique','marcel','marius','solène','paloma','adrien','nadine','sophie','gérard','noémie',
            'claude','michel','marine','gilles','cécile','yvonne','daniel','léonie','fabien','honoré',
            'sylvie','elodie','pascal','pierre','gérald','julien','ariane','maëlle','jérôme','romain',
            'victor','benoît','claire','céline','damien','hélène','régine','jeanne','maxime','cédric',
            'carole','arnaud','serge','ethan','cyril','hervé','clara','henri','aline','bruno','sacha',
            'annie','louis','fanny','régis','julie','sonia','andré','alice','marie','oscar','jules',
            'denis','félix','roger','alain','agnès','kévin','joël','inès','rené','hugo','lise','lola',
            'nora','léna','marc','théo','loïc','eric','jean','maya','maud','aude','malo','lina','anne',
            'paul','noël','yves','éric','rudy','léa','luc','zoé','guy'
        ]

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
        self.pattern_str = r'\b(' + alternation + r')\b'
        # RegExp JS global (g). Pas d'i car tout est en lower-case.
        self.pattern_re = window.RegExp.new(self.pattern_str, "g")
        self.decomp_re = window.RegExp.new(r'~([a-z]{2})', "g")

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
        return chr(ord('a') + a) + chr(ord('a') + b)

    @staticmethod
    def _decode(code):
        return (ord(code[0]) - ord('a')) * 26 + (ord(code[1]) - ord('a'))

    def compress(self, liste_prenoms):
        """Remplace chaque prénom (déjà en lower-case) par ~xy en utilisant RegExp JS."""
        def repl_js(*args):
            # args[1] = groupe capturé (le prénom)
            name = str(args[1]) if len(args) >= 2 else str(args[0])
            idx = self.name_to_index.get(name)
            return '~' + self._encode(idx) if idx is not None else str(args[0])

        out = []
        for s in liste_prenoms:
            js_str = window.String.new(s)
            replaced = js_str.replace(self.pattern_re, repl_js)
            out.append(str(replaced))
        return out

    def decompress(self, compressed):
        """Remplace chaque ~xy par le prénom correspondant en utilisant RegExp JS."""
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


# Exemple d'utilisation en Brython
if __name__ == "__main__":
    comp = FrenchNameCompressor()
    src = ["alice", "bob le chat", "jeanne", "jean", "jean pierre", "antoine"]
    c = comp.compress(src)
    print("compress:", c)
    print("decompress:", comp.decompress(c))
