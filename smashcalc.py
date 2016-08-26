#!/usr/bin/python3.5

"""
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
*< smashcalc.py
*< Author: Euklyd / Fulminant Edge
*< Contact: Discord: euklyd (FE)#3650 (preferred method)
*           http://twitter.com/euklydia (rarely used, but I do check it)
*           Email: euklyd (dot) sf (at) gmail.com
*< Version: 0.2
*< Super barebones applet to calculate knockback and hitstun. Pulls from the
*  KuroganeHammer API. KuroganeHammer and Frannsoft are absolute saints; I
*  can't believe such a convenient API exists.
*
*< Formulas and credits: http://kuroganehammer.com/Smash4/Formulas
*< API documentation: https://github.com/Frannsoft/FrannHammer/wiki
*< Livedocs: http://api.kuroganehammer.com/swagger/ui/index
*
*< TO-DO:      - Add actual documetation strings,
*              - clean up code,
*              - parse weird percent fields (like Fox's throws),
*              - make user interface look pretty (or at least not terrible).
*< Pipe-dream: Implement all this in HTML and JavaScript, so that it could be
*              (potentially) hosted on an actual website. Unfortuantely JS
*              can't make external requests, so the only place that could work
*              is if it were hosted on KuroganeHammer itself.
*              I'm also just not that skilled at JavaScript.
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
"""

from tkinter import ttk, Tk, StringVar, DoubleVar, IntVar
import urllib.request
import json
import math

api_url = "http://api.kuroganehammer.com/api"


"""
Displays knockback, hitstun, and shieldstun outputs.
"""
class ResultsFrame(ttk.Frame):
    def __init__(self, parent, row_n):
        print("ResultsFrame __init__")
        self.parent = parent
        self.results_frame = ttk.Frame(self.parent)
        self.results_frame.grid(column=0, row=(row_n+2))
        self.results_frame['relief'] = 'sunken'

        self.empty = True
        self.init_ui()
        self.clear_fields()

    def init_ui(self):
        self.total_kb = ttk.Label(self.results_frame)
        self.hitstun = ttk.Label(self.results_frame)
        self.shieldstun = ttk.Label(self.results_frame)
        self.powerstun = ttk.Label(self.results_frame)
        self.projstun = ttk.Label(self.results_frame)
        self.pprojstun = ttk.Label(self.results_frame)

        self.total_kb.grid(column=0, row=0, columnspan=2, sticky="W")
        self.hitstun.grid(column=0, row=1, columnspan=2, sticky="W")
        self.shieldstun.grid(column=0, row=2, columnspan=1, sticky="W")
        self.powerstun.grid(column=0, row=3, columnspan=1, sticky="W")
        self.projstun.grid(column=1, row=2, columnspan=1, sticky="W")
        self.pprojstun.grid(column=1, row=3, columnspan=1, sticky="W")

    def clear_fields(self):
        self.total_kb['text'] = "Total knockback: {}".format("")
        self.hitstun['text'] = "Hitstun: {}".format("")

        self.shieldstun['text'] = "Shield stun: {}".format("")
        self.powerstun['text'] = "Perfect shield stun: {}".format("")
        self.projstun['text'] = "Projectile shield stun: {}".format("")
        self.pprojstun['text'] = "Powershield projectile shield stun: {}".format("")

        self.empty = True

    def set_fields(self, damage):
        self.sstun = int(damage / 1.72 + 3) - 1
        self.perfectstun = int(damage / 2.61 + 3) - 1
        self.pstun = int(damage / 3.5 + 3) - 1
        self.perfectpstun = int(damage / 5.22 + 3) - 1
        self.shieldstun['text'] = "Shield stun: {}".format(self.sstun)
        self.powerstun['text'] = "Perfect shield stun: {}".format(self.perfectstun)
        self.projstun['text'] = "Projectile shield stun: {}".format(self.pstun)
        self.pprojstun['text'] = "Powershield projectile shield stun: {}".format(self.perfectpstun)
        self.empty = False

    def set_kb(self, attr_dict):
        print("ResultsFrame.set_kb")
        # target_percent, base_damage, bkb, kbg, misc_multiplier, target_weight, staleness
        v = float(attr_dict['target_percent'])
        bd = float(attr_dict['base_damage'])
        s = float(attr_dict['staleness'])
        w = float(attr_dict['target_weight'])
        g = float(attr_dict['kbg'])
        b = float(attr_dict['bkb'])
        r = float(attr_dict['misc_multiplier'])
        self.kb = ((((((v+bd*s)/10+(((v+bd*s)*bd*(1-(1-s)*0.3))/20))*1.4*(200/(w+100)))+18)*(g/100))+b)*r
        print("MoveFrame set_kb: {}".format(self.kb))
        self.total_kb['text'] = "Total knockback: {}".format(self.kb)
        self.hitstun['text'] = "Hitstun: {}".format(math.floor(self.kb * 0.4) - 1)
        self.total_kb.grid()
        self.hitstun.grid()

    def show(self):
        self.results_frame.grid()

    def hide(self):
        self.results_frame.grid_remove()


