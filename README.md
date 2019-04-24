# Comp_Astro_Final_Project
Project: "Dynamical Hardening of Black Hole Binaries in Active Galactic Nuclei"

Contributors:   Giannis Politopoulos,
		Jacob Bieker,
		Zorry Belcheva,
		Dylan Natoewal,
		Benjamin Gilliam,
		Lindsey Oberhelman,

Summary: The aim of this project, is to simulate an AGN around which, there is a massive disk and a number of binary stellar-mass blackholes. The AGN consists of a SMBH ~1e6 MSun and the binary blackholes ~30 MSun whilst the disk ~10% of the SMBH mass.
The idea behind the simulation, is that the binary blackholes will interact with the AGN disk while orbiting the SMBH, lose energy hence reducing their orbital period and semi major axis. This effect becomes greater the closer the binary blackholes get resulting to their merging. Such mergers are potential candidates for the gravitational waves detected by LIGO.

The total code consists of 7 files.

SuperMAssiveBlackHole.py : Creates the SMBH at the center of the grid

AccretionDisk.py : Creates a disk, using the ProtoPlanetaryDisk in AMUSE

BinaryBlackHole.py : Creates a binary blackhole pair and sets it in orbit around the center of mass. It then sets the center of mass of the binary in orbit around the SMBH.

BinaryBlackHolesWithAGN.py : Calls the aforementioned classes to create the system to be simulated.

Gadget2_Gravity.py : Is an extended version of Gadget2 AMUSE package, to include the function: get_gravity_at_point for the gravitational interaction of the disk with the binaries

main.py : Wraps up everything to be ran for the simulation

plotting.py : Uses everything saved in the simulation for plotting and animation

To run the simulation : The simulation is ran through AMUSE by running the main.py file. The simulation parameters can be seen and tuned through the Option Parser implemented.
The main parameters are: 
  --mass_of_central_black_hole default=1000000.0 MSun
  
  --number_of_binaries default=50
  
  --number_of_gas_particles default=100000
  
  --end_time default=10 Myr
  
  --blackhole_mass default=30 MSun
  
  --gravity_timestep default=100 yr
  
  --bridge_timestep default=0.1 Myr
  
  --smbh_as_potential default=False
  
  --binaries_affect_disk default=False
  
  --disk_mass_fraction default=0.1
  
  --number_of_hydro_workers default=6
  
  --number_of_grav_workers default=12
  
  --filename default=BinaryBlackHoles

