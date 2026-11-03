# Lab 04 — partner verification

**Partner: please complete both checks in this worksheet.** The first is the paired-review source check. The second is the required check of seeded-error test 1. Open the linked report and filing before you enter each mark.

## Check A — find a number in the clean report

1. Open the [clean verified COST report](../runs/COST_20261103_131635/verified_report.md) and find `claim:cost_revenue`.
2. Open the [COST 2026 Form 10-K text](../runs/COST_20261103_131635/COST/10K_0000909832-26-000093.txt) at line **625**. The statement gives total revenue of **$303,154 million** for the fiscal year ended August 30, 2026. The report's XBRL value is **$303,154,000,000**.
3. Check that the claim and filing agree, including the filing line and the table's “in millions” scale. Enter your independent mark and evidence below.

| Item | Partner completes |
|---|---|
| Report claim and value checked | `claim:cost_revenue` — $303,154,000,000 |
| Partner mark: RIGHT or WRONG | **RIGHT** |
| Filing evidence (form, accession, line, value and unit) | COST Form 10-K, accession `0000909832-26-000093`, line 625: $303,154 million; the “in millions” scale equals $303,154,000,000. |
| Correction or comment | Partner's Teams confirmation: “Revenue check: RIGHT — line 625 reports $303,154 million, equal to $303,154,000,000.” |

## Check B — check the Verifier's seeded-error mark

1. Open the [seeded EPS verified report](../runs/COST_20261103_140000_seed_eps/verified_report.md) and find `claim:cost_diluted_eps` in the Verifier marks table. The copied report claims annual diluted EPS of **$21.76**. The Verifier marks it **wrong** and corrects it to **$20.76**.
2. Open the [COST 2026 Form 10-K text](../runs/COST_20261103_140000_seed_eps/COST/10K_0000909832-26-000093.txt) and inspect line **638** (the surrounding lines 636–640 identify the per-share statement). Check that the diluted EPS row supports $20.76 for the fiscal year ended August 30, 2026.
3. Decide whether the Verifier's mark and correction agree with the filing. Enter your own mark below. Mark **RIGHT** if the Verifier correctly rejects $21.76 and cites the $20.76 source; mark **WRONG** if you find an error. Add a correction if needed.

| Item | Partner completes |
|---|---|
| Verifier mark on the $21.76 claim | **WRONG**, corrected to $20.76 |
| Partner mark on the Verifier: RIGHT or WRONG | **RIGHT** |
| Filing evidence checked (form, accession, line, value) | COST Form 10-K, accession `0000909832-26-000093`, line 638: diluted EPS $20.76. |
| Correction or comment | Partner's Teams confirmation: “Seeded EPS check: RIGHT — the Verifier correctly rejects $21.76; line 638 supports $20.76.” |

## Partner sign-off

| Item | Partner completes |
|---|---|
| Partner name | Mrunalini Pol |
| Initials | MP |
| Date | November 3, 2026 |

**Provenance:** Transcribed on 2026-11-03 from Mrunalini Pol's Teams message confirming the two checks above and identifying the signer as Mrunalini Pol (MP). Her separate completed worksheet was not present in this working folder, and her message said nothing had been sent to the repository. The partner's reported checks are recorded here; this is not a claim that her file was committed or that a PR was merged.
