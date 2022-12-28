"""Add summation chanels, save file."""
from typing import Sequence

import mne
import mne_bids
import numpy as np


def summation_channel_name(summation_channels: Sequence[str]) -> str:
    """Create channel name for summation montage from given channels."""
    base_items = None
    channel_numbers = []
    for ch_name in summation_channels:
        items = ch_name.split("_")
        channel_numbers.append(items.pop(2))
        if not base_items:
            base_items = items
    channel_number = f"({'+'.join(channel_numbers)})"
    base_items.insert(2, channel_number)
    summation_channel = "_".join(base_items)
    return summation_channel


def add_summation_channel(
    raw: mne.io.BaseRaw,
    summation_channels: Sequence[str],
    new_channel_name: str = "auto",
    inplace: bool = False,
    scale_data_by_factor: int | float | None = None,
    sort_channels: bool = True,
) -> mne.io.BaseRaw:
    """Sum up signals from given channels and add to MNE Raw object.

    Parameters
    ----------
    raw: MNE Raw object
        MNE Raw object containing data.
    summation_channels: list of str
        Channel names to be summed up.
    new_channel_name: str
        Channel name of new channel to be added
    inplace : bool. Default: False
        Set to True if Raw object should be modified in place.
    scale_data_by_factor
        Factor by which data to scale
    sort_channels: bool. Default: True
        Set to False if channel names should not be sorted alphabetically.

    Returns
    -------
    raw : MNE Raw object
        The Raw object containing the added squared channel.
    """
    if new_channel_name == "auto":
        new_channel_name = summation_channel_name(summation_channels)
    data = raw.get_data(picks=summation_channels)
    new_data = np.expand_dims(data.sum(axis=0), axis=0)
    if scale_data_by_factor is not None:
        new_data *= scale_data_by_factor
    ch_type = raw.get_channel_types(picks=summation_channels[0])
    info = mne.create_info(
        ch_names=[new_channel_name],
        sfreq=raw.info["sfreq"],
        ch_types=ch_type,
        verbose=False,
    )
    raw_new = mne.io.RawArray(
        new_data, info, first_samp=0, copy="auto", verbose=False
    )
    if not inplace:
        raw = raw.copy()
    if not raw.preload:
        raw.load_data()
    raw = raw.add_channels([raw_new], force_update_info=True)
    if sort_channels:
        raw.reorder_channels(sorted(raw.ch_names))
    return raw


def main() -> None:
    """Main function of this script"""
    bids_path = ...  # Enter BIDSPath of file here
    raw = mne_bids.read_raw_bids(bids_path, verbose=False)  # type: ignore

    summation_channels_list = [
        ["LFP_L_02_STN_MT", "LFP_L_03_STN_MT", "LFP_L_04_STN_MT"],
        ["LFP_L_05_STN_MT", "LFP_L_06_STN_MT", "LFP_L_07_STN_MT"],
        ["LFP_R_02_STN_MT", "LFP_R_03_STN_MT", "LFP_R_04_STN_MT"],
        ["LFP_R_05_STN_MT", "LFP_R_06_STN_MT", "LFP_R_07_STN_MT"],
    ]

    for summation_channels in summation_channels_list:
        scaling_factor = 3 / len(summation_channels)
        add_summation_channel(
            raw=raw,
            summation_channels=summation_channels,
            new_channel_name="auto",
            inplace=True,
            scale_data_by_factor=scaling_factor,
            sort_channels=True,
        )

    ### UNCOMMENT TO OVERVWRITE FILE
    # raw = pte.filetools.rewrite_bids_file(raw=raw, bids_path=file)

    raw.plot(block=True, title="Final result")


if __name__ == "__main__":
    main()
