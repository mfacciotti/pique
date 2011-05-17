#!/usr/bin/env python2.6
"""
"""
import scipy.signal
import numpy
import itertools
import operator
import sys
import warnings

# suppress annoying scypy warnings
warnings.simplefilter("ignore", DeprecationWarning)

class PiqueException( Exception ) :
    pass

def readtrack( filename ) :
    """
    Read a track file, return a numpy array.
    """
    data = []
    for line in open( filename ) :
        if line.__contains__( '\"' ) :
            continue
        data.append( float( line.split()[2] ) )
    if len( data ) == 0 :
        raise PiqueException( 'Empty input file or parsing error : ' + filename )
    return numpy.array( data )

def write_strandless_track( data, filename, track_name ) :
    f = open( filename, 'w' )
    f.write( 'sequence\tstrand\tposition\tvalue\n' )
    for n,i in enumerate( data ) :
        if i != 0 :
            f.write( track_name + '\t.\t' + str(n) + '\t' + str(i) + '\n' )
    f.close()

def readbookmarks( filename ) :
    """
    Read a GGB bookmark file.
    """
    regions = []
    for line in open( filename ) :
        if line.__contains__('>') :
            continue
        if line.__contains__('\tName\tAnnotation') :
            continue
        chromosome,start,stop,strand,name,annotations = line.strip().split('\t')
        start, stop = map( int, (start,stop) )
        annot = {}
        for annotation in annotations.split() :
            key,value = annotation.split(':')
            annot[key] = value
        regions.append( {   'start':start,          \
                            'stop':stop,            \
                            'strand':strand,        \
                            'chromosome':chromosome,\
                            'annotations':annot     } )
    return regions

def writebookmarks( filename, track_name, regions ) :
    """
    Write a GGB bookmark file, where any keys besides 'forward' and
    'reverse' are added to the annotation column.
    """
    f = open( filename, 'w' )
    f.write( '>name: ' + track_name + ' peak bookmarks\n' )
    f.write( 'Chromosome\tStart\tEnd\tStrand\tName\tAnnotation\n' )
    for r in regions :
        f.write(    track_name + '\t'                   \
                    + str(r['forward']['start']) + '\t' \
                    + str(r['reverse']['stop'])  + '\t' \
                    + 'none\tpeak\t'                    )
        keys = r.keys()
        keys.remove('forward')
        keys.remove('reverse')
        for key in keys :
            f.write( str(key) + ':' + str(r[key]) + '\n' )
    f.close()

def findregions( data, N ) :
    """
    Return all the regions of an array that exceed N.
    """
    pos = filter(lambda(a) : a[1] == abs(a[1]), zip( range(len(data)),data-N) )
    if len(pos) == 0 :
        return []
    pos = numpy.array( zip(*pos)[0] )
    regions = []
    for k,g in itertools.groupby( enumerate(pos), lambda(i,x):i-x ) :
        l = map( operator.itemgetter(1),g )
        regions.append( {'start':l[0],'stop':l[-1] } )
    return regions

def mask( data, mask_regions ) :
    """
    Mask regions in an array.
    """
    for region in mask_regions :
        data[ region['start'] : region['stop'] ] = 0
    return data

def filterset( data, alpha, l_thresh ) :
    
    window = scipy.signal.blackman( l_thresh )

    dataf = scipy.signal.detrend( data )
    dataf = scipy.signal.wiener( dataf, mysize=alpha )
    datar = scipy.signal.detrend( data[::-1] )
    datar = scipy.signal.wiener( datar, mysize=alpha )

    dataf = scipy.signal.convolve( dataf, window, mode='full' )
    datar = scipy.signal.convolve( datar, window, mode='full' )

    return ( dataf + datar ) / 2.0

def overlaps( forward, reverse ) :
    envelope = []
    for l in forward :
        for m in reverse :
            if m['start'] < l['stop'] < m['stop'] :
                if l['start'] < m['start'] < l['stop'] :
                    envelope.append( {'forward':l,'reverse':m} )
    return envelope

def sizeselect( regions, too_big, too_small ) :
    for region in regions :
        size = region['stop'] - region['start']
        if size > too_big or size < too_small :
            regions.remove( region )
    return regions

def msg( message ) :
    sys.stderr.write( message + '\n' )
