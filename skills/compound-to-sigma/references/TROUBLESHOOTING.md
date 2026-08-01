# compound-to-sigma troubleshooting

Debug a failed run in this order:

1. **Name resolution** — Is the name unambiguous? Try CAS or SMILES instead.
2. **Database match** — Is `$SCM_PKG_ADFCRSDIR/ADFCRS-2018` set and readable? Did the SMILES metadata in the database coskf match?
3. **Environment** — Are `$AMSBIN`, `xtb`, and `obabel` in PATH? Was `amsbashrc.sh` sourced?
4. **Charge/multiplicity** — Did the user supply them explicitly?
5. **xtb** — Did xtb converge? Check `output_dir/<name>/xtb.*` files.
6. **ADF** — Is the license available? Check `output_dir/<name>/adf.rkf` and the AMS log.
7. **CRSJob** — Is the coskf valid? Try `method="COSMO-RS"` first before exotic variants.
