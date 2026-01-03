"""
Le tirage au sort de secret Santa par Aldoniel 
en interne, tout est en lowercase. la majuscule c'est juste à l'affichage
todo exporter l'url ap de a et on t pour que ce soit trié

"""
from browser import document,  html,window #window est l'objet qui donne accès au js global namespace
from browser.local_storage import storage
import RandomClass #la classe random réécrite en python pour pas importer tout stdlib
import frenchnamecompressor


# global variables
doc_usr=html.DIV(Class="w3-container",id="usr" )
doc_adm = html.DIV(Class="w3-container",id="adm",style="display: none;")


class Circularcoord():
    """
    donne un index incrémenté de 1 à chaque appel sans out of bound error,
    en parcourant une liste par indice comme un tableau circulaire
    start=l'indice de départ, ex 0
    outbound=l'indice de fin, ex len-1
    """
    def __init__(self, start:int, outbound:int) -> None:
        self.i: int = start
        self.outbound: int = outbound
        self.size: int = self.outbound + 1
        assert start >=0,"start >=0"
        assert outbound>=0,"outbound>=0" #cad size>0

    def geti(self) -> int:
        self.i = (self.i + 1) % self.size
        return self.i


def decodeURI() -> list[str]:
   """
   renvoie une liste d'élements décodés après ? de l'url, triés
   """
   a:str=str(window.location.search)
   if a=="":
       return []
   c:list[str]= [window.decodeURIComponent(item) for item in a[1:].split("&") ]
   return c
    
def makeURI(liste)-> str:
    ret:list=[]
    for item in liste:
        ret.append(window.encodeURIComponent(item))
    return "&".join(ret)


class ToggleMode:
    tog:bool= False

    @staticmethod
    def toggle(ev):
        #passe du mode créateur à usr
        doc_usr.style.display="block" if ToggleMode.tog else "none"
        doc_adm.style.display="none" if ToggleMode.tog else "block"
        ToggleMode.tog = not ToggleMode.tog