"""
Displays infomation about the selected move. May have multiple displays for
different hitboxes on the same frame (e.g., sweetspots / sourspots,
spikeboxes, etc.)
"""
class MoveFrame(ttk.Frame):
    def __init__(self, parent):
        print("MoveFrame __init__")
        self.parent = parent
        self.move_frame = ttk.Frame(self.parent, padding=10)
        self.move_frame.grid(column=0, row=2)
        self.move_frame['relief'] = 'sunken'
        self.kb = ""
        self.results_list = []

        self.init_ui()
        self.clear_fields()

    def init_ui(self):
        print("MoveFrame init_ui")
        move_attr_padding = ((0, 0, 30, 0), (30, 0, 0, 0))
        self.id = ttk.Label(self.move_frame)
        self.type = ttk.Label(self.move_frame)
        self.name = ttk.Label(self.move_frame)
        self.damage = ttk.Label(self.move_frame, padding=move_attr_padding[0])
        self.angle = ttk.Label(self.move_frame, padding=move_attr_padding[1])
        self.bkb = ttk.Label(self.move_frame, padding=move_attr_padding[0])
        self.kbg = ttk.Label(self.move_frame, padding=move_attr_padding[1])
        self.hitbox_frames = ttk.Label(self.move_frame, padding=move_attr_padding[0])
        self.iasa = ttk.Label(self.move_frame, padding=move_attr_padding[1])
        self.landing_lag = ttk.Label(self.move_frame, padding=move_attr_padding[0])
        self.autocancel = ttk.Label(self.move_frame, padding=move_attr_padding[1])

        self.results_frame = ttk.Frame(self.move_frame, borderwidth=2)
        self.results_frame.grid(row=5)
        # self.total_kb = ttk.Label(self.results_frame)
        # self.hitstun = ttk.Label(self.results_frame)
        # self.shieldstun = ttk.Label(self.results_frame)
        # self.powerstun = ttk.Label(self.results_frame)
        # self.projstun = ttk.Label(self.results_frame)
        # self.pprojstun = ttk.Label(self.results_frame)

        self.name.grid(column=0, row=0, columnspan=2, sticky="EW")
        self.hitbox_frames.grid(column=0, row=1, columnspan=1, sticky="W")
        self.iasa.grid(column=1, row=1, columnspan=1, sticky="W")
        self.damage.grid(column=0, row=2, columnspan=1, sticky="W")
        self.angle.grid(column=1, row=2, columnspan=1, sticky="W")
        self.bkb.grid(column=0, row=3, columnspan=1, sticky="W")
        self.kbg.grid(column=1, row=3, columnspan=1, sticky="W")
        self.landing_lag.grid(column=0, row=4, columnspan=1, sticky="W")
        self.autocancel.grid(column=1, row=4, columnspan=1, sticky="W")

        self.NoMove = ttk.Label(self.results_frame, text="This move has no hitbox!\nFor details, look on http://kuroganehammer.com/Smash4")
        self.NoMove.grid(column=0, row=0)
        self.NoMove.grid_remove()

        # self.total_kb.grid(column=0, row=0, columnspan=2)
        # self.hitstun.grid(column=0, row=1, columnspan=2)
        # self.shieldstun.grid(column=0, row=2, columnspan=1, sticky="W")
        # self.powerstun.grid(column=0, row=3, columnspan=1, sticky="W")
        # self.projstun.grid(column=1, row=2, columnspan=1, sticky="W")
        # self.pprojstun.grid(column=1, row=3, columnspan=1, sticky="W")

    def set_fields(self, move_dict):
        for frame in self.results_list:
            frame.hide()
        print("MoveFrame set_fields")
        self.NoMove.grid_remove()
        move_type = ""
        if (move_dict['type'] == 0):
            move_type = "Aerial"
        elif (move_dict['type'] == 1):
            move_type = "Ground"
        elif (move_dict['type'] == 2):
            move_type = "Special"
        elif (move_dict['type'] == 3):
            move_type = "Throw"
        else:
            move_type = "Illegal move type: {}".format(move_dict['type'])
            print("shit, illegal move")

        self.hitbox_list = self.parse_move(move_dict)
        if (self.hitbox_list == None):
            self.NoMove.grid()
            return

        for i in range(len(self.hitbox_list)):
            if (len(self.hitbox_list) > len(self.results_list)):
                r = ResultsFrame(self.results_frame, len(self.results_list))
                print(self.hitbox_list[i])
                r.set_fields(float(self.hitbox_list[i]['baseDamage']))
                self.results_list.append(r)
            else:
                self.results_list[i].show()
                print("{}: {}".format(i, self.hitbox_list[i]))
                self.results_list[i].set_fields(float(self.hitbox_list[i]['baseDamage']))

        self.id['text'] = "ID = {}".format(move_dict['id'])
        self.type['text'] = "type: {}".format(move_type)
        self.name['text'] = "{}".format(move_dict['name'])
        self.damage['text'] = "Base damage: {}%".format(move_dict['baseDamage'])
        self.angle['text'] = "Angle: {}°".format(move_dict['angle'])
        self.bkb['text'] = "Base knockback: {}".format(move_dict['baseKnockBackSetKnockback'])
        self.kbg['text'] = "Knockback growth: {}".format(move_dict['knockbackGrowth'])
        self.hitbox_frames['text'] = "Frames active: {}".format(move_dict['hitboxActive'])
        self.iasa['text'] = "IASA/FAF: {}".format(move_dict['firstActionableFrame'])
        self.landing_lag['text'] = "Landing lag: {}".format(move_dict['landingLag'])
        self.autocancel['text'] = "Autocancel frames: {}".format(move_dict['autoCancel'])
        # self.total_kb['text'] = "Total knockback: {}".format("")
        # self.hitstun['text'] = "Hitstun: {}".format("")

        # self.sstun = int(float(move_dict['baseDamage']) / 1.72 + 3) - 1
        # self.perfectstun = int(float(move_dict['baseDamage']) / 2.61 + 3) - 1
        # self.pstun = int(float(move_dict['baseDamage']) / 3.5 + 3) - 1
        # self.perfectpstun = int(float(move_dict['baseDamage']) / 5.22 + 3) - 1
        # self.shieldstun['text'] = "Shield stun: {}".format(self.sstun)
        # self.powerstun['text'] = "Perfect shield stun: {}".format(self.perfectstun)
        # self.projstun['text'] = "Projectile shield stun: {}".format(self.pstun)
        # self.pprojstun['text'] = "Powershield projectile shield stun: {}".format(self.perfectpstun)

        self.empty = False

    def parse_move(self, move_dict):
        if (move_dict['baseDamage'] == ''):
            print("no hitbox")
            return None
        print("parsing move:")
        print(move_dict)
        hitbox_list = []
        n_dmg = 1
        n_bkb = 1
        n_kbg = 1
        n_ang = 1
        dmg = [0]
        bkb = [0]
        kbg = [0]
        ang = [0]
        if '/' in move_dict['baseDamage']:
            n_dmg = move_dict['baseDamage'].count('/') + 1
            dmg = move_dict['baseDamage'].split('/')
        if '/' in move_dict['baseKnockBackSetKnockback']:
            n_bkb = move_dict['baseKnockBackSetKnockback'].count('/') + 1
            bkb = move_dict['baseKnockBackSetKnockback'].split('/')
        if '/' in move_dict['knockbackGrowth']:
            n_kbg = move_dict['knockbackGrowth'].count('/') + 1
            kbg = move_dict['knockbackGrowth'].split('/')
        if '/' in move_dict['angle']:
            n_ang = move_dict['angle'].count('/') + 1
            ang = move_dict['angle'].split('/')

        try:
            for i in range(max(n_dmg, n_bkb, n_kbg, n_ang)):
                d = {}
                hitbox_list.append(d)
                if (n_dmg == 1):
                    hitbox_list[i]['baseDamage'] = move_dict['baseDamage']
                    dmg[0] = move_dict['baseDamage']
                else:
                    hitbox_list[i]['baseDamage'] = dmg[i]
                if (n_bkb == 1):
                    hitbox_list[i]['baseKnockBackSetKnockback'] = move_dict['baseKnockBackSetKnockback']
                    bkb[0] = move_dict['baseKnockBackSetKnockback']
                else:
                    hitbox_list[i]['baseKnockBackSetKnockback'] = bkb[i]
                if (n_kbg == 1):
                    hitbox_list[i]['knockbackGrowth'] = move_dict['knockbackGrowth']
                    kbg[0] = move_dict['knockbackGrowth']
                else:
                    hitbox_list[i]['knockbackGrowth'] = kbg[i]
                if (n_ang == 1):
                    hitbox_list[i]['angle'] = move_dict['angle']
                    ang[0] = move_dict['angle']
                else:
                    hitbox_list[i]['angle'] = ang[i]
        except IndexError:
            hitbox_list = [{'baseDamage' : dmg[0], 'baseKnockBackSetKnockback' : bkb[0],
                            'knockbackGrowth' : kbg[0], 'angle' : ang[0]}]

        for hitbox in hitbox_list:
            if 'W' in hitbox['baseKnockBackSetKnockback']:
                print('bkb = {}'.format(hitbox['baseKnockBackSetKnockback']))
                sp = hitbox['baseKnockBackSetKnockback'].find(' ') + 1
                hitbox['baseKnockBackSetKnockback'] = hitbox['baseKnockBackSetKnockback'][sp:]
                print("fixed kb = {}".format(hitbox['baseKnockBackSetKnockback']))

        return hitbox_list

    def set_kb(self, target_weight, target_percent, staleness=1, misc_variable=1):
        print("MoveFrame.set_kb")
        # target_percent, base_damage, bkb, kbg, misc_multiplier, target_weight, staleness
        for frame, hitbox in zip(self.results_list, self.hitbox_list):
            if (frame.empty):
                pass
            else:
                attr_dict = {'target_percent' : target_percent, 'base_damage' : hitbox['baseDamage'],
                             'bkb' : hitbox['baseKnockBackSetKnockback'],
                             'kbg' : hitbox['knockbackGrowth'], 'misc_multiplier' : misc_variable,
                             'target_weight' : target_weight, 'staleness' : staleness}
                frame.set_kb(attr_dict)
        # print("MoveFrame set_kb: {}".format(kb))
        # self.kb = float(kb)
        # self.total_kb['text'] = "Total knockback: {}".format(self.kb)
        # self.hitstun['text'] = "Hitstun: {}".format(math.floor(self.kb * 0.4) - 1)

    def clear_fields(self):
        print("MoveFrame clear_fields")
        self.NoMove.grid_remove()

        self.id['text'] = "ID = {}".format("")
        self.type['text'] = "type: {}".format("")
        self.name['text'] = "{}".format("")
        self.damage['text'] = "Base damage: {}%".format("")
        self.angle['text'] = "Angle: {}°".format("")
        self.bkb['text'] = "Base knockback: {}".format("")
        self.kbg['text'] = "Knockback growth: {}".format("")
        self.hitbox_frames['text'] = "Frames active: {}".format("")
        self.iasa['text'] = "IASA/FAF: {}".format("")
        self.landing_lag['text'] = "Landing lag: {}".format("")
        self.autocancel['text'] = "Autocancel frames: {}".format("")
        # self.total_kb['text'] = "Total knockback: {}".format("")
        # self.hitstun['text'] = "Hitstun: {}".format("")
        # self.shieldstun['text'] = "Shield stun: {}".format("")
        # self.powerstun['text'] = "Perfect shield stun: {}".format("")
        # self.projstun['text'] = "Projectile shield stun: {}".format("")
        # self.pprojstun['text'] = "Powershield projectile shield stun: {}".format("")

        for r in self.results_list:
            r.clear_fields()
            r.hide()

        self.empty = True


