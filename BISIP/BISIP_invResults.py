# -*- coding: utf-8 -*-
"""
Created on Sat Apr 25 14:51:26 2015

@author:    clafreniereberube@gmail.com
            École Polytechnique de Montréal

Copyright (c) 2015-2016 Charles L. Bérubé

This module contains functions to visualize the bayesian inversion results

"""

#==============================================================================
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import FormatStrFormatter
import numpy as np
from os import path, makedirs
from sys import argv
from math import ceil
from pymc import raftery_lewis, gelman_rubin, geweke
from scipy.stats import norm
from BISIP_models import get_data
#==============================================================================

sym_labels = dict([('resi', r"$\rho\/(\Omega\cdot m)$"),
                   ('freq', r"Frequency $(Hz)$"),
                   ('phas', r"-Phase (mrad)"),
                   ('ampl', r"$|\rho|$ (normalized)"),
                   ('real', r"$\rho$' (normalized)"),
                   ('imag', r"$-\rho$'' (normalized)")])

def flatten(x):
    result = []
    for el in x:
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result

def print_resul(pm, model, filename):
#==============================================================================
    # Impression des résultats
    print '\n\nInversion success!'
    print 'Name of file:', filename
    print 'Model used:', model
    e_keys = sorted([s for s in pm.keys() if "_std" in s])
    v_keys = [e.replace("_std", "") for e in e_keys]
    labels = ["{:<8}".format(x+":") for x in v_keys]
    np.set_printoptions(formatter={'float': lambda x: format(x, '6.3E')})
    for l, v, e in zip(labels, v_keys, e_keys):
        print l, pm[v], '+/-', pm[e], np.char.mod('(%.2f%%)',abs(100*pm[e]/pm[v]))

def plot_histo(MDL, model, filename, save):
    keys = sorted([x.__name__ for x in MDL.deterministics]) + sorted([x.__name__ for x in MDL.stochastics])
    keys.remove("zmod")
    for (i, k) in enumerate(keys):
        vect = (MDL.trace(k)[:].size)/(len(MDL.trace(k)[:]))
        if vect > 1:
            keys[i] = [k+"%d"%n for n in range(1,vect+1)]
    keys = list(flatten(keys))
    ncols = 2
    nrows = int(ceil(len(keys)*1.0 / ncols))
    fig, ax = plt.subplots(nrows, ncols, figsize=(10,nrows*2))
    for c, (a, k) in enumerate(zip(ax.flat, keys)):
        if k == "R0":
            stoc = "R0"
        else:
            stoc =  ''.join([i for i in k if not i.isdigit()])
            stoc_num = [int(i) for i in k if i.isdigit()]
        try:
            data = sorted(MDL.trace(stoc)[:][:,stoc_num[0]-1])
        except:
            data = sorted(MDL.trace(stoc)[:])
        fit = norm.pdf(data, np.mean(data), np.std(data))
        plt.axes(a)
        plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)
        plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)
        plt.locator_params(axis = 'y', nbins = 8)
        plt.locator_params(axis = 'x', nbins = 7)
        plt.yticks(fontsize=12)
        plt.xticks(fontsize=12)
        plt.xlabel(k, fontsize=12)
        plt.ylabel("Frequency", fontsize=12)
        hist = plt.hist(data, bins=20, normed=False, label=filename, linewidth=1.0, color="white")
        xh = [0.5 * (hist[1][r] + hist[1][r+1]) for r in xrange(len(hist[1])-1)]
        binwidth = (max(xh) - min(xh)) / len(hist[1])
        fit *= len(data) * binwidth
        plt.plot(data, fit, "-b", linewidth=1.5)
        plt.grid(None)
#        plt.legend(fontsize=8)
#        plt.title(filename, fontsize=8)
    fig.tight_layout(w_pad=0.1, h_pad=1.0)
    for a in ax.flat[ax.size - 1:len(keys) - 1:-1]:
        a.set_visible(False)
    if save:
        save_where = '/Figures/Histograms/'
        actual_path = str(path.dirname(path.realpath(argv[0]))).replace("\\", "/")
        save_path = actual_path+save_where
        print "\nSaving parameter histograms in:\n", save_path
        if not path.exists(save_path):
            makedirs(save_path)
        fig.savefig(save_path+'Histo-%s-%s.pdf'%(model,filename))
    try:    plt.close(fig)
    except: pass
    return fig

