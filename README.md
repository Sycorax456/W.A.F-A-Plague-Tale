# W.A.F-A-Plague-Tale
This Python script rebuilds your dialogue WEM files so that the "A Plague Tale" games can read them correctly with working lipsync animations.

How to Use

. Step 1: Unpack the .7z file into any folder you like.

. Step 2: Open the Python script.

. Step 3: Inside the 7z archive, you will find three directories. Once the GUI script is launched, map each input field to the corresponding directory included in my repository.

. Step 4: Use [mrikso]’s tool to extract the .wem files from the .pck.
(https://github.com/MrIkso/mhws-sound-tool/releases/tag/fix)

. Step 5: Create your edited .wem files, using the exact same names as the original files you want to replace.

. Step 6: Place your edited files in the Mod folder.

. Step 7: Put the original (vanilla) files in the Original folder.

. Step 8: Run the script. The resulting .wem files will be saved in the Output folder.

WAF 1.7

Now if run with arguments (--mod, --original, --output), it runs in CLI mode (no GUI).

ex: python wem_fixer.py --mod ("mods/") --original ("originals/") --output ("patched/")

If no arguments are passed, it launches the GUI.
