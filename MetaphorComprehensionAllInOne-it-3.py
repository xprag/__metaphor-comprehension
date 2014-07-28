#!/usr/bin/env python

# -*- coding: utf-8 -*-

"""

This experiment was created using PsychoPy2 Experiment Builder (v1.64.00), May 22, 2011, at 23:42

If you publish work using this script please cite the relevant PsychoPy publications

  Peirce, JW (2007) PsychoPy - Psychophysics software in Python. Journal of Neuroscience Methods, 162(1-2), 8-13.

  Peirce, JW (2009) Generating stimuli for neuroscience using PsychoPy. Frontiers in Neuroinformatics, 2:10. doi: 10.3389/neuro.11.010.2008

"""



"""

SF: 

	Legenda:

		(?) da verificare

"""



from numpy import * 

from numpy.random import * 

import os 

from psychopy import core, data, event, visual, gui

import psychopy.log 

import pyglet

import re

import datetime

import sys

import shutil

import random



# Problem reading french words otherwise (default encoding is ASCII)

reload(sys) # scaring... but necessary :( setdefaultencoding is deleted from sys, by default

sys.setdefaultencoding('utf-8')



# User-defined variables = ['Instructions', 'key_resp', 'text', 'trial']

known_name_collisions = None  #(collisions are bad)



# Keyboard layout

keyb = 'IT'



# Debug flag (for testing only)

_debug_on = False



#################################

# General definitions and consts

#################################



# SF: ci interessano esattamente le stesse (?)



class DictKeys():

    pass

    

dk = DictKeys()

dk.expInfoName = 'name'

dk.expInfoAge = 'age'

dk.expInfoSex = 'gender'

dk.expInfoHand = 'hand'

# SF: removed: dk.expInfoCondition = 'condition'

dk.expInfoSide = 'side'

dk.expInfoDate = 'date'

# SF: removed: dk.expInfoPattern = 'pattern'

dk.expInfoExpName = 'expName'

#------------------

dk.condMalePos = 'MP'

dk.condMaleNeg = 'MN'

dk.condFemalePos = 'FP'

dk.condFemaleNeg = 'FN'

#------------------

dk.sexMale = 'M'

dk.sexFemale = 'F'

#------------------

dk.handRight = 'R'

dk.handLeft = 'L'

#------------------

dk.sideDefault = 'D'

dk.sideInverted = 'I'

#------------------

dk.patternSemanticPicture = 'SIPI'

dk.patternPictureSemantic = 'PISI'

#------------------



# SF: costruisce la lista delle informazioni sui test già eseguiti e da mostrare all'inizio (?)

dk.condList = [ dk.condMalePos, dk.condMaleNeg, dk.condFemalePos, dk.condFemaleNeg ]

dk.sexList = [ dk.sexMale, dk.sexFemale ]

dk.handList = [ dk.handRight, dk.handLeft ]

dk.sideList = [ dk.sideDefault, dk.sideInverted ]

dk.patternList = [ dk.patternSemanticPicture, dk.patternPictureSemantic ]





class InfoEntry(object):

# SF: definisce inizializzazione della classe InfoEntry (informazioni sulla singola entry: etichetta, valore, limiti, posizione)

    def __init__(self, label, value, range, position):

        self.label = label

        self.value = value

        self.range = range

        self.position = position

        

# SF: stringify il "valore" (campo VALUE) dell'oggetto

    def __str__(self):

        return str(self.value)



# SF: definice l'inizializzazione della classe SubjInfoEntry come quella di InfoEntry (suo "super") 

class SubjInfoEntry(InfoEntry):

    def __init__(self, label, value, range, position):

        super(SubjInfoEntry,self).__init__(label, value, range, position)

# SF: definice l'inizializzazione della classe ExpInfoEntry come quella di InfoEntry (suo "super") 

class ExpInfoEntry(InfoEntry):

    def __init__(self, label, value, range, position):

        super(ExpInfoEntry,self).__init__(label, value, range, position)

# SF: definisce le informazioni standard dell'esperimento: nome, età, genere, mano, condizioni, lato, schema (imamgine->semantica o semantica->immagine)

# SF: ... come: etichetta, valore, lista dei valori possibili, posizione nell'elenco delle informazioni

expInfo= {

    dk.expInfoName: SubjInfoEntry('Name','', [],0),

    dk.expInfoAge: SubjInfoEntry('Age','',[],1),

    dk.expInfoSex: SubjInfoEntry('Gender ' + '/'.join(dk.sexList),'',dk.sexList, 2),

    dk.expInfoHand: SubjInfoEntry('Hand ' + '/'.join(dk.handList),'',dk.handList,3),

# SF: removed: dk.expInfoCondition: ExpInfoEntry('Condition ' + '/'.join(dk.condList),'',dk.condList, 4),

    dk.expInfoSide: ExpInfoEntry('Side ' + '/'.join(dk.sideList),'',dk.sideList,5),

# SF: removed: dk.expInfoPattern: ExpInfoEntry('Pattern ' + '/'.join(dk.patternList),'',dk.patternList,6)

}



############

# Utilities

############



# SF: crea e mostra una finestra di dialogo

def MsgDialog(title, msg):

# SF: crea una nuova finestra con il titolo richiesto

    msg_dlg=gui.Dlg(title)

# SF: aggiunge una riga vuota

    msg_dlg.addText('')

# SF: mostra il messaggio

    msg_dlg.addText(msg)

# SF: aggiunge una riga vuota

    msg_dlg.addText('')

# SF: fa comparire la finestra

    msg_dlg.show()

        

# need a global files_to_move interrupt_dir

# SF: definisce una lista di eventuali file da spostare (files_to_move) nella cartella indicata (interrupt_dir)

files_to_move = []

interrupt_dir = ''



# SF: chiusura esperimento: mostra un messaggio di chiusura e sposta eventuali file interessanti

def quitExpe(msg = None):

    global interrupt_dir

    global files_to_move

    

# SF: se abbiamo specificato il messaggio mostra il messaggio dicendo che l'esperimento è stato interrotto 

    if msg != None:

        MsgDialog('Error: experiment aborted!', msg)

        

# SF: sposta i file (se richiesto)

    if len(files_to_move):

        if not os.path.isdir(interrupt_dir):

            os.makedirs(interrupt_dir) #if this fails (e.g. permissions) we will get error

        for f in files_to_move:

            if os.path.isfile(f):

                newname = interrupt_dir + os.path.sep + os.path.basename(f)

                shutil.move(f, newname)

# SF: chiude l'applicazione (?)

    core.quit()

    

# SF: individua le dimensioni dello schermo del PC

def screen_size():

    s = pyglet.window.get_platform().get_default_display().get_default_screen()

    return s.width, s.height

    

# SF: capisce se il mouse è all'interno del rettangolo specificato  

def mouse_in_rect(mouse_pos, rect_pos, rect_size, units = 'norm'):

    if units == 'pix':

        mouse_pos[0] = mouse_pos[0]*window_size[0]/2

        mouse_pos[1] = mouse_pos[1]*window_size[1]/2

    if mouse_pos[0] >= rect_pos[0] - rect_size[0]/2 and \

       mouse_pos[0] <= rect_pos[0] + rect_size[0]/2 and \

       mouse_pos[1] >= rect_pos[1] - rect_size[1]/2 and \

       mouse_pos[1] <= rect_pos[1] + rect_size[1]/2:

        return True

    return False

   

# SF: (?)

# SF: restituisce diversi valori tra cui: 

# SF: - tempo di risposta RT

# SF: - lista dei pulsanti del mouse premuti

# SF: - zone interessate dal click

# SF: - tempi di risposta su tutti i pulsanti (?)