class MainClass():
    def __init__(self):
        # vérifier que n'a pas déjà joué
        try:
            self.nop=int(storage['nop'])
        except (KeyError,ValueError):
            self.nop= 0 #int
            storage['nop']="0"

        #init compresseur
        self.comp = frenchnamecompressor.FrenchNameCompressor()

        # initialiser la liste des gens depuis l'url

        self.couplage={}#dict[str,str]
        try:
            a: list[str]=decodeURI()
            a=self.comp.decompress(a)
            assert isinstance(a,list),"isinstance(a,list)"
            assert len(a)>0,"len(a)"
            self.gens: list[str] = [item.casefold() for item in a[1:]]
            self.gens.sort()
            try:
                self.seed=int(a[0])
            except Exception as e:
                print("exception lecture seed\n" +repr(e)) 
                self.seed=0 #le 1er élément est un entier seed
            # initialiser le dict au format joueur:destinataire
            random= RandomClass.Random(self.seed)
            self.gensmelanges=random.shuffle(self.gens) # attention, cette class renvoie une liste mélangée alors que la class builtin shuffles in place
            c=Circularcoord(0,len(self.gensmelanges)-1)
            for item in self.gensmelanges:
                self.couplage[item]=self.gensmelanges[c.geti()]

        except AssertionError as e:
            print("init main\n" +repr(e)) 
            self.gens = [""]
            self.gensmelanges=['']
            self.seed=0
            random= RandomClass.Random(self.seed)


    def mkurl(self,ev) -> None:
        """
        récolte la liste des gens dans textarea et crée l'url sur la page
        seed est le 1er élément de l'url
        filtre les lignes d'espaces blancs et strip les entrées
        bloque et return s'il y a des doublons
        """
        txtarea_val=str(document["noms"].value)
        a: list[str] = [b for aa in txtarea_val.casefold().split('\n') if (b := aa.strip())]
        t: set[str]=set(a)
        doublons={}
        doc_url=document["url"]
        if len(t) < len(a):#si doublon
            for item in t:
                nb:int=a.count(item)
                if nb>1:
                    doublons[item]=nb
            doc_url.clear()
            doc_url.textContent=f"erreur : corriger les doublons : {doublons}"
            return
        else:
            try:
                seed:int=int(document["seed"].value)
            except ValueError:
                doc_url.clear()
                doc_url.textContent="entrer un entier pour le générateur de hasard."
                return
            if len(t)==0:
                doc_url.clear()
                doc_url.textContent="il faut saisir la liste des gens infra"
                return
            fullurl:str=str(window.location.href)
            if "?" in fullurl:
                fullurl=fullurl.split("?")[0]
            fullurl=f"{fullurl}?{seed}&{makeURI(self.comp.compress(a))}"
            doc_url.clear()
            doc_url<= html.A(fullurl,href=fullurl)

    def printdestinataire(self,item,ev):
        # affiche le nom du destinataire
        dest=document["dest"]
        dest.clear()
        dest.classList.add("w3-teal");
        dest <= html.H5(f"Je suis {ev.currentTarget.textContent} et j'offrirai un cadeau à {self.couplage[item].title()}")

    def destinataire(self, item: str,ev) -> None:
            # affiche le nom du destinataire une fois
            match self.nop:
                case 0:
                    self.printdestinataire(item,ev)
                    storage['nop']="1"
                case 1:
                    document["pastrich"].clear()
                    document["pastrich"] <= html.P("Sans tricher ;-)")
                #case _ pass
            self.nop += 1
            
    def reset(self,ev):
        "supprime les contrôles une fois et retire le cheat de la session"
        document["pastrich"].clear()
        self.nop=0
        ev.target.unbind("click")


    def main(self):

        #dessiner la page usr
        document <= html.DIV(Class="w3-container w3-right-align w3-margin-top") <= html.BUTTON("changer de mode",).bind("click",ToggleMode.toggle)
        document <= doc_usr
        document <= doc_adm
        doc_usr <= html.H1("Mode utilisateur")
        doc_usr <= html.H3("Secret Santa par Aldoniel ")
        doc_usr <= html.P("Clique sur ton nom pour piocher le destinataire de ton cadeau. (Attention ! Sans tricher, un seul essai)")
        doc_usr <= html.DIV(id="dest",Class="w3-container")
        doc_usr <= html.DIV(id="pastrich")
        
        #ajouter les boutons des gens
        if self.gens !=[""]:
            for item in self.gens:
                doc_usr <= html.P(html.BUTTON(item.title()).bind("click",lambda ev,item=item:self.destinataire(item,ev)))#il faut créer une varible de lambda item sinon ça appelle lamda avec la dernière valeur de item
        else:
            doc_usr <= html.P("Aucune personne dans l'url. Changer vers le mode créateur.")
            ToggleMode.toggle(None)

        
        #dessiner la page créateur
        doc_adm <= html.H1("Mode créateur")
        p0=html.P()
        js_obj_date=window.Date.new()
        p0<=html.INPUT(  type="number",min=0, size=10, value=js_obj_date.getFullYear(),id="seed")
        p0<=html.SPAN("\tmettre un chiffre pour initialiser le générateur de hasard.")
        doc_adm<=p0
        p=html.P()
        p<=html.BUTTON("créer l'url").bind("click",self.mkurl)
        p<=html.SPAN("\t")
        p<=html.SPAN("url",id="url")
        doc_adm <=p
        doc_adm <=html.P ("Saisir infra les prénoms des participants, un par ligne.")
        doc_adm <= html.P (html.TEXTAREA( Class="w3-left-align w3-border w3-button w3-mobile" ,id="noms",rows="35", cols="40", style="overflow-y:auto;"))
        doc_adm <=html.P ('Remarques : Le chiffre qui initialise le générateur de "hasard" permet de garantir que le tirage sera identique chez tout le monde.')
        doc_adm<=html.P(html.BUTTON("Débloquer l'anti-triche : Je promets que c'est à bon escient.").bind("click", self.reset))

app=MainClass()
app.main()

#cheat codes
def avoue():
    print(f"{app.couplage=}")
window.avoue=avoue

def poweroverwhelming():
    app.nop=0
    app.destinataire=MainClass.printdestinataire.__get__(app)
window.poweroverwhelming=poweroverwhelming
