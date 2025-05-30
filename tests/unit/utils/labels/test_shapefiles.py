import os
import shutil
import tempfile

import requests

from kili.use_cases.label.process_shapefiles import get_json_response_from_shapefiles


def get_shapefile_from_gcs(filename):
    base_url = "https://storage.googleapis.com/label-public-staging/cypress-tests/fixtures/satellite/shapefiles"
    temp_dir = tempfile.mkdtemp()
    local_path = os.path.join(temp_dir, f"{filename}.shp")

    url = f"{base_url}/{filename}.shp"
    response = requests.get(url)
    with open(local_path, "wb") as f:
        f.write(response.content)

    return local_path, temp_dir


def is_almost_equal(a, b, tolerance=1e-14):
    """Due to different versions of pyproj, the coordinates of the points may differ slightly.

    This function checks if two coordinates are almost equal within a given tolerance.
    """
    return abs(a - b) <= tolerance


def create_mock_json_interface(job_name, tool_type):
    """Create a mock JSON interface for testing purposes."""
    return {
        "jobs": {
            job_name: {
                "tools": [tool_type],
                "content": {"categories": {"CATEGORY1": {"name": "Category1", "color": "#FF0000"}}},
            }
        }
    }


def test_point_shapefile():
    shapefile_path, temp_dir = get_shapefile_from_gcs("points")
    job_name = "points_job"
    category_name = "point_category"

    # Create mock JSON interface with a marker tool
    json_interface = create_mock_json_interface(job_name, "marker")

    response = get_json_response_from_shapefiles(
        shapefile_paths=[shapefile_path],
        job_names=[job_name],
        category_names=[category_name],
        json_interface=json_interface,
    )

    assert job_name in response
    assert "annotations" in response[job_name]

    annotations = response[job_name]["annotations"]
    assert len(annotations) == 3

    expected_coordinates = [
        {"x": 9.429123117729949, "y": 54.68002984132896},
        {"x": 9.772235200599381, "y": 54.68970515271516},
        {"x": 9.451439350762108, "y": 54.318792605636354},
    ]

    for index, annotation in enumerate(annotations):
        assert annotation["type"] == "marker"
        assert "point" in annotation

        assert is_almost_equal(annotation["point"]["x"], expected_coordinates[index]["x"])
        assert is_almost_equal(annotation["point"]["y"], expected_coordinates[index]["y"])

        assert "categories" in annotation
        assert len(annotation["categories"]) == 1
        assert annotation["categories"][0]["name"] == category_name

    shutil.rmtree(temp_dir)