def mouse_pressed(mouse, mouse_btns=[0,1,2], rects = [], units = 'norm'):

    if mouse_btns == None: 

        mouse_btns = [0,1,2]

        

# SF: individua le due liste 1) dello stato premuto (True) / non premuto (False) dei pulsanti BUTTONS del mouse MOUSE e 2) dei timestamps TS in cui sono stati premuti

    buttons, ts = mouse.getPressed(getTime=True)

# SF: individua la posizione x/y del mouse

    pos = mouse.getPos()



# SF: individua la lista dei tasti del mouse MOUSE_BTNS (0, 1, 2) premuti (BUTTONS:True/False)

    pressed = [ b for b in mouse_btns if buttons[b] ]

# SF: individua la lista dei tempi TS in cui sono stati premuti i tasti del mouse che risultano premuti PRESSED 

    timestp =  [ ts[b] for b in pressed ] 

# SF: individua gli indici relativi alla lista dei rettangoli RECTS dei rettangoli che contengono il mouse

    inrects =  [ i for i in xrange(0, len(rects)) if mouse_in_rect(pos, rects[i][0], rects[i][1], units) ]

    

# SF: inizializza il tempo di risposta RT

    rt = -1

# SF: determina il tempo di risposta RT come il minimo tempo con cui uno qualunque dei pulsanti del mouse è stato premuto

    if len(pressed):

        rt = min(timestp)

        

    return rt, pressed, inrects, timestp 



# SF: individua il rilascio del mouse (?)

def mouse_release(mouse, clock = None):

    delay = None

    if clock != None: 

        delay=clock.getTime()

    while sum(mouse.getPressed()): 

        continue

    if clock != None: 

        delay=clock.getTime()-delay

    return delay



# SF: individua il tempo di risposta RT e la lista dei tasti della tastiera che sono stati premuti RET_KEYS, eventualmente filtrati tra quelli che ci interessano KEY_LIST

def key_pressed(clock, key_list = None):

    keys = event.getKeys()

    rt = clock.getTime()

    

# SF: se è stato premuto ESC l'esperimento termina (?) (pericolo?)

    if 'escape' in keys: 

        quitExpe()



# SF: se richiesto filtra i tasti premuti tra quelli che ci interessano KEY_LIST        

    if key_list != None:

        ret_keys = [ k for k in key_list if k in keys ]



# SF: durante il debug simula la pressione di uno a caso dei tasti indicati come filtro KEY_LIST

        # this is for testing purposes (automatize input, randomly)

        if _debug_on and len(key_list):

            ret_keys = [ key_list[random.randrange(0, len(key_list))] ]

            

    else:

        ret_keys = keys

    

    return rt, ret_keys



# SF: mostra le finestre TO_SHOW e i pulsanti BUTTONS nel contesto WIN; restituisce il tempo di risposta RT, i pulsanti premuti B, i tasti premuti K e i rettangoli eventualmente interessati dal click del mouse RE

def show(win, to_show = [], mouse_btns = [0,1,2], exit_keys = None, buttons = [], delay = 100000, clickReset = True):

# SF: di default si testano tutti i pulsanti del mouse

    if mouse_btns == None: 

        mouse_btns = [0,1,2]

    

# SF: la finestra viene gestita dai pulsanti indicati (vedi sotto)

    use_mouse = False

# SF: la finestra viene sempre chiusa dal tasto ESC

    use_keybd = True # this is always true to capture the ESC key

    

    if len(mouse_btns):

        use_mouse = True

        mouse = event.Mouse(win=win)

# SF: "button" o "r"... (?) in IRONY il valore BUTTONS non viene mai usato...

# SF: individua i rettangoli dei pulsanti della finestra di dialogo (in IRONY il valore BUTTONS non viene mai usato...)

        rects = [ button.rect() for r in buttons ]

        if len(rects): 

            mouse.setVisible(True)

     

    rt,b,k,re = -1,None,None,None

    event.clearEvents()

    

# SF: leggiamo SEMPRE la tastiera

    if use_keybd:

        event.getKeys()

# SF: se si usa il mouse vediamo se un pulsante è stato rilasciato (?)

    if use_mouse:

        mouse_release(mouse)



# SF: definisce un nuovo clock

    clock_show=core.Clock()

    

# SF: resettiamo il pulsante cliccato (se necessario)

    if use_mouse and clickReset:

        mouse.clickReset()

    

# SF: resettiamo il clock

    t=0; clock_show.reset()

    

# SF: ripetiamo fino a che non passa il tempo massimo (100 secondi in generale o 0.5 secondi per ogni risposta)

    while True:



# SF: leggiamo il tempo di risposta

        rt = t= clock_show.getTime()



# SF: se è passato il tempo massimo interrompe

        if t >= delay:

            break

            

# SF: se il tempo passato è positivo (?) mostra le finestre e i pulsanti (NON PRESENTI in Irony)

        if (0.0 <= t):

            for t in to_show:

                t.draw()

            for b in buttons:

                b.draw()

       

# SF: se è richiesto di usare il mouse

        if use_mouse:

# SF: legge il tempo di risposta del mouse RT, i pulsanti premuti BT, gli eventuali rettangoli dei pulsanti a contatto con il mouse RE e i timestamp TS

            rt, bt, re, ts = mouse_pressed(mouse, mouse_btns, rects = rects)



# SF: se non è stato premuto nessun pulsante o non è stato premuto sui pulsanti della finestra       

            if len(bt) and (len(rects) == 0 or len(re)): 

                break

        

# SF: se è richiesto di usare la tastiere (SEMPRE in Irony)

        if use_keybd:



# SF: ricava il tempo di risposta RT e la lista dei tasti premuti K

            rt, k = key_pressed(clock_show, exit_keys)

# SF: se è stato premuto un tasto

            if len(k): 

                break



# SF: scambia la finestra (?)

        win.flip()

        

# SF: se si deve usare il mouse ed è stato cliccato su uno dei pulsanti viene reso visibile (?)

    if use_mouse and len(rects): 

        mouse.setVisible(False)

        

    return rt,b,k,re

 

##################

# Start Form mask

##################



class Stats(object):



# SF: inizializza un dizionario (array associativo) per raccogliere le statistiche dei singoli valori della singola caratteristica selezionata all'inizio del test (sesso, condizioni, lato, mano, schema)

    def __stat_init(self, keys):

        dict = {}

        for x in keys: dict[x] = 0

        return dict

            

# SF: inizializza le statistiche di tutte le caratteristiche (sesso, condizioni, lato, mano, schema)

    def __init__(self, dir):

# SF: inizializza la cartella in cui verranno salvate le statistiche

        self.dir = dir

        self.sex = self.__stat_init(dk.sexList)

        self.condition = self.__stat_init(dk.condList)

        self.side = self.__stat_init(dk.sideList)

        self.hand = self.__stat_init(dk.handList)

        self.pattern = self.__stat_init(dk.patternList)

        

# SF: 

    def make(self):

# SF: definisce lo schema del nome di file relativo ad Irony

        re_stat = re.compile("(?P<SEX>.)_(?P<CND>..)_(?P<PATTERN>....)_(?P<SIDE>.)_(?P<HAND>.).*xlsx$")

# SF: legge tutti i file della cartella delle statistiche

        flist = os.listdir(self.dir)

# SF: per ognuno dei file

        for f in flist:

# SF: se il nome del file corrisponde ai file delle statistiche

            m = re_stat.match(os.path.basename(f))

            if m == None: continue

# SF: legge le caratteristiche (sesso, condizioni, lato, mano, schema) del file

            sex = m.group('SEX')

            cnd = m.group('CND')

            side = m.group('SIDE')

            hand = m.group('HAND')

            pattern = m.group('PATTERN')

# SF: se il nome del file non è coerente con i valori accettabili

            if not (sex in dk.sexList and cnd in dk.condList and side in dk.sideList and hand in dk.handList and pattern in dk.patternList): 

