# Copyright (c) 2016,Vienna University of Technology,
# Department of Geodesy and Geoinformation
# All rights reserved.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL VIENNA UNIVERSITY OF TECHNOLOGY, DEPARTMENT OF
# GEODESY AND GEOINFORMATION BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


"""
Tests for the Equi7Grid().
"""

import numpy as np
import numpy.testing as nptest
from osgeo import osr
import pyproj

from equi7grid.equi7grid import Equi7Grid
from pytileproj.geometry import setup_test_geom_spitzbergen
from pytileproj.geometry import setup_geom_kamchatka


def test_xy2lonlat_doubles():
    """
    Tests xy to lonlat projection using double numbers.
    """
    e7 = Equi7Grid(500)
    x = 5138743.127891
    y = 1307029.157093
    lon_should, lat_should = 15.1, 45.3
    lon, lat = e7.EU.xy2lonlat(x, y)
    nptest.assert_allclose(lon_should, lon)
    nptest.assert_allclose(lat_should, lat)


def test_xy2lonlat_numpy_array():
    """
    Tests xy to lonlat projection using numpy arrays.
    """
    e7 = Equi7Grid(500)
    x = np.array([5138743.127891])
    y = np.array([1307029.157093])
    lon_should, lat_should = 15.1, 45.3
    lon, lat = e7.EU.xy2lonlat(x, y)
    nptest.assert_allclose(lon_should, lon)
    nptest.assert_allclose(lat_should, lat)


def test_lonlat2xy_doubles():
    """
    Tests lonlat to xy projection using double numbers.
    """
    e7 = Equi7Grid(500)
    x_should = 5138743.127891
    y_should = 1307029.157093
    lon, lat = 15.1, 45.3
    sgrid_id, x, y = e7.lonlat2xy(lon, lat)
    assert sgrid_id == 'EU'
    nptest.assert_allclose(x_should, x)
    nptest.assert_allclose(y_should, y)


def test_lonlat2xy_numpy_array():
    """
    Tests lonlat to xy projection using numpy arrays.
    """
    e7 = Equi7Grid(500)
    x_should = np.array([5138743.127891,
                         5138743.127891])
    y_should = np.array([1307029.157093,
                         1307029.157093])
    lon = np.array([15.1, 15.1])
    lat = np.array([45.3, 45.3])
    sgrid_id, x, y = e7.lonlat2xy(lon, lat, 'EU')
    nptest.assert_array_equal(sgrid_id, np.array(['EU', 'EU']))
    nptest.assert_allclose(x_should, x)
    nptest.assert_allclose(y_should, y)


def test_lonlat2xy_numpy_array_no_sgrid():
    """
    Tests lonlat to xy projection using numpy arrays.
    """
    e7 = Equi7Grid(500)
    x_should = np.array([5138743.127891,
                         5138743.127891])
    y_should = np.array([1307029.157093,
                         1307029.157093])
    lon = np.array([15.1, 15.1])
    lat = np.array([45.3, 45.3])
    sgrid_id, x, y = e7.lonlat2xy(lon, lat)
    nptest.assert_array_equal(sgrid_id, np.array(['EU', 'EU']))
    nptest.assert_allclose(x_should, x)
    nptest.assert_allclose(y_should, y)

def test_ij2xy():
    """
    Tests tile indices to xy coordination in the subgrid projection
    """
    e7 = Equi7Grid(500)
    x_should = 3166500
    y_should = 5178000
    tile = e7.EU.tilesys.create_tile(x=3245631, y=5146545)
    x, y = tile.ij2xy(333, 444)
    nptest.assert_allclose(x_should, x)
    nptest.assert_allclose(y_should, y)


def test_xy2ij():
    """
    Tests xy to tile array indices.
    """
    e7 = Equi7Grid(500)
    column_should = 333
    row_should = 444
    tile = e7.EU.tilesys.create_tile(x=3245631, y=5146545)
    column, row = tile.xy2ij(3166500, 5178000)
    nptest.assert_allclose(column_should, column)
    nptest.assert_allclose(row_should, row)