def test_line_shapefile():
    shapefile_path, temp_dir = get_shapefile_from_gcs("lines")
    job_name = "lines_job"
    category_name = "line_category"

    # Create mock JSON interface with a polyline tool
    json_interface = create_mock_json_interface(job_name, "polyline")

    response = get_json_response_from_shapefiles(
        shapefile_paths=[shapefile_path],
        job_names=[job_name],
        category_names=[category_name],
        json_interface=json_interface,
    )

    assert job_name in response
    assert "annotations" in response[job_name]

    annotations = response[job_name]["annotations"]
    assert len(annotations) == 2

    expected_coordinates = [
        [
            {"x": 9.254598688594093, "y": 54.8539201125262},
            {"x": 9.254598688594093, "y": 54.85101839240259},
            {"x": 9.259639164462506, "y": 54.84811646354571},
            {"x": 9.262159402396708, "y": 54.845214325948014},
            {"x": 9.269720116199325, "y": 54.84231197960192},
            {"x": 9.27728083000194, "y": 54.83795806866298},
            {"x": 9.284841543804559, "y": 54.83360368799757},
            {"x": 9.289882019672968, "y": 54.82924883758018},
            {"x": 9.297442733475586, "y": 54.82344163958757},
            {"x": 9.3050034472782, "y": 54.8176336063745},
            {"x": 9.307523685212404, "y": 54.81472927654139},
            {"x": 9.317604636949227, "y": 54.808919990384325},
            {"x": 9.317604636949227, "y": 54.806015034045245},
            {"x": 9.322645112817636, "y": 54.80165720793972},
            {"x": 9.327685588686048, "y": 54.795846042111876},
            {"x": 9.330205826620254, "y": 54.79148711944261},
            {"x": 9.332726064554459, "y": 54.78858090988784},
            {"x": 9.332726064554459, "y": 54.78567449143741},
            {"x": 9.335246302488663, "y": 54.782767864083745},
            {"x": 9.337766540422871, "y": 54.779861027819365},
            {"x": 9.337766540422871, "y": 54.77695398263668},
            {"x": 9.340286778357076, "y": 54.77259302312443},
            {"x": 9.34280701629128, "y": 54.768231593503714},
            {"x": 9.345327254225486, "y": 54.76532371257264},
            {"x": 9.347847492159689, "y": 54.75950732383523},
            {"x": 9.350367730093895, "y": 54.75659881601385},
            {"x": 9.352887968028101, "y": 54.753690099213976},
            {"x": 9.355408205962307, "y": 54.75078117342812},
            {"x": 9.360448681830716, "y": 54.747872038648744},
        ],
        [
            {"x": 9.69312008914582, "y": 54.23407519827612},
            {"x": 9.69312008914582, "y": 54.23996684410168},
            {"x": 9.698160565014232, "y": 54.244385026482774},
            {"x": 9.700680802948435, "y": 54.248802735758346},
            {"x": 9.705721278816847, "y": 54.253219971952795},
            {"x": 9.710761754685256, "y": 54.25763673509049},
            {"x": 9.715802230553667, "y": 54.262053025195925},
            {"x": 9.720842706422076, "y": 54.26794067621736},
            {"x": 9.733443896093105, "y": 54.279713455783224},
            {"x": 9.743524847829923, "y": 54.29148287243299},
            {"x": 9.756126037500952, "y": 54.301778353724266},
            {"x": 9.761166513369362, "y": 54.30913069295533},
            {"x": 9.773767703040386, "y": 54.319421761752565},
            {"x": 9.786368892711415, "y": 54.329710257017844},
            {"x": 9.798970082382441, "y": 54.33852691916026},
            {"x": 9.809051034119262, "y": 54.34734169097022},
            {"x": 9.81661174792188, "y": 54.354685890283136},
            {"x": 9.82165222379029, "y": 54.35615457264444},
            {"x": 9.826692699658699, "y": 54.36202877711568},
            {"x": 9.83677365139552, "y": 54.36937035158181},
            {"x": 9.839293889329728, "y": 54.372306613931215},
            {"x": 9.844334365198137, "y": 54.37671061379559},
            {"x": 9.846854603132343, "y": 54.37964635127597},
            {"x": 9.849374841066547, "y": 54.38258187882158},
            {"x": 9.851895079000752, "y": 54.385517196439665},
            {"x": 9.85441531693496, "y": 54.38845230413754},
            {"x": 9.856935554869166, "y": 54.39138720192253},
        ],
    ]

    for index, annotation in enumerate(annotations):
        assert annotation["type"] == "polyline"
        assert "polyline" in annotation

        for point_index, point in enumerate(annotation["polyline"]):
            assert is_almost_equal(point["x"], expected_coordinates[index][point_index]["x"])
            assert is_almost_equal(point["y"], expected_coordinates[index][point_index]["y"])

        assert "categories" in annotation
        assert len(annotation["categories"]) == 1
        assert annotation["categories"][0]["name"] == category_name

    shutil.rmtree(temp_dir)