# SF: lo salta

                continue

# SF: altrimenti lo conta per le caratteristiche indicate nel nome

            self.sex[sex] = self.sex[sex]  + 1

            self.condition[cnd] = self.condition[cnd] + 1

            self.side[side] = self.side[side] + 1

            self.hand[hand] = self.hand[hand] + 1

            self.pattern[pattern] = self.pattern[pattern] + 1

            

# SF:  costruisce la caselle di testo della finestra iniziale per permettere all'utente di indicare per le caratteristiche del nuovo esperimento del tipo OTYPE indicato e secondo l'ordine indicato al momento della creazione se è specificato SORTED

def expInfoByType(expInfo, otype, sorted = True):

# SF: definisce l'insieme delle caselle di testo

    map = {}

# SF: per ciascuna delle caratteristiche dell'esperimento 

    for x in expInfo.values():

# SF: se la classe dell'oggetto è quella indicata

        if type(x) == otype: 

# SF: inserisce la casella di testo alla posizione desiderata

            map[x.position] = x

# SF: se si desidera che le caselle di testo compaiono nell'ordine indicato le riordina

    if sorted:

        sorted_keys = map.keys()

        sorted_keys.sort()

        return [ map[k] for k in  sorted_keys ]

# restituisce la lista delle caselle del tipo indicato da inserire 

    return map.values()

            

# SF: crea la finestra di dialogo iniziale che mostra e raccoglie i dati statistici      

def makeDlg(expInfo, stats):

    dlg = gui.Dlg(title="Metaphor Comprehension")

# SF: aggiunge le etichette

    dlg.addText('_____________ STATISTICS INFO _____________')

    dlg.addText('Total subjects tested = %d' %(stats.sex[dk.sexMale] + stats.sex[dk.sexFemale]))

    cnds = [ '%s=%d' %(k, v) for k,v in stats.condition.items() ]

    dlg.addText('Condition '+', '.join(cnds))

    sides = [ '%s=%d' %(k, v) for k,v in stats.side.items() ]

    dlg.addText('Side '+', '.join(sides))

    sexs = [ '%s=%d' %(k, v) for k,v in stats.sex.items() ]

    dlg.addText('Sex '+', '.join(sexs))

    hands = [ '%s=%d' %(k, v) for k,v in stats.hand.items() ]

    dlg.addText('Hand '+', '.join(hands))

    patterns = [ '%s=%d' %(k, v) for k,v in stats.pattern.items() ]

    dlg.addText('Patterns '+', '.join(patterns))

    dlg.addText('______________ SUBJECT INFO ______________')

# SF: aggiunge le caselle di testo

    for x in expInfoByType(expInfo, SubjInfoEntry):

        dlg.addField(x.label, x.value)

    dlg.addText('____________ EXPERIMENT INFO ____________')

    for x in expInfoByType(expInfo, ExpInfoEntry):

        dlg.addField(x.label, x.value)

    return dlg



# SF: raccoglie le informazioni EXPINFO digitate dall'utente nelle caselle di testo della finestra di dialogo DLG

def expInfoFromDlg(dlg, expInfo):

    for k,x in expInfo.items():

        if type(x) in [SubjInfoEntry, ExpInfoEntry]:

            x.value = dlg.data[x.position].upper().strip(' ')

            

# SF: verifica che le informazioni raccolte in EXPINFO rientrino nei valori ammessi

def expInfoOk(expInfo):

    for k, x in expInfo.items():

        if not type(x) in [SubjInfoEntry, ExpInfoEntry]:

            continue

        if len(x.range) and x.value not in x.range:

            return False

    age = int(expInfo[dk.expInfoAge].value)

    if age <= 1 or age >= 100:

        return False

    return True



# SF: visualizza la finestra di dialogo e la chiude soltanto quando i dati inseriti sono ammissibili o l'utente la chiude con "Cancel" o ESC

def OpeningForm(expInfo, statistics):

    quit_loop = False

    

    while not quit_loop:

        dlg = makeDlg(expInfo, statistics)

        dlg.show()

    

        if dlg.OK==False: 

            quitExpe()

        try:

            expInfoFromDlg(dlg, expInfo)

            if expInfoOk(expInfo): 

                quit_loop = True

                break

            MsgDialog('Attention', 'Some of the parameters are missing or not within the correct range...')

        except Exception, e:

            print str(e)

            MsgDialog('Attention', 'Some of the parameters are missing or not within the correct range...')



# SF: definisce la classe che crea le permutazioni casuali (?)

class RandomPermutation(object):

    



# SF: crea la permutazione basandola sul numuero N di (?)    

    def __init__(self, n, auto_reset = True):

        self.reset(n)

        self._auto_reset = auto_reset





# SF: crea un array della dimensione indicata

    def reset(self, n):

# SF: crea un array di N elementi nulli

        self._info = [0]*n

# SF: ricorda il numero di elementi dell'array

        self._size = n

# SF: ricorda il numero di elementi ancora disponibili dell'array

        self._free = n

        

# SF: seleziona un elemento della permutazione

    def select(self):



# SF: se non ci sono più elementi disponibili       

        if self._free == 0:

# SF: se la permutazione piò ricominciare automaticamente

            if self._auto_reset:

# SF: crea automaticamente una nuova permutazione      

                self.reset(self._size)

            else:

# SF: altrimenti restituisce un valore di errore

                return -1

            

# SF: individua un valore casuale tra quelli compresi negli elementi ancora disponibili nella permutazione

        p = random.randrange(0, self._free) + 1

        

# SF: individua l'elemento della permutazione

        for i in xrange(0, self._size):

            if self._info[i] == 0: 

                p -= 1

            if p == 0: 

                self._info[i] = 1

                self._free -= 1

                break

                

        return i





# SF: split the list of Test/Practice stories in two balanced sets 

def CheckStoryListBalancement(list, check_marked):

# SF: get the list of "male" stories

    male = [ x for x in list if x['Gender'] == 'M' ]

# SF: get the list of "female" stories

    female = [ x for x in list if x['Gender'] == 'F']

# SF: if no "male" stories are present in the list or the nunber of "male" and "female" stories is not equal or "male" stories are not an even number

    if len(male) == 0 or len(male) != len(female) or (len(male) % 2):

        quitExpe('Story list not balanced by gender')

# SF: get the list of "male" stories with positive context

    male_positive_ctx = [ x for x in male if x['Context'] == 'P' ]

# SF: get the list of "male" stories with negative context

    male_negative_ctx = [ x for x in male if x['Context'] == 'N' ]

# SF: if positive and negative "male" stories are not balanced

    if len(male_positive_ctx) == 0 or len(male_positive_ctx) != len(male_negative_ctx) or (len(male_positive_ctx) % 2):

        quitExpe('Male story list not balanced by context')       

# SF: get the list of "female" stories with positive context

    female_positive_ctx = [ x for x in female if x['Context'] == 'P' ]

# SF: get the list of "female" stories with negative context

    female_negative_ctx = [ x for x in female if x['Context'] == 'N' ]

# SF: if positive and negative "female" stories are not balanced

    if len(female_positive_ctx) == 0 or len(female_positive_ctx) != len(female_negative_ctx) or (len(female_positive_ctx) % 2):

        quitExpe('Female story list not balanced by context')

# SF: if stories are check-marked too balance them again

    if check_marked:

        male_positive_ctx_marked = [ x for x in male_positive_ctx if x['Mark'] == 1 ]

        female_positive_ctx_marked = [ x for x in female_positive_ctx if x['Mark'] == 1 ]

        if len(male_positive_ctx_marked) < len(male_positive_ctx)/2 or \

           len(female_positive_ctx_marked) < len(female_positive_ctx)/2:

            quitExpe('Marked story list is not big enough')