def plot_traces(MDL, model, filename, save):
    keys = sorted([x.__name__ for x in MDL.deterministics]) + sorted([x.__name__ for x in MDL.stochastics])
    keys.remove("zmod")

    for (i, k) in enumerate(keys):
        vect = (MDL.trace(k)[:].size)/(len(MDL.trace(k)[:]))
        if vect > 1:
            keys[i] = [k+"%d"%n for n in range(1,vect+1)]
    keys = list(flatten(keys))
    ncols = 2
    nrows = int(ceil(len(keys)*1.0 / ncols))
    fig, ax = plt.subplots(nrows, ncols, figsize=(10,nrows*2))
    for c, (a, k) in enumerate(zip(ax.flat, keys)):
        if k == "R0":
            stoc = "R0"
        else:
            stoc =  ''.join([i for i in k if not i.isdigit()])
            stoc_num = [int(i) for i in k if i.isdigit()]
        try:
            data = MDL.trace(stoc)[:][:,stoc_num[0]-1]
        except:
            data = MDL.trace(stoc)[:]
#        x = np.arange(MDL.get_state()["sampler"]["_burn"], MDL.get_state()["sampler"]["_iter"], MDL.get_state()["sampler"]["_thin"])
        plt.axes(a)
        plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)
        plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)
        plt.locator_params(axis = 'y', nbins = 6)
        plt.yticks(fontsize=12)
        plt.xticks(fontsize=12)
        plt.ylabel(k, fontsize=12)
        plt.xlabel("Iteration", fontsize=12)
        plt.plot(data, '-', color='b', label=filename, linewidth=1.0)
        plt.grid(None)
#        plt.legend(loc=2, fontsize=8)
#        plt.title(filename, fontsize=8)
    fig.tight_layout()
    for a in ax.flat[ax.size - 1:len(keys) - 1:-1]:
        a.set_visible(False)

    if save:
        save_where = '/Figures/Traces/'
        actual_path = str(path.dirname(path.realpath(argv[0]))).replace("\\", "/")
        save_path = actual_path+save_where
        print "\nSaving traces figure in:\n", save_path
        if not path.exists(save_path):
            makedirs(save_path)
        fig.savefig(save_path+'Trace-%s-%s.pdf'%(model,filename))
    try:    plt.close(fig)
    except: pass
    return fig

def plot_scores(MDL, model, filename, save):
    keys = sorted([x.__name__ for x in MDL.stochastics]) + sorted([x.__name__ for x in MDL.deterministics])
    keys.remove("zmod")
    if model == "Debye":
        adj = -1
        keys.remove("m")
    else: adj = 0
    for (i, k) in enumerate(keys):
        vect = (MDL.trace(k)[:].size)/(len(MDL.trace(k)[:]))
        if vect > 1:
         keys[i] = [k+"%d"%n for n in range(1+adj,vect+1+adj)]
    keys = list(flatten(keys))
    ncols = 2
    nrows = int(ceil(len(keys)*1.0 / ncols))
    plt.ioff()
    fig, ax = plt.subplots(nrows, ncols, figsize=(10,nrows*2))
    for (a, k) in zip(ax.flat, keys):
        plt.axes(a)
        plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)
        plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)
        plt.yticks(fontsize=8)
        plt.xticks(fontsize=8)
        plt.ylabel(k, fontsize=8)
        if k[-1] not in ["%d"%d for d in range(1+adj,8)] or k == "R0":
            try:
                scores = geweke(MDL.trace(k)[:].ravel())
                plt.plot([x[0] for x in scores], [y[1] for y in scores], "bo")
                plt.plot([0,max([x[0] for x in scores])], [2,2], "--g")
                plt.plot([0,max([x[0] for x in scores])], [-2,-2], "--g")
            except:
                print "Singular matrix, can't compute scores for %s"%k
        else:
            try:
                scores = geweke(MDL.trace(k[:-1])[:][:,int(k[-1])-1-adj].ravel())
                plt.plot([x[0] for x in scores], [y[1] for y in scores], "bo")
                plt.plot([0,max([x[0] for x in scores])], [2,2], "--g")
                plt.plot([0,max([x[0] for x in scores])], [-2,-2], "--g")
            except:
                print "Singular matrix, can't compute scores for %s"%k

        plt.grid(None)
        plt.ylim([-3,3])
        plt.yticks(range(-2,3))
        plt.ylabel("$\sigma$ (%s)"%k, fontsize=8)
        plt.xlabel("First iteration", fontsize=8)
    fig.tight_layout()
    for a in ax.flat[ax.size - 1:len(keys) - 1:-1]:
        a.set_visible(False)

    if save:
        save_where = '/Figures/Scores/'
        actual_path = str(path.dirname(path.realpath(argv[0]))).replace("\\", "/")
        save_path = actual_path+save_where
        print "\nSaving Geweke scores in:\n", save_path
        if not path.exists(save_path):
            makedirs(save_path)
        fig.savefig(save_path+'Geweke-%s-%s.pdf'%(model,filename))
    try:    plt.close(fig)
    except: pass
    return fig

