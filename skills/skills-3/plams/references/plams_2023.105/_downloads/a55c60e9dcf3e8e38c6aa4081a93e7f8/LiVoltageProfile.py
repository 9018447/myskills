# Make sure this script was called correctly
if not 'resultsdir' in globals():
    print("\n USAGE: $AMSBIN/plams LiVoltageProfile.py -v resultsdir=[path to .results folder]\n")
    quit()

# Load the job associated with that .results folder
gcmc = AMSJob.load_external(resultsdir)

# Get energy and number of atoms of the initial state (before adding any Li)
initEnergy = gcmc.results.readrkf('GCMC', 'InitialEnergy')
initNumAtoms = len(gcmc.results.get_input_molecule())

# Get chemical potential of Li
muLi = gcmc.results.readrkf('GCMC','Mol1.chemPot')
# Get Faraday's constant in atomic units
Ha2V = Units.convert(1, 'Hartree','kcal/mol')/23.06
# (Note: 23.06 is Faraday's constant in kcal per volt gram equivalent)

# Loop over entries in the History and make dictionaries for the voltages and volumes,
# using the number of Li atoms as the keys to the dictionaries.
# (Note: We start at history step 2, because the first one is the initial system without any Li.)
voltages = {}
volumes  = {}
for iHistEntry in range(2,gcmc.results.readrkf('History', 'nEntries')+1):

    # Get the geometry for the accepted MC step
    iSys = gcmc.results.get_history_molecule(iHistEntry)

    # Find out how many Li atoms it has
    numLiAtoms = sum(atom.symbol == 'Li' for atom in iSys.atoms)
    if numLiAtoms == 0: continue

    totalEnergy = gcmc.results.readrkf('History', 'Energy({:d})'.format(iHistEntry))
    voltage = - Ha2V * (totalEnergy - initEnergy - numLiAtoms*muLi) / numLiAtoms
    if not numLiAtoms in voltages: voltages[numLiAtoms] = []
    voltages[numLiAtoms].append(voltage)

    volume = iSys.unit_cell_volume()
    if not numLiAtoms in volumes: volumes[numLiAtoms] = []
    volumes[numLiAtoms].append(volume)

# Calulate and print averages for voltages and volumes.
print("# Nr. Li atoms, fraction of Li-atoms, Voltage in V, Volume in Angstrom**3")
for numLiAtoms in voltages:
    voltage = sum(voltages[numLiAtoms]) / len(voltages[numLiAtoms])
    volume  = sum(volumes[numLiAtoms])  / len(volumes[numLiAtoms])
    print("{:3d} {:2.3f} {:2.3f} {:2.2f}" \
          .format(numLiAtoms, numLiAtoms/initNumAtoms, voltage, volume))