# SF: return a list of test stories indexes (?)

def test_stories_split_by_context(stories_G, stories_test_list): # prm: list of stories indexes by genders

    stories_G_dict = {}



    stories_G_CP = [ i for i in stories_G if stories_test_list[i]['Context'] == 'P' ] 

# SF: only positive stories are check marked... (?)

    stories_G_CP_Marked = [ i for i in stories_G_CP if stories_test_list[i]['Mark'] == 1 ] 

    stories_G_CP_Normal = [ i for i in stories_G_CP if stories_test_list[i]['Mark'] == 0 ] 

    

# SF: random permutation of test stories of a given genre, positives and marked 

    rp_gcpm = RandomPermutation(len(stories_G_CP_Marked))

    rp_w = RandomPermutation(2)

    stories_G_selection = [[], []]

    context_ids_selection = [[], []]

    

    which = rp_w.select()

    for i in xrange(0, len(stories_G_CP_Marked)):

        if i == len(stories_G_CP_Marked)/2:

            which = rp_w.select()

        k = stories_G_CP_Marked[rp_gcpm.select()]

        stories_G_selection[which].append(k)

        context_ids_selection[which].append(stories_test_list[k]['Context_Id'])

        

# SF: random permutation of test stories of a given genre, positives and "normal" (not marked)

    rp_gcpn = RandomPermutation(len(stories_G_CP_Normal))

    

    for i in xrange(0, len(stories_G_selection)):

        len_selection = len(stories_G_selection[i])

        for j in xrange(0, len(stories_G_CP)/2 - len_selection):

            k = stories_G_CP_Normal[rp_gcpn.select()]

            stories_G_selection[i].append(k)

            context_ids_selection[i].append(stories_test_list[k]['Context_Id'])

    

    stories_G_CN = [ i for i in stories_G if stories_test_list[i]['Context'] == 'N'] 

    

    rp_gcn = RandomPermutation(len(stories_G_CN))

    

    j = 0

    for i in xrange(0, len(stories_G_CN)):

        k = stories_G_CN[rp_gcn.select()]

        c = stories_test_list[k]['Context_Id']

        if c in context_ids_selection[j]: 

            j = (j + 1)%2

        if len(stories_G_selection[j]) < len(stories_G)/2:

            stories_G_selection[j].append(k)

        j = (j + 1)%2

            

    return stories_G_selection





# SF: return a list of practice stories indexes (?)

def practice_stories_split_by_context(stories_G, stories_practice_list): # prm: list of stories indexes by genders

    stories_G_CP = [ i for i in stories_G if stories_practice_list[i]['Context'] == 'P' ] 

    stories_G_CN = [ i for i in stories_G if stories_practice_list[i]['Context'] == 'N' ] 

    stories_G_selection = [[],[]]

    context_ids_selection = [[],[]]

    

    rp = RandomPermutation(len(stories_G_CP))

    for j in [0, 1]:

        for i in xrange(0, len(stories_G_CP)/2):

            k = stories_G_CP[rp.select()]

            stories_G_selection[j].append(k)

            context_ids_selection[j].append(stories_practice_list[k]['Context_Id'])

            

    j = 0

    rp = RandomPermutation(len(stories_G_CN))

    for i in xrange(0, len(stories_G_CN)):

        k = stories_G_CN[rp.select()]

        c = stories_practice_list[k]['Context_Id']

        if c in context_ids_selection[j]:

            j = (j + 1)%2

        if len(stories_G_selection[j]) < len(stories_G)/2:

            stories_G_selection[j].append(k)

        j = (j + 1)%2

    

    return stories_G_selection



#############

# Expe setup

#############



expName ='MetaphorComprehension'#from the Builder filename that created this script

expInfo[dk.expInfoDate] = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

expInfo[dk.expInfoExpName] = expName

# SF: all data are stored in the "data" folder

data_dir = 'data'

# SF: data about tests that have been interrupted are stored in the "data/interrupted" folder

interrupt_dir = data_dir + os.path.sep + 'interrupted'

# SF: data about the experiment are in the "stimuli" folder

stimuli_dir = 'stimuli'+ os.path.sep

# SF: instructions about the experiment are in the "instruction" folder

instruction_dir = 'instructions'+ os.path.sep

# SF: pictures about the experiment are in the "stimuli/pictures" folder

pictures_dir = stimuli_dir + 'pictures' + os.path.sep

my_font = 'Comic Sans MS'



# SF: creates "data" folder, if needed

if not os.path.isdir(data_dir):

    os.makedirs(data_dir)



# Opening mask

# SF: set up statistics object

statistics = Stats(data_dir)

# SF: read statistics from data folder

statistics.make()

# SF: show dialog to start experiment (where subjects can type their info)

OpeningForm(expInfo, statistics)



# set the experiment strings info dictionary

expInfoStr = {}

for k, v in expInfo.items(): expInfoStr[k] = str(v)



""" SF: start removal

# Get the stimuli list

# SF: "conditions" are gender (M/F) and type (P/N)

cond_dict = {}

# SF: builds 2 conditions to be evaluated right after

cond_dict['gender'] = expInfo[dk.expInfoCondition].value in [ dk.condMalePos, dk.condMaleNeg ] and 'M' or 'F' #(?)

cond_dict['type'] = expInfo[dk.expInfoCondition].value in [ dk.condMalePos, dk.condFemalePos ] and 'P' or 'N' #(?)



# SF: set name of stimuli file

adjectives_table=stimuli_dir + 'Adjectives.csv'

# SF: read stimuli table from CSV file

adjectives_list =data.importTrialList(adjectives_table)

# SF: filter data from file by conditions (also accepts type "X" as neutral (?))

adjectives_cond_list = [x for x in adjectives_list if x['Gender'] == cond_dict['gender'] and (x['Type'] == cond_dict['type'] or x['Type'] == 'X')]



# SF: set name of pictures' file

faces_table=stimuli_dir + 'Faces.csv'

# SF: read pictures' table from CSV file

faces_list =data.importTrialList(faces_table)

# SF: filter data from file by conditions (also accepts type "X" as neutral (?))

faces_cond_list = [x for x in faces_list if x['Gender'] == cond_dict['gender'] and (x['Type'] == cond_dict['type'] or x['Type'] == 'X')]



# SF: set name of stories' file

stories_table=stimuli_dir + 'Stories.csv'

# SF: read stories' table from CSV file

stories_list =data.importTrialList(stories_table)

# SF: filter data in two lists (Practice and Test) depending on SentenceBlock flag

stories_practice_list = [ x for x in stories_list if x['SentenceBlock'] == 'P']

stories_test_list = [ x for x in stories_list if x['SentenceBlock'] == 'T']

SF: end removal """



""" SF: start addition """

# SF: set name of arguments' file

arguments_table=stimuli_dir + 'Argomenti.csv'

# SF: read stories' table from CSV file

arguments_list =data.importTrialList(arguments_table)

# SF: filter data in two lists (Practice and Test) depending on SentenceBlock flag

arguments_practice_list = [ x for x in arguments_list if x['SentenceBlock'] == 'P']

arguments_test_list = [ x for x in arguments_list if x['SentenceBlock'] == 'T']



# SF: set name of distractors' file

distractors_table=stimuli_dir + 'Distrattori.csv'

# SF: read stories' table from CSV file

distractors_list =data.importTrialList(distractors_table)

# SF: filter data in two lists (Practice and Test) depending on SentenceBlock flag

distractors_practice_list = [ x for x in distractors_list if x['ArgumentBlock'] == 'P']

distractors_test_list = [ x for x in distractors_list if x['ArgumentBlock'] == 'T']

""" SF: end addition """



