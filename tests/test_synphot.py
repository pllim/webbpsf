#!/usr/bin/env python
import os, sys
sys.path.append('../lib')
import numpy as N
import matplotlib.pyplot as P
import matplotlib
import pywcs, pyfits
#import aplpy, atpy
#import RO.DS9
from IPython.Debugger import Tracer; stop = Tracer()
import logging
_log = logging.getLogger('t')
import time

import webbpsf

import pysynphot
from pysynpol import synplot


def barOutline(xdata, ydata, endstozero=True, *args, **kwargs):
    """ Draw an outlined-box type plot (like IDL's linestyle=10)
    Based on http://www.scipy.org/Cookbook/Matplotlib/UnfilledHistograms

    Parameters
    ----------
    xdata : array_like
        left edge of bin
    ydata : array_like
        value for bin
    endstozero : bool
        Connect the ends of the histogram to the X axis? default True


    You can also supply any number of additional matplotlib keywords that
    will be passed along to plot()
    """

    #(histIn, binsIn) = np.histogram(dataIn, *args, **kwargs)

    stepSize = xdata[1] - xdata[0]

    bins = N.zeros(len(xdata)*2 + 2, dtype=N.float)
    data = N.zeros(len(xdata)*2 + 2, dtype=N.float)
    for bb in range(len(xdata)):
        bins[2*bb + 1] = xdata[bb]
        bins[2*bb + 2] = xdata[min(bb+1, len(xdata)-1)]
        if bb < len(ydata):
            data[2*bb + 1] = ydata[bb]
            data[2*bb + 2] = ydata[bb]

    bins[0] = bins[1]
    bins[-1] = bins[-2]
    data[0] = data[1]
    data[-1] = data[-2]

    if endstozero:
        data = N.concatenate(([0], data,[0]))
        bins = N.concatenate(([bins[0]], bins, [bins[-1]]))

    P.plot(bins,data, *args, **kwargs)



def get_rel_fluxes(obsname='miri,im,f560w', nlambda=10, plot=True, verbose=False):
    raise NotImplemented("Obsolete!")

    star = pysynphot.Icat('ck04models',7700,0.0,2.0)
    band0 = pysynphot.ObsBandpass(obsname)
    #band = band0 *0.01  # convert from percent to real throughput???
    band=band0
       
    # choose reasonable min and max wavelengths
    w_above10 = N.where(band.throughput > 0.25*band.throughput.max())
    minwave = band.wave[w_above10].min()  
    maxwave = band.wave[w_above10].max()

    wavesteps =  N.linspace(minwave,maxwave,nlambda)
    deltawave = wavesteps[1]-wavesteps[0]
    effstims = []
    t0= time.time()
    for wave in wavesteps:
        box = pysynphot.Box(wave, deltawave)
        obs = pysynphot.Observation(star, band*box)
        effstims.append(obs.effstim('counts'))


        if verbose: 
            _log.info("Box [%.3f-%.3f]: %f cts" % (wave-deltawave/2, wave+deltawave/2, effstims[-1]))
        #print band.waveunits.Convert(wave,'micron'), effstims[-1]
    t1 = time.time()
    print "  that took %f seconds for %d wavelengths" % (t1-t0, nlambda)


    effstims = N.array(effstims)
    effstims /= effstims.sum()

    wave_um =  band.waveunits.Convert(wavesteps,'micron')
    if plot:
        P.clf()
        ax=P.subplot(311)
        synplot(star)
        ax.text(0.5, 0.8, "Some random star", horizontalalignment='center', transform = ax.transAxes)


        ax=P.subplot(312,sharex=ax)
        synplot(band)
        ax.text(0.5, 0.8, obsname, horizontalalignment='center', transform = ax.transAxes)
        if 'fnd' in obsname: ax.set_ybound((0,0.002))
     
        ax.set_xbound(1,30)
        P.draw()


        P.subplot(313,sharex=ax)
        #P.plot(wave_um, effstims)
        barOutline(wave_um, effstims)
        ax.set_xbound(1,30)
        
    #print band.waveunits.Convert(minwave,'micron')
    #print band.waveunits.Convert(maxwave,'micron')
    return wave_um, effstims


