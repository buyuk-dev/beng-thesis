# Notes about EEG


## EEG Signal Processing

The electrical potential accross the cell membrane is small, around -70 mV at
rest (1000 microvolts in a millivolt), and it changes around -20 mV during
electrical changes in the cell.

If a large group of these tiny dipoles are aligned in space and their
electrical potentials change at the same time, they can create electrical
potentials which are large enough to conduct through the brain tissue and be
measurable comparing different points on the head.

Electrical potentials measured on the outside of the head fluctuature between
about -200 and 200 μV. You can also see cycles between high and low voltage,
called oscillations, which can occur in the human brain at a number of
frequencies.

Fluctuations in activity of large groups of neurons seem to occur within
certain frequency bands. It is thought that these frequencies are one of the
ways the brain uses to process information. These oscillations can change
during different behaviours, most notably when we are awake vs when we sleep.

Awake state - High frequency Beta waves.
Sleep state - Larger groups of neurons all fire together at low frequencies called Delta waves.

We use the power of those brain waves (Beta, Delta, and others) to provide
neurofeedback or create simple BCI (Brain-Computer Interfaces).

Scalp and skull diffuse the electrical signal from the brain, so measurements
performed outside contain very little spatial information about the signal's
source. Additionally, each extracranial measurement could be caused by many
different configurations of dipoles inside the brain.

EEG electrodes locations are standarized in a regular grid covering the surface of the head.
Each location is designated by a code:
- letter indicating the location of the head (F-Frontal; C-Central; P-Parietal; T-Temporal; O-Occipital; Fp-Fronto-polar).
- The suffix has a 'z' if along the midline, odd numbers over the left hemisphere, and even over the right.
- Numbers start along the midline and get larger for more lateral sites on the head.

Can location of reference electrode affect the signal quality?
How about using multiple reference electrodes?
What if we used each electrode as a reference for all others creating a fully connected graph of electrodes/reference electrodes?
Would more reference electrodes yield more spatial information about the signal source?

