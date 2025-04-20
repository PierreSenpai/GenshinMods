# Author: SilentNightSound#7430
# Special Thanks:
#   Takoyaki#0697 (for demonstrating principle and creating the first proof of concept)
#   HazrateGolabi#1364 (for implementing the code to limit toggles to the on-screen character)

#   HummyR#8131, Modder4869#4818 (3.0+ Character Shader Fix)
# V3.0 of Mod Merger/Toggle Creator Script

# Merges multiple mods into one, which can be toggled in-game by pressing a key

# USAGE: Run this script in a folder which contains all the mods you want to merge
# So if you want to merge mods CharA, CharB, and CharC put all 3 folders in the same folder as this script and run it

# This script will automatically search through all subfolders to find mod ini files.
# It will not use .ini if that ini path/name contains "disabled"

# NOTE: This script will only function on mods generated using the 3dmigoto GIMI plugin

import os
import re
import argparse
import hashlib

def main():
    parser = argparse.ArgumentParser(description="Generates a merged mod from several mod folders")
    parser.add_argument("-r", "--root", type=str,  default=".",  help="Location to use to create mod")
    parser.add_argument("-s", "--store", action="store_true", help="Use to keep the original .ini files enabled after completion")
    parser.add_argument("-e", "--enable", action="store_true", help="Re-enable disabled .ini files")
    parser.add_argument("-n", "--name", type=str,  default="merged.ini", help="Name of final .ini file")
    parser.add_argument("-k", "--key", type=str, default="", help="Key to press to switch mods")
    parser.add_argument("-c", "--compress",  action="store_true", help="Makes the output mods as small as possible (warning: difficult to reverse, have backups)")
    parser.add_argument("-a", "--active", action="store_true",  default=True, help="Only active character gets swapped when swapping)")
    parser.add_argument("-ref", "--reflection", action="store_true", help="Applies reflection fix for 3.0+ characters")

    args = parser.parse_args()
    swap_unidentified = []
    swap_mondstadt = []
    swap_liyue = []
    swap_dragonspine = []
    swap_inazuma = []
    swap_enkanomiya = []
    swap_chasm = []
    swap_sumeru_forest = []
    swap_sumeru_desert = []
    swap_fontaine = []
    swap_teapot = []
    swap_chenyu = []
    swap_natlan = []
    print("\nGenshin Mod Merger/Toggle Creator Script\n")

    if args.active:
        print("Setting to swap only the active(on-screen) character")

    if args.enable:
        print("Re-enabling all .ini files")
        enable_ini(args.root)
        print()

    if not args.store:
        print("\nWARNING: Once this script completes, it will disable all .ini files used to generate the merged mod (which is required in order for the final version to work without conflicts)")
        print("You can prevent this behaviour by using the -s flag")
        print("This script also has the ability to re-enable all mods in the current folder and all subfolders by using the -e flag - use this flag if you need to regenerate the merged ini again")

    if args.compress:
        print("\nWARNING2: The -c/--compress option makes the output smaller, but it will be difficult to retrieve the original mods from the merged one. MAKE SURE TO HAVE BACKUPS, and consider only using option after you are sure everything is good")

    print("\nSearching for .ini files")
    ini_files = collect_ini(args.root, args.name)

    if not ini_files:
        print("Found no .ini files - make sure the mod folders are in the same folder as this script.")
        print("If using this script on a group of files that are already part of a toggle mod, use -e to enable .ini and regenerate the merge ini")
        return

    print("\nFound:")
    for i, ini_file in enumerate(ini_files):
        print(f"\t{i}:  {ini_file}")

    print("\nThis script will merge using the order listed above (0 is the default the mod will start with, and it will cycle 0,1,2,3,4,0,1...etc)")
    print("If this is fine, please press ENTER. If not, please enter the order you want the script to merge the mods (example: 3 0 1 2)")
    print("If you enter less than the total number, this script will only merge those listed.\n")
    #ini_files = get_user_order(ini_files)
    for i, ini_file in enumerate(ini_files):
        if re.search(r'\b' + 'MON' + r'\b', ini_file):
            swap_mondstadt.append(i)
        if re.search(r'\b' + 'LIY' + r'\b', ini_file):
            swap_liyue.append(i)
        if re.search(r'\b' + 'DRA' + r'\b', ini_file):
            swap_dragonspine.append(i)
        if re.search(r'\b' + 'INA' + r'\b', ini_file):
            swap_inazuma.append(i)
        if re.search(r'\b' + 'ENK' + r'\b', ini_file):
            swap_enkanomiya.append(i)
        if re.search(r'\b' + 'CHA' + r'\b', ini_file):
            swap_chasm.append(i)
        if re.search(r'\b' + 'SUF' + r'\b', ini_file):
            swap_sumeru_forest.append(i)
        if re.search(r'\b' + 'SUD' + r'\b', ini_file):
            swap_sumeru_desert.append(i)
        if re.search(r'\b' + 'FON' + r'\b', ini_file):
            swap_fontaine.append(i)
        if re.search(r'\b' + 'TEA' + r'\b', ini_file):
            swap_teapot.append(i)
        if re.search(r'\b' + 'UNI' + r'\b', ini_file):
            swap_unidentified.append(i)
        if re.search(r'\b' + 'CHE' + r'\b', ini_file):
            swap_chenyu.append(i)
        if re.search(r'\b' + 'NAT' + r'\b', ini_file):
            swap_natlan.append(i)
    if args.key:
        key = args.key
    else:
        print("\nPlease enter the key that will be used to cycle mods (can also enter this with -k flag, or set later in .ini). Key must be a single letter\n")
        key = input()
        while not key or len(key) != 1:
            print("\nKey not recognized, must be a single letter\n")
            key = input()
        key = key.lower()

    constants =    "; Constants ---------------------------\n\n"
    overrides =    "; Overrides ---------------------------\n\n"
    shader    =    "; Shader ------------------------------\n\n"
    commands  =    "; CommandList -------------------------\n\n"
    resources =    "; Resources ---------------------------\n\n"

    swapvar = "swapvar"
    constants += f"[Constants]\nglobal persist ${swapvar} = 0\n"
    constants +="""global persist $swap_unidentified = -1
global persist $swap_mondstadt = -1
global persist $swap_liyue = -1
global persist $swap_dragonspine = -1
global persist $swap_inazuma = -1
global persist $swap_enkanomiya = -1
global persist $swap_chasm = -1
global persist $swap_sumeru_forest = -1
global persist $swap_sumeru_desert = -1
global persist $swap_fontaine = -1
global persist $swap_teapot = -1
global persist $swapvar_not_assigned = -1
global persist $swap_chenyu = -1
global persist $swap_natlan = -1
global persist $isfirstload = 1
global $not_assigned = 0
global persist $regioncheck 
"""
    if args.active:
        constants += f"global $active\n"
    if args.reflection:
        constants += f"global $reflection\n"
    constants += "global $creditinfo = 0\n"
    constants += f"\n[KeySwapMondstadt]\n"
    constants += f"condition = ($active == 1 && $regioncheck == 1)||$isfirstload == 1\n"
    constants += f"key = {key}\ntype = cycle\n"
    constants += f"$swap_mondstadt = "
    constants += ','.join(str(x) for x in swap_mondstadt)
    constants += f"\n"
    constants += f"$creditinfo = 0\n"
    constants += f"\n[KeySwapLiyue]\n"
    constants += f"condition = ($active == 1 && $regioncheck == 2)||$isfirstload == 1\n"
    constants += f"key = {key}\ntype = cycle\n"
    constants += f"$swap_liyue = "
    constants += ','.join(str(x) for x in swap_liyue)
    constants += f"\n"
    constants += f"$creditinfo = 0\n"
    constants += f"\n[KeySwapDragonspine]\n"
    constants += f"condition = ($active == 1 && $regioncheck == 3)||$isfirstload == 1\n"
    constants += f"key = {key}\ntype = cycle\n"
    constants += f"$swap_dragonspine = "
    constants += ','.join(str(x) for x in swap_dragonspine)
    constants += f"\n"
    constants += f"$creditinfo = 0\n"
    constants += f"\n[KeySwapInazuma]\n"
    constants += f"condition = ($active == 1 && $regioncheck == 4)||$isfirstload == 1\n"
    constants += f"key = {key}\ntype = cycle\n"
    constants += f"$swap_inazuma = "
    constants += ','.join(str(x) for x in swap_inazuma)
    constants += f"\n"
    constants += f"$creditinfo = 0\n"
    constants += f"\n[KeySwapEnkanomiya]\n"
    constants += f"condition = ($active == 1 && $regioncheck == 5)||$isfirstload == 1\n"
    constants += f"key = {key}\ntype = cycle\n"
    constants += f"$swap_enkanomiya = "
    constants += ','.join(str(x) for x in swap_enkanomiya)
    constants += f"\n"
    constants += f"$creditinfo = 0\n"
    constants += f"\n[KeySwapChasm]\n"
    constants += f"condition = ($active == 1 && $regioncheck == 6)||$isfirstload == 1\n"
    constants += f"key = {key}\ntype = cycle\n"
    constants += f"$swap_chasm = "
    constants += ','.join(str(x) for x in swap_chasm)
    constants += f"\n"
    constants += f"$creditinfo = 0\n"
    constants += f"\n[KeySwapSumeruForest]\n"
    constants += f"condition = ($active == 1 && $regioncheck == 7)||$isfirstload == 1\n"
    constants += f"key = {key}\ntype = cycle\n"
    constants += f"$swap_sumeru_forest = "
    constants += ','.join(str(x) for x in swap_sumeru_forest)
    constants += f"\n"
    constants += f"$creditinfo = 0\n"
    constants += f"\n[KeySwapSumeruDesert]\n"
    constants += f"condition = ($active == 1 && $regioncheck == 8)||$isfirstload == 1\n"
    constants += f"key = {key}\ntype = cycle\n"
    constants += f"$swap_sumeru_desert = "
    constants += ','.join(str(x) for x in swap_sumeru_desert)
    constants += f"\n"
    constants += f"$creditinfo = 0\n"
    constants += f"\n[KeySwapFontaine]\n"
    constants += f"condition = ($active == 1 && $regioncheck == 9)||$isfirstload == 1\n"
    constants += f"key = {key}\ntype = cycle\n"
    constants += f"$swap_fontaine = "
    constants += ','.join(str(x) for x in swap_fontaine)
    constants += f"\n"
    constants += f"$creditinfo = 0\n"
    constants += f"\n[KeySwapTeapot]\n"
    constants += f"condition = ($active == 1 && $regioncheck == 10)||$isfirstload == 1\n"
    constants += f"key = {key}\ntype = cycle\n"
    constants += f"$swap_teapot = "
    constants += ','.join(str(x) for x in swap_teapot)
    constants += f"\n"
    constants += f"$creditinfo = 0\n"
    constants += f"\n[KeySwapUnidentified]\n"
    constants += f"condition = ($active == 1 && $regioncheck == 0)||$isfirstload == 1\n"
    constants += f"key = {key}\ntype = cycle\n"
    constants += f"$swap_unidentified = "
    constants += ','.join(str(x) for x in swap_unidentified)
    constants += f"\n"
    constants += f"$creditinfo = 0\n"
    constants += f"\n[KeySwapNotAssgigned]\n"
    constants += f"condition = ($active == 1 && $not_assigned == 1)||$isfirstload == 1\n"
    constants += f"key = {key}\ntype = cycle\n"
    constants += f"$swapvar_not_assigned = "
    constants += ','.join([str(x) for x in range(len(ini_files))])
    constants += f"\n"
    constants += f"$isfirstload = 0\n"
    constants += f"$creditinfo = 0\n"
    constants += f"\n[KeySwapChenyu]\n"
    constants += f"condition = ($active == 1 && $regioncheck == 11)||$isfirstload == 1\n"
    constants += f"key = {key}\ntype = cycle\n"
    constants += f"$swap_chenyu = "
    constants += ','.join(str(x) for x in swap_chenyu)
    constants += f"\n"
    constants += f"$isfirstload = 0\n"
    constants += f"$creditinfo = 0\n"
    constants += f"\n[KeySwapNatlan]\n"
    constants += f"condition = ($active == 1 && $regioncheck == 12)||$isfirstload == 1\n"
    constants += f"key = {key}\ntype = cycle\n"
    constants += f"$swap_natlan = "
    constants += ','.join(str(x) for x in swap_natlan)
    constants += f"\n\n"
    if args.active or args.reflection:
        constants += f"[Present]\n"
    if args.active:
        constants += f"post $active = 0\n"
    if args.reflection:
        constants += f"post $reflection = 0\n"
    constants +=f"post $not_assigned = 0\n"
    constants +=r'$regioncheck = $\global\region\regioncheck'
    constants +=f"\nrun = CommandListCheckAssigned\n"
    constants +=f"run = CommandListSetOutfit\n"



    print("Parsing ini sections")
    all_mod_data = []
    ini_group = 0
    for ini_file in ini_files:
        with open(ini_file, "r", encoding="utf-8") as f:
            ini_text = ["["+x.strip() for x in f.read().split("[")]
            for section in ini_text[1:]:
                mod_data = parse_section(section)
                mod_data["location"] = os.path.dirname(ini_file)
                mod_data["ini_group"] = ini_group
                all_mod_data.append(mod_data)
        ini_group += 1

    if [x for x in all_mod_data if "name" in x and x["name"].lower() == "creditinfo"]:
        constants += "run = CommandListCreditInfo\n\n"
    else:
        constants += "\n"

    if [x for x in all_mod_data if "name" in x and x["name"].lower() == "transparency"]:
        shader += """[CustomShaderTransparency]
blend = ADD BLEND_FACTOR INV_BLEND_FACTOR
blend_factor[0] = 0.5
blend_factor[1] = 0.5
blend_factor[2] = 0.5
blend_factor[3] = 1
handling = skip
drawindexed = auto

"""

    print("Calculating overrides and resources")
    command_data = {}
    seen_hashes = {}
    reflection = {}
    n = 1
    for i in range(len(all_mod_data)):
        # Overrides. Since we need these to generate the command lists later, need to store the data
        if "hash" in all_mod_data[i]:
            index = -1
            if "match_first_index" in all_mod_data[i]:
                index = all_mod_data[i]["match_first_index"]
            # First time we have seen this hash, need to add it to overrides
            if (all_mod_data[i]["hash"], index) not in command_data:
                command_data[(all_mod_data[i]["hash"], index)] = [all_mod_data[i]]
                overrides += f"[{all_mod_data[i]['header']}{all_mod_data[i]['name']}]\nhash = {all_mod_data[i]['hash']}\n"
                if index != -1:
                    overrides += f"match_first_index = {index}\n"
                # These are custom commands GIMI implements, they do not need a corresponding command list
                if "VertexLimitRaise" not in all_mod_data[i]["name"]:
                    overrides += f"run = CommandList{all_mod_data[i]['name']}\n"
                if index != -1 and args.reflection:
                    overrides += f"ResourceRef{all_mod_data[i]['name']}Diffuse = reference ps-t1\nResourceRef{all_mod_data[i]['name']}LightMap = reference ps-t2\n$reflection = {n}\n"
                    reflection[all_mod_data[i]['name']] = f"ResourceRef{all_mod_data[i]['name']}Diffuse,ResourceRef{all_mod_data[i]['name']}LightMap,{n}"
                    n+=1
                if args.active:
                    if "Position" in all_mod_data[i]["name"]:
                        overrides += f"$active = 1\n"

                overrides += "\n"
            # Otherwise, we have seen the hash before and we just need to append it to the commandlist
            else:
                command_data[(all_mod_data[i]["hash"], index)].append(all_mod_data[i])
        elif "header" in all_mod_data[i] and "CommandList" in all_mod_data[i]["header"]:
            command_data.setdefault((all_mod_data[i]["name"],0),[]).append(all_mod_data[i])
        # Resources
        elif "filename" in all_mod_data[i] or "type" in all_mod_data[i]:

            resources += f"[{all_mod_data[i]['header']}{all_mod_data[i]['name']}.{all_mod_data[i]['ini_group']}]\n"
            for command in all_mod_data[i]:
                if command in ["header", "name", "location", "ini_group"]:
                    continue
                if command == "filename":
                    with open(f"{all_mod_data[i]['location']}\\{all_mod_data[i][command]}", "rb") as f:
                        sha1 = hashlib.sha1(f.read()).hexdigest()
                    if sha1 in seen_hashes and args.compress:
                        resources += f"{command} = {seen_hashes[sha1]}\n"
                        os.remove(f"{all_mod_data[i]['location']}\\{all_mod_data[i][command]}")
                    else:
                        seen_hashes[sha1] = f"{all_mod_data[i]['location']}\\{all_mod_data[i][command]}"
                        resources += f"{command} = {all_mod_data[i]['location']}\\{all_mod_data[i][command]}\n"
                else:
                    resources += f"{command} = {all_mod_data[i][command]}\n"
            resources += "\n"

    if args.reflection:
        print("Character Shader Fix")
        refresources = ''
        CommandPart = ['ReflectionTexture', 'Outline']
        shadercode = """
[ShaderOverrideReflectionTexture]
hash=26eb354bad491b6f
allow_duplicate_hash=overrule
run=CommandListReflectionTexture

[ShaderOverrideReflectionTextureDress]
hash=b04806463c319e15
allow_duplicate_hash=overrule
run=CommandListReflectionTexture

[ShaderOverrideReflectionTextureBlink]
hash=167cf8a1f4f9ed4f
allow_duplicate_hash=overrule
run=CommandListReflectionTexture

; OPTIONAL: shader hash for outline. replace this incase regex does not work.
[ShaderOverrideOutlineTexture]
hash=f6eb050ef75da1b7
allow_duplicate_hash=overrule
run=CommandListOutline\\n
        """
        shader += f"{shadercode}\n"
        for i in range(len(CommandPart)):
            ref  = f"[CommandList{CommandPart[i]}]\n"
            ref += f"if $reflection != 0\n\tif "
            for x in reflection:
                r = reflection[x].split(",")
                ref += f"$reflection == {r[2]}\n"
                ps = [['ps-t0','ps-t1'],['ps-t1','ps-t2']]
                ref += f"\t\t{ps[i][0]} = copy {r[0]}\n\t\t{ps[i][1]} = copy {r[1]}\n"
                ref += f"\telse if "
                if i == 0:
                    refresources += f"[{r[0]}]\n[{r[1]}]\n"
            ref = ref.rsplit("else if",1)[0] + "endif\n"
            ref += f"drawindexed=auto\n"
            ref += f"$reflection = 0\n"
            ref += f"endif\n\n"
            commands += ref

    print("Constructing command lists")
    tabs = 1

    for hash, index in command_data:
        if "VertexLimitRaise" in command_data[(hash, index)][0]["name"]:
            continue
        commands += f"[CommandList{command_data[(hash, index)][0]['name']}]\nif "
        for model in command_data[(hash, index)]:
            commands += f"${swapvar} == {model['ini_group']}\n"
            for command in model:
                if command in ["header", "name", "hash", "match_first_index", "location", "ini_group"]:
                    continue

                if command == "endif":
                    tabs -= 1
                    for i in range(tabs):
                        commands += "\t"
                    commands += f"{command}"
                elif "else if" in command:
                    tabs -= 1
                    for i in range(tabs):
                        commands += "\t"
                    commands += f"{command} = {model[command]}"
                    tabs += 1
                else:
                    for i in range(tabs):
                        commands += "\t"
                    if command[:2] == "if" or command[:7] == "else if":
                        commands += f"{command} == {model[command]}"
                    else:
                        commands += f"{command} = {model[command]}"
                    if command[:2] == "if":
                        tabs += 1
                    elif (command[:2] in ["vb", "ib", "ps", "vs", "th"] or "Resource" in model[command]) and model[command].lower() != "null":
                        commands += f".{model['ini_group']}"
                commands += "\n"
            commands += "else if "
        commands = commands.rsplit("else if",1)[0] + "endif\n\n"
    commands +="""
[CommandListCheckAssigned]
if $regioncheck == 0 && $swap_unidentified == -1
	$not_assigned = 1
else if $regioncheck == 1 && $swap_mondstadt == -1
	$not_assigned = 1
else if $regioncheck == 2 && $swap_liyue == -1
	$not_assigned = 1
else if $regioncheck == 3 && $swap_dragonspine == -1
	$not_assigned = 1
else if $regioncheck == 4 && $swap_inazuma == -1
	$not_assigned = 1
else if $regioncheck == 5 && $swap_enkanomiya == -1
	$not_assigned = 1
else if $regioncheck == 6 && $swap_chasm == -1
	$not_assigned = 1
else if $regioncheck == 7 && $swap_sumeru_forest == -1
	$not_assigned = 1
else if $regioncheck == 8 && $swap_sumeru_desert == -1
	$not_assigned = 1
else if $regioncheck == 9 && $swap_fontaine == -1
	$not_assigned = 1
else if $regioncheck == 10 && $swap_teapot == -1
	$not_assigned = 1
else if $regioncheck == 11 && $swap_chenyu == -1
	$not_assigned = 1
else if $regioncheck == 12 && $swap_natlan == -1
	$not_assigned = 1
endif

[CommandListSetOutfit]
if $regioncheck == 0 && $swap_unidentified != -1
	$swapvar = $swap_unidentified
else if $regioncheck == 1 && $swap_mondstadt != -1
	$swapvar = $swap_mondstadt
else if $regioncheck == 2 && $swap_liyue != -1
	$swapvar = $swap_liyue
else if $regioncheck == 3 && $swap_dragonspine != -1
	$swapvar = $swap_dragonspine		
else if $regioncheck == 4 && $swap_inazuma != -1
	$swapvar = $swap_inazuma
else if $regioncheck == 5 && $swap_enkanomiya != -1
	$swapvar = $swap_enkanomiya
else if $regioncheck == 6 && $swap_chasm != -1
	$swapvar = $swap_chasm
else if $regioncheck == 7 && $swap_sumeru_forest != -1
	$swapvar = $swap_sumeru_forest
else if $regioncheck == 8 && $swap_sumeru_desert != -1
	$swapvar = $swap_sumeru_desert
else if $regioncheck == 9 && $swap_fontaine != -1
	$swapvar = $swap_fontaine
else if $regioncheck == 10 && $swap_teapot != -1
	$swapvar = $swap_teapot
else if $regioncheck == 11 && $swap_chenyu != -1
	$swapvar = $swap_chenyu
else if $regioncheck == 12 && $swap_natlan != -1
	$swapvar = $swap_natlan
else
	$swapvar = $swapvar_not_assigned
endif

"""
    commands += "\n"
    print("Printing results")
    result = f"; Merged Mod: {', '.join([x for x in ini_files])}\n\n"
    if args.reflection:
        result += f"{refresources}\n"
    result += constants
    result += shader
    result += overrides
    result += commands
    result += resources
    if args.reflection:
        result += "\n\n; For fixing green reflections and broken outlines colors on 3.0+ characters\n"
    else:
        result += "\n\n"
    result += "; .ini generated by GIMI (Genshin-Impact-Model-Importer) mod merger script\n"

    result += "; If you have any issues or find any bugs, please open a ticket at https://github.com/SilentNightSound/GI-Model-Importer/issues or contact SilentNightSound#7430 on discord"

    with open(args.name, "w", encoding="utf-8") as f:
        f.write(result)

    if not args.store:
        print("Cleanup and disabling ini")
        for file in ini_files:
            os.rename(file, os.path.join(os.path.dirname(file), "DISABLED") + os.path.basename(file))


    print("All operations completed")