def test_proj4_reprojection_accuracy():
    """
    Tests the proj4 reproject accuracy by forward and backward reprojection.
    """
    geo_sr = osr.SpatialReference()
    geo_sr.SetWellKnownGeogCS("EPSG:4326")
    # Africa
    aeqd_proj = ('PROJCS["Azimuthal_Equidistant",'
                 'GEOGCS["GCS_WGS_1984",'
                 'DATUM["D_WGS_1984",'
                 'SPHEROID["WGS_1984",6378137.0,298.257223563]],'
                 'PRIMEM["Greenwich",0.0],'
                 'UNIT["Degree",0.0174532925199433]],'
                 'PROJECTION["Azimuthal_Equidistant"],'
                 'PARAMETER["false_easting",5621452.01998],'
                 'PARAMETER["false_northing",5990638.42298],'
                 'PARAMETER["longitude_of_center",21.5],'
                 'PARAMETER["latitude_of_center",8.5],UNIT["Meter",1.0]]')
    aeqd_sr = osr.SpatialReference()
    aeqd_sr.ImportFromWkt(aeqd_proj)
    p_grid = pyproj.Proj(aeqd_sr.ExportToProj4())
    p_geo = pyproj.Proj(geo_sr.ExportToProj4())

    # test locations in Africa
    points = [(-31.627336, 30.306273),
              (-14.589038, -43.880131),
              (79.423313, -35.261658),
              (23.456413, 10.457987)]

    for i, pt in enumerate(points):
        # from lat/lon to aeqd
        aeqd_x, aeqd_y = pyproj.transform(p_geo, p_grid, pt[0], pt[1])
        # from aeqd to lat/lon
        lon, lat = pyproj.transform(p_grid, p_geo, aeqd_x, aeqd_y)
        # print info

        print("testing location {}:".format(i))
        _info = "   ({:f},{:f}) -> ({:f},{:f}) -> ({:f},{:f})"
        print(_info.format(pt[0], pt[1], aeqd_x, aeqd_y, lon, lat))
        print("    difference: ({:f},{:f})".format(lon - pt[0], lat - pt[1]))
        nptest.assert_allclose(pt[0], lon)
        nptest.assert_allclose(pt[1], lat)


def test_decode_tilename():
    """
    Tests the decoding of tilenames.
    """
    e7_500 = Equi7Grid(500)
    e7_10 = Equi7Grid(10)

    assert e7_500.EU.tilesys.decode_tilename('EU500M_E042N006T6') == \
           ('EU', 500, 600000, 4200000, 600000, 'T6')
    assert e7_10.OC.tilesys.decode_tilename('OC010M_E085N091T1') == \
           ('OC', 10, 100000, 8500000, 9100000, 'T1')

    assert e7_500.EU.tilesys.decode_tilename('E042N006T6') == \
           ('EU', 500, 600000, 4200000, 600000, 'T6')
    assert e7_10.OC.tilesys.decode_tilename('E085N091T1') == \
           ('OC', 10, 100000, 8500000, 9100000, 'T1')

    with nptest.assert_raises(ValueError) as excinfo:
        e7_10.EU.tilesys.decode_tilename('E042N006T6')
    assert str(excinfo.exception).startswith('"tilename" is not properly defined!')


def test_find_overlapping_tilenames():
    """
    Tests search for tiles which share the same extent_m but
    with different resolution and tilecode.
    """
    e7_500 = Equi7Grid(500)
    e7_10 = Equi7Grid(10)

    tiles1_should = ['EU025M_E042N006T3', 'EU025M_E042N009T3',
                     'EU025M_E045N006T3', 'EU025M_E045N009T3']
    tiles1 = e7_500.EU.tilesys.find_overlapping_tilenames('EU500M_E042N006T6',
                                                          target_sampling=25)
    assert sorted(tiles1) == sorted(tiles1_should)

    tiles2_should =['E042N006T3', 'E042N009T3', 'E045N006T3', 'E045N009T3']
    tiles2 = e7_500.EU.tilesys.find_overlapping_tilenames('E042N006T6',
                                                        target_tiletype='T3')
    assert sorted(tiles2) == sorted(tiles2_should)

    tiles3_should =['EU500M_E042N012T6']

    tiles3 = e7_10.EU.tilesys.find_overlapping_tilenames('E044N015T1',
                                                         target_sampling=500)
    assert sorted(tiles3) == sorted(tiles3_should)

    tiles4_should =['E039N009T3']
    tiles4 = e7_10.EU.tilesys.find_overlapping_tilenames('E041N011T1',
                                                        target_tiletype='T3')
    assert sorted(tiles4) == sorted(tiles4_should)


def test_search_tiles_lon_lat_extent():
    """
    Tests searching for tiles with input of lon lat extent
    """
    e7 = Equi7Grid(500)
    tiles = e7.search_tiles_in_roi(extent=[0, 30, 10, 40],
                                   coverland=True)

    tiles_all = e7.search_tiles_in_roi(extent=[-179.9, -89.9, 179.9, 89.9],
                                       coverland=True)
    desired_tiles = ['EU500M_E036N006T6', 'EU500M_E042N000T6',
                     'EU500M_E042N006T6', 'AF500M_E030N084T6',
                     'AF500M_E030N090T6', 'AF500M_E036N084T6',
                     'AF500M_E036N090T6', 'AF500M_E042N084T6',
                     'AF500M_E042N090T6']

    assert len(tiles_all) == 832
    assert sorted(tiles) == sorted(desired_tiles)


