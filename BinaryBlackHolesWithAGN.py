from AccretionDisk import AccretionDisk
from SuperMassiveBlackHole import SuperMassiveBlackHole
from BinaryBlackHole import BinaryBlackHole
from amuse.datamodel import Particle, Particles, ParticlesSuperset
from amuse.couple.bridge import Bridge
from amuse.community.huayno.interface import Huayno
from Gadget2_Gravity import Gadget2_Gravity
import numpy as np
from amuse.lab import units, nbody_system, constants, Particles
from amuse.io import write_set_to_file
from amuse.units.generic_unit_converter import ConvertBetweenGenericAndSiUnits


class BinaryBlackHolesWithAGN(object):

    def __init__(self, mass_of_central_black_hole, number_of_binaries, number_of_gas_particles, disk_mass_fraction, binaries_affect_disk=False,
                 radiative_transfer=False, timestep=0.1 | units.Myr, end_time = 5 | units.Myr, number_of_hydro_workers=1, number_of_grav_workers=1, steps_of_inclination = 18,
                 disk_powerlaw=1):
        self.smbh = SuperMassiveBlackHole(mass=mass_of_central_black_hole)
        self.inner_boundary = self.smbh.radius * 100
        self.outer_boundary = self.smbh.radius * 100000
        self.steps_of_inclination = steps_of_inclination
        self.end_time = end_time
        self.binary_codes = []
        self.binary_code_from_channels = []
        self.binary_code_to_channels = []
        self.number_of_gas_particles = number_of_gas_particles
        self.disk_converter = nbody_system.nbody_to_si(self.smbh.super_massive_black_hole.mass, self.inner_boundary)
        self.gadget_converter = nbody_system.nbody_to_si(disk_mass_fraction*self.smbh.super_massive_black_hole.mass, self.outer_boundary)
        self.disk = AccretionDisk(fraction_of_central_blackhole_mass=disk_mass_fraction,
                                  number_of_particles=self.number_of_gas_particles,
                                  disk_min=1.,
                                  disk_max=self.outer_boundary/self.inner_boundary,
                                  number_of_workers=number_of_hydro_workers,
                                  gadget_converter=self.gadget_converter,
                                  disk_converter=self.disk_converter,
                                  powerlaw=disk_powerlaw,
                                  end_time=self.end_time)
        write_set_to_file(self.disk.gas_particles, "Initial_AccretionDisk_SMBH_Mass_{}_MSun.hdf5".format(self.smbh.super_massive_black_hole.mass.value_in(units.MSun)), "hdf5")

        self.binaries = Particles()
        self.binaries_affect_disk = binaries_affect_disk
        self.number_of_binaries = number_of_binaries
        self.hydro_code = self.disk.hydro_code
        # Generate the binary locations and masses
        self.all_grav_particles = Particles()
        self.all_grav_particles.add_particle(self.smbh.super_massive_black_hole)
        self.generate_binaries()
        self.gravity_converter = nbody_system.nbody_to_si(self.all_grav_particles.mass.sum(), self.all_grav_particles.virial_radius())

        # Now add them to a combined gravity code
        self.grav_code = Huayno(self.gravity_converter, number_of_workers=number_of_grav_workers)
        # Adding them gravity
        self.grav_code.particles.add_particles(self.all_grav_particles)

        # Channels to update the particles here
        self.channel_from_grav_to_binaries = self.grav_code.particles.new_channel_to(self.all_grav_particles)
        self.channel_from_binaries_to_grav = self.all_grav_particles.new_channel_to(self.grav_code.particles)

        self.timestep = timestep
        self.bridge = self.create_bridges(timestep)
        self.evolve_model(self.end_time)

    def evolve_model(self, end_time):

        sim_time = 0. | self.end_time.unit

        # New particle superset of all particles in the sim
        # Initial Conditions
        all_sim_particles = ParticlesSuperset([self.grav_code.particles, self.disk.hydro_code.gas_particles])
        write_set_to_file(all_sim_particles, "{}_Binaries_{}_Gas_AGN_sim_Initial.hdf5".format(self.number_of_binaries, self.number_of_gas_particles), "amuse")

        while sim_time < end_time:
            sim_time += self.timestep
            self.bridge.evolve_model(sim_time)
            print('Time: {}'.format(sim_time.value_in(units.yr)), flush=True)

            self.channel_from_grav_to_binaries.copy()
            self.disk.hydro_channel_to_particles.copy()

            # New particle superset of all particles in the sim
            all_sim_particles = ParticlesSuperset([self.grav_code.particles, self.disk.hydro_code.gas_particles])
            write_set_to_file(all_sim_particles, "{}_Binaries_{}_Gas_AGN_sim.hdf5".format(self.number_of_binaries, self.number_of_gas_particles), "amuse")

        self.grav_code.stop()
        self.disk.hydro_code.stop()


    def generate_binaries(self):
        blackhole_masses = [30,30]
        initial_outer_semi_major_axis = np.random.uniform(self.inner_boundary.value_in(self.outer_boundary.unit), self.outer_boundary.value_in(self.outer_boundary.unit), 1)[0]
        initial_outer_eccentricity = np.random.uniform(0, 180, 1)[0]
        binaries = BinaryBlackHole(blackhole_masses[0], blackhole_masses[1], self.smbh.super_massive_black_hole.mass,
                                   initial_outer_semi_major_axis= initial_outer_semi_major_axis | (self.outer_boundary.unit),
                                   initial_outer_eccentricity=0.6,
                                   inner_eccentricity=0.6,
                                   inclination=initial_outer_eccentricity,
                                   )

        self.all_grav_particles.add_particles(binaries.blackholes)
        self.binaries.add_particles(binaries.blackholes)

    def create_bridges(self, timestep=0.1 | units.Myr):
        """
        Bridge between SMBH and disk one way
        Bridge between disk and Binaries, one way
        SMBH and Binaries are in the same gravity, no bridge
        Possibly bridge from binaries to the gas

        :return:
        """

        self.bridge = Bridge(use_threading=True)
        self.bridge.timestep = timestep
        self.bridge.add_system(self.grav_code, (self.hydro_code,))
        self.bridge.add_system(self.hydro_code, (self.grav_code, ))

        return self.bridge