def plot_summary(MDL, model, filename, ch_n, save):
    keys = sorted([x.__name__ for x in MDL.stochastics]) + sorted([x.__name__ for x in MDL.deterministics])
    keys.remove("zmod")
    if model == "Debye":
        adj = -1
        keys.remove("m")
    else: adj = 0
    for (i, k) in enumerate(keys):
        vect = (MDL.trace(k)[:].size)/(len(MDL.trace(k)[:]))
        if vect > 1:
         keys[i] = [k+"%d"%n for n in range(1+adj,vect+1+adj)]
    keys = list(reversed(sorted(flatten(keys))))
    try:    r_hat = gelman_rubin(MDL)
    except:
        print "\nTwo or more chains of equal length required for Gelman-Rubin convergence"
    fig, axes = plt.subplots(figsize=(8,5))
    gs2 = gridspec.GridSpec(3, 3)
    ax1 = plt.subplot(gs2[:, :-1])
    ax2 = plt.subplot(gs2[:, -1], sharey = ax1)
    ax1.set_title(filename)
    ax2.set_xlabel("R-hat")
    ax2.plot([1,1], [-1,len(keys)], "--b")
    for (i, k) in enumerate(keys):
        test = k[-1] not in ["%d"%d for d in range(1+adj,8)] or k == "R0"
        for c in range(ch_n):
            if test:
                imp = None
                val_m = MDL.stats(k[:imp], chain=c)[k[:imp]]['mean']
                hpd_h = MDL.stats(k[:imp], chain=c)[k[:imp]]['95% HPD interval'][0]
                hpd_l = MDL.stats(k[:imp], chain=c)[k[:imp]]['95% HPD interval'][1]
            else:
                imp = -1
                val_m = MDL.stats(k[:imp], chain=c)[k[:imp]]['mean'][int(k[-1])-1-adj]
                hpd_h = MDL.stats(k[:imp], chain=c)[k[:imp]]['95% HPD interval'][0][int(k[-1])-1-adj]
                hpd_l = MDL.stats(k[:imp], chain=c)[k[:imp]]['95% HPD interval'][1][int(k[-1])-1-adj]
            val = val_m
            err = [[abs(hpd_h-val_m)],
                    [abs(hpd_l-val_m)]]
            if ch_n % 2 != 0:   o_s = 0
            else:               o_s = 0.5
            ax1.scatter(val, i - (ch_n/2)*(1./ch_n/1.4) + (1./ch_n/1.4)*(c+o_s), color="DeepSkyBlue", marker="o", s=50, edgecolors='k')
            ax1.errorbar(val, i - (ch_n/2)*(1./ch_n/1.4) + (1./ch_n/1.4)*(c+o_s), xerr=err, color="k", fmt=" ", zorder=0)
        if ch_n >= 2:
            R = np.array(r_hat[k[:imp]])
            R[R > 3] = 3
            if test:
                ax2.scatter(R, i, color="b", marker="s", s=50, edgecolors='k')
            else:
                ax2.scatter(R[int(k[-1])-1], i, color="b", marker="s", s=50, edgecolors='k')
    ax1.set_ylim([-1, len(keys)])
    ax1.set_yticks(range(0,len(keys)))
    ax1.set_yticklabels(keys)
    plt.setp(ax2.get_yticklabels(), visible=False)
    ax2.set_xlim([0.5, 3.5])
    ax2.set_xticklabels(["","1","2","3+"])
    ax2.set_xticks([0.5, 1, 2, 3])
    ax1.set_xlabel("Parameter values")

    if save:
        save_where = '/Figures/Summaries/'
        actual_path = str(path.dirname(path.realpath(argv[0]))).replace("\\", "/")
        save_path = actual_path+save_where
        print "\nSaving summary figure in:\n", save_path
        if not path.exists(save_path):
            makedirs(save_path)
        fig.savefig(save_path+'Summary-%s-%s.pdf'%(model,filename))
    try:    plt.close(fig)
    except: pass

    return fig

