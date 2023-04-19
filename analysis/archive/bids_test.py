"""
.. _read_bids_datasets-example:

======================
01. Read BIDS datasets
======================

When working with electrophysiological data in the BIDS format, an important
resource is the `OpenNeuro <https://openneuro.org/>`_ database. OpenNeuro
works great with MNE-BIDS because every dataset must pass a validator
that tests to ensure its format meets BIDS specifications before the dataset
can be uploaded, so you know the data will work with a script like in this
example without modification.

We have various data types that can be loaded via the ``read_raw_bids``
function:

- MEG
- EEG (scalp electrodes)
- iEEG (ECoG and SEEG)
- the anatomical MRI scan of a study participant

In this tutorial, we show how ``read_raw_bids`` can be used to load and
inspect BIDS-formatted data.

"""
# Authors: Adam Li <adam2392@gmail.com>
#          Richard Höchenberger <richard.hoechenberger@gmail.com>
#          Alex Rockhill <aprockhill@mailbox.org>
#
# License: BSD-3-Clause

# %%
# Imports
# -------
# We are importing everything we need for this example:
import os
import os.path as op
#import openneuro
import mne
#mne.viz.set_browser_backend('qt')
from mne.datasets import sample
from mne_bids import BIDSPath, read_raw_bids, print_dir_tree, make_report

# %%
# Download a subject's data from an OpenNeuro BIDS dataset
# --------------------------------------------------------
#
# Download the data, storing each in a ``target_dir`` target directory, which,
# in ``mne-bids`` terminology, is the `root` of each BIDS dataset. This example
# uses this `EEG dataset <https://openneuro.org/datasets/ds002778>`_ of
# resting-state recordings of patients with Parkinson's disease.
#

# .. note: If the keyword argument include is left out of
#          ``openneuro.download``, the whole dataset will be downloaded.
#          We're just using data from one subject to reduce the time
#          it takes to run the example.

dataset = 'ds002778'
subject = 'EL006'

# Download one subject's data from each dataset
bids_root = "C:\\Users\\alessia\\Documents\\Jobs\\ICN\\vigor-stim\\Data\\rawdata\\"# op.join(op.dirname(sample.data_path()), dataset)
subject = "EL006"
bids_path = BIDSPath(root=bids_root, suffix="ieeg", subject=subject, task="VigorStimR", description="neurobehav")

bids_path = BIDSPath(root=bids_root, suffix="ieeg_neuro_behav", subject=subject, task="VigorStim")

# %%
# We can now retrieve a list of all MEG-related files in the dataset:

print(bids_path.match())

raw = read_raw_bids(bids_path=bids_path, verbose=False)

# %%
# Now we can inspect the ``raw`` object to check that it contains to correct
# metadata.
#
# Basic subject metadata is here.

print(raw.info['subject_info'])

# %%
# Power line frequency is here.

print(raw.info['line_freq'])

# %%
# Sampling frequency is here.

print(raw.info['sfreq'])

# %%
# Events are now Annotations
print(raw.annotations)

# %%
# Plot the raw data.

raw.plot()
print("h")

# %%
# .. LINKS
#
# .. _parkinsons_eeg_dataset:
#    https://openneuro.org/datasets/ds002778
#
