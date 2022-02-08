#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  7 15:12:43 2022

@author: haascp
"""
import os
import pandas as pd
import datapane as dp

from mocca.visualization.basic_plots import plot_1D_data
from mocca.visualization.results_plot import plot_chrom_with_peaks
from mocca.report.utils import settings_to_df
from mocca.report.hplc_input import exps_to_df
from mocca.peak.utils import average_peak_spectrum


def chroms_to_dict(chroms):
    chrom_dict = {'index': [],
                  'file': [],
                  'bad_data': [],
                  'compound_run': [],
                  'istd_added': [],
                  'num_peaks': []}

    for i, chrom in enumerate(chroms):
        chrom_dict['index'].append(i + 1)
        chrom_dict['file'].append(os.path.basename(chrom.experiment.path))
        chrom_dict['bad_data'].append(chrom.bad_data)
        chrom_dict['compound_run'].append(chrom.experiment.compound is not None)
        chrom_dict['istd_added'].append(chrom.experiment.istd is not None)
        chrom_dict['num_peaks'].append(len(chrom.peaks))
    return chrom_dict


def chroms_to_df(chroms):
    chrom_dict = chroms_to_dict(chroms)
    chrom_df = pd.DataFrame(chrom_dict)
    return chrom_df


def peaks_to_result_df(peaks):
    peaks_dict = {'peak_id': [],
                  'retention_time': [],
                  'compound_id': [],
                  'concentration': [],
                  'integral': [],
                  'is_pure': [],
                  'is_saturated': [],
                  'is_compound': []}
    for peak in peaks:
        times = peak.dataset.time
        peaks_dict['peak_id'].append(peak.idx)
        peaks_dict['retention_time'].append(times[peak.maximum + peak.offset])
        peaks_dict['compound_id'].append(peak.compound_id)
        peaks_dict['concentration'].append(peak.concentration)
        peaks_dict['integral'].append(peak.integral)
        peaks_dict['is_pure'].append(peak.pure)
        peaks_dict['is_saturated'].append(peak.saturation)
        peaks_dict['is_compound'].append(peak.is_compound)
    return pd.DataFrame(peaks_dict)

def create_chrom_page(chrom, index):
    exp_df = exps_to_df([chrom.experiment])
    
    chrom_plot = plot_chrom_with_peaks(chrom)
    
    spectrum_plots = []
    for peak in chrom:
        spectrum = average_peak_spectrum(peak)
        wls = peak.dataset.wavelength
        
        df = pd.DataFrame({'x': wls,
                           'y': spectrum})
        title_base = f"UV-Vis spectrum of peak at {round(peak.dataset.time[peak.maximum +peak.offset], 3)} min"
        if peak.compound_id:
            title = title_base + f' ({peak.compound_id})'
        elif not peak.pure:
            title = title_base + ' (impure)'
        else:
            title = title_base
        plot = plot_1D_data(df, xlabel='Wavelength (nm)',
                            ylabel='Absorbance (mAU)',
                            title=title)
        spectrum_plots.append(plot)

    peaks_df = peaks_to_result_df(chrom.peaks)
    return dp.Page(
        title=str(index),
        blocks=[
            dp.Group(
                dp.Text(f"## Details to chromatogram {index}"),
                dp.Text("## MOCCA (Multiway Online Chromatographic Chemical Analysis)"),
                columns=2
            ),
            dp.Text("### Table: Experiment as given by the user."),
            dp.Table(exp_df, label="experiment_table"),
            dp.Text("### Figure: Chromatogram with highlighted peaks."),
            dp.Plot(chrom_plot),
            dp.Text("### Table: Peaks found in the chromatogram."),
            dp.DataTable(peaks_df),
            dp.Text("### Figures: Averaged UV-Vis spectra over the picked peak."),
            dp.Group(
                *spectrum_plots,
                columns=2
                )
        ],        
    )


def report_chroms(chroms, settings, report_path):
    chrom_df = chroms_to_df(chroms)
    summary_page = dp.Page(
        title="Start page",
        blocks=[
            dp.Group(
                dp.Text("# Results by chromatogram report"),
                dp.Text("## MOCCA (Multiway Online Chromatographic Chemical Analysis)"),
                columns=2
            ),
            dp.Text("### Table: Settings and thresholds used to process chromatograms."),
            dp.Table(settings_to_df(settings), label="settings_table"),
            dp.Text("### Table: Chromatograms processed during the campaign."),
            dp.DataTable(chrom_df, label="chrom_table")
        ],
    )
    chrom_pages = []
    for i, chrom in enumerate(chroms):
        page = create_chrom_page(chrom, i + 1)
        chrom_pages.append(page)
    r = dp.Report(
        summary_page,
        *chrom_pages
    )
    r.save(path=os.path.join(report_path, "report_chroms.html"), open=True)