def plot_autocorr(MDL, model, filename, save):
    keys = sorted([x.__name__ for x in MDL.stochastics]) + sorted([x.__name__ for x in MDL.deterministics])
    keys.remove("zmod")
    if model == "Debye":
        adj = -1
        keys.remove("m")
    else: adj = 0
    for (i, k) in enumerate(keys):
        vect = (MDL.trace(k)[:].size)/(len(MDL.trace(k)[:]))
        if vect > 1:
         keys[i] = [k+"%d"%n for n in range(1+adj,vect+1+adj)]
    keys = list(flatten(keys))
    ncols = 2
    nrows = int(ceil(len(keys)*1.0 / ncols))
    fig, ax = plt.subplots(nrows, ncols, figsize=(10,nrows*2))
    for (a, k) in zip(ax.flat, keys):
        if k[-1] not in ["%d"%d for d in range(1+adj,8)] or k =="R0":
            data = sorted(MDL.trace(k)[:].ravel())
        else:
            data = sorted(MDL.trace(k[:-1])[:][:,int(k[-1])-1-adj].ravel())
        plt.axes(a)
        plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)
        plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)
        plt.yticks(fontsize=12)
        plt.xticks(fontsize=12)
        plt.ylabel(k, fontsize=12)
        to_thin = len(data)/50
        if to_thin != 0: plt.xlabel("Lags / %d"%to_thin, fontsize=8)
        else: plt.xlabel("Lags", fontsize=12)
        max_lags = None
        if len(data) > 50: data= data[::to_thin]
        plt.acorr(data, usevlines=True, maxlags=max_lags, detrend=plt.mlab.detrend_mean)
        plt.grid(None)
    fig.tight_layout()
    for a in ax.flat[ax.size - 1:len(keys) - 1:-1]:
        a.set_visible(False)
    if save:
        save_where = '/Figures/Autocorrelations/'
        actual_path = str(path.dirname(path.realpath(argv[0]))).replace("\\", "/")
        save_path = actual_path+save_where
        print "\nSaving autocorrelation figure in:\n", save_path
        if not path.exists(save_path):
            makedirs(save_path)
        fig.savefig(save_path+'Autocorr-%s-%s.pdf'%(model,filename))
    try:    plt.close(fig)
    except: pass
    return fig

def plot_debye(sol, filename, save, draw):
    if draw or save:
        fig, ax = plt.subplots(figsize=(6,4))
        x = sol["data"]["tau"]
        y = 100*sol["params"]["m"]
        plt.errorbar(x[(x>1e-3)&(x<1e1)], y[(x>1e-3)&(x<1e1)], None, None, "-k", linewidth=2, label="Debye RTD")
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        plt.xlabel("Relaxation time (s)", fontsize=14)
        plt.ylabel("Chargeability (%)", fontsize=14)
        plt.yticks(fontsize=14), plt.xticks(fontsize=14)
        plt.xscale("log")
        plt.xlim([1e-3, 1e1])
        plt.legend(numpoints=1, fontsize=14)
        fig.tight_layout()
    if save:
        save_where = '/Figures/Debye distributions/'
        actual_path = str(path.dirname(path.realpath(argv[0]))).replace("\\", "/")
        save_path = actual_path+save_where
        print "\nSaving relaxation time distribution figure in:\n", save_path
        if not path.exists(save_path):
            makedirs(save_path)
        fig.savefig(save_path+'Polynomial-RTD-%s.pdf'%(filename))
    try:    plt.close(fig)
    except: pass
    if draw:    return fig
    else:       return None

def plot_debye_histo(sol, filename, save, draw):
    if draw or save:
        fig, ax = plt.subplots(figsize=(6,4))
        x = np.log10(sol["data"]["tau"])
        y = 100*sol["params"]["m"]
        plt.bar(x[(x>-3)&(x<1)], y[(x>-3)&(x<1)], width=0.2)
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        plt.xlabel("log Relaxation time (s)", fontsize=14)
        plt.ylabel("Chargeability (%)", fontsize=14)
        plt.yticks(fontsize=14), plt.xticks(fontsize=14)
        plt.legend(numpoints=1, fontsize=14)
        fig.tight_layout()
    if save:
        save_where = '/Figures/Debye distributions/'
        actual_path = str(path.dirname(path.realpath(argv[0]))).replace("\\", "/")
        save_path = actual_path+save_where
        print "\nSaving relaxation time distribution figure in:\n", save_path
        if not path.exists(save_path):
            makedirs(save_path)
        fig.savefig(save_path+'Discrete-RTD-%s.pdf'%(filename))
    try:    plt.close(fig)
    except: pass
    if draw:    return fig
    else:       return None

