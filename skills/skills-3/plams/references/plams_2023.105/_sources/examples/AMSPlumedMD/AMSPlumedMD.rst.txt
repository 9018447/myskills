.. _AMSPlumedMD:

AMS biased MD / PLUMED
=======================

Example illustrating how to run AMS MD with

* AMS Restraints

* AMS EngineAddon WallPotential

* Plumed restraints

During this simulation, the reaction H₂CO₃(g) → H₂O(g) + CO₂(g) is enforced by
a PLUMED MovingRestraint between one of the hydrogen and oxygen atoms.

The WallPotential keeps the two product molecules near each other.

To follow along, either

* Download :download:`ams_plumed.py` (run as ``$AMSBIN/amspython ams_plumed.py``).
* Download :download:`ams_plumed.ipynb` (see also: how to install `Jupyterlab <../../../Scripting/Python_Stack/Python_Stack.html#install-and-run-jupyter-lab-jupyter-notebooks>`__ in AMS)

.. include:: ams_plumed.rst.include

Complete Python code
----------------------------

.. literalinclude:: ams_plumed.py
    :language: python