""" SF: start removal

# SF: set name of fillers' file

fillers_table= stimuli_dir + 'Fillers.csv'

# SF: read fillers' table from CSV file

fillers_list = data.importTrialList(fillers_table)

# SF: filter data in two lists (Practice and Test) depending on FillerBlock flag

fillers_practice_list = [ x for x in fillers_list if x['FillerBlock'] == 'P']

fillers_test_list = [ x for x in fillers_list if x['FillerBlock'] == 'T']

SF: end removal """



# SF: Check if lists of Practice/Test stories are balanced, if not quit

CheckStoryListBalancement(stories_practice_list, False)

CheckStoryListBalancement(stories_test_list, True)



# SF: Split the stories in 2 sets depending on genre and context

stories_M = [ i for i in xrange(0, len(stories_test_list)) if stories_test_list[i]['Gender'] == 'M' ]

stories_F = [ i for i in xrange(0, len(stories_test_list)) if stories_test_list[i]['Gender'] == 'F' ]

stories_M_first, stories_M_second = test_stories_split_by_context(stories_M, stories_test_list)

stories_F_first, stories_F_second = test_stories_split_by_context(stories_F, stories_test_list)



stories_first_test_list = [ stories_test_list[i] for i in stories_M_first + stories_F_first ]

stories_second_test_list = [ stories_test_list[i] for i in stories_M_second + stories_F_second ]



stories_M = [ i for i in xrange(0, len(stories_practice_list)) if stories_practice_list[i]['Gender'] == 'M' ]

stories_F = [ i for i in xrange(0, len(stories_practice_list)) if stories_practice_list[i]['Gender'] == 'F' ]

stories_M_first, stories_M_second = practice_stories_split_by_context(stories_M, stories_practice_list)

stories_F_first, stories_F_second = practice_stories_split_by_context(stories_F, stories_practice_list)



# SF: join stories from "male" and "female" positive sets

stories_first_practice_list = [ stories_practice_list[i] for i in stories_M_first + stories_F_first ]

# SF: join stories from "male" and "female" negative sets

stories_second_practice_list = [ stories_practice_list[i] for i in stories_M_second + stories_F_second ]



# Split the fillers

# SF: create a random permutation with half the elements in the filler list

rp = RandomPermutation(len(fillers_test_list)/2)

# SF: create a permutation with the first half of the elements (?)

permutation = [ rp.select() for i in xrange(0, len(fillers_test_list)/2) ]

fillers_first_test_list = [ fillers_test_list[i] for i in permutation ]

fillers_second_test_list = [ fillers_test_list[j] for j in xrange(0, len(fillers_test_list)) if j not in permutation ]



# Keyboard input

choice_keys_dict = {}

if keyb == 'US':

    choice_keys_dict['screen'] = keys_screen = { 'left': 'a', 'right': '\\' }

    choice_keys_dict['input']  = { 'a': 'a', 'backslash': '\\' }

elif keyb == 'IT':

    choice_keys_dict['screen'] = keys_screen = { 'left': 'q', 'right': '+' }

    choice_keys_dict['input']  = { 'q': 'q', 'plus': '+' }

else:

    msgDialog('Keyboard layout not supported')

    quitExpe()



# File names  

file_name = data_dir + os.path.sep + '%s_%s_%s_%s_%s_%s_%s' %(expInfo[dk.expInfoSex], expInfo[dk.expInfoCondition],

# SF: removed: expInfo[dk.expInfoPattern],

expInfo[dk.expInfoSide], expInfo[dk.expInfoHand], expInfo[dk.expInfoExpName], expInfo[dk.expInfoDate])

logfile_name = file_name+'.log'

excel_file = file_name+'.xlsx'

psychopy.log.console.setLevel(psychopy.log.warning) 

log_file = psychopy.log.LogFile(logfile_name, level=psychopy.log.EXP, encoding='utf8')

#files_to_move.append(logfile_name)

files_to_move.append(excel_file)



# setup the Window

window_size=screen_size()

win = visual.Window(size=window_size, fullscr=True, screen=0, allowGUI=False, allowStencil=False, color='Black', colorSpace='rgb')



# Set up instructions

text_elem = {

    'begin':   

        { 'fname': 'instruction_begin.txt', 'font': my_font, 'pos': (0, 0), 'height': 0.05, 'color': 'white', 'HAlign':'center', 'VAlign':'center', 'wrapWidth': 1.2 },

    'begin_sp':   

        { 'fname': 'None', 'font': my_font, 'pos': (0, 0), 'height': 0.05, 'color': 'white', 'HAlign':'center', 'VAlign':'center', 'wrapWidth': 1.2 },

    'begin_pp':   

        { 'fname': 'None', 'font': my_font, 'pos': (0, 0), 'height': 0.05, 'color': 'white', 'HAlign':'center', 'VAlign':'center', 'wrapWidth': 1.2 },

    'begin_ic':   

        { 'fname': 'instruction_mc_begin.txt', 'font': my_font, 'pos': (0, 0), 'height': 0.05, 'color': 'white', 'HAlign':'center', 'VAlign':'center', 'wrapWidth': 1.2 },

    'end':     

        { 'fname': 'instruction_end.txt', 'font': my_font, 'pos': (0, 0), 'height': 0.08, 'color': 'white', 'HAlign':'center', 'VAlign':'center', 'wrapWidth': 1 },

    'generic':  

        { 'fname': None, 'font': my_font, 'pos': (0, -0.8), 'height': 0.05, 'color': 'yellow', 'HAlign':'center', 'VAlign':'center', 'wrapWidth': 2 },

    'attention_getter':  

        { 'fname': None, 'text':'+', 'font': 'Arial', 'pos': (0, 0), 'height': 0.25, 'color': 'red', 'HAlign':'center', 'VAlign':'center', 'wrapWidth': 2 },

    'adjective':

        { 'fname': None, 'font': 'Arial', 'pos': (0, 0.4), 'height': 0.2, 'color': 'white', 'HAlign':'center', 'VAlign':'center', 'wrapWidth': 2 },

    'choice_adjective':

        { 'fname': None, 'font': my_font, 'pos': (0, -0.3), 'height': 0.07, 'color': 'yellow', 'HAlign':'center', 'VAlign':'center', 'wrapWidth': 1.5 },

    'choice_face':

        { 'fname': None, 'font': my_font, 'pos': (0, -0.7), 'height': 0.07, 'color': 'yellow', 'HAlign':'center', 'VAlign':'center', 'wrapWidth': 1.5 },

    'prime':     

        { 'fname': None, 'font': my_font, 'pos': (0, 0.2), 'height': 0.08, 'color': 'white', 'HAlign':'center', 'VAlign':'center', 'wrapWidth': 1.5 },

    'target':     

        { 'fname': None, 'font': my_font, 'pos': (0, -0.1), 'height': 0.08, 'color': 'red', 'HAlign':'center', 'VAlign':'center', 'wrapWidth': 1 },

    'choice_prime':

        { 'fname': None, 'font': my_font, 'pos': (0, -0.6), 'height': 0.07, 'color': 'yellow', 'HAlign':'center', 'VAlign':'center', 'wrapWidth': 2 },

    'question':

        { 'fname': None, 'font': my_font, 'pos': (0, -0.3), 'height': 0.07, 'color': 'yellow', 'HAlign':'center', 'VAlign':'center', 'wrapWidth': 1.2 },

    'filler':     

        { 'fname': None, 'font': my_font, 'pos': (0, 0.2), 'height': 0.08, 'color': 'white', 'HAlign':'center', 'VAlign':'center', 'wrapWidth': 1.5 },

    'choice_filler':

        { 'fname': None, 'font': my_font, 'pos': (0, -0.5), 'height': 0.07, 'color': 'yellow', 'HAlign':'center', 'VAlign':'center', 'wrapWidth': 2 },

}