def save_resul(MDL, pm, model, filepath):
    # Fonction pour enregistrer les résultats
    sample_name = filepath.replace("\\", "/").split("/")[-1].split(".")[0]

    save_where = '/Results/'
    actual_path = str(path.dirname(path.realpath(argv[0]))).replace("\\", "/")
    save_path = actual_path+save_where+"%s/"%sample_name
    print "\nSaving csv file in:\n", save_path
    if not path.exists(save_path):
        makedirs(save_path)
    if model == 'Debye': tag = 0
    else: tag = 1
    A = []
    headers = []
    for c, key in enumerate(sorted(pm.keys())):
        A.append(list(np.array(pm[key]).ravel()))
        key = model[:2]+"_"+key
        if len(A[c]) == 1:
            headers.append(key)
        else:
            for i in range(len(A[c])):
                headers.append(key+"%d" %(i+tag))
    headers = ','.join(headers)
    results = np.array(flatten(A))
    np.savetxt(save_path+'INV_%s_%s.csv' %(model,sample_name), results[None],
               header=headers, comments='', delimiter=',')
    vars_ = ["%s"%x for x in MDL.stochastics]+["%s"%x for x in MDL.deterministics]
    if "zmod" in vars_: vars_.remove("zmod")
    MDL.write_csv(save_path+'STATS_%s_%s.csv' %(model,sample_name), variables=(vars_))

def merge_results(model,files):
    save_where = '/Batch results/'
    actual_path = str(path.dirname(path.realpath(argv[0]))).replace("\\", "/")
    save_path = actual_path+save_where
    print "\nMerging csv files"
    if not path.exists(save_path):
        makedirs(save_path)
    to_merge = actual_path+"/Results/%s/INV_%s_%s.csv" %(files[0],model,files[0])
    headers = np.genfromtxt(to_merge, delimiter=",", dtype=str, skip_footer=1)
    merged_inv_results = np.empty((len(files), len(headers)))
    for i, f in enumerate(files):
        merged_inv_results[i] = np.loadtxt(actual_path+"/Results/%s/INV_%s_%s.csv" %(f,model,f), delimiter=",", skiprows=1)
    rows = np.array(files, dtype=str)[:, np.newaxis]
    hd = ",".join(["ID"] + list(headers))
    np.savetxt(save_path+"Merged_%s_%s_TO_%s.csv" %(model,files[0],files[-1]), np.hstack((rows, merged_inv_results)), delimiter=",", header=hd, fmt="%s")
    print "Batch file successfully saved in:\n", save_path

def plot_data(filename, headers, ph_units):
    data = get_data(filename,headers,ph_units)
    # Graphiques du data
    Z = data["Z"]
    dZ = data["Z_err"]
    f = data["freq"]
    Zr0 = max(abs(Z))
    zn_dat = Z/Zr0
    zn_err = dZ/Zr0
    Pha_dat = 1000*data["pha"]
    Pha_err = 1000*data["pha_err"]
    Amp_dat = data["amp"]/Zr0
    Amp_err = data["amp_err"]/Zr0

    fig, ax = plt.subplots(3, 1, figsize=(5,8))
    for t in ax:
        t.tick_params(labelsize=12)
    # Real-Imag
    plt.axes(ax[0])
    plt.errorbar(zn_dat.real, -zn_dat.imag, zn_err.imag, zn_err.real, '.b', label=filename)
    plt.xlabel(sym_labels['real'], fontsize=12)
    plt.ylabel(sym_labels['imag'], fontsize=12)

    plt.xlim([None, 1])
    plt.ylim([0, None])
#    plt.legend(numpoints=1, fontsize=9)
#    plt.title(filename, fontsize=10)
    # Freq-Phas
    plt.axes(ax[1])
    plt.errorbar(f, -Pha_dat, Pha_err, None, '.b', label=filename)
    ax[1].set_yscale("log", nonposy='clip')
    ax[1].set_xscale("log")
    plt.xlabel(sym_labels['freq'], fontsize=12)
    plt.ylabel(sym_labels['phas'], fontsize=12)
#    plt.legend(loc=2, numpoints=1, fontsize=9)
    plt.ylim([1,1000])
    # Freq-Ampl
    plt.axes(ax[2])
    plt.errorbar(f, Amp_dat, Amp_err, None, '.b', label=filename)
    ax[2].set_xscale("log")
    plt.xlabel(sym_labels['freq'], fontsize=12)
    plt.ylabel(sym_labels['ampl'], fontsize=12)
    plt.ylim([None,1.0])
#    plt.legend(numpoints=1, fontsize=9)
    fig.tight_layout()

    plt.close(fig)
    return fig

def plot_fit(data, fit, model, filepath, save=False, draw=True):
    sample_name = filepath.replace("\\", "/").split("/")[-1].split(".")[0]
    # Graphiques du fit
    f = data["freq"]
    Zr0 = max(abs(data["Z"]))
    zn_dat = data["Z"]/Zr0
    zn_err = data["Z_err"]/Zr0
    zn_fit = fit["best"]/Zr0
    zn_min = fit["lo95"]/Zr0
    zn_max = fit["up95"]/Zr0
    Pha_dat = 1000*data["pha"]
    Pha_err = 1000*data["pha_err"]
    Pha_fit = 1000*np.angle(fit["best"])
    Pha_min = 1000*np.angle(fit["lo95"])
    Pha_max = 1000*np.angle(fit["up95"])
    Amp_dat = data["amp"]/Zr0
    Amp_err = data["amp_err"]/Zr0
    Amp_fit = abs(fit["best"])/Zr0
    Amp_min = abs(fit["lo95"])/Zr0
    Amp_max = abs(fit["up95"])/Zr0
    if draw or save:
        fig, ax = plt.subplots(2, 1, figsize=(6,8))
        for t in ax:
            t.tick_params(labelsize=14)
        # Real-Imag
