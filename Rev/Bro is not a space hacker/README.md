# Rev - Bro is not a space hacker

**Point: 52**

Congratulations earthling! You found the culprit that deleted those files...

By investigating the USB further, a team member found out that there is a program that would unlock the airlock of that spaceship.

Your mission is to reconstruct the access chain, verify the airlock authentication path and recover the hidden evidence that explains who triggered the wipe, why it was done and what was meant to stay buried.

## Soulution

Access chain reconstructed

1. crew_log.txt gives token prefix: ASTRA9- and says the second half is in secure cache.
2. Deleted cache file inode_18.bin contains: BRO-1337.
3. Full token: ASTRA9-BRO-1337.
4. Running airlockauth inside analysis/fat with that token returns signal verified (wrong token returns access denied).

Airlock auth path (reversed)

1. Read seed32.bin, nav.bc, payload.enc.
2. Compute h1 = SHA256(nav.bc).
3. Compute k = SHA256(seed32.bin || token || h1).
4. Decrypt payload.enc with repeating-key XOR using k.
5. Check decrypted data starts with UVT{.

Hidden evidence

1. inode_19.bin (mission debrief) is authored by Lt. Orin Voss and documents anomalous EM readings from cargo bay C-7, then cache purge instructions.
2. crew_log.txt records that diagnostics confirmed wipe request and marked /diagnostics and /tmp for deletion.
3. Inference: wipe was intentionally triggered by maintenance/diagnostics under Voss’s direction to bury C-7 telemetry evidence.
4. The buried secret is the decrypted payload above (the flag).

# Flag:

Flag: UVT{S0m3_s3cR3tZ_4r_nVr_m3Ant_t0_B_SHRD}
