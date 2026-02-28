# Sea of Fire

**Point: 289**

At the bottom of the sea, you find an ancient disc-like relic. A true UFO!

By sheer luck, you breach the entrance and go inside to explore. What could possibly go wrong?

Well, tripping over some circuit that lights up the interior, awakening dormant aliens. You run for your life, but get lost in a sprawling maze that, defying all known laws of physics, dwarfs the outer shell

Shaking violently, the now-activated UFO beams into outer space. Hurry up and turn this thing off before it collides with a dying star!

# Soulution

looking at the game files showed it was a Unity IL2CPP build.

Using cpp2il dumps, i read the code and discovered the check took place in \_odc70232313.ValidatePassword, which runs a custom VM.

Next i used UnityPy to read level1 and get the path of instructions, from beginning to end (which i found in RoomInstructionTrigger components in level1).

then i reversed the vm opcodes and lookup table.

after that i had chatgpt make me a python script that ran it in reverse and that checked that the input that was found met the final condition (top = 1).

# Flag

`UVT{Fly_m3_in70_a_5Up3rn0vA}`