for e in text_elem:   

    t = text_elem[e]

    if t['fname'] == None:

        if not ('text' in t):

            t['text'] = None

    else:

        print instruction_dir + t['fname']

        instruction_file = open(instruction_dir + t['fname'], 'r')

        t['text'] = instruction_file.read()

        instruction_file.close()

    t['obj'] = visual.TextStim(win=win, ori=0, text=t['text'],

        alignHoriz=t['HAlign'], alignVert=t['VAlign'],

        font=t['font'], pos=t['pos'], height=t['height'],

        color=t['color'], colorSpace=u'rgb', wrapWidth=t['wrapWidth'])



# SF: get rid of pictures

"""

patch_elem = {

    'face': 

        { 'dir': pictures_dir, 'tex': None, 'pos': (0,100), 'size': (506, 650), 'units':'pix', 'mask': None }

}



for e in patch_elem:   

    p = patch_elem[e]

    p['obj'] = visual.PatchStim(win=win, tex=None, mask=u'None',

             ori=0, pos=[0, 100], size=[506, 650], units='pix', sf=None, phase=0.0,

             color=[1,1,1], colorSpace=u'rgb',

             texRes=128, interpolate=False)

"""



###################

# SEMANTIC PRIMING

###################



def semantic_task(adjectives, text_elem, choice_keys_dict, sheet_name, extra_info, side_info_dict, data_file, append):

    adjectives_len = len(adjectives)

    adjectives_permutation = RandomPermutation(adjectives_len)



    trial_clock = core.Clock()

    trials_list = [ { 'Trial': '%d' %(i+1) } for i in xrange(0, 2*adjectives_len) ]

    trials = data.TrialHandler(trialList = trials_list, nReps=1, method=u'sequential', extraInfo=extra_info)

    trial_count = 0

    

    for thisTrial in trials:

        which_adjective = adjectives_permutation.select()

        adjective_info = adjectives[which_adjective]

        text_elem['adjective']['obj'].setText(adjective_info['Adjective'])

        

        #run the trial

        keys_to_press = choice_keys_dict['input'].keys()

        timestamps = []

        register_time = False

        continue_trial=True

        event.clearEvents()

        t=0; trial_clock.reset()

    

        while continue_trial and (t<1000000.0000):

            t = trial_clock.getTime()

            rt_k, keys = key_pressed(trial_clock, keys_to_press)

            

            if t >= 0:



                if len(keys) == 0:

                    text_elem['adjective']['obj'].draw()

                    text_elem['choice_adjective']['obj'].draw()

                    register_time = True

                elif len(timestamps) > 0:

                    rt_adjective = rt_k - timestamps[0]

                    key_adjective = choice_keys_dict['input'][keys[0]]

                    continue_trial = False

                    if trial_count < 2*adjectives_len - 1:

                        text_elem['choice_adjective']['obj'].draw()

                    

            win.flip()

            

            if register_time:

                timestamps.append(trial_clock.getTime())

                register_time = False

            

        for k,v in adjective_info.items():

            trials.addData(k, v)

                    

        trials.addData('Key', key_adjective)

        trials.addData('Response', side_info_dict['CHOICE'][key_adjective])

        trials.addData('RT', rt_adjective)

        trial_count += 1

        core.wait(0.5)



    trials.saveAsExcel(data_file, sheetName = sheet_name,

                       stimOut=[],

                       dataOut=['all_raw'],

                       appendFile = append)

                       



###################

# PICTURE PRIMING

###################



def picture_task(pictures, text_elem, patch_elem, choice_keys_dict, sheet_name, extra_info, side_info_dict, data_file, append):

    pictures_len = len(pictures)

    pictures_permutation = RandomPermutation(pictures_len)

    

    trial_clock = core.Clock()

    trials_list = [ { 'Trial': '%d' %(i+1) } for i in xrange(0, 2*pictures_len) ]

    trials = data.TrialHandler(trialList = trials_list, nReps=1, method=u'sequential', extraInfo=extra_info)

    trial_count = 0

    

    for thisTrial in trials:

        which_picture = pictures_permutation.select()

        picture_info = pictures[which_picture]

        patch_elem['face']['obj'].setTex(patch_elem['face']['dir'] + picture_info['Face'])

        

        #run the trial

        keys_to_press = choice_keys_dict['input'].keys()

        timestamps = []

        register_time = False

        continue_trial=True

        event.clearEvents()

        t=0; trial_clock.reset()

    

        while continue_trial and (t<1000000.0000):

            t = trial_clock.getTime()

            rt_k, keys = key_pressed(trial_clock, keys_to_press)

            

            if t >= 0:



                if len(keys) == 0:

                    patch_elem['face']['obj'].draw()

                    text_elem['choice_face']['obj'].draw()

                    register_time = True

                elif len(timestamps) > 0:

                    rt_picture = rt_k - timestamps[0]

                    key_picture = choice_keys_dict['input'][keys[0]]

                    continue_trial = False

                    if trial_count < 2*pictures_len - 1:

                        text_elem['choice_face']['obj'].draw()

                    

            win.flip()

            

            if register_time:

                timestamps.append(trial_clock.getTime())

                register_time = False

                

        for k,v in picture_info.items():

            trials.addData(k, v)

                    

        trials.addData('Key', key_picture)

        trials.addData('Response', side_info_dict['CHOICE'][key_picture])

        trials.addData('RT', rt_picture)

        trial_count += 1

        core.wait(0.5)



    trials.saveAsExcel(data_file, sheetName = sheet_name,

                       stimOut=[],

                       dataOut=['all_raw'],

                       appendFile = append)



#############

# IRONY TASK

#############





