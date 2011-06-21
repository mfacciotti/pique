#!/usr/bin/env python
"""
Generate coverage tracks from a BAM file.
"""
import pysam
import numpy

def loadBAM( file ) :
    """
    Read eeach contig in a BAM file and return a dictionary of tracks.
    Each track contains scalar length, and two vectors representing
    the forward and everse coverage across the contig.
    """
    samfile = pysam.Samfile( file, 'rb' )
    tracks = {}

    # loop over the congigs and build forward and reverse coverage
    # tracks for them
    for n,name in enumerate(samfile.references) :
        
        length = samfile.lengths[n]
        tracks[name] = {    'length'  : length,                 \
                            'forward' : numpy.zeros(length),    \
                            'reverse' : numpy.zeros(length), }
        
        for pileupcolumn in samfile.pileup( name, 0, length) :
            
            fn,rn = 0,0
            
            for pileupread in pileupcolumn.pileups :
                
                if pileupread.alignment.is_reverse :
                    rn = rn + 1
                else :
                    fn = fn + 1
                
            tracks[name]['forward'][pileupcolumn.pos] = fn
            tracks[name]['reverse'][pileupcolumn.pos] = rn
            
    samfile.close()
    
    return tracks