def test_polygon_simple_shapefile():
    shapefile_path, temp_dir = get_shapefile_from_gcs("polygons-simple")
    job_name = "polygons_job"
    category_name = "polygon_category"

    # Create mock JSON interface with a semantic tool
    json_interface = create_mock_json_interface(job_name, "semantic")

    response = get_json_response_from_shapefiles(
        shapefile_paths=[shapefile_path],
        job_names=[job_name],
        category_names=[category_name],
        json_interface=json_interface,
    )

    assert job_name in response
    assert "annotations" in response[job_name]

    annotations = response[job_name]["annotations"]
    assert len(annotations) == 2

    expected_polygons = [
        [
            {"x": 9.504102244080421, "y": 54.51885219373373},
            {"x": 9.50914271994883, "y": 54.52031500197589},
            {"x": 9.514183195817239, "y": 54.52324046127452},
            {"x": 9.519223671685653, "y": 54.52470311233283},
            {"x": 9.526784385488268, "y": 54.52762825727203},
            {"x": 9.534345099290885, "y": 54.5290907511548},
            {"x": 9.539385575159296, "y": 54.530553192647545},
            {"x": 9.54694628896191, "y": 54.53347791846672},
            {"x": 9.557027240698734, "y": 54.53494020279502},
            {"x": 9.564587954501349, "y": 54.53640243473699},
            {"x": 9.58474985797499, "y": 54.537864614293596},
            {"x": 9.602391523514429, "y": 54.53932674146574},
            {"x": 9.607431999382838, "y": 54.53932674146574},
            {"x": 9.614992713185453, "y": 54.53932674146574},
            {"x": 9.625073664922276, "y": 54.53932674146574},
            {"x": 9.6376748545933, "y": 54.53640243473699},
            {"x": 9.647755806330125, "y": 54.53494020279502},
            {"x": 9.652796282198533, "y": 54.53347791846672},
            {"x": 9.657836758066946, "y": 54.532015581751224},
            {"x": 9.662877233935355, "y": 54.530553192647545},
            {"x": 9.667917709803763, "y": 54.5290907511548},
            {"x": 9.672958185672178, "y": 54.52762825727203},
            {"x": 9.677998661540586, "y": 54.52470311233283},
            {"x": 9.683039137408995, "y": 54.52031500197589},
            {"x": 9.68807961327741, "y": 54.51592642005906},
            {"x": 9.69312008914582, "y": 54.51300043679112},
            {"x": 9.698160565014232, "y": 54.51007424392256},
            {"x": 9.700680802948435, "y": 54.50714784144595},
            {"x": 9.705721278816847, "y": 54.50422122935397},
            {"x": 9.70824151675105, "y": 54.5012944076392},
            {"x": 9.713281992619462, "y": 54.49836737629428},
            {"x": 9.713281992619462, "y": 54.49544013531181},
            {"x": 9.715802230553667, "y": 54.49251268468445},
            {"x": 9.718322468487873, "y": 54.48958502440482},
            {"x": 9.718322468487873, "y": 54.48665715446552},
            {"x": 9.720842706422076, "y": 54.48372907485923},
            {"x": 9.723362944356282, "y": 54.48080078557854},
            {"x": 9.723362944356282, "y": 54.4778722866161},
            {"x": 9.723362944356282, "y": 54.474943577964545},
            {"x": 9.723362944356282, "y": 54.47201465961652},
            {"x": 9.723362944356282, "y": 54.469085531564694},
            {"x": 9.723362944356282, "y": 54.46615619380165},
            {"x": 9.718322468487873, "y": 54.46322664632007},
            {"x": 9.715802230553667, "y": 54.46029688911259},
            {"x": 9.710761754685256, "y": 54.458831931859336},
            {"x": 9.70824151675105, "y": 54.45590186004921},
            {"x": 9.703201040882641, "y": 54.454436745490504},
            {"x": 9.700680802948435, "y": 54.4515063590612},
            {"x": 9.695640327080024, "y": 54.450041087188765},
            {"x": 9.690599851211612, "y": 54.447110386123754},
            {"x": 9.685559375343203, "y": 54.44564495692932},
            {"x": 9.680518899474793, "y": 54.444179475292394},
            {"x": 9.67547842360638, "y": 54.44271394121207},
            {"x": 9.670437947737971, "y": 54.44271394121207},
            {"x": 9.66539747186956, "y": 54.44271394121207},
            {"x": 9.660356996001148, "y": 54.44271394121207},
            {"x": 9.65531652013274, "y": 54.44271394121207},
            {"x": 9.650276044264329, "y": 54.44271394121207},
            {"x": 9.645235568395915, "y": 54.44271394121207},
            {"x": 9.640195092527508, "y": 54.44271394121207},
            {"x": 9.635154616659097, "y": 54.444179475292394},
            {"x": 9.630114140790685, "y": 54.444179475292394},
            {"x": 9.625073664922276, "y": 54.44564495692932},
            {"x": 9.620033189053865, "y": 54.447110386123754},
            {"x": 9.614992713185453, "y": 54.447110386123754},
        ],
        [
            {"x": 10.05351411373718, "y": 54.316481719000855},
            {"x": 10.063595065473999, "y": 54.316481719000855},
            {"x": 10.068635541342411, "y": 54.316481719000855},
            {"x": 10.076196255145028, "y": 54.31501161884114},
            {"x": 10.081236731013437, "y": 54.31354146615765},
            {"x": 10.088797444816052, "y": 54.31207126094944},
            {"x": 10.096358158618667, "y": 54.31060100321563},
            {"x": 10.103918872421284, "y": 54.30913069295533},
            {"x": 10.119040300026516, "y": 54.307660330167586},
            {"x": 10.136681965565955, "y": 54.3061899148515},
            {"x": 10.14928315523698, "y": 54.30324892663077},
            {"x": 10.164404582842211, "y": 54.301778353724266},
            {"x": 10.174485534579034, "y": 54.29883705031446},
            {"x": 10.189606962184266, "y": 54.297366319809335},
            {"x": 10.204728389789498, "y": 54.29442470119416},
            {"x": 10.217329579460522, "y": 54.29148287243299},
            {"x": 10.224890293263142, "y": 54.29001187924538},
            {"x": 10.22993076913155, "y": 54.28854083351855},
            {"x": 10.234971244999961, "y": 54.2870697352516},
            {"x": 10.237491482934166, "y": 54.2841273810937},
            {"x": 10.232451007065757, "y": 54.28118481676442},
            {"x": 10.227410531197346, "y": 54.27824204225648},
            {"x": 10.222370055328936, "y": 54.275299057562655},
            {"x": 10.214809341526319, "y": 54.27088418640758},
            {"x": 10.194647438052675, "y": 54.262053025195925},
            {"x": 10.184566486315855, "y": 54.25616453327161},
            {"x": 10.174485534579034, "y": 54.25174761245104},
            {"x": 10.156843869039594, "y": 54.24291235159091},
            {"x": 10.13920220350016, "y": 54.23407519827612},
            {"x": 10.129121251763339, "y": 54.229655911887264},
            {"x": 10.124080775894928, "y": 54.22670945808131},
            {"x": 10.119040300026516, "y": 54.22376279396289},
            {"x": 10.113999824158107, "y": 54.22228938303425},
            {"x": 10.108959348289698, "y": 54.22081591952478},
            {"x": 10.103918872421284, "y": 54.219342403433615},
            {"x": 10.098878396552875, "y": 54.217868834759784},
        ],
    ]

    for index, annotation in enumerate(annotations):
        assert annotation["type"] == "semantic"
        assert "boundingPoly" in annotation
        assert "mid" in annotation

        assert len(annotation["boundingPoly"]) == 1

        assert "normalizedVertices" in annotation["boundingPoly"][0]

        outer_ring = annotation["boundingPoly"][0]["normalizedVertices"]
        assert len(outer_ring) == len(expected_polygons[index])
        for point_index, point in enumerate(outer_ring):
            assert is_almost_equal(point["x"], expected_polygons[index][point_index]["x"])
            assert is_almost_equal(point["y"], expected_polygons[index][point_index]["y"])

        assert "categories" in annotation
        assert len(annotation["categories"]) == 1
        assert annotation["categories"][0]["name"] == category_name

    shutil.rmtree(temp_dir)


