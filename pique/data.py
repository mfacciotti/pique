#!/usr/bin/env python
"""
Data representations
"""
import numpy
import fileIO
import processing

class PiqueDataException( Exception ) :
    pass

class PiqueData :
    """
    Container class for managing Pique data.
    """
    def __init__( self ) :
        self.data = {}
        self.filtered = {}    
    
    def __init__( self, IP_file, BG_file, map_file=None ) :
        self.data       = {}
        self.filtered   = {}
        self.load_data( IP_file, BG_file )
        
        # load genome map file, if provided
        if map_file :
            
            gff = fileIO.loadGFF( map_file )
            
            region_contigs = []
            for region in gff['regions'] :
                contig = region['contig']
                if not self.data.has_key( contig ) :
                    raise PiqueDataException( 'Map file contains unknown contig : ' + contig )
                if not region_contigs.__contains__( contig ) :
                    region_contigs.append( contig )

            # remove default regions from mapped contigs
            for contig in region_contigs :
                self.del_analysis_region( contig, 0, self.data[contig]['length'] )
        
            for region in gff['regions'] :
                contig = region['contig']
                start  = region['start']
                stop   = region['stop']
                self.add_analysis_region( contig, start, stop )
            
            # add masks
            for mask in gff['masks'] :
                contig = mask['contig']
                start  = mask['start']
                stop   = mask['stop']
                self.add_mask( contig, start, stop )

    def add_contig( self,   contig_name,    \
                            IP_forward,     \
                            IP_reverse,     \
                            BG_forward,     \
                            BG_reverse      ) :
        
        l = map(len, [IP_forward, IP_reverse, BG_forward, BG_reverse ] )
        if not all( x == l[0] for x in l ) :
            raise PiqueDataException( 'Track have different lengths.' )
        
        IP = { 'forward' : IP_forward, 'reverse' : IP_reverse }
        BG = { 'forward' : BG_forward, 'reverse' : BG_reverse }
        
        self.data[ contig_name ] = { 'IP' : IP, 'BG' : BG }
        
        # create a default analysis region spanning the whole contig
        length = len( IP_forward )
        region = { 'start' : 0, 'stop' : length }
        self.data[ contig_name ][ 'length' ]  = length
        self.data[ contig_name ][ 'regions' ] = [ region ]
        
        # create an empty mask list
        self.data[ contig_name ][ 'masks' ] = []

    def load_data( self, IP_file, BG_file ) :
        """
        Digest and load data from BAM files containing alignments of
        IP and background reads.
        
        BAM files must be prepared in such a way that the contig names
        are identical, and each IP track must be identical in length
        to its corresponding background contig.
        """
        
        IP_tracks = fileIO.loadBAM( IP_file )
        BG_tracks = fileIO.loadBAM( BG_file )
        
        IP_contigs = IP_tracks.keys()
        BG_contigs = BG_tracks.keys()
        
        IP_contigs.sort()
        BG_contigs.sort()
        
        if not len(IP_contigs) == len(BG_contigs) :
            raise PiqueDataException( 'BG and IP have different number of contigs.' )
        
        if not all( map( lambda x : x[0] == x[1], zip(IP_contigs,BG_contigs) ) ) :
            raise PiqueDataException( 'BG and IP contig names do not match.',   \
                                    { 'IP' : IP_contigs, 'BG' : BG_contigs } )
        
        for contig in IP_contigs :
            IP_forward = IP_tracks[contig]['forward']
            IP_reverse = IP_tracks[contig]['reverse']
            BG_forward = BG_tracks[contig]['forward']
            BG_reverse = BG_tracks[contig]['reverse']
            
            self.add_contig( contig,    IP_forward, \
                                        IP_reverse, \
                                        BG_forward, \
                                        BG_reverse  )
    
    def del_analysis_region( self, contig, start, stop ) :
        """
        Remove an alaysis region from a contig.
        """
        region = { 'start' : start, 'stop' : stop }
        
        if not self.data[contig]['regions'].__contains__( region ) :
            raise PiqueDataException( 'Analysis region does not exist.', region )
        else :
            self.data[contig]['regions'].remove( region )
        
    def add_analysis_region( self, contig, start, stop ) :
        """
        Add an analysis region to a contig. Overlapping regions are
        not allowed.
        """
        for region in self.data[contig]['regions'] :
            if region['start'] < start and region['stop'] > start   \
                or region['start'] < stop and region['stop'] > stop :
                raise PiqueDataException( 'Overlapping analysis regions are not allowed.' )
            
        if start < 0 or start > self.data[contig]['length'] :
            raise PiqueDataException( 'Analysis region start coordinate out of bounds.' )

        if stop < 0 or stop > self.data[contig]['length'] :
            raise PiqueDataException( 'Analysis region stop coordinate out of bounds.' )
        
        if start > stop :
            raise PiqueDataException( 'Analysis region orientation is reversed.' )

        self.data[contig]['regions'].append( { 'start' : int(start), 'stop' : int(stop) } )

    def add_mask( self, contig, start, stop ) :
        """
        Add a mask to a contig. Overlapping masks are not allowed.
        """
        for mask in self.data[contig]['masks'] :
            if mask['start'] < start and mask['stop'] > start   \
                or mask['start'] < stop and mask['stop'] > stop :
                raise PiqueDataException( 'Overlapping masks are not allowed.' )
            
        if start < 0 or start > self.data[contig]['length'] :
            raise PiqueDataException( 'Mask start coordinate out of bounds.' )

        if stop < 0 or stop > self.data[contig]['length'] :
            raise PiqueDataException( 'Mask stop coordinate out of bounds.' )
        
        if start > stop :
            raise PiqueDataException( 'Mask orientation is reversed.' )

        self.data[contig]['masks'].append( { 'start' : int(start), 'stop' : int(stop) } )