#        plt.axes(ax[0])
#        plt.errorbar(zn_dat.real, -zn_dat.imag, zn_err.imag, zn_err.real, '.', label='Data')
#        plt.plot(zn_fit.real, -zn_fit.imag, 'r-', label='Fit')
#        plt.fill_between(zn_fit.real, -zn_max.imag, -zn_min.imag, color='0.5', alpha=0.5)
#        plt.xlabel(sym_labels['real'], fontsize=14)
#        plt.ylabel(sym_labels['imag'], fontsize=14)
#        plt.legend(numpoints=1, fontsize=14)
#        plt.xlim([None, 1])
#        plt.ylim([0, None])
#        plt.title(sample_name, fontsize=10)
        # Freq-Phas
        plt.axes(ax[0])
#        NRMS_P = 100*np.sqrt(np.mean((Pha_dat-Pha_fit)**2))/abs(max(Pha_dat)-min(Pha_fit))
        plt.errorbar(f, -Pha_dat, Pha_err, None, '.', label='Data')
        plt.loglog(f, -Pha_fit, 'r-', label='Fitted model')
        ax[0].set_yscale("log", nonposy='clip')
        plt.fill_between(f, -Pha_max, -Pha_min, color='dimgray', alpha=0.3, label='95% HPD')
        plt.xlabel(sym_labels['freq'], fontsize=14)
        plt.ylabel(sym_labels['phas'], fontsize=14)

#        handles, labels = ax[0].get_legend_handles_labels()
        # sort both labels and handles by labels
#        labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: t[0]))
#        ax[0].legend(handles, labels, loc=2, numpoints=1, fontsize=14)

        ax[0].legend(loc=2, numpoints=1, fontsize=12)
        plt.ylim([1,1000])
#        plt.title(sample_name, fontsize=10)

        # Freq-Ampl
        plt.axes(ax[1])
#        NRMS_A = 100*np.sqrt(np.mean((Amp_dat-Amp_fit)**2))/abs(max(Amp_dat)-min(Amp_fit))
        plt.errorbar(f, Amp_dat, Amp_err, None, '.', label='Data')
        plt.semilogx(f, Amp_fit, 'r-', label='Fitted model')
        plt.fill_between(f, Amp_max, Amp_min, color='dimgray', alpha=0.3, label='95% HPD')
        plt.xlabel(sym_labels['freq'], fontsize=14)
        plt.ylabel(sym_labels['ampl'], fontsize=14)

#        handles, labels = ax[1].get_legend_handles_labels()
        # sort both labels and handles by labels
#        labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: t[0]))
#        ax[1].legend(handles, labels, loc=1, numpoints=1, fontsize=14)
        ax[1].legend(loc=1, numpoints=1, fontsize=12)
        plt.ylim([None,1.0])
#        plt.title(sample_name, fontsize=12)
        fig.tight_layout()

    if save:
        save_where = '/Figures/Fit figures/'
        actual_path = str(path.dirname(path.realpath(argv[0]))).replace("\\", "/")
        save_path = actual_path+save_where
        print "\nSaving fit figure in:\n", save_path
        if not path.exists(save_path):
            makedirs(save_path)
        fig.savefig(save_path+'FIT-%s-%s.pdf'%(model,sample_name))
    try:    plt.close(fig)
    except: pass
    if draw:    return fig
    else:       return None

def plot_pymc_histo(M, model, filename):
    from pymc.Matplot import plot
    save_where = '/Histograms/'
    actual_path = str(path.dirname(path.realpath(argv[0]))).replace("\\", "/")
    save_path = actual_path+save_where+"%s/"%filename
    print "\nSaving histograms in:\n", save_path
    if not path.exists(save_path):
        makedirs(save_path)
    # Histogrammes, trace et autocorrélation
    plot(M, path=save_path+'HIS-%s-%s'%(model,filename), verbose=0)
    plt.close("all")

def print_diagn(M, q, r, s):
    return raftery_lewis(M, q, r, s, verbose=0)