def test_polygon_multipart_with_holes_shapefile():
    shapefile_path, temp_dir = get_shapefile_from_gcs("polygons-multipart-with-holes-epsg-3857")
    job_name = "multipart_polygons_job"
    category_name = "multipart_polygon_category"
    from_epsg = 3857

    # Create mock JSON interface with a semantic tool
    json_interface = create_mock_json_interface(job_name, "semantic")

    response = get_json_response_from_shapefiles(
        shapefile_paths=[shapefile_path],
        job_names=[job_name],
        category_names=[category_name],
        json_interface=json_interface,
        from_epsgs=[from_epsg],
    )

    assert job_name in response
    assert "annotations" in response[job_name]

    annotations = response[job_name]["annotations"]

    # We expect 3 annotations in total:
    # 1. First polygon (single part with one hole)
    # 2. Second polygon first part (with one hole)
    # 3. Second polygon second part (without hole)
    assert len(annotations) == 3

    for annotation in annotations:
        assert annotation["type"] == "semantic"
        assert "boundingPoly" in annotation
        assert "mid" in annotation
        assert "categories" in annotation
        assert len(annotation["categories"]) == 1
        assert annotation["categories"][0]["name"] == category_name

    polygons_with_hole = [a for a in annotations if len(a["boundingPoly"]) == 2]
    polygons_without_hole = [a for a in annotations if len(a["boundingPoly"]) == 1]

    assert len(polygons_with_hole) == 2, "Expected 2 polygons with holes"
    assert len(polygons_without_hole) == 1, "Expected 1 polygon without hole"

    # The two parts of the second polygon should have the same mid (multipart polygon)
    mids = [a["mid"] for a in annotations]
    unique_mids = set(mids)

    # We expect to have two unique mids (one for each multipart polygon)
    assert len(unique_mids) == 2, "Expected 2 unique mids (one for each multipart polygon)"

    first_polygon_mid = None
    second_polygon_mid = None

    for mid in unique_mids:
        count = mids.count(mid)
        if count == 1:
            first_polygon_mid = mid
        elif count == 2:
            second_polygon_mid = mid

    first_polygon = next(a for a in annotations if a["mid"] == first_polygon_mid)
    assert (
        len(first_polygon["boundingPoly"]) == 2
    ), "First polygon should have an exterior and a hole"

    expected_first_polygon_exterior = [
        {"x": 10.066352118869245, "y": 54.30541031990684},
        {"x": 10.066352118869245, "y": 54.30374459928154},
        {"x": 10.067303725951296, "y": 54.302078811251825},
        {"x": 10.069206940115404, "y": 54.299857655691945},
        {"x": 10.071110154279511, "y": 54.29763638029652},
        {"x": 10.073964975525673, "y": 54.29597034510601},
        {"x": 10.077771403853886, "y": 54.29263807249193},
        {"x": 10.081577832182099, "y": 54.289860972662524},
        {"x": 10.087287474674419, "y": 54.28652820567689},
        {"x": 10.09014229592058, "y": 54.284861721057666},
        {"x": 10.100609973823166, "y": 54.278750700633786},
        {"x": 10.106319616315487, "y": 54.27541703469998},
        {"x": 10.112980865889861, "y": 54.27097172724174},
        {"x": 10.116787294218074, "y": 54.26930461332397},
        {"x": 10.122496936710395, "y": 54.26652594027893},
        {"x": 10.130109793366822, "y": 54.26263548332326},
        {"x": 10.13772265002325, "y": 54.25985636070905},
        {"x": 10.139625864187357, "y": 54.25930051370671},
        {"x": 10.140577471269408, "y": 54.258188797222125},
        {"x": 10.13581943585914, "y": 54.257077050764025},
        {"x": 10.132013007530926, "y": 54.255965274332006},
        {"x": 10.125351757956555, "y": 54.2537416315447},
        {"x": 10.121545329628342, "y": 54.25262976518862},
        {"x": 10.1101260446437, "y": 54.24873799688302},
        {"x": 10.089190688838528, "y": 54.240953358606696},
        {"x": 10.082529439264153, "y": 54.23817277465062},
        {"x": 10.080626225100046, "y": 54.237616635374195},
        {"x": 10.075868189689778, "y": 54.23483582656345},
        {"x": 10.070158547197458, "y": 54.23205483036714},
        {"x": 10.067303725951296, "y": 54.22982989848838},
        {"x": 10.066352118869245, "y": 54.228717387574044},
        {"x": 10.06540051178719, "y": 54.22649227579349},
        {"x": 10.061594083458978, "y": 54.222598041573804},
        {"x": 10.05969086929487, "y": 54.21925983416582},
        {"x": 10.054932833884603, "y": 54.21647778849808},
        {"x": 10.049223191392285, "y": 54.21592135687366},
        {"x": 10.040658727653804, "y": 54.21759062925591},
        {"x": 10.033997478079431, "y": 54.22204169241398},
        {"x": 10.026384621423004, "y": 54.22704856498273},
        {"x": 10.024481407258897, "y": 54.22816112087297},
        {"x": 10.021626586012736, "y": 54.23038614270175},
        {"x": 10.014965336438362, "y": 54.23372345057153},
        {"x": 10.009255693946043, "y": 54.23650433433578},
        {"x": 10.006400872699881, "y": 54.23706048860261},
        {"x": 10.001642837289616, "y": 54.2392850307181},
        {"x": 9.997836408961401, "y": 54.24150945291306},
        {"x": 9.995933194797296, "y": 54.2426216190413},
        {"x": 9.994981587715241, "y": 54.24373375519058},
        {"x": 9.99402998063319, "y": 54.24540190320478},
        {"x": 9.992126766469083, "y": 54.24706998376848},
        {"x": 9.992126766469083, "y": 54.24818200000578},
        {"x": 9.991175159387028, "y": 54.24929398626606},
        {"x": 9.991175159387028, "y": 54.2504059425497},
        {"x": 9.991175159387028, "y": 54.251517868857086},
        {"x": 9.990223552304974, "y": 54.2537416315447},
        {"x": 9.98927194522292, "y": 54.255965274332006},
        {"x": 9.98927194522292, "y": 54.257632927739785},
        {"x": 9.98927194522292, "y": 54.25874465921108},
        {"x": 9.98927194522292, "y": 54.260968032234096},
        {"x": 9.991175159387028, "y": 54.26207967378659},
        {"x": 9.992126766469083, "y": 54.263747079917664},
        {"x": 9.993078373551135, "y": 54.26541441861271},
        {"x": 9.99402998063319, "y": 54.26652594027893},
        {"x": 9.992126766469083, "y": 54.26819316658351},
        {"x": 9.990223552304974, "y": 54.26986032545557},
        {"x": 9.988320338140866, "y": 54.27152741689642},
        {"x": 9.988320338140866, "y": 54.27263877372918},
        {"x": 9.987368731058814, "y": 54.273750100593496},
        {"x": 9.984513909812655, "y": 54.275972664418326},
        {"x": 9.984513909812655, "y": 54.277639508622684},
        {"x": 9.984513909812655, "y": 54.278750700633786},
    ]
    expected_first_polygon_hole = [
        {"x": 10.041134531194832, "y": 54.27736170593762},
        {"x": 10.02115078247171, "y": 54.255131422337385},
        {"x": 10.02115078247171, "y": 54.254019593450096},
        {"x": 10.02115078247171, "y": 54.25290773458783},
        {"x": 10.022102389553762, "y": 54.251795845750195},
        {"x": 10.023053996635817, "y": 54.250683926936794},
        {"x": 10.024957210799924, "y": 54.250683926936794},
        {"x": 10.02686042496403, "y": 54.25012795628907},
        {"x": 10.02971524621019, "y": 54.24901599251131},
        {"x": 10.031618460374297, "y": 54.24901599251131},
        {"x": 10.034473281620455, "y": 54.24845999938118},
        {"x": 10.03827970994867, "y": 54.24845999938118},
        {"x": 10.041134531194832, "y": 54.24845999938118},
        {"x": 10.043037745358937, "y": 54.24845999938118},
        {"x": 10.044940959523043, "y": 54.24845999938118},
        {"x": 10.04684417368715, "y": 54.24901599251131},
        {"x": 10.048747387851257, "y": 54.24901599251131},
        {"x": 10.050650602015363, "y": 54.24957197814726},
        {"x": 10.055408637425632, "y": 54.25012795628907},
        {"x": 10.05826345867179, "y": 54.25123989009049},
        {"x": 10.060166672835896, "y": 54.252351793915956},
        {"x": 10.062069887000003, "y": 54.25290773458783},
        {"x": 10.063973101164112, "y": 54.254019593450096},
        {"x": 10.06587631532822, "y": 54.255687325540535},
        {"x": 10.067779529492325, "y": 54.25735499018858},
        {"x": 10.067779529492325, "y": 54.25846672915327},
        {"x": 10.067779529492325, "y": 54.259578438144544},
        {"x": 10.067779529492325, "y": 54.26124594543213},
        {"x": 10.067779529492325, "y": 54.26291338528172},
        {"x": 10.067779529492325, "y": 54.26513653351321},
        {"x": 10.067779529492325, "y": 54.266803816012555},
        {"x": 10.06682792241027, "y": 54.269026754448525},
        {"x": 10.064924708246165, "y": 54.270693879604806},
        {"x": 10.063021494082058, "y": 54.271249573005605},
        {"x": 10.06111827991795, "y": 54.27180525891418},
        {"x": 10.059215065753843, "y": 54.27180525891418},
        {"x": 10.057311851589738, "y": 54.27291660825478},
        {"x": 10.05255381617947, "y": 54.27402792762705},
        {"x": 10.048747387851257, "y": 54.27513921703135},
        {"x": 10.045892566605096, "y": 54.27625047646807},
    ]

    first_polygon_exterior = first_polygon["boundingPoly"][0]["normalizedVertices"]
    assert len(first_polygon_exterior) == len(expected_first_polygon_exterior)
    for i, point in enumerate(first_polygon_exterior):
        assert is_almost_equal(point["x"], expected_first_polygon_exterior[i]["x"])
        assert is_almost_equal(point["y"], expected_first_polygon_exterior[i]["y"])

    first_polygon_hole = first_polygon["boundingPoly"][1]["normalizedVertices"]
    assert len(first_polygon_hole) == len(expected_first_polygon_hole)
    for i, point in enumerate(first_polygon_hole):
        assert is_almost_equal(point["x"], expected_first_polygon_hole[i]["x"])
        assert is_almost_equal(point["y"], expected_first_polygon_hole[i]["y"])

    second_polygon_parts = [a for a in annotations if a["mid"] == second_polygon_mid]
    assert len(second_polygon_parts) == 2, "Second polygon should have two parts"

    second_polygon_part_with_hole = next(
        (p for p in second_polygon_parts if len(p["boundingPoly"]) == 2), None
    )
    second_polygon_part_without_hole = next(
        (p for p in second_polygon_parts if len(p["boundingPoly"]) == 1), None
    )

    assert (
        second_polygon_part_with_hole is not None
    ), "Second polygon should have a part with a hole"
    assert (
        second_polygon_part_without_hole is not None
    ), "Second polygon should have a part without a hole"

    expected_second_polygon_part1_exterior = [
        {"x": 9.743281514512121, "y": 54.327336022364776},
        {"x": 9.745184728676229, "y": 54.326226141014146},
        {"x": 9.746136335758283, "y": 54.32511622971394},
        {"x": 9.748991157004443, "y": 54.32345130660728},
        {"x": 9.75089437116855, "y": 54.32123130430449},
        {"x": 9.752797585332656, "y": 54.31956622395528},
        {"x": 9.755652406578816, "y": 54.317346011990956},
        {"x": 9.75945883490703, "y": 54.313460352756536},
        {"x": 9.761362049071137, "y": 54.311239811304716},
        {"x": 9.763265263235244, "y": 54.30957432658446},
        {"x": 9.764216870317298, "y": 54.306798368939404},
        {"x": 9.76802329864551, "y": 54.29458193095311},
        {"x": 9.768974905727562, "y": 54.281806324151766},
        {"x": 9.763265263235244, "y": 54.27625047646807},
        {"x": 9.757555620742924, "y": 54.27180525891418},
        {"x": 9.754700799496762, "y": 54.269582470326306},
        {"x": 9.748991157004443, "y": 54.26624806267213},
        {"x": 9.747087942840336, "y": 54.26458075769461},
        {"x": 9.744233121594176, "y": 54.26346918357892},
        {"x": 9.74232990743007, "y": 54.26180176620838},
        {"x": 9.73947508618391, "y": 54.26069011716278},
        {"x": 9.731862229527483, "y": 54.25791086341763},
        {"x": 9.72044294454284, "y": 54.25679910946609},
        {"x": 9.716636516214628, "y": 54.25624322125008},
        {"x": 9.710926873722308, "y": 54.25624322125008},
        {"x": 9.70616883831204, "y": 54.25624322125008},
        {"x": 9.698555981655614, "y": 54.25624322125008},
        {"x": 9.693797946245349, "y": 54.25679910946609},
        {"x": 9.689991517917132, "y": 54.25791086341763},
        {"x": 9.688088303753027, "y": 54.25791086341763},
        {"x": 9.684281875424814, "y": 54.259578438144544},
        {"x": 9.681427054178654, "y": 54.26124594543213},
        {"x": 9.678572232932492, "y": 54.26346918357892},
        {"x": 9.675717411686334, "y": 54.26569230183903},
        {"x": 9.673814197522226, "y": 54.26847103107829},
        {"x": 9.672862590440173, "y": 54.270138178711726},
        {"x": 9.670959376276066, "y": 54.273472271686934},
        {"x": 9.670007769194013, "y": 54.27569485049564},
        {"x": 9.670007769194013, "y": 54.276806094948725},
        {"x": 9.66905616211196, "y": 54.27791730943482},
        {"x": 9.66905616211196, "y": 54.280139648507614},
        {"x": 9.668104555029906, "y": 54.282361867717135},
        {"x": 9.667152947947853, "y": 54.283472932374146},
        {"x": 9.666201340865799, "y": 54.28513947317607},
        {"x": 9.664298126701691, "y": 54.2862504629222},
        {"x": 9.663346519619639, "y": 54.287361422704656},
        {"x": 9.663346519619639, "y": 54.288472352523826},
        {"x": 9.662394912537584, "y": 54.28958325238011},
        {"x": 9.662394912537584, "y": 54.2906941222739},
    ]
    expected_second_polygon_part1_hole = [
        {"x": 9.72044294454284, "y": 54.29791404627456},
        {"x": 9.700459195819722, "y": 54.283472932374146},
        {"x": 9.700459195819722, "y": 54.282361867717135},
        {"x": 9.701410802901774, "y": 54.28125077309509},
        {"x": 9.702362409983827, "y": 54.280139648507614},
        {"x": 9.702362409983827, "y": 54.27902849395432},
        {"x": 9.702362409983827, "y": 54.27791730943482},
        {"x": 9.702362409983827, "y": 54.276806094948725},
        {"x": 9.70331401706588, "y": 54.27569485049564},
        {"x": 9.705217231229987, "y": 54.274583576075166},
        {"x": 9.70616883831204, "y": 54.273472271686934},
        {"x": 9.709023659558202, "y": 54.27291660825478},
        {"x": 9.710926873722308, "y": 54.27291660825478},
        {"x": 9.71473330205052, "y": 54.27291660825478},
        {"x": 9.716636516214628, "y": 54.27291660825478},
        {"x": 9.718539730378735, "y": 54.27291660825478},
        {"x": 9.721394551624895, "y": 54.273472271686934},
        {"x": 9.723297765789003, "y": 54.27402792762705},
        {"x": 9.72520097995311, "y": 54.27513921703135},
        {"x": 9.727104194117215, "y": 54.27625047646807},
        {"x": 9.728055801199268, "y": 54.27736170593762},
        {"x": 9.729959015363375, "y": 54.27958407497672},
        {"x": 9.730910622445428, "y": 54.281806324151766},
        {"x": 9.730910622445428, "y": 54.2845839670665},
        {"x": 9.730910622445428, "y": 54.28569497179461},
        {"x": 9.729959015363375, "y": 54.28680594655886},
        {"x": 9.728055801199268, "y": 54.29013869107229},
        {"x": 9.727104194117215, "y": 54.29236037093575},
        {"x": 9.724249372871057, "y": 54.29513730223186},
        {"x": 9.722346158706948, "y": 54.29680337112751},
    ]

    second_polygon_part1_exterior = second_polygon_part_with_hole["boundingPoly"][0][
        "normalizedVertices"
    ]
    assert len(second_polygon_part1_exterior) == len(expected_second_polygon_part1_exterior)
    for i, point in enumerate(second_polygon_part1_exterior):
        assert is_almost_equal(point["x"], expected_second_polygon_part1_exterior[i]["x"])
        assert is_almost_equal(point["y"], expected_second_polygon_part1_exterior[i]["y"])

    second_polygon_part1_hole = second_polygon_part_with_hole["boundingPoly"][1][
        "normalizedVertices"
    ]
    assert len(second_polygon_part1_hole) == len(expected_second_polygon_part1_hole)
    for i, point in enumerate(second_polygon_part1_hole):
        assert is_almost_equal(point["x"], expected_second_polygon_part1_hole[i]["x"])
        assert is_almost_equal(point["y"], expected_second_polygon_part1_hole[i]["y"])

    expected_second_polygon_part2_exterior = [
        {"x": 9.833684187307194, "y": 54.376695428400765},
        {"x": 9.8355874014713, "y": 54.376695428400765},
        {"x": 9.837490615635408, "y": 54.37614115764688},
        {"x": 9.840345436881567, "y": 54.37503259369006},
        {"x": 9.843200258127728, "y": 54.37447830048706},
        {"x": 9.844151865209781, "y": 54.373369691631616},
        {"x": 9.846055079373889, "y": 54.372261052843264},
        {"x": 9.848909900620047, "y": 54.369489324913275},
        {"x": 9.851764721866207, "y": 54.366163004438846},
        {"x": 9.852716328948262, "y": 54.36505417107696},
        {"x": 9.852716328948262, "y": 54.36394530777921},
        {"x": 9.852716328948262, "y": 54.3628364145452},
        {"x": 9.850813114784154, "y": 54.361173018562845},
        {"x": 9.8498615077021, "y": 54.359509555221706},
        {"x": 9.848909900620047, "y": 54.35784602452046},
        {"x": 9.847958293537994, "y": 54.35673696663003},
        {"x": 9.847958293537994, "y": 54.35562787880078},
        {"x": 9.847958293537994, "y": 54.35451876103234},
        {"x": 9.847958293537994, "y": 54.353409613324295},
        {"x": 9.8498615077021, "y": 54.35230043567628},
        {"x": 9.851764721866207, "y": 54.35174583562464},
        {"x": 9.853667936030316, "y": 54.35119122808787},
        {"x": 9.855571150194423, "y": 54.350636613065895},
        {"x": 9.859377578522635, "y": 54.345644741026426},
        {"x": 9.859377578522635, "y": 54.3445353537875},
        {"x": 9.860329185604687, "y": 54.34342593660546},
        {"x": 9.860329185604687, "y": 54.34120701241043},
        {"x": 9.860329185604687, "y": 54.33510435326343},
        {"x": 9.858425971440582, "y": 54.33343983446173},
        {"x": 9.855571150194423, "y": 54.33122037124456},
        {"x": 9.852716328948262, "y": 54.3295556952188},
        {"x": 9.847006686455941, "y": 54.327336022364776},
        {"x": 9.841297043963621, "y": 54.326226141014146},
        {"x": 9.8355874014713, "y": 54.32567118910777},
        {"x": 9.83273258022514, "y": 54.32567118910777},
        {"x": 9.828926151896928, "y": 54.32567118910777},
        {"x": 9.8213132952405, "y": 54.326226141014146},
        {"x": 9.816555259830233, "y": 54.327336022364776},
        {"x": 9.814652045666127, "y": 54.3278909518091},
        {"x": 9.81274883150202, "y": 54.32844587376619},
        {"x": 9.810845617337913, "y": 54.3295556952188},
        {"x": 9.8070391890097, "y": 54.331775248279165},
        {"x": 9.805135974845594, "y": 54.33343983446173},
        {"x": 9.80418436776354, "y": 54.33454952114954},
        {"x": 9.803232760681485, "y": 54.33565917789071},
        {"x": 9.802281153599433, "y": 54.336768804685605},
        {"x": 9.801329546517378, "y": 54.338433188729574},
        {"x": 9.801329546517378, "y": 54.34231648947989},
        {"x": 9.801329546517378, "y": 54.34342593660546},
        {"x": 9.800377939435325, "y": 54.3445353537875},
        {"x": 9.800377939435325, "y": 54.346754098322606},
        {"x": 9.799426332353272, "y": 54.34786342567645},
        {"x": 9.799426332353272, "y": 54.348972723088345},
        {"x": 9.797523118189165, "y": 54.350081990558685},
        {"x": 9.796571511107112, "y": 54.35174583562464},
        {"x": 9.795619904025058, "y": 54.35285502824281},
        {"x": 9.794668296943005, "y": 54.353964190920784},
        {"x": 9.793716689860952, "y": 54.35562787880078},
        {"x": 9.7927650827789, "y": 54.35673696663003},
        {"x": 9.791813475696845, "y": 54.35784602452046},
        {"x": 9.791813475696845, "y": 54.35895505247248},
        {"x": 9.790861868614794, "y": 54.36006405048648},
        {"x": 9.790861868614794, "y": 54.361173018562845},
    ]

    second_polygon_part2_exterior = second_polygon_part_without_hole["boundingPoly"][0][
        "normalizedVertices"
    ]
    assert len(second_polygon_part2_exterior) == len(expected_second_polygon_part2_exterior)
    for i, point in enumerate(second_polygon_part2_exterior):
        assert is_almost_equal(point["x"], expected_second_polygon_part2_exterior[i]["x"])
        assert is_almost_equal(point["y"], expected_second_polygon_part2_exterior[i]["y"])

    shutil.rmtree(temp_dir)
