namespace_to_url_base = {
    "GO":        "http://purl.obolibrary.org/obo/GO_",
    "CHEBI":     "http://purl.obolibrary.org/obo/CHEBI_",
    "CL":        "http://purl.obolibrary.org/obo/CL_",
    "CLO":       "http://purl.obolibrary.org/obo/CLO_",
    "OBI":       "http://purl.obolibrary.org/obo/OBI_",
    "PATO":      "http://purl.obolibrary.org/obo/PATO_",
    "PO":        "http://purl.obolibrary.org/obo/PO_",
    "PR":        "http://purl.obolibrary.org/obo/PR_",
    "XAO":       "http://purl.obolibrary.org/obo/XAO_",
    "ZFA":       "http://purl.obolibrary.org/obo/ZFA_",
    "BFO":       "http://purl.obolibrary.org/obo/BFO_",
    "BTO":       "http://purl.obolibrary.org/obo/BTO_",
    "CARO":      "http://purl.obolibrary.org/obo/CARO_",
    "DOID":      "http://purl.obolibrary.org/obo/DOID_",
    "FMA":       "http://purl.obolibrary.org/obo/FMA_",
    "IAO":       "http://purl.obolibrary.org/obo/IAO_",
    "UBERON":    "http://purl.obolibrary.org/obo/UBERON_",
    "ENVO":      "http://purl.obolibrary.org/obo/ENVO_",
    "HP":        "http://purl.obolibrary.org/obo/HP_",
    "APO":       "http://purl.obolibrary.org/obo/APO_",
    "FYPO":      "http://purl.obolibrary.org/obo/FYPO_",
    "FBdv":      "http://purl.obolibrary.org/obo/FBdv_",
    "FBbt":      "http://purl.obolibrary.org/obo/FBbt_",
    "FBcv":      "http://purl.obolibrary.org/obo/FBcv_",
    "EGID":      "http://www.ncbi.nlm.nih.gov/gene/",
    "taxonomy":  "http://www.ncbi.nlm.nih.gov/taxonomy/",
    "stringdb":  "http://string-db.org/interactions/",
    "stitchdb":  "http://stitchdb-db.org/interactions/",
    "MESH":      "http://www.nlm.nih.gov/cgi/mesh/2016/MB_cgi?field=uid&term=",
    # temporary mapping and URL
    "hm":        "http://ltl.mml.cam.ac.uk/lion/"
}

def expand_namespace(url):
    """Expand namespace in URL if possible, return URL otherwise."""
    if ':' not in url:
        return url
    ns, rest = url.split(':', 1)
    if ns not in namespace_to_url_base:
        return url
    else:
        return namespace_to_url_base[ns] + rest
    
