

# Author: SilentNightSound
# GIMI reverse script, V1.0
# DO NOT PUBLICLY DISTRIBUTE WITHOUT PERMISSION
#
# Usage:
# Put this in a mod folder and run. The resulting output will be in a folder called reversed
# Import mods into blender using the import raw buffer ib+vb option in the GIMI plugin

import os
import shutil

def main():

    print("\nGIMI reverse script, characters only\n\n*******************************************\n")
    print("\nONLY USE THIS FOR MAKING PERSONAL MODS. DO NOT USE ASSETS FROM OTHER MODDERS WITHOUT ASKING PERMISSION\n")
    print("\n*******************************************\n")
    print("Press ENTER if you agree, otherwise please close the window:")
    input()

    position_file = search_file("Position.buf")
    texcoord_file = search_file("Texcoord.buf")
    blend_file    = search_file("Blend.buf")
    if not position_file or not texcoord_file or not blend_file:
        print("ERROR: Unable to find required file. Exiting")
        return

    print("Reading information from ini")
    ini_file = [x for x in os.listdir(".") if ".ini" in x]
    if len(ini_file) == 0:
        print(f"ERROR: unable to find .ini file. Ensure you are running this in the same folder as Char.ini. Exiting")
        return
    if len(ini_file) > 1:
        print(f"ERROR: more than one .ini file identified {ini_file}. Please remove files until only one remains, then run script again. Exiting")
    ini_file = ini_file[0]

    with open(ini_file, "r") as f:
        ini_data = f.read()
        texcoord_stride = int(ini_data.split(texcoord_file)[0].split("\n")[-2].split("=")[1].strip())
        ib_format = "DXGI_FORMAT_R16_UINT"
        if "DXGI_FORMAT_R32_UINT" in ini_data:
            ib_format = "DXGI_FORMAT_R32_UINT"
    print(f"Texcoord stride: {texcoord_stride}")

    with open(position_file, "rb") as f, open(texcoord_file, "rb") as g, open(blend_file, "rb") as h:
        position_data = f.read()
        texcoord_data = g.read()
        blend_data = h.read()

    i = 0
    h = 0
    j = 0
    vb = bytearray()
    while i < len(position_data):
        vb += position_data[i:i + 40]
        vb += blend_data[h:h + 32]
        vb += texcoord_data[j:j + texcoord_stride]
        i += 40
        h += 32
        j += texcoord_stride

    charname = position_file.split("Position")[0]
    parts = [x for x in os.listdir(".") if "Head.ib" in x or "Body.ib" in x or "Dress.ib" in x or "Extra.ib" in x]

    print("Constructing format files")
    format_file = f"stride: {40+32+texcoord_stride}\ntopology: trianglelist\nformat: {ib_format}\n\
element[0]:\n  SemanticName: POSITION\n  SemanticIndex: 0\n  Format: R32G32B32_FLOAT\n  InputSlot: 0\n  AlignedByteOffset: 0\n  InputSlotClass: per-vertex\n  InstanceDataStepRate: 0\n\
element[1]:\n  SemanticName: NORMAL\n  SemanticIndex: 0\n  Format: R32G32B32_FLOAT\n  InputSlot: 0\n  AlignedByteOffset: 12\n  InputSlotClass: per-vertex\n  InstanceDataStepRate: 0\n\
element[2]:\n  SemanticName: TANGENT\n  SemanticIndex: 0\n  Format: R32G32B32A32_FLOAT\n  InputSlot: 0\n  AlignedByteOffset: 24\n  InputSlotClass: per-vertex\n  InstanceDataStepRate: 0\n\
element[3]:\n  SemanticName: BLENDWEIGHT\n  SemanticIndex: 0\n  Format: R32G32B32A32_FLOAT\n  InputSlot: 0\n  AlignedByteOffset: 40\n  InputSlotClass: per-vertex\n  InstanceDataStepRate: 0\n\
element[4]:\n  SemanticName: BLENDINDICES\n  SemanticIndex: 0\n  Format: R32G32B32A32_SINT\n  InputSlot: 0\n  AlignedByteOffset: 56\n  InputSlotClass: per-vertex\n  InstanceDataStepRate: 0\n\
element[5]:\n  SemanticName: COLOR\n  SemanticIndex: 0\n  Format: R8G8B8A8_UNORM\n  InputSlot: 0\n  AlignedByteOffset: 72\n  InputSlotClass: per-vertex\n  InstanceDataStepRate: 0\n\
element[6]:\n  SemanticName: TEXCOORD\n  SemanticIndex: 0\n  Format: R32G32_FLOAT\n  InputSlot: 0\n  AlignedByteOffset: 76\n  InputSlotClass: per-vertex\n  InstanceDataStepRate: 0\n"
    if texcoord_stride == 20:
        format_file += "element[7]:\n  SemanticName: TEXCOORD\n  SemanticIndex: 1\n  Format: R32G32_FLOAT\n  InputSlot: 0\n  AlignedByteOffset: 84\n  InputSlotClass: per-vertex\n  InstanceDataStepRate: 0\n"

    if not os.path.isdir("reversed"):
        os.mkdir("reversed")

    for part in parts:
        body_part = os.path.splitext(part)[0].split(charname)[1]
        with open(os.path.join("reversed", f"{charname}{body_part}.vb"), "wb") as f, open(os.path.join("reversed", f"{charname}{body_part}.fmt"), "w") as g:
            f.write(vb)
            g.write(format_file)
            shutil.copyfile(part, os.path.join("reversed", part))

    print("All results saved to reversed, exiting")

def search_file(name):
    print(f"Searching for {name} file")
    file_data = [x for x in os.listdir(".") if name in x]
    if len(file_data) != 1:
        print(f"ERROR: Unable to find {name}. Ensure it is in the folder, and only one {name} exists")
        return ""
    file_data = file_data[0]
    print(f"Found: {name}")
    return file_data

if __name__ == "__main__":
    main()