def plot_par():
    rc = {u'agg.path.chunksize': 0,
          u'animation.avconv_args': [],
          u'animation.avconv_path': u'avconv',
          u'animation.bitrate': -1,
          u'animation.codec': u'mpeg4',
          u'animation.convert_args': [],
          u'animation.convert_path': u'convert',
          u'animation.ffmpeg_args': [],
          u'animation.ffmpeg_path': u'ffmpeg',
          u'animation.frame_format': u'png',
          u'animation.mencoder_args': [],
          u'animation.mencoder_path': u'mencoder',
          u'animation.writer': u'ffmpeg',
          u'axes.axisbelow': False,
          u'axes.color_cycle': [u'b', u'g', u'r', u'c', u'm', u'y', u'k'],
          u'axes.edgecolor': u'black',
          u'axes.facecolor': u'white',
          u'axes.formatter.limits': [-7, 7],
          u'axes.formatter.use_locale': False,
          u'axes.formatter.use_mathtext': False,
          u'axes.formatter.useoffset': True,
          u'axes.grid': True,
          u'axes.grid.which': u'major',
          u'axes.hold': True,
          u'axes.labelcolor': u'black',
          u'axes.labelsize': 12.0,
          u'axes.labelweight': u'normal',
          u'axes.linewidth': 1.0,
          u'axes.titlesize': 12.0,
          u'axes.titleweight': u'normal',
          u'axes.unicode_minus': True,
          u'axes.xmargin': 0.0,
          u'axes.ymargin': 0.0,
          u'axes3d.grid': True,
          u'backend.qt4': u'PyQt4',
          u'backend.qt5': u'PyQt5',
          u'backend_fallback': True,
          u'contour.negative_linestyle': u'dashed',
          u'docstring.hardcopy': True,
          u'examples.directory': u'',
          u'figure.autolayout': False,
          u'figure.dpi': 72.0,
          u'figure.edgecolor': u'white',
          u'figure.facecolor': u'white',
          u'figure.figsize': [6.0, 4.0],
          u'figure.frameon': True,
          u'figure.max_open_warning': 20,
          u'figure.subplot.bottom': 0.125,
          u'figure.subplot.hspace': 0.2,
          u'figure.subplot.left': 0.125,
          u'figure.subplot.right': 0.9,
          u'figure.subplot.top': 0.9,
          u'figure.subplot.wspace': 0.2,
          u'font.cursive': [u'Apple Chancery',
                            u'Textile',
                            u'Zapf Chancery',
                            u'Sand',
                            u'cursive'],
          u'font.family': [u'sans-serif'],
          u'font.fantasy': [u'Comic Sans MS',
                            u'Chicago',
                            u'Charcoal',
                            u'Impact',
                            u'Western',
                            u'fantasy'],
          u'font.monospace': [u'Bitstream Vera Sans Mono',
                              u'Andale Mono',
                              u'Nimbus Mono L',
                              u'Courier New',
                              u'Courier',
                              u'Fixed',
                              u'Terminal',
                              u'monospace'],
          u'font.sans-serif': [u'Helvetica',
                               u'Bitstream Vera Sans',
                               u'Lucida Grande',
                               u'Verdana',
                               u'Geneva',
                               u'Lucid',
                               u'Arial',
                               u'Avant Garde',
                               u'sans-serif'],
          u'font.serif': [u'Bitstream Vera Serif',
                          u'New Century Schoolbook',
                          u'Century Schoolbook L',
                          u'Utopia',
                          u'ITC Bookman',
                          u'Bookman',
                          u'Nimbus Roman No9 L',
                          u'Times New Roman',
                          u'Times',
                          u'Palatino',
                          u'Charter',
                          u'serif'],
          u'font.size': 14.0,
          u'font.stretch': u'normal',
          u'font.style': u'normal',
          u'font.variant': u'normal',
          u'font.weight': u'medium',
          u'grid.alpha': 0.3,
          u'grid.color': u'black',
          u'grid.linestyle': u':',
          u'grid.linewidth': 1.0,
          u'image.aspect': u'equal',
          u'image.cmap': u'jet',
          u'image.interpolation': u'bilinear',
          u'image.lut': 256,
          u'image.origin': u'upper',
          u'image.resample': False,
          u'interactive': False,
          u'keymap.all_axes': [u'a'],
          u'keymap.back': [u'left', u'c', u'backspace'],
          u'keymap.forward': [u'right', u'v'],
          u'keymap.fullscreen': [u'f', u'ctrl+f'],
          u'keymap.grid': [u'g'],
          u'keymap.home': [u'h', u'r', u'home'],
          u'keymap.pan': [u'p'],
          u'keymap.quit': [u'ctrl+w', u'cmd+w'],
          u'keymap.save': [u's', u'ctrl+s'],
          u'keymap.xscale': [u'k', u'L'],
          u'keymap.yscale': [u'l'],
          u'keymap.zoom': [u'o'],
          u'legend.borderaxespad': 0.5,
          u'legend.borderpad': 0.2,
          u'legend.columnspacing': 2.0,
          u'legend.fancybox': False,
          u'legend.fontsize': 12.0,
          u'legend.framealpha': None,
          u'legend.frameon': True,
          u'legend.handleheight': 0.7,
          u'legend.handlelength': 1.5,
          u'legend.handletextpad': 0.8,
          u'legend.isaxes': True,
          u'legend.labelspacing': 0.2,
          u'legend.loc': u'upper right',
          u'legend.markerscale': 1.0,
          u'legend.numpoints': 1,
          u'legend.scatterpoints': 1,
          u'legend.shadow': False,
          u'lines.antialiased': True,
          u'lines.color': u'blue',
          u'lines.dash_capstyle': u'butt',
          u'lines.dash_joinstyle': u'miter',
          u'lines.linestyle': u'-',
          u'lines.linewidth': 1.0,
          u'lines.marker': u'None',
          u'lines.markeredgewidth': 1.0,
          u'lines.markersize': 6.0,
          u'lines.solid_capstyle': u'projecting',
          u'lines.solid_joinstyle': u'miter',
          u'mathtext.bf': u'serif:bold',
          u'mathtext.cal': u'cursive',
          u'mathtext.default': u'regular',
          u'mathtext.fallback_to_cm': True,
          u'mathtext.fontset': u'stixsans',
          u'mathtext.it': u'serif:italic',
          u'mathtext.rm': u'serif',
          u'mathtext.sf': u'sans',
          u'mathtext.tt': u'monospace',
          u'nbagg.transparent': True,
          u'patch.antialiased': True,
          u'patch.edgecolor': u'black',
          u'patch.facecolor': u'blue',
          u'patch.linewidth': 1.0,
          u'path.effects': [],
          u'path.simplify': True,
          u'path.simplify_threshold': 0.1111111111111111,
          u'path.sketch': None,
          u'path.snap': True,
          u'pdf.compression': 6,
          u'pdf.fonttype': 3,
          u'pdf.inheritcolor': False,
          u'pdf.use14corefonts': False,
          u'pgf.debug': False,
          u'pgf.preamble': [],
          u'pgf.rcfonts': True,
          u'pgf.texsystem': u'xelatex',
          u'plugins.directory': u'.matplotlib_plugins',
          u'polaraxes.grid': True,
          u'ps.distiller.res': 6000,
          u'ps.fonttype': 3,
          u'ps.papersize': u'letter',
          u'ps.useafm': False,
          u'ps.usedistiller': False,
          u'savefig.bbox': u'tight',
          u'savefig.directory': u'~',
          u'savefig.dpi': 200,
          u'savefig.edgecolor': u'white',
          u'savefig.facecolor': u'white',
          u'savefig.format': u'pdf',
          u'savefig.frameon': True,
          u'savefig.jpeg_quality': 95,
          u'savefig.orientation': u'portrait',
          u'savefig.pad_inches': 0.1,
          u'savefig.transparent': False,
          u'svg.fonttype': u'path',
          u'svg.image_inline': True,
          u'svg.image_noscale': False,
          u'text.antialiased': True,
          u'text.color': u'black',
          u'text.dvipnghack': None,
          u'text.hinting': True,
          u'text.hinting_factor': 8,
          u'text.latex.preamble': [],
          u'text.latex.preview': False,
          u'text.latex.unicode': False,
          u'text.usetex': False,
          u'timezone': u'UTC',
          u'tk.window_focus': False,
          u'toolbar': u'toolbar2',
          u'verbose.fileo': u'sys.stdout',
          u'verbose.level': u'silent',
          u'webagg.open_in_browser': True,
          u'webagg.port': 8988,
          u'webagg.port_retries': 50,
          u'xtick.color': u'k',
          u'xtick.direction': u'in',
          u'xtick.labelsize': 12.0,
          u'xtick.major.pad': 4.0,
          u'xtick.major.size': 6.0,
          u'xtick.major.width': 1.0,
          u'xtick.minor.pad': 4.0,
          u'xtick.minor.size': 3.0,
          u'xtick.minor.width': 1.0,
          u'ytick.color': u'k',
          u'ytick.direction': u'in',
          u'ytick.labelsize': 12.0,
          u'ytick.major.pad': 4.0,
          u'ytick.major.size': 6.0,
          u'ytick.major.width': 1.0,
          u'ytick.minor.pad': 4.0,
          u'ytick.minor.size': 3.0,
          u'ytick.minor.width': 1.0}
    return rc