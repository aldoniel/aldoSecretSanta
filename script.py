"""
Le tirage au sort de secret Santa par Aldoniel 
en interne, tout est en lowercase. la majuscule c'est juste à l'affichage
"""
from browser import document,  html,window #window est l'objet qui donne accès au js global namespace
from browser.local_storage import storage
import RandomClass #la classe random réécrite en python pour pas importer tout stdlib
import frenchnamecompressor


# global variables
doc_usr=html.DIV(id="usr")
doc_adm = html.DIV(id="adm",style="display: none;")


class Circularcoord():
    """
    donne un index incrémenté de 1 à chaque appel sans out of bound error,
    en parcourant une liste par indice comme un tableau circulaire
    start=l'indice de départ, ex 0
    outbound=l'indice de fin, ex len-1
    attention ne vérifie pas si size=0 ou si start est outbound...
    """
    def __init__(self, start:int, outbound:int) -> None:
        self.i: int = start
        self.outbound: int = outbound
        self.size: int = self.outbound + 1

    def geti(self) -> int:
        i: int = self.i
        self.i = (self.i + 1) % self.size
        return i


def decodeURI() -> list[str]:
   """
   renvoie une liste d'élements décodés après ? de l'url, triés
   """
   a:str=str(window.location.search)
   a=a.lower()
   if a=="":
       return []
   #b: list[str]=a[1:].split("&")
   c:list[str]= [window.decodeURIComponent(item) for item in a[1:].split("&") ]
   c.sort()
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
            a=decodeURI()
            a=self.comp.decompress(a)
            assert isinstance(a,list)
            assert len(a)>0
            self.gens=a[1:]
            self.gens.sort()
            try:
                self.seed=int(a[0:1][0])
                print("error")
            except Exception as e:
                print("exception !!)")
                print(e)
                self.seed=0 #le 1er élément est un entier seed
            # initialiser le dict au format joueur:destinataire
            random= RandomClass.Random(self.seed)
            self.gensmelanges=random.shuffle(self.gens) # attention, cette class renvoie une liste mélangée alors que la class builtin shuffles in place
            c=Circularcoord(1,len(self.gensmelanges)-1)
            for item in self.gensmelanges:
                self.couplage[item]=self.gensmelanges[c.geti()]

        except AssertionError:
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
        a: list[str] = [b for aa in txtarea_val.lower().replace("~","").split('\n') if (b := aa.strip())]
        a=self.comp.compress(a) #compression
        t: set[str]=set(a)
        doublons={}
        doc_url=document["url"]
        if len(t) < len(a):#si doublon
            for item in t:
                nb:int=a.count(item)
                if nb>1:
                    doublons[item]=nb
            print(f"erreur : corriger les doublons : {doublons}")
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
            fullurl=f"{fullurl}?{seed}&{makeURI(t)}"
            doc_url.clear()
            doc_url<= html.A(fullurl,href=fullurl)

    def destinataire(self, item: str) -> None:
            # affiche le nom du destinataire cadeau
            match self.nop:
                case 0:
                    doc_usr <= html.P(self.couplage[item].capitalize())
                    storage['nop']="1"
                case 1:
                    doc_usr <= html.P("Sans tricher ;-)")
                #case _ pass
            self.nop += 1
            
    def reset(self,ev,p):
        "supprime les contrôles une fois et retire le cheat de la session"
        self.nop=0
        p.unbind("click")


    def main(self):

        #dessiner la page usr
        document <= html.P(html.BUTTON("changer de mode",).bind("click",ToggleMode.toggle),align="right",id="bout")
        document <= doc_usr
        document <= doc_adm
        doc_usr <= html.H1("Le tirage au sort de secret Santa par Aldoniel (Mode utilisateur)")
        doc_usr <= html.P("Clique sur ton nom pour savoir à qui est secrètement destiné ton cadeau. (Attention ! Sans tricher, un seul essai)")
        
        #ajouter les boutons des gens
        if self.gens !=[""]:
            for item in self.gens:
                doc_usr <= html.P(html.BUTTON(item.capitalize()).bind("click",lambda ev,item=item:self.destinataire(item)))#il faut créer une varible de lambda item sinon ça appelle lamda avec la dernière valeur de item
        else:
            doc_usr <= html.P("Aucune personne dans l'url. Changer vers le mode créateur.")
            ToggleMode.toggle(None)

        
        #dessiner la page créateur
        doc_adm <= html.H1("Mode créateur")
        p0=html.P()
        js_obj_date=window.Date.new()
        p0<=html.INPUT(type="number",min=0, size=10, value=js_obj_date.getFullYear(),id="seed")
        p0<=html.SPAN("\tmettre un chiffre pour initialiser le générateur de hasard.")
        doc_adm<=p0
        p=html.P()
        p<=html.BUTTON("créer l'url").bind("click",self.mkurl)
        p<=html.SPAN("\t")
        p<=html.SPAN("url",id="url")
        doc_adm <=p
        doc_adm <=html.P ("Saisir infra les prénoms des participants, un par ligne.")
        doc_adm <= html.P (html.TEXTAREA(id="noms",rows="35", cols="80"))
        doc_adm <=html.P ('Remarques : Le chiffre qui initialise le générateur de "hasard" permet de garantir que le tirage sera identique chez tout le monde. Ne pas utiliser ~ dans les noms (caractère réservé).')
        p2=html.P()
        p2<=html.BUTTON("Débloquer l'anti-triche : Je promets que c'est à bon escient.").bind("click", lambda ev, p2=p2: self.reset(ev, p2))
        doc_adm<=p2

app=MainClass()
app.main()

#cheat code
def avoue():
    print(f"{app.couplage=}")
window.avoue=avoue