def metaphor_task(practice, stories, fillers, text_elem, choice_keys_dict, sheet_name, extra_info, side_info_dict, msg_at_last, data_file, append):



    def marked_story_balance(stories, stories_G_C, targets):

        stories_G_C_Marked_Neg = [ i for i in stories_G_C if stories[i]['Mark'] == 1 and targets[i] == 0 ]

        stories_G_C_Marked_Pos = [ i for i in stories_G_C if stories[i]['Mark'] == 1 and targets[i] == 1 ]

        stories_G_C_Normal_Neg = [ i for i in stories_G_C if stories[i]['Mark'] == 0 and targets[i] == 0 ]

        n = len(stories_G_C)/2 - len(stories_G_C_Marked_Neg)

        if n <= 0:

            return

        rp_mp = RandomPermutation(len(stories_G_C_Marked_Pos))

        rp_nn = RandomPermutation(len(stories_G_C_Normal_Neg))

        while n > 0:

            targets[stories_G_C_Marked_Pos[rp_mp.select()]] = 0

            targets[stories_G_C_Normal_Neg[rp_nn.select()]] = 1

            n -= 1

            

    def randomize_targets(stories, practice):    

        targets = [-1] * len(stories)

        for gnd in ['M','F']:

            for ctx in ['P','N']:

                stories_G_C = [ i for i in xrange(0, len(stories)) if stories[i]['Gender'] == gnd and stories[i]['Context'] == ctx ]

                rp = RandomPermutation(len(stories_G_C))

                for i in xrange(0, len(stories_G_C)):

                    targets[stories_G_C[rp.select()]] = i % 2 # 0 == negative target

                if not practice and ctx == 'P':

                    marked_story_balance(stories, stories_G_C, targets)

        return targets

    

    stories_len = len(stories)

    fillers_len = len(fillers)

    rp = RandomPermutation(stories_len)

    stories_permutation = [ rp.select() for x in stories ] 

    targets_permutation = randomize_targets(stories, practice)

    rp = RandomPermutation(fillers_len)

    fillers_permutation = [ rp.select() for x in fillers ]

   

    trial_clock = core.Clock()

    trials_list = [ { 'Trial': '%d' %(i+1) } for i in xrange(0, stories_len) ]

    trials = data.TrialHandler(trialList = trials_list, nReps=1, method=u'sequential', extraInfo=extra_info)

        

    trial_count = 0

    for thisTrial in trials:

                

        which_story = stories_permutation[trial_count]

        story_info = stories[which_story]

        target_word = targets_permutation[stories_permutation[trial_count]] == 0 and 'TW_Negative' or 'TW_Positive'

        which_filler = fillers_permutation[trial_count]

        filler_info = fillers[which_filler]

        text_elem['prime']['obj'].setText(story_info['Sentence'])

        text_elem['target']['obj'].setText(story_info[target_word])

        text_elem['filler']['obj'].setText(filler_info['Filler'])

        text_elem['generic']['obj'].setText(u'Appuyer sur la barre Â« espace Â» pour lire le dernier mot...')

        text_elem['generic']['obj'].setPos((0,-0.4))

        text_elem['generic']['obj'].setHeight(0.06)

        show(win, [ text_elem['attention_getter']['obj'] ], exit_keys = [], mouse_btns = [], delay = 0.5)

        

        timestamps = []

        register_time = False

        keys_to_press = ['space']

        event.clearEvents()

        continue_trial = True

        t = 0; step = 0; trial_clock.reset()

        

        while continue_trial and (t < 1000000.0000):

            t = trial_clock.getTime()

            rt_k, keys = key_pressed(trial_clock, keys_to_press)

              

            if t >= 0:

                

                if step == 0:

                    

                    if len(keys) == 0:

                        text_elem['prime']['obj'].draw()

                        text_elem['generic']['obj'].draw()

                    else:

                        keys_to_press = choice_keys_dict['input'].keys()

                        register_time = True

                        step = 1

                    

                if step == 1:

                    

                    if len(timestamps) == 0 or t < timestamps[0] + 1.0:

                        text_elem['prime']['obj'].draw()

                        text_elem['target']['obj'].draw()

                    else:

                        keys = []

                        event.getKeys()

                        register_time = True

                        step = 2

                    

                if step == 2:

                    

                    if len(keys) == 0:

                        #text_elem['prime']['obj'].draw()

                        text_elem['question']['obj'].draw()

                        text_elem['choice_prime']['obj'].draw()

                    elif len(timestamps) == 2:

                        rt_prime = rt_k - timestamps[1]

                        key_prime = choice_keys_dict['input'][keys[0]]

                        keys = []

                        event.getKeys()

                        register_time = True

                        step = 3

                        

                if step == 3:

                    

                    if len(keys) == 0:

                        text_elem['filler']['obj'].draw()

                        text_elem['choice_filler']['obj'].draw()

                    elif len(timestamps) == 3:

                        rt_filler = rt_k - timestamps[2]

                        key_filler = choice_keys_dict['input'][keys[0]]

                        continue_trial = False

            

            win.flip()

            

            # time registration right after flipping

            if register_time:

                timestamps.append(trial_clock.getTime())

                register_time = False

                

        for k,v in story_info.items():

            trials.addData(k, v)

                    

        trials.addData('TW_Type', target_word)

        trials.addData('TW_Value', story_info[target_word])

        trials.addData('RT_Prime', rt_prime)

        trials.addData('Key_Prime', key_prime)

        trials.addData('Response_Prime', side_info_dict['CHOICE_PRIME'][key_prime])

        

        for k,v in filler_info.items():

            trials.addData(k, v)

     

        trials.addData('RT_Filler', rt_filler)

        trials.addData('Key_Filler', key_filler)

        trials.addData('Response_Filler', side_info_dict['CHOICE_FILLER'][key_filler])

        

        trial_count += 1

        '''

        if trial_count < stories_len or msg_at_last:

            text_elem['generic']['obj'].setPos((0,0))

            text_elem['generic']['obj'].setHeight(0.07)

            text_elem['generic']['obj'].setText(u'Appuyer sur la barre Â« espace Â» pour poursuivre...')

            show(win, [ text_elem['generic']['obj'] ], exit_keys = ['space'], mouse_btns = [], delay = 100000)

        '''

    trials.saveAsExcel(data_file, sheetName = sheet_name,

                       stimOut=[],

                       dataOut=['all_raw'],

                       appendFile = append)





######################

# Experiment segments

######################



# This is just a way to arrange the pieces of the expe: no parameters passed to the functions, only locals and globals



# SF: show general instructions

def general_instruction():

    text_elem['generic']['obj'].setText(u'Appuyer sur la barre Â« espace Â» pour commencer...')

    text_elem['generic']['obj'].setPos((0, -0.35))

    show(win, [ text_elem['begin']['obj'], text_elem['generic']['obj']], exit_keys = ['space'], mouse_btns = [], delay = 100000)



# SF: show semantic priming

def semantic_priming():

# SF: set up a first priming defining the Yes/No sides

    side_sp_dict = {}

    side_sp_dict['FM'] = cond_dict['gender'] == 'M' and u'Maschile' or u'Femminile'

    side_sp_dict['SIDE_FM'] = expInfo[dk.expInfoSide].value == dk.sideDefault and keys_screen['left'] or keys_screen['right']

    side_sp_dict['SIDE_NEUTRAL'] = expInfo[dk.expInfoSide].value == dk.sideDefault and keys_screen['right']  or keys_screen['left']

    side_sp_dict['CHOICE'] = side_sp_choice_dict = {}

    side_sp_choice_dict[keys_screen['left']] = expInfo[dk.expInfoSide].value == dk.sideDefault and side_sp_dict['FM'] or 'Neutro'

    side_sp_choice_dict[keys_screen['right']] = expInfo[dk.expInfoSide].value == dk.sideDefault and 'Neutre' or side_sp_dict['FM']



    text_elem['generic']['obj'].setText(u'Premere la barra dello « spazio » per cominciare...')

    text_elem['generic']['obj'].setPos((0, -0.5))

    text_elem['generic']['obj'].setHeight(0.05)

    text_elem['begin_sp']['obj'].setText(text_elem['begin_sp']['text'] %side_sp_dict)

    text_elem['choice_adjective']['obj'].setText('[ %s ] <- %s                       %s -> [ %s ]' %(keys_screen['left'], side_sp_choice_dict[keys_screen['left']], side_sp_choice_dict[keys_screen['right']], keys_screen['right']))

# SF: run the priming

    show(win, [ text_elem['begin_sp']['obj'], text_elem['generic']['obj']], exit_keys = ['space'], mouse_btns = [], delay = 100000)

    semantic_task(adjectives_cond_list, text_elem, choice_keys_dict, 'Semantic Priming', expInfoStr, side_sp_dict, data_file = excel_file, append = True)



    text_elem['generic']['obj'].setText(u"Avete completato questa parte dell'esperimento !\nPremere la barra dello « spazio » per passare alla successiva...")

    text_elem['generic']['obj'].setPos((0, 0))

    text_elem['generic']['obj'].setHeight(0.07)

    show(win, [ text_elem['generic']['obj']], exit_keys = ['space'], mouse_btns = [], delay = 100000)



# SF: show picture priming (not to be taken into consideration for Metaphor Comprehension