"""
The main window. Contains everything else, and manages selections of
characters / moves as well as user input of text fields and checkboxes.
"""
class SmashCalc(ttk.Frame):
    def __init__(self, parent):
        print("SmashCalc __init__")
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.chars_url = "{}/characters".format(api_url)
        self.get_chars()
        self.init_ui()
        self.rage = 1
        self.move_name = ""
        self.enemy_weight = -1

    def init_ui(self):
        print("UI init")
        self.set_title()
        # charbox = ttk.Listbox()
        print("making frames")
        print(type(self.parent))
        self.content = ttk.Frame(self.parent, padding=10)
        print(type(self.content))
        self.content.grid(column=0, row=0, sticky="NSEW")
        # self.user_image
        # self.enemy_image
        print("making boxes")
        self.init_user()
        self.init_enemy()
        self.init_move()

    def init_user(self):
        self.user_frame = ttk.Frame(self.content, borderwidth=2)
        self.user_frame.grid(column=0, row=0)
        self.user_frame['padding'] = (20,10)
        # self.user_frame['borderwidth'] = 2
        self.user_frame['relief'] = 'sunken'

        self.user_label = ttk.Label(self.user_frame, text="Attacker")
        self.user_label.grid(column=0, row=0, columnspan=2, rowspan=1)

        self.userchar = StringVar()
        self.userchar.set('none')
        self.user_menu = ttk.Combobox(self.user_frame)
        self.user_menu.grid(column=0, row=1, columnspan=2, rowspan=1)
        self.user_menu['values'] = self.chars
        self.user_menu.bind('<<ComboboxSelected>>', self.on_user_menu_input)

        self.userdmg = StringVar()
        self.userdmg.set('')
        self.userdmg.trace('w', self.on_user_damage_input)

        self.rage_box = ttk.Label(self.user_frame, text="Rage multiplier:")
        self.rage_box.grid(column=0, row=5, columnspan=2, sticky="W")
        self.user_percentbox = ttk.Label(self.user_frame, text="%:")
        self.user_percentbox.grid(column=0, row=2, columnspan=1, rowspan=1, sticky="W")
        validate_cmd = (self.register(self.on_percent_validate), '%d', '%S', '%P')
        self.user_damage_entry = ttk.Entry(self.user_frame, textvariable=self.userdmg,
                                           validate="key", validatecommand=validate_cmd)
        self.user_damage_entry.grid(column=1, row=2, columnspan=1, rowspan=1, sticky="W")

    def init_enemy(self):
        self.enemy_frame = ttk.Frame(self.content, borderwidth=2)
        self.enemy_frame.grid(column=1, row=0)
        self.enemy_frame['padding'] = (20,10)
        # self.enemy_frame['borderwidth'] = 2
        self.enemy_frame['relief'] = 'sunken'

        self.enemy_label = ttk.Label(self.enemy_frame, text="Target")
        self.enemy_label.grid(column=0, row=0, columnspan=2, rowspan=1)

        self.enemychar = StringVar()
        self.enemychar.set('none')

        self.enemy_menu = ttk.Combobox(self.enemy_frame)
        self.enemy_menu.grid(column=0, row=1, columnspan=2, rowspan=1)
        self.enemy_menu['values'] = self.chars
        self.enemy_menu.bind('<<ComboboxSelected>>', self.on_enemy_menu_input)

        self.enemydmg = StringVar()
        self.enemydmg.set('')
        self.enemydmg.trace('w', self.on_enemy_damage_input)

        self.enemy_percentbox = ttk.Label(self.enemy_frame, text="%:")
        self.enemy_percentbox.grid(column=0, row=2, columnspan=1, rowspan=1, sticky="W")
        validate_cmd = (self.register(self.on_percent_validate), '%d', '%S', '%P')
        self.enemy_damage_entry = ttk.Entry(self.enemy_frame, textvariable=self.enemydmg,
                                            validate="key", validatecommand=validate_cmd)
        self.enemy_damage_entry.grid(column=1, row=2, columnspan=1, rowspan=1, sticky="W")
        self.weight_box = ttk.Label(self.enemy_frame, text="Weight:")
        self.weight_box.grid(column=0, row=3, columnspan=2, sticky="W")
        self.is_crouch = DoubleVar()
        self.is_smash = DoubleVar()
        self.is_meteor = DoubleVar()
        self.is_crouch.set(1)
        self.is_smash.set(1)
        self.is_meteor.set(1)
        self.crouch_check = ttk.Checkbutton(self.enemy_frame, variable=self.is_crouch,
                                            text="Crouching", command=self.on_crouch_check,
                                            offvalue=1, onvalue=0.85)
        self.smash_check = ttk.Checkbutton(self.enemy_frame, variable=self.is_smash,
                                           text="Charging smash", command=self.on_smash_check,
                                           offvalue=1, onvalue=1.2)
        self.meteor_check = ttk.Checkbutton(self.enemy_frame, variable=self.is_meteor,
                                            text="Grounded meteor", command=self.on_meteor_check,
                                            offvalue=1, onvalue=0.8)
        self.crouch_check.grid(column=2, row=1, sticky="W")
        self.smash_check.grid(column=2, row=2, sticky="W")
        self.meteor_check.grid(column=2, row=3, sticky="W")

    def init_move(self):
        self.move_frame = ttk.Frame(self.content, borderwidth=2)
        self.move_frame['padding'] = (20, 10)
        # self.move_frame['borderwidth'] = 2
        self.move_frame['relief'] = 'sunken'
        self.move_frame.grid(column=0, row=1, columnspan=2, sticky="WE")
        self.move_label = ttk.Label(self.move_frame, text="Attacking move:")
        self.move_label.grid(column=0, row=0, sticky="W")
        self.move_menu = ttk.Combobox(self.move_frame)
        self.move_menu.grid(column=0, row=1, columnspan=1, rowspan=1, sticky="NSEW")
        self.move_menu['width'] = 40
        # self.moves = []
        # self.move_menu['values'] = self.moves
        self.move_menu.bind('<<ComboboxSelected>>', self.on_move_menu_input)
        self.move_info_frame = MoveFrame(self.move_frame)

    def get_chars(self):
        print("getting all char data")
        response = urllib.request.urlopen(self.chars_url).read().decode('utf-8')
        chars_data = json.loads(response)
        self.chars = []
        self.name_to_id = {}
        for char in chars_data:
            self.chars.append(char['name'])
            self.name_to_id[char['name']] = char['id']

    def set_title(self, title=""):
        if (title != ""):
            self.parent.title("SmashCalc - {}".format(title))
        else:
            self.parent.title("SmashCalc")

    def on_user_menu_input(self, val):
        self.userchar = self.user_menu.get()
        print("user entry! {}".format(self.userchar))
        moves_url = "{}/characters/{}/moves".format(
                    api_url, self.name_to_id[self.userchar])
        response = urllib.request.urlopen(moves_url).read().decode('utf-8')
        self.moves_data = json.loads(response)
        self.moves = []
        self.move_to_id = {}
        self.moves_dict = {}
        for move in self.moves_data:
            print(type(move))
            print(move)
            # print(type(self.move_to_id))
            # print(self.move_to_id)
            # print("{}, {}".format(move['name'], move['id']))
            self.moves.append(move['name'])
            # self.move_to_id[move['name']] = move['id']
            self.moves_dict[move['name']] = move
        self.set_title(self.userchar)
        self.move_info_frame.clear_fields()
        # print(self.moves)
        # print(self.move_to_id)
        # print(self.moves_data)
        self.move_menu['values'] = self.moves
        # self.movebox =
        # self.move_data = {}
        self.update_move_fields(clear=True)

    def on_enemy_menu_input(self, val):
        self.enemychar = self.enemy_menu.get()
        print("enemy entry! {}".format(self.enemychar))
        data_url = "{}/characters/{}/characterattributes".format(
                   api_url, self.name_to_id[self.enemychar])
        response = urllib.request.urlopen(data_url).read().decode('utf-8')
        attr_data = json.loads(response)
        # print(attr_data)
        for item in attr_data:
            print(item)
            print(item['name'])
            if (item['name'] == 'WEIGHT VALUE'):
                self.enemy_weight = float(item['value'])
                print("weight of {} is {}".format(self.enemychar, self.enemy_weight))
        self.weight_box['text'] = "Weight: {}".format(int(self.enemy_weight))
        self.update_kb()

    def on_move_menu_input(self, val):
        # data_url = "{}/characters/{}/characterattributes".format(
        #            api_url, self.name_to_id[self.enemychar])
        # response = urllib.request.urlopen(data_url).read().decode('utf-8')
        # self.move_data = json.loads(response)
        # print(self.name_to_id)
        # print(self.moves_data[0])
        self.move_name = self.move_menu.get()
        print(self.moves_dict[self.move_menu.get()])
        self.update_move_fields()
        # self.BKB
        # self.name
        # self.
        self.update_kb()

    def on_user_damage_input(self, *args):
        print("user percent changed!")
        # self.percent = self.userdmg.get()
        # print(self.percent)
        print(self.userdmg.get())
        if (self.userdmg.get() == ''):
            return
        dmg = float(self.userdmg.get())
        if (dmg < 35):
            self.rage = 1
        elif (dmg > 150):
            self.rage = 1.15
        else:
            self.rage = 1 + (dmg - 35) * (.15) / (115)
        print("rage is now {}".format(self.rage))
        self.rage_box['text'] = "Rage multiplier: {: <4.2f}x".format(self.rage)
        self.update_kb()

    def on_enemy_damage_input(self, *args):
        print("enemy percent changed!")
        if (self.enemydmg.get() != ''):
            self.update_kb()

    # validate_cmd = (self.register(self.on_percent_validate), '%d', '%S', '%P')
    def on_percent_validate(self, why, change, new_value):
        print("validation")
        if (why == '1'):
            print("reason: insertion")
        elif (why == '0'):
            print("reason: deletion")
        else:
            print("UKNOWN REASON: {}".format(why))

        if (new_value == ''):
            print("empty box")
            return True
        try:
            float(new_value)
            # self.percent = float(new_value)
        except ValueError:
            return False
        # print(self.percent)
        # if (self.percent < 35):
        #     self.rage = 1
        # elif (self.percent > 150):
        #     self.rage = 1.15
        # else:
        #     self.rage = 1 + (self.percent - 35) * (.15) / (115)
        # print("rage is now {}".format(self.rage))
        # self.rage_box['text'] = "Rage multiplier: {: <4.2f}x".format(self.rage)

        # self.update_kb()

        return True

    def on_crouch_check(self):
        print("crouch: {}".format(self.is_crouch))
        self.update_kb()
    def on_smash_check(self):
        print("smash: {}".format(self.is_smash))
        self.update_kb()
    def on_meteor_check(self):
        print("meteor: {}".format(self.is_meteor))
        self.update_kb()

    def update_move_fields(self, clear=False):
        if (clear):
            self.move_name = ""
            self.kb = 0
            return
        else:
            print(self.moves_dict)
            print("move name: {}".format(self.move_name))
            print(self.moves_dict[self.move_name])
            self.move_info_frame.set_fields(self.moves_dict[self.move_name])
            self.update_kb()

    # set_kb(self, target_weight, target_percent, staleness=1, misc_variable=1):
    def update_kb(self):
        print("update_kb?")
        if (self.move_name != "" and self.move_info_frame.empty == False and self.enemy_weight > 0):
            print("updating")
            misc_var = float(self.rage) * self.is_crouch.get() * self.is_smash.get() * self.is_meteor.get()
            # Using onvalue and offvalue so don't need these.
            # if (self.is_crouch):
            #     misc_var = misc_var * 0.85
            # if (self.is_smash):
            #     misc_var = misc_var * 1.2
            # if (self.is_meteor):
            #     misc_var = misc_var * 0.8

            # self.move_info_frame.set_kb(self.enemy_weight, self.enemy_damage_entry.get(), staleness=1, misc_variable=misc_var)
            self.move_info_frame.set_kb(self.enemy_weight, float(self.enemydmg.get()), staleness=1, misc_variable=misc_var)
        else:
            print("nevermind")
            pass


"""
Entirely sets up for everything else.
"""
def SmashCalcLoop():
    print("main started")
    root = Tk()
    calc = SmashCalc(root)
    root.geometry("600x500+300+300")
    print("starting loop")
    calc.mainloop()
    print("exit")

if __name__ == '__main__':
    SmashCalcLoop()
