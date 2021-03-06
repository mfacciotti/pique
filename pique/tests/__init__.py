"""
nose tests for pique.
"""
import pique.data
import numpy

def test_init_PiqueData() :
    
    # does the data load?
    D = pique.data.PiqueData( 'data/IP.bam', 'data/WCE.bam' )
    
    # did we get the expected number of contigs?
    assert len( D.data.keys() ) == 3
    
    # are they the ones we were looking for?
    assert D.data.keys().__contains__( 'Chromosome' )
    assert D.data.keys().__contains__( 'PNRC100' )
    assert D.data.keys().__contains__( 'PNRC200' )
    
    # is the track data present?
    for contig in D.data.keys() :
        assert type(D.data[contig]['IP']['forward']) is numpy.ndarray
        assert type(D.data[contig]['IP']['reverse']) is numpy.ndarray
        assert type(D.data[contig]['BG']['forward']) is numpy.ndarray
        assert type(D.data[contig]['BG']['reverse']) is numpy.ndarray