def picture_priming():

    side_pp_dict = {}

    side_pp_dict['PN'] = cond_dict['type'] == 'P' and u'positif' or u'negatif'

    side_pp_dict['SIDE_PN'] = expInfo[dk.expInfoSide].value == dk.sideDefault and keys_screen['left'] or keys_screen['right']

    side_pp_dict['SIDE_NEUTRAL'] = expInfo[dk.expInfoSide].value == dk.sideDefault and keys_screen['right']  or keys_screen['left']

    side_pp_dict['CHOICE'] = side_pp_choice_dict = {}

    side_pp_choice_dict[keys_screen['left']] = expInfo[dk.expInfoSide].value == dk.sideDefault and side_pp_dict['PN'] or 'neutre'

    side_pp_choice_dict[keys_screen['right']] = expInfo[dk.expInfoSide].value == dk.sideDefault and 'neutre' or side_pp_dict['PN']

    

    text_elem['generic']['obj'].setText(u'Appuyer sur la barre Â« espace Â» pour commencer...')

    text_elem['generic']['obj'].setPos((0, -0.5))

    text_elem['generic']['obj'].setHeight(0.05)

    text_elem['begin_pp']['obj'].setText(text_elem['begin_pp']['text'] %side_pp_dict)

    text_elem['choice_face']['obj'].setText('[ %s ] <- %s                       %s -> [ %s ]' %(keys_screen['left'], side_pp_choice_dict[keys_screen['left']], side_pp_choice_dict[keys_screen['right']], keys_screen['right']))

    

    show(win, [ text_elem['begin_pp']['obj'], text_elem['generic']['obj']], exit_keys = ['space'], mouse_btns = [], delay = 100000)

    picture_task(faces_cond_list, text_elem, patch_elem, choice_keys_dict, 'Picture Priming', expInfoStr, side_pp_dict, data_file = excel_file, append = True)

    

    text_elem['generic']['obj'].setText(u"Vous avez bien terminÃ© cette partie de l'expÃ©rience !\nAppuyer sur la barre Â« espace Â» pour passer Ã  la suivante...")

    text_elem['generic']['obj'].setPos((0, 0))

    text_elem['generic']['obj'].setHeight(0.07)

    show(win, [ text_elem['generic']['obj']], exit_keys = ['space'], mouse_btns = [], delay = 100000)



side_mc_dict = {}



# SF: run first half of the test

def metaphor_comprehension_first():

    global side_mc_dict

# SF: set up a first experiment defining the Yes/No sides

    side_mc_dict['SIDE_POSITIVE'] = expInfo[dk.expInfoSide].value == dk.sideDefault and keys_screen['left'] or keys_screen['right']

    side_mc_dict['SIDE_NEGATIVE'] = expInfo[dk.expInfoSide].value == dk.sideDefault and keys_screen['right'] or keys_screen['left']

    side_mc_dict['CHOICE_PRIME'] = side_mc_choice_prime_dict = {}

    side_mc_choice_prime_dict[keys_screen['left']] = expInfo[dk.expInfoSide].value == dk.sideDefault and u'Buono' or u'Cattivo'

    side_mc_choice_prime_dict[keys_screen['right']] = expInfo[dk.expInfoSide].value == dk.sideDefault and u'Cattivo' or u'Buono'

    side_mc_dict['CHOICE_FILLER'] = side_mc_choice_filler_dict = {}

    side_mc_choice_filler_dict[keys_screen['left']] = expInfo[dk.expInfoSide].value == dk.sideDefault and u'Si' or u'No'

    side_mc_choice_filler_dict[keys_screen['right']] = expInfo[dk.expInfoSide].value == dk.sideDefault and u'No' or u'Si'

    

    text_elem['choice_prime']['obj'].setText(u'[ %s ] <- %s               %s -> [ %s ]' %(keys_screen['left'], side_mc_choice_prime_dict[keys_screen['left']], side_mc_choice_prime_dict[keys_screen['right']], keys_screen['right']))

    text_elem['choice_filler']['obj'].setText(u'[ %s ] <- %s                   %s -> [ %s ]' %(keys_screen['left'], side_mc_choice_filler_dict[keys_screen['left']], side_mc_choice_filler_dict[keys_screen['right']], keys_screen['right']))

    text_elem['question']['obj'].setText(u'Il personaggio che esprime il commento è buono o cattivo?')

    text_elem['begin_ic']['obj'].setText(text_elem['begin_ic']['text'] %side_mc_dict)

    text_elem['generic']['obj'].setText(u'Premere la barra dello « spazio » per cominciare...')

    text_elem['generic']['obj'].setPos((0, -0.8))

    text_elem['generic']['obj'].setHeight(0.05)

    

    show(win, [ text_elem['begin_ic']['obj'], text_elem['generic']['obj']], exit_keys = ['space'], mouse_btns = [], delay = 100000)

    metaphor_task(True, stories_first_practice_list,  fillers_practice_list, text_elem, choice_keys_dict, 'Metaphor Comprehension Practice 1', expInfoStr, side_mc_dict, msg_at_last = True, data_file = excel_file, append = True)

    metaphor_task(False, stories_first_test_list, fillers_first_test_list, text_elem, choice_keys_dict, 'Metaphor Comprehension Test 1', expInfoStr, side_mc_dict, msg_at_last = False, data_file = excel_file, append = True)

    

    text_elem['generic']['obj'].setText(u"Avete completato questa parte dell'esperimento !\nPremere la barra dello « spazio » per passare alla successiva...")

    text_elem['generic']['obj'].setPos((0, 0))

    text_elem['generic']['obj'].setHeight(0.07)

    show(win, [ text_elem['generic']['obj']], exit_keys = ['space'], mouse_btns = [], delay = 100000)

 

# SF: run second half of the test

def metaphor_comprehension_second():

    global side_mc_dict

    text_elem['generic']['obj'].setText(u'Premere la barra dello « spazio » per cominciare...')

    text_elem['generic']['obj'].setPos((0, -0.8))

    text_elem['generic']['obj'].setHeight(0.05)

    show(win, [ text_elem['begin_ic']['obj'], text_elem['generic']['obj']], exit_keys = ['space'], mouse_btns = [], delay = 100000)

    metaphor_task(True, stories_second_practice_list,  fillers_practice_list, text_elem, choice_keys_dict, 'Metaphor Comprehension Practice 2', expInfoStr, side_mc_dict, msg_at_last = True, data_file = excel_file, append = True)

    metaphor_task(False, stories_second_test_list, fillers_second_test_list, text_elem, choice_keys_dict, 'Metaphor Comprehension Test 2', expInfoStr, side_mc_dict, msg_at_last = False, data_file = excel_file, append = True)

    

# SF: run a temporary break between first and second half of the test

def temporary_break():

    text_elem['generic']['obj'].setText(u"E' ORA DI FARE UNA PAUSA !\nChiamate lo sperimentatore...")

    text_elem['generic']['obj'].setColor('red')

    text_elem['generic']['obj'].setHeight(0.08)

    text_elem['generic']['obj'].setPos((0, 0))

    show(win, [ text_elem['generic']['obj']], exit_keys = ['p'], mouse_btns = [], delay = 100000)

    text_elem['generic']['obj'].setColor('yellow')



# SF: end the test

def end():

    files_to_move = []

    show(win, [ text_elem['end']['obj'] ], mouse_btns=[], exit_keys = [], delay = 5)



######################

# Experiment template

######################



# SF: show general instructions

general_instruction()



# SF: set up a different priming depending on the schema selected by the subject

# SF: removed: if expInfoStr[dk.expInfoPattern] == dk.patternSemanticPicture:

# SF: show semantic priming

    semantic_priming()

else:

# SF: show picture priming

# SF: removed:     picture_priming()



# SF: run first half of the test

metaphor_comprehension_first()

# SF: run a temporary break between first and second half of the test

temporary_break()



# SF: set up again a different priming depending on the schema selected by the subject

# SF: removed: if expInfoStr[dk.expInfoPattern] == dk.patternSemanticPicture:

# SF: show semantic priming

# SF: removed:     picture_priming()

else:

# SF: show picture priming

    semantic_priming()



# SF: run second half of the test

metaphor_comprehension_second()

# SF: end the test

end()



###########

# Shutdown

###########



win.close()

core.quit()