def plot_weights_miri():
    inst = webbpsf.MIRI()
    filtlist_W = [f for f in inst.filter_list if f[-1] == 'W']
    filtlist_C = [f for f in inst.filter_list if f[-1] != 'W']

    #filtlist_C = [f for f in inst.filter_list if f[-1] == 'C']


    from matplotlib.backends.backend_pdf import PdfPages
    pdf=PdfPages('weights_miri.pdf')

    plotweights('miri', filtlist=filtlist_W)
    Mstar = pysynphot.Icat('ck04models',3500,0.0,2.0)
    plotweights('miri', filtlist=filtlist_W, overplot=True, ls='--', source=Mstar)
    pdf.savefig()


    plotweights('miri', filtlist=filtlist_C)
    Mstar = pysynphot.Icat('ck04models',3500,0.0,2.0)
    plotweights('miri', filtlist=filtlist_C, overplot=True, ls='--', source=Mstar)
    pdf.savefig()

    pdf.close()


def plot_weights_nircam():
    inst = webbpsf.NIRCam()
    filtlist_W = [f for f in inst.filter_list if f[-1] == 'W']
    filtlist_M = [f for f in inst.filter_list if f[-1] == 'M']
    filtlist_N = [f for f in inst.filter_list if f[-1] == 'N' or f[-1] =='2']

    #filtlist_C = [f for f in inst.filter_list if f[-1] == 'C']


    from matplotlib.backends.backend_pdf import PdfPages
    pdf=PdfPages('weights_nircam.pdf')

    plotweights('nircam', filtlist=filtlist_W)
    Mstar = pysynphot.Icat('ck04models',3500,0.0,2.0)
    plotweights('nircam', filtlist=filtlist_W, overplot=True, ls='--', source=Mstar)
    pdf.savefig()


    plotweights('nircam', filtlist=filtlist_M)
    Mstar = pysynphot.Icat('ck04models',3500,0.0,2.0)
    plotweights('nircam', filtlist=filtlist_M, overplot=True, ls='--', source=Mstar)
    pdf.savefig()

    plotweights('nircam', filtlist=filtlist_N)
    Mstar = pysynphot.Icat('ck04models',3500,0.0,2.0)
    plotweights('nircam', filtlist=filtlist_N, overplot=True, ls='--', source=Mstar)
    pdf.savefig()


    pdf.close()





def plotweights(instrument='miri', nlambda =None, filtlist = None, source=None, overplot=False, **kwargs):

    if source is None:
        source= pysynphot.Icat('ck04models',5700,0.0,2.0)

    inst = webbpsf.Instrument(instrument)
    if filtlist is None:
        filters = inst.filter_list
    else:
        filters = filtlist

    if not overplot:
        P.clf()
        P.subplots_adjust(hspace=0.02)

    ax=P.subplot(311)
    synplot(source, **kwargs)
    ax.set_ylim(1e-0, 1e8)
    legend_font = matplotlib.font_manager.FontProperties(size=10)
    P.legend(loc='lower left', prop=legend_font)

    for filt in filters:
        if filt[0].upper() != 'F': continue # skip the IFUs...
        nlambda = inst._filter_nlambda_default[filt]
        print "----------- %s: %d -----------" % (filt, nlambda)
        obsname = ('%s,im,%s'%(instrument, filt)).lower()
        P.subplot(312, sharex=ax)
        inst.filter=filt
        #try:
        band = inst._getSynphotBandpass() #pysynphot.ObsBandpass(obsname)
        synplot(band, **kwargs)
            #ls ="-"
        #except:
            #P.plot([0,30],[0,0]) # plot something to keep color progression in sync...
            #ls ="--"
            #continue

        #waves, weights = get_rel_fluxes(obsname, nlambda, plot=False)
        waves, weights = inst._getWeights(source, nlambda=nlambda)
        #print waves
        #print weights

        P.subplot(313, sharex=ax)
        P.ylabel("Weight")
        P.xlabel("Wavelength [$\mu$m]")

        # barOutline wants to be called with the left edge of each bin, not the center.
        wave_step = waves[1]-waves[0]
        plot_waves = N.concatenate( (waves,[waves[-1]+wave_step]))-wave_step/2
        plot_weights = N.concatenate((weights, [0]))
        barOutline(plot_waves*1e6, plot_weights, label=filt, **kwargs)

        P.draw()
        #stop()
 
    locs = {'miri': 'upper left', 'nircam': 'upper right', 'tfi': 'upper right'}
    bounds = {'miri': (4, 30), 'nircam': (0.5, 6), 'tfi': (0.5, 6), 'nirspec': (0.5, 6), 'fgs': (0.5, 6)}


    P.legend(loc=locs[instrument], prop=legend_font)
    if instrument =='nircam':
        ax.set_xscale('linear')
    ax.set_xbound(*bounds[instrument])


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(name)-12s: %(levelname)-8s %(message)s',)

    #get_rel_fluxes()