# Collects all .ini files from current folder and subfolders
def collect_ini(path, ignore):
    ini_files = []
    for root, dir, files in os.walk(path):
        if "disabled" in root.lower():
            continue
        for file in files:
            if "disabled" in file.lower() or ignore.lower() in file.lower():
                continue
            if os.path.splitext(file)[1] == ".ini":
                ini_files.append(os.path.join(root, file))
    return ini_files

# Re-enables disabled ini files
def enable_ini(path):
    for root, dir, files in os.walk(path):
        for file in files:
            if os.path.splitext(file)[1] == ".ini" and ("disabled" in root.lower() or "disabled" in file.lower()):
                print(f"\tRe-enabling {os.path.join(root, file)}")
                new_path = re.compile("disabled", re.IGNORECASE).sub("", os.path.join(root, file))
                os.rename(os.path.join(root, file), new_path)


# Gets the user's preferred order to merge mod files
def get_user_order(ini_files):

    choice = input()

    # User entered data before pressing enter
    while choice:
        choice = choice.strip().split(" ")

        if len(choice) > len(ini_files):
            print("\nERROR: please only enter up to the number of the original mods\n")
            choice = input()
        else:
            try:
                result = []
                choice = [int(x) for x in choice]
                if len(set(choice)) != len(choice):
                    print("\nERROR: please enter each mod number at most once\n")
                    choice = input()
                elif max(choice) >= len(ini_files):
                    print("\nERROR: selected index is greater than the largest available\n")
                    choice = input()
                elif min(choice) < 0:
                    print("\nERROR: selected index is less than 0\n")
                    choice = input()
                    print()
                else:
                    for x in choice:
                        result.append(ini_files[x])
                    return result
            except ValueError:
                print("\nERROR: please only enter the index of the mods you want to merge separated by spaces (example: 3 0 1 2)\n")
                choice = input()

    # User didn't enter anything and just pressed enter
    return ini_files


# Parses a section from the .ini file
def parse_section(section):
    mod_data = {}
    recognized_header = ("[TextureOverride", "[ShaderOverride", "[Resource", "[Constants", "[Present", "[CommandList", "[CustomShader")
    for line in section.splitlines():
        if not line.strip() or line[0] == ";":  # comments and empty lines
            continue

        # Headers
        for header in recognized_header:
            if header in line:
                # I give up on trying to merge the reflection fix, it's way too much work. Just re-apply after merging
                if "CommandListReflectionTexture" in line or "CommandListOutline" in line:
                    return {}
                mod_data["header"] = header[1:]
                mod_data["name"] = line.split(header)[1][:-1]
                break
        # Conditionals
        if "==" in line:
            key, data = line.split("==",1)
            mod_data[key.strip()] = data.strip()
        elif "endif" in line:
            key, data = "endif", ""
            mod_data[key.strip()] = data.strip()
        # Properties
        elif "=" in line:
            key, data = line.split("=")
            # See note on reflection fix above
            if "CharacterIB" in key or "ResourceRef" in key:
                continue

            mod_data[key.strip()] = data.strip()

    return mod_data


if __name__ == "__main__":
    main()