def test_search_tiles_lon_lat_extent_by_points():
    """
    Tests searching for tiles with input of lon lat points
    """
    e7 = Equi7Grid(500)
    tiles = e7.search_tiles_in_roi(
        extent=[(10, 40), (5, 50), (-90.9, -1.2), (-175.2, 66)],
        coverland=True)

    desired_tiles = ['EU500M_E042N006T6', 'EU500M_E042N018T6',
                     'AS500M_E072N090T6', 'SA500M_E036N066T6']

    assert sorted(tiles) == sorted(desired_tiles)


def test_search_tiles_spitzbergen():
    """
    Tests the tile searching over Spitzbergen in the polar zone; ROI defined
    by a 4-corner polygon over high latitudes (is much curved on the globe).
    """

    grid = Equi7Grid(500)

    spitzbergen_geom = setup_test_geom_spitzbergen()
    spitzbergen_geom_tiles = sorted(['EU500M_E054N042T6', 'EU500M_E054N048T6',
                                     'EU500M_E060N042T6', 'EU500M_E060N048T6'])
    tiles = sorted(grid.search_tiles_in_roi(spitzbergen_geom,
                                            coverland=False))

    assert sorted(tiles) == sorted(spitzbergen_geom_tiles)

    spitzbergen_geom_tiles = sorted(['EU500M_E054N042T6', 'EU500M_E054N048T6',
                                     'EU500M_E060N048T6'])
    tiles = sorted(grid.search_tiles_in_roi(spitzbergen_geom,
                                            coverland=True))

    assert sorted(tiles) == sorted(spitzbergen_geom_tiles)


def test_search_tiles_kamchatka():
    """
    Tests the tile searching over Kamchatka in far east Sibiria;

    This test is especially nice, as it contains also a tile that covers both,
    the ROI and the continental zone, but the intersection of the tile and
    the ROI is outside of the zone.

    Furthermore, it also covers zones that consist of a multipolygon, as it
    is located at the 180deg/dateline.
    """

    grid = Equi7Grid(500)

    kamchatka_geom = setup_geom_kamchatka()
    kamchatka_geom_tiles = sorted(['AS500M_E072N078T6', 'AS500M_E078N078T6',
                                   'AS500M_E078N084T6', 'NA500M_E036N078T6',
                                   'NA500M_E036N084T6', 'NA500M_E042N078T6',
                                   'NA500M_E042N084T6'])
    tiles = sorted(grid.search_tiles_in_roi(kamchatka_geom, coverland=False))

    assert sorted(tiles) == sorted(kamchatka_geom_tiles)


def test_identify_tiles_overlapping_xybbox():
    """
    Tests identification of tiles covering a bounding box
    given in equi7 coordinats
    """

    e7_500 = Equi7Grid(500)
    e7_10 = Equi7Grid(10)

    tiles1_should = ['EU500M_E048N006T6', 'EU500M_E054N006T6',
                     'EU500M_E060N006T6', 'EU500M_E048N012T6',
                     'EU500M_E054N012T6', 'EU500M_E060N012T6']

    tiles2_should = ['EU010M_E051N011T1', 'EU010M_E052N011T1',
                     'EU010M_E051N012T1', 'EU010M_E052N012T1']

    tiles1 = e7_500.EU.tilesys.identify_tiles_overlapping_xybbox(
                                         [5138743, 1111111, 6200015, 1534657])

    tiles2 = e7_10.EU.tilesys.identify_tiles_overlapping_xybbox(
                                         [5138743, 1111111, 5299999, 1234657])

    assert sorted(tiles1) == sorted(tiles1_should)
    assert sorted(tiles2) == sorted(tiles2_should)


def test_get_covering_tiles():
    """
    Tests the search for co-locating tiles of other type.
    """

    e7g_40 = Equi7Grid(40)
    e7g_10 = Equi7Grid(10)

    fine_tiles = ['EU010M_E005N058T1', 'EU010M_E005N059T1',
                  'EU010M_E005N060T1', 'EU010M_E005N061T1']

    target_tiletype = e7g_40.get_tiletype()
    target_sampling = e7g_40.core.sampling

    # invoke the results as tile name in short form
    coarse_tiles_shortform = e7g_10.EU.tilesys.get_covering_tiles(fine_tiles,
                                             target_tiletype=target_tiletype)

    # invoke the results as tile name in long form
    coarse_tiles_longform = e7g_10.EU.tilesys.get_covering_tiles(fine_tiles,
                                           target_sampling=target_sampling)

    assert sorted(coarse_tiles_shortform) == ['E003N057T3', 'E003N060T3']
    assert sorted(coarse_tiles_longform) == ['EU040M_E003N057T3', 'EU040M_E003N060T3']